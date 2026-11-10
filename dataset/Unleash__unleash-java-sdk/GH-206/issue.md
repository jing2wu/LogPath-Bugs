# SDK exposes Api key in logs

- Issue: https://github.com/Unleash/unleash-java-sdk/issues/206
- Opened by chriswk on 2023-08-07, closed on 2023-08-07
- Labels: bug
- Fix commit: 499ecd5367491eb387774440eec5bf5a9e3ec763

## Report

### Describe the bug

When instantiating more than one client in the same process, Unleash warns you that this is not a recommended way to do so. When it warns you the ERROR log message contains the API key it has seen more than one client instance for.

### Steps to reproduce the bug

Instantiate two UnleashClients in the same process from the same Unleash Config.
Once the second client is instantiated, observe that the error message contains the api key

### Expected behavior

I'd still like to see the ERROR message, but with a redacted API key.

### Logs, error output, etc.

_No response_

### Screenshots

_No response_

### Additional context

_No response_

### Unleash version

_No response_

### Subscription type

None

### Hosting type

None

### SDK information (language and version)

unleash-client-java:8.2.0
