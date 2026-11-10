# Multiple filter invocations in `AsyncLoggerConfig`

- Issue: https://github.com/apache/logging-log4j2/issues/1550
- Opened by ppkarwasz on 2023-07-12, closed on 2023-09-15
- Labels: bug
- Fix commit: 59f88190fcd3bc0e6fbd90668625feae3ad1e671

## Report

## Description

The `AsyncLoggerConfig` calls [`AbstractFilterable#isFiltered(LogEvent)`](https://logging.apache.org/log4j/2.x/log4j-core/apidocs/org/apache/logging/log4j/core/filter/AbstractFilterable.html#isFiltered-org.apache.logging.log4j.core.LogEvent-) three times:
 * twice on the calling thread (for asynchronous and synchronous dispatch),
 * once on the logging thread.

While this is not a problem _per se_, this causes unnecessary problems to stateful filters like in micrometer-metrics/micrometer#2176.

## Configuration

**Version:** 2.20.0
