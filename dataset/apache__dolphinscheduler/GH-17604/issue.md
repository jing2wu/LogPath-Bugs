# [Bug] [api-server] Worker group cannot be assigned to a project

- Issue: https://github.com/apache/dolphinscheduler/issues/17604
- Opened by k1z on 2025-10-27, closed on 2025-11-06
- Labels: bug, backend, priority:high
- Fix commit: e72716b96231906618ac2f0521bee51008e88043

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When I assigned a workgroup to a project, it prompted me: Failed to assign a workgroup to the project


<img width="679" height="482" alt="Image" src="https://github.com/user-attachments/assets/0eb2368d-9f54-4b8b-b86e-6f2470423ff3" />

<img width="325" height="102" alt="Image" src="https://github.com/user-attachments/assets/7cee2d00-6237-4ba7-8bb3-4134cdc8fa12" />

api-server log

<img width="1917" height="86" alt="Image" src="https://github.com/user-attachments/assets/a24c7aaa-e249-4d98-bf32-15a8b5ff3a01" />


2025-10-27 15:04:22.235 ERROR [qtp767266208-12279] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[143] - Failed to delete worker groups [[worker-240.118]] for the project [运维].
2025-10-27 15:04:22.235 ERROR [qtp767266208-12279] o.a.d.a.e.ApiExceptionHandler:[40] - org.apache.dolphinscheduler.api.controller.ProjectWorkerGroupController#assignWorkerGroups[3 args] Meet a ServiceException: 给项目分配工作组失败


but, if i create a new project ,  can assign

2025-10-27 15:05:28.525 INFO  [qtp767266208-12436] o.a.d.a.s.i.ProjectServiceImpl:[134] - Project is created and id is :7
2025-10-27 15:05:32.122 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[141] - Success to delete worker groups [[default, worker-240.118, Linux-prod, worker-10.10.243.142]] for the project [测试] .
2025-10-27 15:05:32.124 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [default] for the project [测试] .
2025-10-27 15:05:32.124 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [worker-240.118] for the project [测试] .
2025-10-27 15:05:32.125 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [Linux-prod] for the project [测试] .
2025-10-27 15:05:32.125 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [worker-10.10.243.142] for the project [测试] .



### What you expected to happen

I have no idea

### How to reproduce

assigned a worker group to project, 

### Anything else

_No response_

### Version

3.3.1

### Are you willing to submit PR?

- [ ] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by github-actions[bot] on 2025-10-27

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When I assigned a workgroup to a project, it prompted me: Failed to assign a workgroup to the project


<img width="679" height="482" alt="Image" src="https://github.com/user-attachments/assets/0eb2368d-9f54-4b8b-b86e-6f2470423ff3" />

<img width="325" height="102" alt="Image" src="https://github.com/user-attachments/assets/7cee2d00-6237-4ba7-8bb3-4134cdc8fa12" />

api-server log

<img width="1917" height="86" alt="Image" src="https://github.com/user-attachments/assets/a24c7aaa-e249-4d98-bf32-15a8b5ff3a01" />


2025-10-27 15:04:22.235 ERROR [qtp767266208-12279] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[143] - Failed to delete worker groups [[worker-240.118]] for the project [运维].
2025-10-27 15:04:22.235 ERROR [qtp767266208-12279] o.a.d.a.e.ApiExceptionHandler:[40] - org.apache.dolphinscheduler.api.controller.ProjectWorkerGroupController#assignWorkerGroups[3 args] Meet a ServiceException: 给项目分配工作组失败


but, if i create a new project ,  can assign

2025-10-27 15:05:28.525 INFO  [qtp767266208-12436] o.a.d.a.s.i.ProjectServiceImpl:[134] - Project is created and id is :7
2025-10-27 15:05:32.122 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[141] - Success to delete worker groups [[default, worker-240.118, Linux-prod, worker-10.10.243.142]] for the project [测试] .
2025-10-27 15:05:32.124 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [default] for the project [测试] .
2025-10-27 15:05:32.124 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [worker-240.118] for the project [测试] .
2025-10-27 15:05:32.125 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [Linux-prod] for the project [测试] .
2025-10-27 15:05:32.125 INFO  [qtp767266208-12308] o.a.d.a.s.i.ProjectWorkerGroupRelationServiceImpl:[155] - Success to add worker group [worker-10.10.243.142] for the project [测试] .



### What you expected to happen

I have no idea

### How to reproduce

assigned a worker group to project, 

### Anything else

_No response_

### Version

3.3.1

### Are you willing to submit PR?

- [ ] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by Mrhs121 on 2025-10-28

This difference can only handle the situation where a new wg is added. For instance, if p1 currently has only one wg w1, and you delete w1 and add w2, you can see that the value of the difference at this time is w2. Then, the following code will first delete w2, and an error will definitely occur at this point.
https://github.com/apache/dolphinscheduler/blob/24e599760f6b6d20d2a9c2c415243bc2f05840f9/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L128-L163
