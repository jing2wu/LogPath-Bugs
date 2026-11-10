# [Bug] [Master] WorkflowSerialCoordinator cannot restart after HA failover, serial dispatch dies silently

- Issue: https://github.com/apache/dolphinscheduler/issues/18624
- Opened by yaodongen on 2026-09-08, closed on 2026-09-09
- Labels: bug, need more information, backend
- Fix commit: def57c5eb07acbfa624c8b5d4ce2e2e17c0b5633

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

`SERIAL_WAIT` / `SERIAL_DISCARD` / `SERIAL_PRIORITY` workflows stop being dispatched after the master coordinator changes hands, and never recover. The master still reports itself ACTIVE and holds the leader node, so no peer takes over either.

The only trace is a single swallowed exception:

```
2026-09-08 03:24:57.607 INFO  o.a.d.s.m.e.w.s.WorkflowSerialCoordinator - WorkflowSerialCoordinator starting...
2026-09-08 03:24:57.607 ERROR o.a.d.r.a.h.AbstractHAServer - Trigger ServerStatusChangeListener from STAND_BY -> ACTIVE error
java.lang.IllegalStateException: InternalThread is already started
	at org.apache.dolphinscheduler.server.master.engine.workflow.serial.WorkflowSerialCoordinator.start(WorkflowSerialCoordinator.java:83)
	at org.apache.dolphinscheduler.server.master.engine.MasterCoordinator$MasterCoordinatorListener.changeToActive(MasterCoordinator.java:98)
	at org.apache.dolphinscheduler.registry.api.ha.AbstractServerStatusChangeListener.change(AbstractServerStatusChangeListener.java:33)
```

Note the `starting...` with no matching `started...` — that mismatch is the only way to detect the state from outside.

**Root cause.** `WorkflowSerialCoordinator.close()` does not reset `internalThread`:

```java
@Override
public void close() {
    flag = false;
}
```

while `start()` refuses to run if it is still set:

```java
public synchronized void start() {
    if (flag) { throw new IllegalStateException("WorkflowSerialCoordinator is already started"); }
    if (internalThread != null) { throw new IllegalStateException("InternalThread is already started"); }
    ...
}
```

So the coordinator is single-use, but `MasterCoordinatorListener` treats it as restartable — `changeToStandBy()` calls `close()` and `changeToActive()` calls `start()` on the same instance:

```java
public void changeToActive()  { taskGroupCoordinator.start(); workflowSerialCoordinator.start(); ... }
public void changeToStandBy() { taskGroupCoordinator.close(); workflowSerialCoordinator.close(); ... }
```

The sibling `TaskGroupCoordinator.close()` in that same listener already handles this correctly (interrupts the thread and nulls the field), which is why task groups survive a failover and serial dispatch does not.

Two things make the failure silent rather than loud:

1. `AbstractHAServer.statusChange` sets `serverStatus` **before** notifying the listeners, and swallows listener exceptions:

```java
private void statusChange(ServerStatus targetStatus) {
    final ServerStatus originStatus = serverStatus;
    serverStatus = targetStatus;                 // already ACTIVE
    synchronized (this) {
        try {
            serverStatusChangeListeners.forEach(listener -> listener.change(originStatus, serverStatus));
        } catch (Exception ex) {
            log.error("Trigger ServerStatusChangeListener from {} -> {} error", originStatus, targetStatus, ex);
        }
    }
}
```

The master therefore ends up ACTIVE with a dead coordinator, holding `/nodes/master-coordinator`, so no other master will take over.

2. `taskGroupCoordinator.start()` runs first and succeeds, so task-group scheduling keeps working and the master looks healthy.


### What you expected to happen

After an `ACTIVE -> STAND_BY -> ACTIVE` transition the serial coordinator restarts and queued `t_ds_serial_command` rows are dispatched, as they are on a fresh master process.

### How to reproduce

1. Run two masters with the JDBC registry.
2. Create a workflow whose execution type is `SERIAL_WAIT` and put it on a schedule.
3. Make the coordinator change hands twice, so that one master goes `ACTIVE -> STAND_BY -> ACTIVE` within the same JVM. Restarting both masters together is enough; so is any event that reaps the leader's ephemeral node (with `REGISTRY_TERM_REFRESH_INTERVAL=2s` and `REGISTRY_TERM_EXPIRE_TIMES=3`, a 6s stall does it).
4. That master logs the exception above.
5. `t_ds_serial_command` rows stay at `state=0` (WAITING) indefinitely and workflow instances stay in `SERIAL_WAIT`.

Observed on 3.4.2: instances queued for 6h+, the oldest serial command waiting since 04:00 UTC. Restarting the ACTIVE master (fresh JVM, `internalThread` null) recovers immediately — the queued commands launch within one 5s round.

A unit test reproduces it directly: `start()` -> `close()` -> `start()` on one instance throws `InternalThread is already started`.

### Anything else

- Affects every 3.4.x. `WorkflowSerialCoordinator` was introduced in 3.4.0 by #17531 (DSIP-92, refactor workflow serial strategy) and `close()` has been unchanged since. Still present on `dev` and in 3.4.3.
- Single-master deployments never hit it: `AbstractHAServer` only returns to ACTIVE from a REMOVE event carrying *another* server's identify, which cannot occur when one master is the sole writer of that path. That is presumably why this has gone unreported.
- Workaround until the fix ships: run a single master, or restart the ACTIVE master after any failover and confirm `starting...`/`started...` are paired.

### Version

3.4.2

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by ruanwenjun on 2026-09-08

I'm curious as to why your master coordinator node didn't shut itself down after it became inactive. Is this happen in the production?
This might related to the jdbc registry plugin https://github.com/apache/dolphinscheduler/pull/18416.

## Comment by yaodongen on 2026-09-09

Good questions — I dug into both.

### Why it did not shut itself down

It never disconnected, so that path was never reached. `RegistryStoppable` → `System.exit(1)` fires on registry *connection loss*; here the JDBC registry was healthy throughout. The master went STAND_BY from an ordinary `REMOVE` event on `/nodes/master-coordinator`, not from an expired session.

The trigger is that `serverIdentify` is `masterConfig.getMasterAddress()`, which on a StatefulSet is stable across restarts:

1. We restarted both masters. The previous process's ephemeral coordinator node was still present, holding the **same** address string.
2. The new process ran `participateElection()`:

```java
if (registry.acquireLock(electionLock)) {
    if (!registry.exists(selectorPath)) {
        registry.put(selectorPath, serverIdentify, true);
        return true;
    }
    return serverIdentify.equals(registry.get(selectorPath));   // true -- and no put()
}
```

The path existed and its value equalled its own identify, so it returned `true` and became ACTIVE **without ever registering an ephemeral node of its own**.

3. The dead process's client row was then purged and its ephemeral node deleted. The resulting `REMOVE` carried that same address, which the live master reads as "that was me" and goes STAND_BY.

master-0, where the two `serverStartupTime` values are the old and new process at the same address:

```
03:24:39.332  WorkflowSerialCoordinator started...
03:24:40.374  Server MasterServerMetadata(...serverStartupTime=1787709361200...) removed
03:24:40.376  Server MasterServerMetadata(...serverStartupTime=1788837878575...) added
03:24:58.479  The status is standby now.
```

master-1 went through the same thing slightly earlier, so when it picked the role back up it was on its second `changeToActive()` in one JVM:

```
03:23:54.550  TaskGroupCoordinator closed            # -> STAND_BY
03:24:57.606  The status is active now.
03:24:57.607  WorkflowSerialCoordinator starting...
03:24:57.607  ERROR AbstractHAServer - Trigger ServerStatusChangeListener from STAND_BY -> ACTIVE error
              java.lang.IllegalStateException: InternalThread is already started
```

### On #18416

I don't think it covers this. That one handles a heartbeat row purged while the database is unavailable, so the client enters the disconnect state machine and the service terminates. Here the database was fine and no session expired — the flip came from a stale ephemeral node with a reused identity after a restart, which #18416 would not have prevented.

More to the point, the coordinator defect is independent of *how* the flip happens. Any `ACTIVE -> STAND_BY -> ACTIVE` within one JVM breaks it, including a perfectly legitimate failover (peer dies, this master takes over, later steps down, later takes over again), because `close()` leaves `internalThread` set. `TaskGroupCoordinator.close()`, invoked from the same listener one line earlier, already nulls it — this PR just makes the two match.

### Is this production

Our internal dev/staging cluster on EKS, not customer-facing. But the workflows are our real ETL pipeline, and instances sat in `SERIAL_WAIT` for 6h+ before anyone noticed: the master keeps reporting ACTIVE and keeps holding the leader node, so nothing alerts and no peer takes over.
