# Cannot create a GitLab webhook

- Issue: https://github.com/terrakube-io/terrakube/issues/2855
- Opened by themaroqa on 2026-01-19, closed on 2026-01-19
- Labels: bug
- Fix commit: 355fe119c5376a1fa7485dddcccd409a04bcb4a4

## Report

### Bug description 🐞

I cannot add a webhook to a GitLab project part of a pretty large GitLab group (~ 1000 projects).
The UI seems stuck while creating and looking at the logs I find the following:

```
INFO 1 --- [      task-1062] i.t.a.p.v.p.gitlab.GitLabWebhookService  : {"url":"[REDACTED]","push_events":"true", "merge_requests_events": "true", "releases_events": true, "enable_ssl_verification":"false","token":"[REDACTED]"}
INFO 1 --- [      task-1062] i.t.a.p.v.p.gitlab.GitLabWebhookService  : Search gitlab project id using [REDACTED], https://gitlab.com/api/v4 
```

and then after exactly 30 seconds

```
ERROR 1 --- [      task-1062] i.t.a.p.v.p.gitlab.GitLabWebhookService  : Failed to retrieve project ID. Error: java.lang.InterruptedException
WARN 1 --- [      task-1062] i.t.a.p.v.p.gitlab.GitLabWebhookService  : Project with path i[REDACTED] not found after checking all pages
```

Here are my assumptions looking at the code here https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java (forgive me I am not a Java dev):
- I can 100% ensure the project exists and there are no typos in the name
- The getGitlabProjectId function paginate the results by 25 projects. 
- Every call to Gitlab API takes between 2 to 5 seconds (pretty slow, I admit)
- My project is not in the first 4/5 pages (please note that in other projects I can create the webhook, probably because those are included in the first pages)
- Somewhere a 30 seconds timeout happen

Could it be some timeout of the Java client you are using? if so: is there some env variable I can use to increase it?

### Steps to reproduce

Manage ~1000 projects in GitLab
Try to create a webhook in one of those

### Expected behavior

_No response_

### Example repository

_No response_

### Anything else?

_No response_

## Comment by alfespa17 on 2026-01-19

The code is using this particular method to find the project id

https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L377

Internally it is using the project API here
https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L394

By default this value has 25 per page, maybe this could use some environment variable to be able to customize it like [here](https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/resources/application.properties#L97)

https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L396

I guess this require something like to change the timeout

`.block(Duration.ofSeconds(30))`

I can add the code but I dont really have a way to test it

## Comment by themaroqa on 2026-01-19

I can test it for you. I will only need the tag of the terrakube-api (I guess) docker image to test

## Comment by alfespa17 on 2026-01-19

I will create a new tag later today once I merge all the dependencies updates

## Comment by alfespa17 on 2026-01-19

You can use this build, it should be ready in some minutes [2.30.0-beta.2](https://github.com/terrakube-io/terrakube/releases/tag/2.30.0-beta.2)

https://github.com/terrakube-io/terrakube/actions/runs/21143863171

## Comment by themaroqa on 2026-01-20

I tested it. Unfortunately that's not the root cause of the issue. I've set VcsGitlabTimeOut to 120 but still after 30 seconds I hit the timeout. I enabled debug log for the API and I see that it reads 12 pages before "giving up" with the same java.lang.InterruptedException error. 
I also double checked my whole network infrastructure but I would say there are no 30 seconds timeout there. 

PS: Be careful about VcsGitlabPageSize variable. I set it to 50 and I hit a buffer overflow error because the message was too big. Maybe there was a reason for having it fixed :)

## Comment by alfespa17 on 2026-01-20

Maybe you can try doing the same request to the project API using the same query parameter from the below like with postman 

https://github.com/terrakube-io/terrakube/blob/4f47b469d8ae15dfcd66c35334a0405cb6fee51e/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L394

Maybe you can see what happens when it reaches page 12

## Comment by themaroqa on 2026-01-20

I have a simple postman script that run the /projects api iterating through pages. When it reaches page 12 nothing strange happens. It simply proceed to call page 13. It reads 38 pages and it takes 3 minutes to complete as average. 
The only workaround I am thinking about is to use a dedicated GitLab user instead of my own account for setting up the VCS Provider that has access only to a subset of projects. 

Anyhow I suggest you to add the `simple=true` query parameter (https://docs.gitlab.com/api/projects/#list-all-projects). You only need the id and the path_with_namespace values. Doing that every call to the API takes 1/3 of the time and those results are still given in the response.

<img width="1108" height="123" alt="Image" src="https://github.com/user-attachments/assets/f38b3073-7168-4dcb-9d72-35c1185a03f6" />

Let me know if you want to try other fixes. Otherwise I am going on with my workaround. 
If you agree I could also contribute creating the PR for the `simple=true` adjustment.

## Comment by vezzalinistefano on 2026-01-20

hi! at my company we are having the same problem, wouldn't it be possible to put the project_id as a user-inserted parameter?

## Comment by vezzalinistefano on 2026-01-20

also i do not really get why creating a new webhook needs to GET every project and then filter them client side(?), am I missing something maybe?

## Comment by alfespa17 on 2026-01-20

> I have a simple postman script that run the /projects api iterating through pages. When it reaches page 12 nothing strange happens. It simply proceed to call page 13. It reads 38 pages and it takes 3 minutes to complete as average. The only workaround I am thinking about is to use a dedicated GitLab user instead of my own account for setting up the VCS Provider that has access only to a subset of projects.
> 
> Anyhow I suggest you to add the `simple=true` query parameter (https://docs.gitlab.com/api/projects/#list-all-projects). You only need the id and the path_with_namespace values. Doing that every call to the API takes 1/3 of the time and those results are still given in the response.
> 
> <img alt="Image" width="1108" height="123" src="https://private-user-images.githubusercontent.com/23500853/538042573-f38b3073-7168-4dcb-9d72-35c1185a03f6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg5MzQyNTUsIm5iZiI6MTc2ODkzMzk1NSwicGF0aCI6Ii8yMzUwMDg1My81MzgwNDI1NzMtZjM4YjMwNzMtNzE2OC00ZGNiLTlkNzItMzVjMTE4NWEwM2Y2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjAlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIwVDE4MzIzNVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTMzYTZmNTU3YmMxY2M3ZmQwYjMzZmM1MmEzMGE4NzU1NTA2NzFkMzRhNTM0OWE0NjlhODE3MTUxN2ZmOTZkNGQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.VPatdnO8IlmEvuPDheDimJtP3O3f9KC0sH0fBamKDMQ">
> Let me know if you want to try other fixes. Otherwise I am going on with my workaround. If you agree I could also contribute creating the PR for the `simple=true` adjustment.

Hello @themaroqa there is one test case here

https://github.com/terrakube-io/terrakube/blob/b5afd59e06c9e6189b2a8c3ccc237023ffda8167/api/src/test/java/io/terrakube/api/VcsGitlabTests.java#L56

Terrakube only requires `id, path and path_with_namespace`, if adding the  `simple=true` query parameter returns that information I guess it could work without any issue.

If that is the case, you can send the PR with code change

## Comment by alfespa17 on 2026-01-20

> also i do not really get why creating a new webhook needs to GET every project and then filter them client side(?), am I missing something maybe?

Because Terrakube needs to find the project Id to send the request to create/update webhooks

Example:

https://github.com/terrakube-io/terrakube/blob/b5afd59e06c9e6189b2a8c3ccc237023ffda8167/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L356

## Comment by vezzalinistefano on 2026-01-21

yeah I get it but can't we query using the project path? 

example with curl:

```bash
PROJECT_PATH="super-awesome/project"

curl --silent --header "PRIVATE-TOKEN: $TOKEN" \
     "$GITLAB_URL/api/v4/projects/${PROJECT_PATH//\//%2F}"
```

Docs: https://docs.gitlab.com/api/projects/#get-a-single-project
