# Latest released version does not properly display logs

- Issue: https://github.com/jenkinsci/pipeline-graph-view-plugin/issues/224
- Opened by dawidmalina on 2023-02-24, closed on 2023-03-07
- Labels: bug
- Fix commit: 4d8f64de99d3ded41f378d938a7af658a581dc9c

## Report

### Jenkins and plugins versions report

```
Jenkins: 2.375.3
OS: Linux - 5.10.147+
Java: 11.0.18 - Eclipse Adoptium (OpenJDK 64-Bit Server VM)
---
ansicolor:1.0.2
antisamy-markup-formatter:155.v795fb_8702324
apache-httpcomponents-client-4-api:4.5.13-138.v4e7d9a_7b_a_e61
authentication-tokens:1.4
authorize-project:1.4.0
basic-branch-build-strategies:71.vc1421f89888e
blueocean:1.27.1
blueocean-autofavorite:1.2.5
blueocean-bitbucket-pipeline:1.27.1
blueocean-commons:1.27.1
blueocean-config:1.27.1
blueocean-core-js:1.27.1
blueocean-dashboard:1.27.1
blueocean-display-url:2.4.1
blueocean-events:1.27.1
blueocean-git-pipeline:1.27.1
blueocean-github-pipeline:1.27.1
blueocean-i18n:1.27.1
blueocean-jwt:1.27.1
blueocean-personalization:1.27.1
blueocean-pipeline-api-impl:1.27.1
blueocean-pipeline-editor:1.27.1
blueocean-pipeline-scm-api:1.27.1
blueocean-rest:1.27.1
blueocean-rest-impl:1.27.1
blueocean-web:1.27.1
bootstrap5-api:5.2.1-3
bouncycastle-api:2.26
branch-api:2.1051.v9985666b_f6cc
build-with-parameters:1.6
caffeine-api:2.9.3-65.v6a_47d0f4d1fe
checks-api:1.8.1
cloudbees-bitbucket-branch-source:796.v6cb_1559e1673
cloudbees-folder:6.795.v3e23d3c6f194
command-launcher:90.v669d7ccb_7c31
commons-lang3-api:3.12.0-36.vd97de6465d5b_
commons-text-api:1.10.0-27.vb_fa_3896786a_7
conditional-buildstep:1.4.2
configuration-as-code:1569.vb_72405b_80249
credentials:1214.v1de940103927
credentials-binding:523.vd859a_4b_122e6
display-url-api:2.3.7
docker-commons:1.21
docker-workflow:563.vd5d2e5c4007f
durable-task:504.vb10d1ae5ba2f
echarts-api:5.4.0-1
envinject:2.881.v37c62073ff97
envinject-api:1.199.v3ce31253ed13
favorite:2.4.1
font-awesome-api:6.2.0-3
gcp-secrets-manager-credentials-provider:0.3.1
ghprb:1.42.2
git:5.0.0
git-client:4.1.0
git-parameter:0.9.18
github:1.37.0
github-api:1.303-400.v35c2d8258028
github-branch-source:1701.v00cc8184df93
handy-uri-templates-2-api:2.1.8-22.v77d5b_75e6953
htmlpublisher:1.31
instance-identity:142.v04572ca_5b_265
ionicons-api:31.v4757b_6987003
jackson2-api:2.13.4.20221013-295.v8e29ea_354141
jakarta-activation-api:2.0.1-3
jakarta-mail-api:2.0.1-3
javax-activation-api:1.2.0-5
javax-mail-api:1.6.2-8
jaxb:2.3.7-1
jdk-tool:63.v62d2fd4b_4793
jenkins-design-language:1.27.1
jjwt-api:0.11.5-77.v646c772fddb_0
job-dsl:1.81
jquery3-api:3.6.1-2
junit:1177.v90374a_ef4d09
kubernetes:3883.v4d70a_a_a_df034
kubernetes-client-api:6.4.1-208.vfe09a_9362c2c
kubernetes-credentials:0.10.0
mailer:438.v02c7f0a_12fa_4
matrix-auth:3.1.5
matrix-project:785.v06b_7f47b_c631
metrics:4.2.13-420.vea_2f17932dd6
mina-sshd-api-common:2.9.2-50.va_0e1f42659a_a
mina-sshd-api-core:2.9.2-50.va_0e1f42659a_a
okhttp-api:4.9.3-108.v0feda04578cf
parameterized-trigger:2.45
pipeline-build-step:2.18.1
pipeline-graph-analysis:202.va_d268e64deb_3
pipeline-graph-view:157.vd6123e1b_a_e2e
pipeline-groovy-lib:629.vb_5627b_ee2104
pipeline-input-step:466.v6d0a_5df34f81
pipeline-milestone-step:111.v449306f708b_7
pipeline-model-api:2.2118.v31fd5b_9944b_5
pipeline-model-definition:2.2118.v31fd5b_9944b_5
pipeline-model-extensions:2.2118.v31fd5b_9944b_5
pipeline-rest-api:2.31
pipeline-stage-step:305.ve96d0205c1c6
pipeline-stage-tags-metadata:2.2118.v31fd5b_9944b_5
pipeline-stage-view:2.31
plain-credentials:143.v1b_df8b_d3b_e48
plugin-usage-plugin:4.0
plugin-util-api:2.20.0
popper2-api:2.11.6-2
prometheus:2.1.1
pubsub-light:1.17
rebuild:1.34
role-strategy:562.v44e9a_e828d0e
run-condition:1.5
saml:4.372.v89f13e4c9e97
scm-api:631.v9143df5b_e4a_a
script-security:1229.v4880b_b_e905a_6
snakeyaml-api:1.33-90.v80dcb_3814d35
sse-gateway:1.26
ssh-agent:295.v9ca_a_1c7cc3a_a_
ssh-credentials:305.v8f4381501156
sshd:3.249.v2dc2ea_416e33
structs:324.va_f5d6774f3a_d
timestamper:1.21
token-macro:321.vd7cc1f2a_52c8
trilead-api:2.84.v72119de229b_7
uno-choice:2.6.4
variant:59.vf075fe829ccb
workflow-api:1208.v0cc7c6e0da_9e
workflow-basic-steps:1010.vf7a_b_98e847c1
workflow-cps:3618.v13db_a_21f0fcf
workflow-durable-task-step:1234.v019404b_3832a
workflow-job:1268.v6eb_e2ee1a_85a
workflow-multibranch:733.v109046189126
workflow-scm-step:400.v6b_89a_1317c9a_
workflow-step-api:639.v6eca_cd8c04a_a_
workflow-support:839.v35e2736cfd5c
```


### What Operating System are you using (both controller, and any agents involved in the problem)?

Linux

### Reproduction steps

Jenkinsfile

```
pipeline {
    agent any
    stages {
        stage('Main') {
            steps {
                sh 'hostname'
                sh 'ls -lta'
                sh 'ls -lta /'
                sh 'sleep 60'
                sh 'ps -efww'
            }
        }
    }
}

```

### Expected Results

Blue Ocean:

![Screenshot 2023-02-24 at 09 23 46](https://user-images.githubusercontent.com/5910851/221128956-63bc90cb-f209-443f-a51b-ff18a3348b54.png)


### Actual Results

![Screenshot 2023-02-24 at 09 21 45](https://user-images.githubusercontent.com/5910851/221128998-362f1615-e4f3-4cd8-8b3f-2aa3a431b0f8.png)


### Anything else?

_No response_

## Comment by dawidmalina on 2023-02-25

Thank you for the very quick response 👍

## Comment by stuartrowe on 2023-03-06

This is still an issue for any step node with an associated `ErrorAction`. 

The simplest example is a `bat` / `sh` step that runs a script with a non-zero exit code. The actual output of the script is hidden and only the exception message from the `ErrorAction` is displayed.

```
pipeline {
    agent any
    stages {
        stage('Main') {
            steps {
                bat 'hostname'
                bat 'dir'
                bat 'tasklist && exit /b 1'
            }
        }
    }
}
```

![image](https://user-images.githubusercontent.com/551572/223209727-357ffbc1-5d2c-4f7e-b831-aa4ee5234d81.png)

## Comment by timbrown5 on 2023-03-07

Linux alternative:
```
pipeline {
    agent any
    stages {
        stage('Main') {
            steps {
                sh 'hostname'
                sh 'cd'
                sh 'ps aux && exit 1'
            }
        }
    }
}
```
