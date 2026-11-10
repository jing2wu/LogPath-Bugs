# CEF: empty value in numerically-typed field logs a stack trace per message

- Issue: https://github.com/Graylog2/graylog2-server/issues/26833
- Opened by fpetersen-gl on 2026-07-30, closed on 2026-08-03
- Labels: bug, triaged, needs-backport
- Fix commit: 199fefc3ff18dd80d8e3fa211ee5752d7c930685

## Report

## Expected Behavior

A CEF message with an empty value for a numerically-typed extension (e.g. `cfp1=`) should
be handled quietly — the field skipped without logging a stack trace for every message.

## Current Behavior

`MappedMessage` logs a WARN with a full stack trace per message, flooding `server.log`:

    WARN [MappedMessage] Could not transform CEF field [cfp1] according to standard. Skipping.
    java.lang.NumberFormatException: empty String
        at org.graylog.plugins.cef.parser.CEFMapping.convertFloat(CEFMapping.java:232)
        at org.graylog.plugins.cef.parser.MappedMessage.mapExtensions(MappedMessage.java:52)

Seen with a SecureAuth IdP appliance that emits an empty `cfp1` on nearly every event.

## Root Cause

`CEFMapping` converters call `Float.parseFloat` / `Long.parseLong` / `new BigInteger(...)`
directly with no empty-value check, and `MappedMessage.mapExtensions` logs the caught
exception with the throwable attached. This affects every numerically-typed CEF field,
not just `cfp1`.

Both entry points share this path, so a pipeline is not a workaround:
- `CEFCodec.java:137` (CEF input)
- `CEFParserFunction.java:74` (`parse_cef()`)

## Possible Solution

Treat an empty/blank extension value as absent before conversion, and drop the stack
trace from the warning (or lower it to debug) so genuinely malformed values stay
diagnosable without flooding.

Related, both fixed per-field rather than generically: #4839, #7371

## Context

Reproduced on `master`; `MappedMessage` unchanged since the plugin was merged into core,
so all 7.0.x/7.1.x are affected. Reported on 7.0.5.

Workaround: set `org.graylog.plugins.cef.parser.MappedMessage` to `ERROR`.

## Your Environment
<!--- Include as many relevant details about the environment you experienced the bug in -->

* Graylog Version: 7.0.5
* Java Version: unknown
* OpenSearch Version: unknown
* MongoDB Version: unknown
* Operating System: unknown
* Browser version: unknown

## Checklist
[x] This issue fix need to be backported.
[ ] Does this issue have **security** implications?

## Comment by patrickmann on 2026-08-03

Re-opened for backport

## Comment by fpetersen-gl on 2026-08-03

Main PR plus backports to 7.1 and 7.0 merged, closing this ticket.
