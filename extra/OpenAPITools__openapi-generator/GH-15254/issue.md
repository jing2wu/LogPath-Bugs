# [BUG,RUST] New AbstractRustCodegen.java not handling period-delimited model names well.

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/15254
- Opened by jnicholls on 2023-04-18, closed on 2025-06-29
- Labels: Issue: Bug
- Fix commit: 03effd7d0511325a1571971bea4b86cf38a1a17f

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [X] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

I am working with the [Microsoft Graph API specification](https://raw.githubusercontent.com/microsoftgraph/msgraph-metadata/master/openapi/v1.0/openapi.yaml) (although I used `yq -o=json eval openapi.yaml > openapi.json` to convert to a JSON spec first, since there are too many Yaml code points for swagger-parser in v6.5.0 of openapi-generator). It has models named in the following format:

* `microsoft.graph.user`
* `microsoft.graph.authenticationMethod`
* `microsoft.graph.fido2AuthenticationMethod`

etc. The Rust client generator is outputting the following warnings:

> [main] WARN  o.o.c.languages.AbstractRustCodegen - MicrosoftGraphFido2AuthenticationMethod cannot be used as a model name. Renamed to MicrosoftPeriodGraphPeriodFido2AuthenticationMethod

> [main] WARN  o.o.c.languages.AbstractRustCodegen - microsoft/graph/fido2_authentication_method cannot be used as a model file name. Renamed to microsoft_period_graph_period_fido2_authentication_method

This output is perplexing, as `MicrosoftGraphFido2AuthenticationMethod` post-sanitizing is completely legitimate for Rust, but it still performs another pass and adds `Period` in placements where `.` is in the original model name.

Likewise, the module file pathing `microsoft/graph/fido2_authentication_method` would be perfectly legitimate (assuming proper supporting `mod.rs` files were generated along the path) as a module path and file name. Or if not that `microsoft_graph_fido2_authentication_method` would be perfectly good as well, without the added `_period` separator in the module path name.

I realize these may be two separate issues, but since `Period` and `_period` are likely rooted with the same failing to handle `.` delimited model names, I bet they can be solved together.

##### openapi-generator version

6.5.0

##### OpenAPI declaration file content or url

https://raw.githubusercontent.com/microsoftgraph/msgraph-metadata/master/openapi/v1.0/openapi.yaml

converted to json with:

```
yq -o=json eval openapi.yaml > openapi.json
```

##### Generation Details

```
openapi-generator generate -g rust \
  -i openapi.json \
  -o ms-graph-rust \
  --additional-properties=useSingleRequestParameter=true \
  --skip-validate-spec
```

##### Steps to reproduce

1. Download the openapi.yaml spec.
2. Convert to openapi.json spec.
3. Run the above command, see all of the WARN output.

##### Suggest a fix

I briefly reviewed the AbstractRustCodegen class and how its calling down into DefaultCodegen for various name sanitizing and character replacement, but didn't dig very deep. I feel like the owner of AbstractRustCodegen will know of a good way to handle this issue immediately after reading this description.

## Comment by jnicholls on 2023-04-18

Tagging @jacob-pro here. Jacob, you introduced and iterated a bit on the `AbstractRustCodegen` implementation, so thought you might have some insights here as well as a possible workaround (other than generating an inline name map of all the models, which did cross my mind...)

## Comment by mickvangelderen on 2024-11-21

Is it as simple as replacing

```java
        // Replace hyphens with underscores
        name = name.replaceAll("-", "_");
```

with

```java
        // Replace hyphens with underscores
        name = name.replaceAll("[\.-]", "_");
```

in [`AbstractRustCodegen.java`](https://github.com/OpenAPITools/openapi-generator/blob/2b891f6da9db9cf24fe0186f5635d550c958c657/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/AbstractRustCodegen.java#L184C1-L185C42)?

## Comment by wing328 on 2024-11-22

@mickvangelderen can you please file a PR with the suggested fix when you've time? Thank you.

## Comment by mickvangelderen on 2024-11-22

I do not understand the ins-and outs of openapi-generator. If someone can help me find the change (commits) that changed the behavior I would be more confident to write a PR.

For now I am using v5.3.1 which is good enough for my purposes.
