# Wrong handling of old or not yet valid requests

- Issue: https://github.com/swedenconnect/signservice/issues/82
- Opened by Razumain on 2022-10-19, closed on 2022-10-27
- Labels: bug
- Fix commit: 4f562ead1734533a9798ce51c3ccc46927438083

## Report

Requests with a request time set in the past or in the future results in a sign response to the requesting Service Provider.

No Sign Response should be returned unless the date and replay checks pass.

## Comment by martin-lindstrom on 2022-10-19

If the replay check fail I agree with you, but provided that we check the signature before the date checks there is actually better if we send back an error response. The sender is legitimate and has probably a clock skew error.

## Comment by martin-lindstrom on 2022-10-20

Will throw unrecoverable exception -> error page is displayed.
