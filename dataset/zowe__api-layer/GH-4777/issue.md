# Peer node read timeout too short (15s) — causes cascading retry loop under load

- Issue: https://github.com/zowe/api-layer/issues/4777
- Opened by balhar-jakub on 2026-07-03, closed on 2026-08-31
- Labels: bug, Priority: High, size/S
- Fix commit: c7c1051bad5d72225e5b982184a1c12961574d8c

## Report

## Problem

The `peer-node-read-timeout-ms` is set to 15,000ms (15 seconds) in `discovery-service/src/main/resources/application.yml`. Under load — especially on z/OS — peer batch replication calls can exceed this timeout, triggering a cascading retry loop that the code itself warns about.

### Root cause

`ApimlPeerEurekaNode.ReplicationTaskProcessor` catches read timeouts via `maybeReadTimeOut()` and returns `ProcessingResult.Congestion`. The Netflix batcher then waits only 1,000ms (`SERVER_UNAVAILABLE_SLEEP_TIME_MS`) before retrying. Read timeouts are **never escalated to permanent errors** — unlike network connection failures, which are gated by `maxPeerRetries`.

Retry cycle: **15s timeout → 1s delay → 15s timeout → 1s delay → … forever**

With `max-threads-for-peer-replication: 6`, all six threads can be stuck in this loop simultaneously, leaving no capacity for replication to other peers.

### The code explicitly warns about this

```java
// ApimlPeerEurekaNode.java lines 421 and 458
log.error("It seems to be a socket read timeout exception, it will retry later. "
    + "if it continues to happen and some eureka node occupied all the cpu time, "
    + "you should set property 'eureka.server.peer-node-read-timeout-ms' to a bigger value", e);
```

The authors anticipated this exact scenario.

### Why read timeouts never stop

```java
// Lines 418-431
} catch (Throwable e) {
    networkIssueCounter.fail(e.getLocalizedMessage());
    if (maybeReadTimeOut(e)) {
        return ProcessingResult.Congestion;  // ← ALWAYS retries, never PermanentError
    } else if (isNetworkConnectException(e) && !networkIssueCounter.hasReachedMax()) {
        return ProcessingResult.TransientError;
    } else {
        return ProcessingResult.PermanentError;  // ← other errors DO escalate
    }
}
```

### Affected properties

| Property | Default | Location |
|---|---|---|
| `eureka.server.peer-node-read-timeout-ms` | `15000` | `discovery-service/src/main/resources/application.yml:97`, `apiml/src/main/resources/application.yml:19` |
| `eureka.server.max-threads-for-peer-replication` | `6` | Same files |

### Workaround (zowe.yaml)

These properties can be overridden through `zowe.environments` in `zowe.yaml`, since Spring Boot picks up environment variables via relaxed binding:

```yaml
zowe:
  environments:
    EUREKA_SERVER_PEER_NODE_READ_TIMEOUT_MS: 30000
    EUREKA_SERVER_MAX_THREADS_FOR_PEER_REPLICATION: 10
```

Note: `zowe.environments` is global to all Zowe components. There is no component-specific escape hatch for arbitrary environment variables. However, only the Discovery Service consumes `eureka.server.*` properties, so the global scope has no unintended effects.

## Comment by balhar-jakub on 2026-07-07

## Problem Analysis — Peer node read timeout causes cascading retry loop (#4777)

### Refined Problem Statement

When Discovery Service instances replicate state across peers, batch replication calls can exceed the 15-second `peer-node-read-timeout-ms` under load — especially on z/OS where HTTP throughput is slower. The `ReplicationTaskProcessor` catches these socket read timeouts and returns `ProcessingResult.Congestion`, which schedules a retry after just 1 second (`SERVER_UNAVAILABLE_SLEEP_TIME_MS`). The retry hits the same 15-second timeout, and the cycle repeats **forever**.

This creates a 16-second loop per thread (15s timeout + 1s wait) with no escape hatch. Network connection failures are properly gated — `networkIssueCounter` tracks successive failures and escalates to `PermanentError` after `maxPeerRetries` (default 10) — but the `hasReachedMax()` check is **not applied** to read timeouts. The result: all 6 replication threads can be stuck simultaneously with no capacity to serve other peers.

**Real-world scenario:** In a 2-node DS HA setup on z/OS under moderate load, batch replication calls regularly take 17-20 seconds. Node A's 6 threads all time out replicating to Node B, returning Congestion every 16 seconds. Node B's 6 threads do the same to Node A. No replication succeeds. Service registrations and heartbeats queued for replication are dropped or delayed, causing registered services to disappear from the registry on non-originating nodes.

### Current Architecture Touchpoints

| Component | File | Role |
|---|---|---|
| `ApimlPeerEurekaNode.ReplicationTaskProcessor` | `apiml-common/.../ApimlPeerEurekaNode.java:398-471` | Core replication logic; `process(task)` and `process(tasks)`. Read timeouts caught at lines 420-423 and 457-460. |
| `NetworkIssueCounter` | Inner class, same file:363-396 | Tracks consecutive failures; `hasReachedMax()` checks against `maxPeerRetries` (10). Used for connect exceptions but NOT for read timeouts. |
| `maybeReadTimeOut()` | Same file:558-574 | Detects socket read timeouts via regex `*read*time*out*` on IOException messages. |
| `EurekaConfig` | `discovery-service/.../EurekaConfig.java:52-53` | Injects `apiml.discovery.maxPeerRetries` (default 10). |
| `RefreshablePeerEurekaNodes` | `discovery-service/.../RefreshablePeerEurekaNodes.java:100` | Creates `ApimlPeerEurekaNode` with `maxPeerRetries`. |
| `application.yml` (discovery-service) | Line 97 | `peer-node-read-timeout-ms: 15000` |
| `application.yml` (apiml) | Line 19 | `peer-node-read-timeout-ms: 15000` |
| `ApimlDependencyLogHider` | `apiml-utility/.../ApimlDependencyLogHider.java:30` | Already suppresses `eureka.server.peer-node-read-timeout-ms` from startup logs (minor privacy concern). |

### Scope

**In:**
- Apply `networkIssueCounter.hasReachedMax()` gate to read timeout handling in both `process(task)` and `process(tasks)` methods
- Escalate read timeouts to `PermanentError` after `maxPeerRetries` consecutive failures (matching connect-exception behavior)
- Evaluate and potentially increase the default `peer-node-read-timeout-ms` value

**Out:**
- Changing the `SERVER_UNAVAILABLE_SLEEP_TIME_MS` (1000ms) — this is a Netflix Eureka constant
- Modifying how `ProcessingResult.Congestion` vs `TransientError` flows through the Netflix batcher
- Changing the `max-threads-for-peer-replication` default (6) — separate concern
- Any change to the single-task `process(task)` endpoint timeout behavior (different code path)

### Acceptance Criteria

1. **AC1:** After `maxPeerRetries` consecutive read timeout failures, the `ReplicationTaskProcessor` escalates to `PermanentError` instead of returning `Congestion` — in both `process(task)` and `process(tasks)` methods.
2. **AC2:** A successful replication resets the counter so transient read timeouts don't accumulate across healthy periods.
3. **AC3:** Existing behavior for connection failures and non-read-timeout errors is unchanged.
4. **AC4:** Unit tests cover: (a) read timeout escalates after N retries, (b) successful replication resets counter, (c) connection failure behavior unchanged.
5. **AC5:** Default `peer-node-read-timeout-ms` increased to a value that accommodates z/OS batch replication latency (exact value TBD by architect based on z/OS performance data).

### Design Questions for Architect

1. **Should read timeouts use the same `networkIssueCounter` or a separate counter?** The counter currently tracks ALL failures (connect + read timeout) but `hasReachedMax()` is only checked in the connect-exception branch. Could simply add the check to the read-timeout branch, but this means connect failures "consume" retry budget for read timeouts and vice versa. Is that desirable, or should read timeouts have their own counter?

2. **What's the appropriate new default for `peer-node-read-timeout-ms`?** The current 15s is too low for z/OS. What value balances responsiveness (fail fast on a genuinely dead peer) with z/OS throughput? Consider: 30s, 45s, 60s? Should this be configurable per-environment?

3. **`PermanentError` behavior:** When read timeouts are escalated, what happens to the replication tasks? Are they dropped? Does the peer get marked as unavailable? What's the downstream impact on service registry consistency?

4. **Logging and observability:** The existing log warning (lines 421, 458) already tells operators about the problem. After escalation to PermanentError, should there be additional logging or metrics? Could this tie into OTel signals (related to #4704)?

5. **ApimlDependencyLogHider impact:** This class already suppresses `eureka.server.peer-node-read-timeout-ms` from logs. If we change the property name or add new properties, does this need updating?

6. **Backward compatibility:** If a site has already worked around this by setting `peer-node-read-timeout-ms` very high in `zowe.yaml`, will the new escalation logic interfere? (It shouldn't — if timeouts are high enough, read timeouts won't occur and the counter won't trigger.)

### Constraints

- Must not break Netflix Eureka's internal batching retry mechanics (`TaskDispatchers`, `TaskExecutors`)
- Must not change the public API of `ProcessingResult` enum
- Changes must be compatible with both z/OS and non-z/OS deployments
- Config changes (timeout value) must be backwards-compatible (existing `zowe.yaml` overrides continue to work)

## Comment by balhar-jakub on 2026-07-07

## Solution Design — Socket Read Timeout Escalation for Peer Replication (#4777)

### Architecture Overview

The fix is confined to `ApimlPeerEurekaNode.ReplicationTaskProcessor` — a single class in `apiml-common`. No new classes, no API changes, no configuration schema changes. The change addresses a **missing gate check**: `networkIssueCounter.hasReachedMax()` is never consulted in the read-timeout branch, even though `networkIssueCounter.fail()` IS called for read timeouts (lines 419, 456). The counter increments but the guard is bypassed.

### Root Cause (confirmed from code)

In `ReplicationTaskProcessor` the counter (`networkIssueCounter`) tracks ALL exceptions via `fail()` at the top of the catch block, but the `hasReachedMax()` gate is only checked in the *connection failure* branch. The read-timeout branch returns `Congestion` unconditionally:

```
process(task) lines 418-431:      process(tasks) lines 455-468:
  catch (Throwable e) {             catch (Throwable e) {
    fail(e.getMessage());             fail(e.getMessage());
    if (maybeReadTimeOut(e))          if (maybeReadTimeOut(e))
      return Congestion;  ← BUG       return Congestion;  ← BUG
    else if (isNetwork... &&          else if (isNetwork... &&
             !hasReachedMax())                 !hasReachedMax())
      return TransientError;            return TransientError;
    else                              else
      return PermanentError;            return TransientError;
  }                                 }
```

### Solution

**In both `process(task)` and `process(tasks)`: Insert a `hasReachedMax()` gate inside the `maybeReadTimeOut()` branch before returning `Congestion`. If the counter has reached max, return `PermanentError` instead.**

```java
// process(ReplicationTask task) — replace lines 420-423
if (maybeReadTimeOut(e)) {
    if (networkIssueCounter.hasReachedMax()) {
        log.error("Read timeout from peer {} has repeated {} times (max={}). "
            + "Escalating to permanent error; replication task will be dropped.",
            peerId, networkIssueCounter.getCountText(), maxPeerRetries, e);
        return ProcessingResult.PermanentError;
    }
    log.error("It seems to be a socket read time out exception ...", e);
    return ProcessingResult.Congestion;
}
```

```java
// process(List<ReplicationTask> tasks) — replace lines 457-460
if (maybeReadTimeOut(e)) {
    if (networkIssueCounter.hasReachedMax()) {
        log.error("Read timeout from peer {} has repeated {} times (max={}). "
            + "Escalating to permanent error; {} batch replication tasks will be dropped.",
            peerId, networkIssueCounter.getCountText(), maxPeerRetries, tasks.size(), e);
        return ProcessingResult.PermanentError;
    }
    log.error("It seems to be a socket read time out exception ...", e);
    return ProcessingResult.Congestion;
}
```

**Why `getCountText()` needs visibility:** Currently `NetworkIssueCounter.getCountText()` is `private`. Expose it as package-private so the log message can include the current count (e.g. "10+/10"). Minimal change — same class, same package.

### Design Decisions

**Decision 1: Use the same `networkIssueCounter` (shared counter).**

The PM's question asked whether read timeouts should use a separate counter. We use the SAME counter because:
- `fail()` is already called for read timeouts at lines 419 and 456 — the counter already tracks all exception types together
- Connection failures and read timeouts both indicate the peer is unhealthy; sharing the retry budget means a peer that fails in BOTH ways gets cut off faster, which is correct
- A separate counter adds complexity with no clear benefit: if a peer fails reads 10 times, it's broken regardless of whether those 10 failures included connection failures
- The current connection-failure retry budget of 10 (`maxPeerRetries`) means 10 total network-level errors of any kind → escalation. This is a reasonable threshold for read timeouts too
- The acceptance criteria say "consecutive" read timeout failures trigger escalation, but since `fail()` is called for all exceptions, a single successful replication resets the counter (line 408) — providing the "consecutive" behavior implicitly

**Decision 2: New default `peer-node-read-timeout-ms` = 30000 (30 seconds).**

- Current: 15000ms (15s). Eureka Netflix default: 200ms. The 15s is already generous for cloud deployments but insufficient for z/OS batch replication under load
- 30s doubles the window while still providing timely failure detection
- 45s or 60s was considered but risks delaying detection of genuinely hung peers
- Operators with exceptionally large registries can override to 45s or 60s via zowe.yaml: `components.discovery.eureka.server.peer-node-read-timeout-ms`
- See Netflix EurekaServerConfig: `peerNodeReadTimeoutMs` maps to `eureka.server.peer-node-read-timeout-ms`

**Decision 3: PermanentError drops the task.**

When the read timeout escalates to `PermanentError`, the batcher framework discards the task from the replication queue. No retry. `handleFailure()` is NOT called (consistent with how connection-failure → PermanentError works at line 429). This means:
- The individual replication event is lost for that peer
- The peer will catch up via the next full registry sync cycle
- This is the same behavior as existing connection-failure escalation at line 429
- Six threads are freed for replication to OTHER peers — the key fix

**Decision 4: Escalation gets a distinct, visible log message.**

The escalation log is at ERROR level with actionable information (peer ID, count, max). It is NOT added to `ApimlDependencyLogHider` because:
- This is a genuine operational event that operators need to see
- It fires at most once per peer per recovery cycle
- Unlike the existing "It seems to be a socket read time out" message (which fires every 15s per thread and IS properly hidden), the escalation log fires exactly once when the counter hits max

**Decision 5: Backward compatibility is fully maintained.**

- No new configuration properties, no removed properties
- `eureka.server.peer-node-read-timeout-ms` continues to work; only its default changes
- `apiml.discovery.maxPeerRetries` continues to work; now also gates read timeouts
- Existing `zowe.yaml` overrides of either property are honored
- `ApimlDependencyLogHider` already hides `"eureka.server.peer-node-read-timeout-ms"` (the property name in the log message); the new escalation log message does NOT contain that string, so it passes through the filter as intended

### Files to Modify

| File | Change | Area |
|---|---|---|
| `apiml-common/src/main/java/org/zowe/apiml/product/eureka/client/ApimlPeerEurekaNode.java` | Add `hasReachedMax()` gate in both read-timeout branches (lines 420-423, 457-460); expose `getCountText()` to package-private | Core fix |
| `discovery-service/src/main/resources/application.yml` | Line 82: `peer-node-read-timeout-ms: 15000` → `30000` | Timeout default |
| `apiml/src/main/resources/application.yml` | Line 19: `peer-node-read-timeout-ms: 15000` → `30000` | Timeout default |
| `apiml-common/src/test/java/org/zowe/apiml/product/eureka/client/ReplicationTaskProcessorTest.java` | Add tests for read-timeout escalation after N retries + counter reset | Tests |

### Unit Test Plan (AC4)

1. **Read timeout escalates after N retries (single task):** Configure `TestableInstanceReplicationTask` to throw `SocketTimeoutException` N times. Verify: first N-1 calls return `Congestion`, Nth call returns `PermanentError`. Test with `process(task)`.

2. **Read timeout escalates after N retries (batch):** Same but with `process(List<ReplicationTask>)`. Use `replicationClient.withReadtimeOut(N)`.

3. **Successful replication resets counter:** Throw N-1 read timeouts, then have one success, then throw one more read timeout. Verify: the last read timeout returns `Congestion` (not `PermanentError`) because the counter was reset.

4. **Connection failure behavior unchanged:** Verify existing tests still pass — connection failures still escalate after N retries, SSL exceptions still return `PermanentError` immediately, 503 still returns `Congestion`.

### Independent Implementation Areas

This is a single, cohesive change across one Java file + two YAML files + one test file. One engineer task can handle the entire implementation.

1. **Area 1 (core fix + tests + config):** All changes in ApimlPeerEurekaNode.java, both YAML files, and ReplicationTaskProcessorTest.java.

### Edge Cases & Risks

- **Risk: Counter shared between connection failures and read timeouts** — a peer with both types of failures exhausts the retry budget faster. Mitigation: this is acceptable; the peer IS unhealthy. On z/OS, network partitions typically present as either connection failures OR read timeouts, not both simultaneously.
- **Risk: 30s timeout may still be too low for some large z/OS deployments** — mitigation: operators can override via zowe.yaml. The 30s default is a safe middle ground.
- **Edge case: Counter race condition** — `AtomicInteger` is used for the counter, so concurrent read timeout + connection failure increments are thread-safe. The `hasReachedMax()` check is atomic.

### Answering PM's Design Questions

1. **Separate counter?** No — same counter. Simpler, already tracks all exception types, and correctly treats the peer as unhealthy regardless of failure mode.

2. **New default timeout?** 30s. Doubles current default. Balances z/OS latency with timely failure detection.

3. **PermanentError task behavior?** Tasks are dropped from the replication queue. The peer catches up via full registry sync. Same behavior as connection-failure escalation.

4. **Additional logging?** Yes — a distinct ERROR-level log for escalation. NOT hidden by ApimlDependencyLogHider.

5. **ApimlDependencyLogHider impact?** No changes needed. The existing "eureka.server.peer-node-read-timeout-ms" filter continues to hide the per-attempt log. The new escalation log has a different message and intentionally passes through.

6. **Backward compatibility?** Fully maintained. No config schema changes. Existing overrides honored.

### AC Traceability

| AC | How Addressed |
|---|---|
| AC1: Read timeout escalates to PermanentError after maxPeerRetries | `hasReachedMax()` gate inserted in both `process(task)` and `process(tasks)` read-timeout branches |
| AC2: Successful replication resets counter | Already works — `networkIssueCounter.success()` at line 408 resets counter on any 2xx response |
| AC3: Connection failure behavior unchanged | Connection failure path (lines 424-426, 461-463) is not modified |
| AC4: Unit tests | Four test cases outlined above |
| AC5: Default timeout increased for z/OS | 15000 → 30000 in both YAML files |
