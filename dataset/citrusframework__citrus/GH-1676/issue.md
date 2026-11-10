# Stale AWS clients in registry when LocalStack containers are recreated between tests

- Issue: https://github.com/citrusframework/citrus/issues/1676
- Opened by christophd on 2026-08-06, closed on 2026-08-07
- Labels: bug
- Fix commit: cc6a8a1360e0530bad8f1bdbd2da7cb95bfe7668

## Report

## Description

Citrus auto-creates AWS service clients for LocalStack and Floci Testcontainers instances via `StartLocalStackAction`. The created client instances are registered in the Citrus reference resolver. However, Citrus does not overwrite client instances between tests, which causes failures when each test creates its own LocalStack Testcontainers instance.

## Steps to Reproduce

1. Write multiple test classes, each creating its own LocalStack Testcontainers instance via `StartLocalStackAction`
2. The first test creates AWS clients and registers them in the Citrus reference resolver
3. The second test creates a new LocalStack container (with different mapped ports)
4. The second test reuses the AWS clients from the reference resolver — these still point to the old container's mapped ports

## Expected Behavior

When a new LocalStack/Floci Testcontainers instance is started, the AWS clients in the reference resolver should be updated to reflect the new container's mapped ports. Alternatively, clients should be cleaned up from the registry when a Testcontainers instance is stopped and removed.

## Actual Behavior

The AWS clients registered by the first test remain in the reference resolver with stale port mappings. Subsequent tests that create new Testcontainers instances fail because the clients connect to the wrong (old) ports.

## Additional Context

Possible approaches:
- Overwrite existing client instances in the bean registry when `StartLocalStackAction` creates new clients
- Clean up clients from the registry when the Testcontainers instance is stopped/removed
