# [Bug] [Worker Group Manage] ProjetctWorker assignWorkerGroups have some logic error

- Issue: https://github.com/apache/dolphinscheduler/issues/17798
- Opened by yaowanli on 2025-12-16, closed on 2025-12-19
- Labels: bug, help wanted, discussion, priority:middle
- Fix commit: 1629d3302532c8b3a5b81dd4b3aafeddd98262b1

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

In Project A, Project A is assigned to the "test" workgroup, and internal workflows are also assigned to the "test" workgroup.

1. With existing workgroups, clearing all workgroups and assigning only the "default" workgroup results in both "test" and "default" workgroups being displayed.

The page retrieves groupings by obtaining the workgroups of workflows and scheduled jobs, then the project's grouping table, merging the data, and removing duplicates; therefore, two workgroups are displayed, which is normal.

2. With existing workgroups, clearing all workgroups, and then clearing all workgroups a second time, results in an error message: "Failed to assign workgroups to the project."

The prompt is incorrect. It should indicate that no workgroup can be cleared, or that no error message should be displayed.

Alternatively, since a workgroup is already in use internally, clearing the "test" workgroup should not be allowed.

3. Clear all workgroups, then assign the "default" group, and then assign the "test" workgroup. The prompt is: "Worker group [test] is referenced by a task or scheduled task in the project and cannot be reassigned."

This is an incorrect error message. In reality, since no "test" workgroup has been assigned, it should be allowed to be assigned, not prohibited.

### What you expected to happen

Therefore, I believe the workgroup assignment logic should be refactored in the ProjectWorkerGroup code. After line 130 of `oupRelationServiceImpl`, the logic for deletion and insertion is adjusted as follows:

Solution 1: Extreme Simplification
The page should allow free workgroup assignment, but the workflow workgroups and scheduled job workgroups should be combined and displayed during the echo.

Solution 2: Complexity
When assigning workgroups on the page, let's assume the new workgroup is A and the project workgroup is B.

1) If the difference between A and B is greater than 0, directly add a new workgroup based on the difference.

2) If the difference between B and A is greater than 0 (including cases where A is empty), check if the workgroups in the difference have already been assigned to workflows or scheduled jobs. If not, they can be deleted; if already assigned, they cannot be deleted.

### How to reproduce

you can see the What happened


### Anything else

_No response_

### Version

3.3.2

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by SbloodyS on 2025-12-16

> Solution 1: Extreme Simplification
> The page should allow free workgroup assignment, but the workflow workgroups and scheduled job workgroups should be
> combined and displayed during the echo.

Current workgroup permissions and project binding, which violates the design of permission management.

> Solution 2: Complexity
> When assigning workgroups on the page, let's assume the new workgroup is A and the project workgroup is B.
> 
> If the difference between A and B is greater than 0, directly add a new workgroup based on the difference.
> 
> If the difference between B and A is greater than 0 (including cases where A is empty), check if the workgroups in the 
> difference have already been assigned to workflows or scheduled jobs. If not, they can be deleted; if already assigned, they
> cannot be deleted.

What do you mean by `If the difference between A and B is greater than 0, directly add a new workgroup based on the difference`? I'm a little confused. Please provide an example.

## Comment by yaowanli on 2025-12-16

> > Solution 1: Extreme Simplification
> > The page should allow free workgroup assignment, but the workflow workgroups and scheduled job workgroups should be
> > combined and displayed during the echo.
> 
> Current workgroup permissions and project binding, which violates the design of permission management.
> 
> > Solution 2: Complexity
> > When assigning workgroups on the page, let's assume the new workgroup is A and the project workgroup is B.
> > If the difference between A and B is greater than 0, directly add a new workgroup based on the difference.
> > If the difference between B and A is greater than 0 (including cases where A is empty), check if the workgroups in the
> > difference have already been assigned to workflows or scheduled jobs. If not, they can be deleted; if already assigned, they
> > cannot be deleted.
> 
> What do you mean by `If the difference between A and B is greater than 0, directly add a new workgroup based on the difference`? I'm a little confused. Please provide an example.

For example , the new workgroup A now has [a,b,c,d] ,and the project workgroup now has [b,c,d,f]
so  difference between A and B is A-B = [a] ,is greater than 0, we can directly add the group [a]  into the project workgroup 
so  difference between B and A is B-A = [f] ,is greater than 0, we can directly delete group [f] when it doesn't belong to a workflow or scheduled job. if [f] has been assigned, deletion is not allowed and an exception should be displayed.

## Comment by SbloodyS on 2025-12-16

We don't need multiple projects for workgroup comparison. We only need to check whether the worker group to be added exists in the authorized project.

## Comment by Mrhs121 on 2025-12-16

> > > Solution 1: Extreme Simplification
> > > The page should allow free workgroup assignment, but the workflow workgroups and scheduled job workgroups should be
> > > combined and displayed during the echo.
> > 
> > 
> > Current workgroup permissions and project binding, which violates the design of permission management.
> > > Solution 2: Complexity
> > > When assigning workgroups on the page, let's assume the new workgroup is A and the project workgroup is B.
> > > If the difference between A and B is greater than 0, directly add a new workgroup based on the difference.
> > > If the difference between B and A is greater than 0 (including cases where A is empty), check if the workgroups in the
> > > difference have already been assigned to workflows or scheduled jobs. If not, they can be deleted; if already assigned, they
> > > cannot be deleted.
> > 
> > 
> > What do you mean by `If the difference between A and B is greater than 0, directly add a new workgroup based on the difference`? I'm a little confused. Please provide an example.
> 
> For example , the new workgroup A now has [a,b,c,d] ,and the project workgroup now has [b,c,d,f] so difference between A and B is A-B = [a] ,is greater than 0, we can directly add the group [a] into the project workgroup so difference between B and A is B-A = [f] ,is greater than 0, we can directly delete group [f] when it doesn't belong to a workflow or scheduled job. if [f] has been assigned, deletion is not allowed and an exception should be displayed.

The logic you mentioned about this addition and deletion workergroup should be fine in the current code logic
`B-A = [f] `
https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L128-L129
`A-B = [a]`
https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L150-L151




The main problem lies here,  For instance, I clear all the workers under the current project from the page and then click Submit.  
（In this sample project, there is only a shell task, and this shell task is assigned to workergroup `new`）
<img width="1473" height="599" alt="Image" src="https://github.com/user-attachments/assets/e392872b-a563-4413-aa38-f7ff206909d9" />

Because we clicked "Clear", the workerGroups passed by the front end through the api are an empty collection. Therefore, it will go to this if branch. It can be seen that before deletion, no judgment was made on whether the worker groups to be deleted could be deleted, but they were directly deleted from the database.

https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L97-L105

and  there is also a bit of a problem with the logic for determining whether there are tasks occupying the workergroup here. For instance, if usedWorkerGroups is [new] and needDeletedWorkerGroups is [default,new], it will be determined that no task is occupying the Workergroups to be deleted.  
Here, intersection should be used to determine whether there is a task occupying this workergroup instead of containsAll. For example: `boolean hasIntersection =! Collections.disjoint(usedWorkerGroups, needDeletedWorkerGroups);
`
https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L132-L137

## Comment by yaowanli on 2025-12-16

> We don't need multiple projects for workgroup comparison. We only need to check whether the worker group to be added exists in the authorized project.

Perhaps there were some issues with my wording; I was referring to the allocation of work groups within the same project.
the new workgroup A now has [a,b,c,d] ,and the project workgroup now has [b,c,d,f]，these workgroup  all belongs to Project 1

## Comment by SbloodyS on 2025-12-16

@Mrhs121 Yes. You are right. Would you like to fix it?

## Comment by yaowanli on 2025-12-16

> > > > Solution 1: Extreme Simplification
> > > > The page should allow free workgroup assignment, but the workflow workgroups and scheduled job workgroups should be
> > > > combined and displayed during the echo.
> > > 
> > > 
> > > Current workgroup permissions and project binding, which violates the design of permission management.
> > > > Solution 2: Complexity
> > > > When assigning workgroups on the page, let's assume the new workgroup is A and the project workgroup is B.
> > > > If the difference between A and B is greater than 0, directly add a new workgroup based on the difference.
> > > > If the difference between B and A is greater than 0 (including cases where A is empty), check if the workgroups in the
> > > > difference have already been assigned to workflows or scheduled jobs. If not, they can be deleted; if already assigned, they
> > > > cannot be deleted.
> > > 
> > > 
> > > What do you mean by `If the difference between A and B is greater than 0, directly add a new workgroup based on the difference`? I'm a little confused. Please provide an example.
> > 
> > 
> > For example , the new workgroup A now has [a,b,c,d] ,and the project workgroup now has [b,c,d,f] so difference between A and B is A-B = [a] ,is greater than 0, we can directly add the group [a] into the project workgroup so difference between B and A is B-A = [f] ,is greater than 0, we can directly delete group [f] when it doesn't belong to a workflow or scheduled job. if [f] has been assigned, deletion is not allowed and an exception should be displayed.
> 
> The logic you mentioned about this addition and deletion workergroup should be fine in the current code logic `B-A = [f] `
> 
> [dolphinscheduler/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java](https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L128-L129)
> 
> Lines 128 to 129 in [8c4d921](/apache/dolphinscheduler/commit/8c4d921c63ff4d91e50fc4549adfe50bee4464f5)
> 
>  Set<String> needDeletedWorkerGroups = 
>          SetUtils.difference(projectWorkerGroupNames, unauthorizedWorkerGroupNames); 
> 
> `A-B = [a]`
> [dolphinscheduler/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java](https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L150-L151)
> 
> Lines 150 to 151 in [8c4d921](/apache/dolphinscheduler/commit/8c4d921c63ff4d91e50fc4549adfe50bee4464f5)
> 
>  Set<String> needAssignedWorkerGroups = 
>          SetUtils.difference(unauthorizedWorkerGroupNames, projectWorkerGroupNames); 
> The main problem lies here, For instance, I clear all the workers under the current project from the page and then click Submit. （In this sample project, there is only a shell task, and this shell task is assigned to workergroup `new`） <img alt="Image" width="1473" height="599" src="https://private-user-images.githubusercontent.com/15990723/526858643-e392872b-a563-4413-aa38-f7ff206909d9.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjU4NTU1NTksIm5iZiI6MTc2NTg1NTI1OSwicGF0aCI6Ii8xNTk5MDcyMy81MjY4NTg2NDMtZTM5Mjg3MmItYTU2My00NDEzLWFhMzgtZjdmZjIwNjkwOWQ5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTEyMTYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMjE2VDAzMjA1OVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWUzZmVhY2Y2OWY3M2ZjMzdkYTg3N2ZkMjBhMmQzNzAzZTgxMjliYzlmNmNmZDE1MjczNzQ4ODI2ZDMwM2QzN2YmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.KSZ7tJe5JIZI9pi8GwpPNqD9ZNZgu5hD8LagVzzZd6M">
> 
> Because we clicked "Clear", the workerGroups passed by the front end through the api are an empty collection. Therefore, it will go to this if branch. It can be seen that before deletion, no judgment was made on whether the worker groups to be deleted could be deleted, but they were directly deleted from the database.
> 
> [dolphinscheduler/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java](https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L97-L105)
> 
> Lines 97 to 105 in [8c4d921](/apache/dolphinscheduler/commit/8c4d921c63ff4d91e50fc4549adfe50bee4464f5)
> 
>  if (CollectionUtils.isEmpty(workerGroups)) { 
>      boolean deleted = projectWorkerGroupDao.deleteByProjectCode(projectCode); 
>      if (deleted) { 
>          putMsg(result, Status.SUCCESS); 
>      } else { 
>          putMsg(result, Status.ASSIGN_WORKER_GROUP_TO_PROJECT_ERROR); 
>      } 
>      return result; 
>  } 
> and there is also a bit of a problem with the logic for determining whether there are tasks occupying the workergroup here. For instance, if usedWorkerGroups is [new] and needDeletedWorkerGroups is [default,new], it will be determined that no task is occupying the Workergroups to be deleted. Here, intersection should be used to determine whether there is a task occupying this workergroup instead of containsAll. For example: `boolean hasIntersection =! Collections.disjoint(usedWorkerGroups, needDeletedWorkerGroups); `
> 
> [dolphinscheduler/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java](https://github.com/apache/dolphinscheduler/blob/8c4d921c63ff4d91e50fc4549adfe50bee4464f5/dolphinscheduler-api/src/main/java/org/apache/dolphinscheduler/api/service/impl/ProjectWorkerGroupRelationServiceImpl.java#L132-L137)
> 
> Lines 132 to 137 in [8c4d921](/apache/dolphinscheduler/commit/8c4d921c63ff4d91e50fc4549adfe50bee4464f5)
> 
>  if (CollectionUtils.isNotEmpty(needDeletedWorkerGroups)) { 
>      Set<String> usedWorkerGroups = getAllUsedWorkerGroups(project); 
>      if (CollectionUtils.isNotEmpty(usedWorkerGroups) && usedWorkerGroups.containsAll(needDeletedWorkerGroups)) { 
>          throw new ServiceException(Status.USED_WORKER_GROUP_EXISTS, 
>                  SetUtils.intersection(usedWorkerGroups, needDeletedWorkerGroups).toSet()); 
>      }

Yes! You get me, that's it,

## Comment by Mrhs121 on 2025-12-16

> [@Mrhs121](https://github.com/Mrhs121) Yes. You are right. Would you like to fix it?

Ok. Assign it to me

## Comment by SbloodyS on 2025-12-16

> > [@Mrhs121](https://github.com/Mrhs121) Yes. You are right. Would you like to fix it?
> 
> Ok. Assign it to me

Done.
