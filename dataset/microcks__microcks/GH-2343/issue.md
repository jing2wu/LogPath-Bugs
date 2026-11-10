# fix(web): WebhookController fails to register webhooks for operations containing hyphens or slashes

- Issue: https://github.com/microcks/microcks/issues/2343
- Opened by shellyco-code on 2026-09-30, closed on 2026-10-01
- Labels: kind/bug, component/mocks, kind/enhancement
- Fix commit: da2cb1f250d7e3f6fba7b80c4579db726437ce85

## Report

### Description

When attempting to register a webhook for an API operation whose name contains hyphens (`-`) or forward slashes (`/`), the registration fails with a 404 response (`"OperationId is invalid"` or `"Operation not found"`).

### Steps to Reproduce

1. Define an OpenAPI or AsyncAPI service with an operation containing hyphens or path slashes (e.g., `POST /api/v1/user-profiles` or `order-placed-event WEBHOOK`).
2. Attempt to register a webhook via the UI or directly via `POST /api/webhooks` with payload:
   ```json
   {
     "operationId": "<serviceId>-order-placed-event WEBHOOK",
     "targetUrl": "https://example.com/webhook"
   }
3. Observe the response:
For names with hyphens: HTTP 404 "OperationId is invalid"
For names with slashes encoded as ! by frontend: HTTP 404 "Operation not found"

Expected Behavior
Webhook registrations should succeed regardless of whether operation names include hyphens or slashes.

Actual Behavior
In WebhookController.java:
java
String[] parts = registrationRequest.getOperationId().split("-");
if (parts.length != 2) {
   log.error("Invalid operationId received for webhook registration");
   return new ResponseEntity<>("OperationId is invalid", HttpStatus.NOT_FOUND);
}
Because split("-") produces more than 2 elements when the operation name contains hyphens, it is rejected immediately.
The Angular UI encodes / into ! to prevent URL path routing collisions (encodeOperationId(operationId)), but WebhookController does not convert ! back to / before looking up operations in the service or when querying the repository.
Proposed Solution
Split operationId using indexOf('-') instead of split("-") so only the delimiter between serviceId and operationName is split.
Unescape ! back to / in operationName upon registration and in the list/count endpoints.

## Comment by lbroudoux on 2026-09-30

Good catch @shellyco-code !

## Comment by lbroudoux on 2026-10-01

The new encoding needs to be replicated into the Testcontainers modules that added support for Webhook registration recently!
