# Renovate probe doesn't detect all supported config file names

- Issue: https://github.com/jenkins-infra/plugin-health-scoring/issues/483
- Opened by viceice on 2024-03-13, closed on 2024-03-19
- Labels: bug
- Fix commit: f347c18eb12700a4ce723ce77f6ff4661ff2692f

## Report

### Description of the bug

I've my renovate configs in repo root, which is allowed by renovate and isn't detected by the renovate probe.

- https://github.com/renovatebot/renovate/blob/b92afa4bd436d6725c4daef7a29d79335eb9f419/lib/config/app-strings.ts#L1
- https://github.com/jenkinsci/scoring-load-balancer-plugin/blob/main/renovate.json
- https://github.com/jenkinsci/additional-identities-plugin/blob/main/renovate.json
- https://groups.google.com/g/jenkinsci-dev/c/l6WwouOW4KY

Will now move to `.github` folder to workaround

## Comment by alecharp on 2024-03-13

Thank you for bringing that to my attention. 
I'll make sure to fix that as soon as possible.

## Comment by alecharp on 2024-03-18

@viceice when you have a moment, please have a look at the pull request linked to see if the fix sounds acceptable to you. Thanks.
