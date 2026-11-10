# CLI triggered plans losing file permissions

- Issue: https://github.com/terrakube-io/terrakube/issues/1773
- Opened by aniekgul on 2025-02-07, closed on 2026-09-23
- Labels: bug
- Fix commit: 760d766b500bc9d9c6b9df466754c7d9992fa3ae

## Report

### Bug description 🐞

Running a plan triggered off the CLI I saw the following errors from a data source that uses a shell script:
```
��� Terraform is running. On Unix-based platforms, the file on the filesystem
��� must have the executable bit set. On Windows-based platforms, no action is
��� typically necessary.
���
��� Platform: linux
��� Program: "../scripts/cloudrun_digest.sh"
��� Error: exec: "../scripts/cloudrun_digest.sh": permission denied
���
```

Taking a look at the file permissions in the executor pod it seems like the file is missing the execute bit:
```
cnb@job-71-v7mlh:/workspace$ ls -la /home/cnb/.terraform-spring-boot/executor/acc9516c-d292-43f2-ba08-329f7c1caca5/835d9bfd-84d0-4489-a36d-ab59ed982c9d/scripts
total 32
drwxr-xr-x  2 cnb cnb 4096 Feb  7 00:26 .
drwxr-xr-x 12 cnb cnb 4096 Feb  7 00:26 ..
-rw-r--r--  1 cnb cnb 1793 Feb  7 00:26 cloudrun_digest.sh
```

versus the same files in a run created on the UI
```
cnb@job-73-v4nwd:/workspace$ ls -la /home/cnb/.terraform-spring-boot/executor/acc9516c-d292-43f2-ba08-329f7c1caca5/835d9bfd-84d0-4489-a36d-ab59ed982c9d/scripts
total 32
drwxr-xr-x  2 cnb cnb 4096 Feb  7 00:35 .
drwxr-xr-x 13 cnb cnb 4096 Feb  7 00:35 ..
-rwxr-xr-x  1 cnb cnb 1793 Feb  7 00:35 cloudrun_digest.sh
```

### Steps to reproduce

1. Create a data source that uses an external script, [example](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external#example-usage)
2. Run a plan via the UI (should pass)
3. Run a plan via CLI (should fail)

### Expected behavior

_No response_

### Example repository

_No response_

### Anything else?

_No response_

## Comment by alfespa17 on 2025-02-07

You could add a small script to run `chmod` something like

```yaml
flow:
  - type: "terraformPlan"
    step: 100
    commands:
      - runtime: "BASH"
        priority: 100
        before: true
        script: |
          echo $PATH
          Chmod +x my_script.sh
  - type: "terraformApply"
    step: 300
```

That could be a workaround

## Comment by aniekgul on 2025-02-07

Yeah that works as a workaround, good call
