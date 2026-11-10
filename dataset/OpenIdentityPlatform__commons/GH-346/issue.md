# Tamper-evident CSV audit: reading or querying a topic with no event yet throws NullPointerException

- Issue: https://github.com/OpenIdentityPlatform/commons/issues/346
- Opened by vharseko on 2026-10-17, closed on 2026-10-18
- Labels: bug, java
- Fix commit: 64fbb9be947d8c91d5f1955c5fb7d04d68d9283e

## Report

`SecureCsvWriter` writes the CSV header with the first event, so the audit file of a tamper-evident topic is empty after the handler starts, and after a `rotate` action, until an event is published. `CsvAuditEventHandler.getEntries()` reads such a file: `CsvSecureMapReader.getHeader(true)` returns `null`, and `convertDotNotationToSlashes(null)` throws a `NullPointerException`.

- `readEvent()` catches only `ResourceException` and `IOException`, so the exception is thrown out of the call instead of a `NotFoundException` promise.
- `queryEvents()` catches every exception, so it answers `BadRequestException` instead of an empty result.

### Expected

A file without a header holds no event: `readEvent()` answers `NotFoundException`, and `queryEvents()` answers no result.

#339 covers resuming such a file.

Found by code reading in the review of the fix for #336; not reproduced.
