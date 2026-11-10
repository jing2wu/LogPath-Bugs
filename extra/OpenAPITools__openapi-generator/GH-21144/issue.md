# [BUG,rust-axum] Generated Server fails to supply correct number of Generic Arguments in routing

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21144
- Opened by Chrystalkey on 2025-04-25, closed on 2025-06-16
- Labels: Issue: Bug
- Fix commit: db38f0f55609e570b1ab224fc167409accae3223

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apitools.dev/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description
When Generating a spec in openapi-generator-cli version 7.12.0, The generator rust-axum fails to build a compiling module due to supplying the wrong number of generic arguments to the routing functions in src/server/mod.rs.
Such as: 
```rust
.route("/api/v1/auth",
            delete(auth_delete::<I, A, E, C>).delete(auth_delete::<I, A, E>).post(auth_post::<I, A, E, C>).post(auth_post::<I, A, E>)
        )
```
Should be
```rust
.route("/api/v1/auth",
            delete(auth_delete::<I, A, E, C>).delete(auth_delete::<I, A, E, C>).post(auth_post::<I, A, E, C>).post(auth_post::<I, A, E>)
        )
```

##### openapi-generator version
7.12.0
rustc version 1.85

##### OpenAPI declaration file content or url
https://raw.githubusercontent.com/Chrystalkey/landtagszusammenfasser/refs/tags/rust-axum-body-wrapped/docs/specs/openapi.yml

##### Generation Details
`java -jar "./oapi-generator/openapi-generator-cli.jar" generate -g rust-axum -i "$(Get-Location)/oapi-generator/openapi.yml" -o "$(Get-Location)/oapicode"`
on linux replace with `$(pwd)`

##### Steps to reproduce
```bash
curl https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/bin/utils/openapi-generator-cli.sh > openapi-generator-cli
chmod u+x openapi-generator-cli
curl https://raw.githubusercontent.com/Chrystalkey/landtagszusammenfasser/refs/tags/rust-axum-body-wrapped/docs/specs/openapi.yml > openapi.yml
OPENAPI_GENERATOR_VERSION="7.12.0" ./$DIRECTORY/openapi-generator-cli generate -g rust-axum -i $DIRECTORY/openapi.yml -o $(pwd)/oapicode
cd oapicode
cargo build
```

##### Related issues/PRs
related/prestep to my issue tbd

##### Suggest a fix

This can be fixed by plainly grep-replacing `<I, A, E>` by `<I, A, E, C>`. With that the compilation of the module works.
