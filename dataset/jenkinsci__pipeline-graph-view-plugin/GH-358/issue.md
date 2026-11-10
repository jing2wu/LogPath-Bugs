# Parallel skipped stage from declarative not rendered quite right (blue circle is added)

- Issue: https://github.com/jenkinsci/pipeline-graph-view-plugin/issues/358
- Opened by timja on 2024-03-11, closed on 2024-03-11
- Labels: bug
- Fix commit: ecb8c5841335c42b0062bf35a885ea8e7f646f9c

## Report

### Jenkins and plugins versions report

<details>
  <summary>Environment</summary>

  <!-- Paste your environment details below -->
  ```text
  Paste the output here
  ```

</details>


### What Operating System are you using (both controller, and any agents involved in the problem)?

.

### Reproduction steps

This is built off of this PR: https://github.com/jenkinsci/pipeline-model-definition-plugin/pull/700

```groovy
pipeline {
    agent none
    stages {
        stage("foo") {
            steps {
                echo "hello"
            }
        }

        stage('first-parallel') {
            parallel {
                stage("bar") {
                    when {
                        expression {
                            return false
                        }
                    }
                    steps {
                        echo "I will be skipped"
                    }
                }

                stage("baz") {
                    steps {
                        error "I will not be skipped but I will fail"
                    }
                }
            }
        }

        stage('second-parallel') {
            parallel {
                stage("bar2") {
                    steps {
                        echo "bar2 skipped for earlier failure"
                    }
                }
                stage("baz2") {
                    steps {
                        echo "bar3 skipped for earlier failure"
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "I have failed"
        }
        success {
            echo "I have succeeded"
        }
    }
}
```

### Expected Results

(from blue ocean)
<img width="508" alt="image" src="https://github.com/jenkinsci/pipeline-graph-view-plugin/assets/21194782/90fe0f86-39ab-4d39-b9b3-13dbf0cb6327">


### Actual Results

<img width="608" alt="image" src="https://github.com/jenkinsci/pipeline-graph-view-plugin/assets/21194782/214177cd-87d0-4f14-891c-8e6d7160075b">


### Anything else?

_No response_

### Are you interested in contributing a fix?

Possibly

## Comment by timja on 2024-03-11

The flow node for the stage is correctly being picked up as skipped:

<img width="853" alt="image" src="https://github.com/jenkinsci/pipeline-graph-view-plugin/assets/21194782/8ec9cac7-d792-4db0-b025-e40a1709f5bc">

<img width="869" alt="image" src="https://github.com/jenkinsci/pipeline-graph-view-plugin/assets/21194782/957a713a-97d8-4fe8-91e5-3b699423b7e6">

## Comment by timja on 2024-03-11

Stage JSON:

```json
      {
        "name": "first-parallel",
        "state": "failure",
        "completePercent": 50,
        "type": "STAGE",
        "title": "first-parallel",
        "id": "10",
        "pauseDurationMillis": "Queued 0 ms",
        "totalDurationMillis": "Took 1.8 sec",
        "children": [
          {
            "name": "bar",
            "state": "not_built",
            "completePercent": 50,
            "type": "PARALLEL",
            "title": "bar",
            "id": "14",
            "pauseDurationMillis": "Queued 0 ms",
            "totalDurationMillis": "Took 0.74 sec",
            "children": [],
            "seqContainerName": null,
            "nextSibling": null,
            "synthetic": false,
            "isSequential": false,
            "startTimeMillis": "Started 5 min 25 sec ago"
          },
          {
            "name": "baz",
            "state": "failure",
            "completePercent": 50,
            "type": "PARALLEL",
            "title": "baz",
            "id": "15",
            "pauseDurationMillis": "Queued 0 ms",
            "totalDurationMillis": "Took 0.73 sec",
            "children": [],
            "seqContainerName": null,
            "nextSibling": null,
            "synthetic": false,
            "isSequential": false,
            "startTimeMillis": "Started 5 min 25 sec ago"
          }
        ],
        "seqContainerName": null,
        "nextSibling": null,
        "synthetic": false,
        "isSequential": false,
        "startTimeMillis": "Started 5 min 25 sec ago"
      }
```

## Comment by timja on 2024-03-11

State is not_built when it should be skipped

## Comment by timja on 2024-03-11

Looking at the debug logs it was remapped.

Original:

 17 [label="{id: 17, name: bar, type: STAGE, state: SKIPPED, result: NOT_BUILT}"]

Remapped:
 14 [label="{id: 14, name: bar, type: PARALLEL, state: NOT_BUILT, result: NOT_BUILT}"]

## Comment by timja on 2024-03-11

@timbrown5 any idea?

## Comment by timja on 2024-03-11

This https://github.com/jenkinsci/pipeline-graph-analysis-plugin/blob/master/src/main/java/org/jenkinsci/plugins/workflow/pipelinegraphanalysis/StatusAndTiming.java#L490
returns `bar -> {GenericStatus@22910} "NOT_EXECUTED"`

Called from here:
https://github.com/jenkinsci/pipeline-graph-view-plugin/blob/25eb2abf625d7adfcbd068a4ed9e02f441b69146/src/main/java/io/jenkins/plugins/pipelinegraphview/treescanner/ParallelBlockRelationship.java#L162

Which tries to map it to a `NodeRunStatus` and falls into https://github.com/jenkinsci/pipeline-graph-view-plugin/blob/25eb2abf625d7adfcbd068a4ed9e02f441b69146/src/main/java/io/jenkins/plugins/pipelinegraphview/utils/NodeRunStatus.java#L96-L99

## Comment by timja on 2024-03-11

https://github.com/jenkinsci/pipeline-graph-view-plugin/pull/359
