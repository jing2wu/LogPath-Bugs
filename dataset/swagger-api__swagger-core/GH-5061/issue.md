# [Bug]: Number example treated as a string when generating swagger file.

- Issue: https://github.com/swagger-api/swagger-core/issues/5061
- Opened by SandorArpa on 2026-02-23, closed on 2026-04-07
- Labels: Bug
- Fix commit: 395083590a304bb3da382ea5850430b089f9b725

## Report

## Description of the problem/issue

The following mark up 
`@SchemaProperty(
               name = "price",
               schema = @Schema(example = "9090", maximum = "10000000", type = "number", minimum = "1",
               description = "Price override for the payment amount. If not present this will defaults to price of product.")) (https://github.com/alphagov/pay-products/blob/529c1873e6ff2e7842a63654aeb50d7d19cb1fda/src/main/java/uk/gov/pay/products/resources/PaymentResource.java#L107)

interpreted as a string in version 2.2.43:

`type: number
  description: Price override for the payment amount. If not present this will defaults to price of product.
  example: "9090"
  maximum: 10000000
  minimum: 1`.

In version 2.2.42 it was interpreted as a number:
`type: number
  description: Price override for the payment amount. If not present this will defaults to price of product.
  example: 9090
  maximum: 10000000
  minimum: 1`.


## Affected Version

2.2.42 to 2.2.43

## Steps to Reproduce
Setup a SchemaProperty in a RequestBody where type = "number' and example = "1000"

## Expected Behavior

Example is a number, not a string

## Actual Behavior

Example is a string

## Logs / Stack Traces

N/A

## Additional Context
Change did not affect Java classes, eg:

`@Schema(example = "1000.00") 
 private final BigDecimal averageAmount;`

is still interpreted as a number.

## Checklist

- [x] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [ x] I have provided sufficient information for maintainers to reproduce the issue.

## Comment by Darthpi on 2026-02-27

I believe the additional context is not correct, given this example.
(This may be a different cause/area but I would title it exactly the same as this bug so I'll include it here)

comparison between 2.2.43 and 2.2.44 (tested with BigDecimal and Double)
Given this example endpoint and dto:

```
@PostMapping(path = "/example", consumes = MediaType.APPLICATION_JSON_VALUE)
public ResponseEntity<ExampleDto> crud() {
  return null;
}
```
  
```
private record ExampleDto(
  @Schema(example = "10.00", description = "Bug test decimal value") BigDecimal exampleDec) {
})
```

api-docs

```
2.2.42
"ExampleDto": {
	"type": "object",
	"properties": {
		"exampleDec": {
			"type": "number",
			"description": "Bug test decimal value",
			"example": 10.0   <------
		}
	}
}
```

```
2.2.43
"ExampleDto": {
	"type": "object",
	"properties": {
		"exampleDec": {
			"type": "number",
			"description": "Bug test decimal value",
			"example": "10.00"   <-----
		}
	}
}	
```

## Comment by ewaostrowska on 2026-04-07

The issue should be by https://github.com/swagger-api/swagger-core/pull/5062 and will be a part of the next release. It includes as well fix for default and examples (OAS 3.1)
