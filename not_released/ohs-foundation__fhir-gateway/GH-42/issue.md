# Pass body of FHIR operation error responses to the client

- Issue: https://github.com/ohs-foundation/fhir-gateway/issues/42
- Opened by bashir2 on 2022-12-17, closed on 2023-01-20
- Labels: bug, P1:must
- Fix commit: 3dff3419b69a2d26515a80708f65983838b3bb7e

## Report

If there is an error in a FHIR API call, we currently do not pass the HTTP response entity body to the client.
