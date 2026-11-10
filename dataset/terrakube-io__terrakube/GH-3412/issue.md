# Mirrored providers with trust_signature fail due to truncation

- Issue: https://github.com/terrakube-io/terrakube/issues/3412
- Opened by TJonesy on 2026-08-17, closed on 2026-08-21
- Labels: bug, good first issue, help wanted
- Fix commit: af51941b945f6cdb725ae6b855547bb75856af2f

## Report

### Bug description 🐞

The provider trust_signature is limited to 32 characaters. Terraform init then fails to armor-decode when verifying the signature and terraform init aborts:

```
Error: Failed to install provider

Error while installing registry.example.com/myorg/coderd v0.0.22:
error verifying trust signature: unexpected EOF
```

This only affects providers whose upstream registry metadata actually populates trust_signature. In our registry, 15 of 16 mirrored providers store '' and work fine; only coder/coderd publishes a trust signature and fails to verify.

### Steps to reproduce

1. Import a provider whose upstream metadata sets `signing_keys.gpg_public_keys[].trust_signature` — e.g. coder/coderd.
2. `GET /terraform/providers/v1/{ns}/coderd/0.0.22/download/linux/amd64` → trust_signature is 32 chars.
3. `terraform init` with that provider → `error verifying trust signature: unexpected EOF`.

### Expected behavior

Full trust_signature to be stored and successful terraform init.

### Example repository

```
terraform {
  required_providers {
    coderd = {
      source  = "registry.terrakube.example.com/myorg/coderd"
      version = "0.0.22"
    }
  }
}

provider "coderd" {
  url = "coder.example.com"
}
```

### Anything else?

[api/src/main/java/io/terrakube/api/plugin/scheduler/provider/ProviderRefreshJob.java (line 266 at 8785648):](https://github.com/terrakube-io/terrakube/blob/87856489435637b5980e0be06ce89513e21f631b/api/src/main/java/io/terrakube/api/plugin/scheduler/provider/ProviderRefreshJob.java#L266)

```
impl.setKeyId(truncate(key.path("key_id").asText(""), 32));
impl.setAsciiArmor(key.path("ascii_armor").asText(""));            // no truncate — text column
impl.setTrustSignature(truncate(key.path("trust_signature").asText(""), 32));  // ← 32 is key_id's bound
impl.setSource(truncate(key.path("source").asText("unknown"), 64));
```

The truncation matches the schema, so both need changing:

```
implementation.trust_signature   character varying(32)
implementation.ascii_armor       text
```

## Comment by alfespa17 on 2026-08-17

Hello @TJonesy, would you like to help with the liquibase migration to fix the column?
