# Webhook Creation Fails: Gitlab Project ID Lookup Issue (424 Failed Dependency)

- Issue: https://github.com/terrakube-io/terrakube/issues/2300
- Opened by crs07 on 2025-07-11, closed on 2025-07-11
- Labels: bug
- Fix commit: 1d66a53766cc0beb06a81a5668a11ef9916a0a63

## Report

### Bug description 🐞

We are unable to create webhooks from Terrakube to GitLab Enterprise. The Terrakube API returns a 424 Failed Dependency because it fails to retrieve the GitLab project's ID.

Symptoms:
- Terrakube UI error: 424 Failed Dependency.
- Terrakube API logs show: Search gitlab project id using it/testing-repo, https://gitlab.ourdomain.com/api/v4 followed by Response from Gitlab: [].

Root Cause:
Terrakube attempts to find the Gitlab project ID using the GET /api/v4/search?scope=projects&search=<query> API endpoint. Terrakube passes the full project path, including groups and project names (e.g., <group/project>), as the value for the search parameter.

However, on Gitlab, this specific search query does not return any results:
curl -v -H "PRIVATE-TOKEN: $PRIV_TOKEN" "https://gitlab.ourdomain.com/api/v4/search?scope=projects&search=<group>/<project>"
Result: [] (empty JSON array)

Our tests indicate that this search endpoint does not reliably find projects when given the full <group>/<project> format, returning an empty result. This prevents Terrakube from obtaining the necessary projectId to create the webhook.

Relevant Code Section:
The issue originates in the io.terrakube.api.plugin.vcs.provider.gitlab.GitLabWebhookService.getGitlabProjectId method, where the HttpRequest for project lookup is built:

// File: io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java
// ... (code omitted for brevity) ...
public String getGitlabProjectId(String ownerAndRepo, String accessToken, String gitlabBaseUrl) throws IOException, InterruptedException {
    // ...
    HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(gitlabBaseUrl + "/search?scope=projects&search=" + ownerAndRepo)) // THIS IS THE PROBLEMATIC LINE
            .header("Authorization", "Bearer " + accessToken)
            .header("Content-Type", "application/json")
            .GET()
            .build();
    // ... (rest of the method which processes the response) ...
}



### Steps to reproduce

Configure a GitLab VCS Provider in Terrakube using OAuth.

- Ensure the Terrakube OAuth application in GitLab has the api scope granted.
- Ensure the GitLab user used for authorization has at least a "Maintainer" role on the target project (<group>/<project>).

Create/Configure a Terrakube Workspace linked to a GitLab repository using its full path (e.g., <group>/<project>) as the "Source".

Attempt to create a new webhook for this Workspace via the Terrakube UI.

---
curl -H "PRIVATE-TOKEN: $PRIV_TOKEN" \
  "https://gitlab.ourdomain.com/api/v4/search?scope=projects&search=<group>/<subgroup>" | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100     2  100     2    0     0      4      0 --:--:-- --:--:-- --:--:--     4
[] <-------- (empty JSON array)


curl -H "PRIVATE-TOKEN: $PRIV_TOKEN" \
  "https://gitlab.ourdomain.com/api/v4/search?scope=projects&search=<group>/<subgroup>/<project>" | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100     2  100     2    0     0      4      0 --:--:-- --:--:-- --:--:--     4
[] <--------- (empty JSON array)


curl -H "PRIVATE-TOKEN: $PRIV_TOKEN" \                                                                                                                                                                                                ✘ INT
  "https://gitlab.ourdomain.com/api/v4/search?scope=projects&search=<project>" | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   947  100   947    0     0    912      0  0:00:01  0:00:01 --:--:--   913
[
  {
    "id": 1234,
    "description": "",
    "name": "<project>",
    "name_with_namespace": "GROUP / subgroup / <project>",
    "path": "<project>",
    "path_with_namespace": "<group>/<subgroup>/<project>",
    "created_at": "2025-06-13T13:20:09.577Z",
    "default_branch": "main",
    "tag_list": [],
    "topics": [],
    "ssh_url_to_repo": "git@gitlab.ourdomain.com:<group>/<subgroup>/<project>.git",
    "http_url_to_repo": "https://gitlab.ourdomain.com/<group>/<subgroup>/<project>.git",
    "web_url": "https://gitlab.ourdomain.com/<group>/<subgroup>/<project>",
    "readme_url": "https://gitlab.ourdomain.com/<group>/<subgroup>/<project>/-/blob/main/README.md",
    "forks_count": 0,
    "avatar_url": null,
    "star_count": 0,
    "last_activity_at": "2025-07-10T16:14:54.340Z",
    "namespace": {
      "id": 5678,
      "name": "subgroup",
      "path": "subgroup",
      "kind": "group",
      "full_path": "<group>/<subgroup>",
      "parent_id": 0123,
      "avatar_url": null,
      "web_url": "https://gitlab.ourdomain.com/groups/<group>/<subgroup>"
    }
  }
] 

### Expected behavior

When attempting to create a webhook, Terrakube's internal GitLab integration (GitLabWebhookService.getGitlabProjectId) should successfully query the GitLab API to obtain the correct numeric project ID. This requires that the project lookup query is accurately formed based on GitLab's API expectations for project identification, for instance, by querying the /api/v4/search endpoint using the project's simple name (e.g., "terraform-repo") instead of its full path, which reliably returns the project's ID.

### Example repository

_No response_

### Anything else?

_No response_

## Comment by alfespa17 on 2025-07-11

I already fixed this @crs07 you could test with this version

https://github.com/terrakube-io/terrakube/releases/tag/2.27.0-beta.3

This was the pr

https://github.com/terrakube-io/terrakube/pull/2274

## Comment by crs07 on 2025-07-11

Thanks for your prompt response and the recent fixes.

Unfortunately, the issue still persists on my end with version 2.27.0. Still empty data and 424 error. I’ve already tried the following steps:

- Deleted the existing GitLab application, VCS configuration, and related Workspaces
- Created a new GitLab application and re-registered the VCS
- Created multiple new workspaces using both HTTPS and SSH methods

All attempts are still failing with the same behavior.

Here’s the relevant log snippet from the pod:

```
Search gitlab project id using group/subgroup/project, https://gitlab.ourgitlab.com/api/v4
Response from Gitlab: []
Parsed Project ID:
```

```
Search gitlab project id using group/project, https://gitlab.ourgitlab.com/api/v4
Response from Gitlab: []
Parsed Project ID:
```

It seems the GitLab search API returns an empty response, even though the project exists and is accessible.

Could you please recheck the backend or provide any additional debugging steps I might try?

## Comment by alfespa17 on 2025-07-11

Did you grant api, repository_read and repository_write to the oauth app?

## Comment by alfespa17 on 2025-07-11

This are the test cases that I used

https://github.com/terrakube-io/terrakube/blob/9dd9381fb3695add090c9b03b96a1ef2e1592c94/api/src/main/java/io/terrakube/api/plugin/vcs/WebhookServiceBase.java#L42

## Comment by alfespa17 on 2025-07-11

This is the Api that is using

https://github.com/terrakube-io/terrakube/blob/9dd9381fb3695add090c9b03b96a1ef2e1592c94/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L168

Once it gets the response it is looking for the field path_with_namspace to find the ID 

https://github.com/terrakube-io/terrakube/blob/9dd9381fb3695add090c9b03b96a1ef2e1592c94/api/src/main/java/io/terrakube/api/plugin/vcs/provider/gitlab/GitLabWebhookService.java#L186

## Comment by crs07 on 2025-07-11

Yes, I granted API, read and write repositories. I just tried both user and wide applications but I'm still facing the same issue.

Also, I’ve been testing the current approach in the Java code, which uses the GitLab search API and then filters the results by matching path_with_namespace to find the project ID. However, when I run the equivalent curl command with the full group/subgroup/project path, I don’t get any results unless I search only by the project name without the group or subgroup prefix.

From my research and testing, I believe a more reliable method would be to query the GitLab API directly for the project by its full path (group/subgroup/project) using the endpoint:

```
GET /projects/{url_encoded_full_path}
```

For example, the equivalent curl command is:
```
curl -H "PRIVATE-TOKEN: $TOKEN" "https://gitlab.example.com/api/v4/projects/group%2Fsubgroup%2Fproject"
```

I’ve prepared a sample Java method maybe you could do something like this:

```
public String getGitlabProjectIdByFullPath(String projectFullPath, String accessToken, String gitlabBaseUrl) throws IOException, InterruptedException {
    String encodedProjectPath = URLEncoder.encode(projectFullPath, StandardCharsets.UTF_8);
    String projectId = "";

    HttpClient client = HttpClient.newHttpClient();
    HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(gitlabBaseUrl + "/projects/" + encodedProjectPath))
            .header("Authorization", "Bearer " + accessToken)
            .header("Content-Type", "application/json")
            .GET()
            .build();

    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

    if (response.statusCode() == 200) {
        ObjectMapper objectMapper = new ObjectMapper();
        JsonNode jsonNode = objectMapper.readTree(response.body());
        projectId = jsonNode.path("id").asText();
    } else {
        System.err.println("Failed to retrieve project. Status: " + response.statusCode());
        System.err.println("Response: " + response.body());
    }

    return projectId;
}
```

Please let me know your thoughts.

## Comment by crs07 on 2025-07-11

When you're querying with scope=projects, you can't search using path_with_namespace. It only works with the project name, not the full path like group/subgroup/project. That's why it never returns the project ID.

## Comment by alfespa17 on 2025-07-11

> When you're querying with scope=projects, you can't search using path_with_namespace. It only works with the project name, not the full path like group/subgroup/project. That's why it never returns the project ID.

It works with gitlab.com as you can see below:

<img width="706" height="596" alt="Image" src="https://github.com/user-attachments/assets/642e31a4-b640-42c3-a6b3-01d03ae92eee" />

<img width="706" height="596" alt="Image" src="https://github.com/user-attachments/assets/5e8905d7-8a46-4777-a8b5-3dcd5fed12b5" />

Not sure what is the difference betwwent gitlab.com and Gitlab Enterprise

I used the above for my testing

## Comment by alfespa17 on 2025-07-11

> Yes, I granted API, read and write repositories. I just tried both user and wide applications but I'm still facing the same issue.
> 
> Also, I’ve been testing the current approach in the Java code, which uses the GitLab search API and then filters the results by matching path_with_namespace to find the project ID. However, when I run the equivalent curl command with the full group/subgroup/project path, I don’t get any results unless I search only by the project name without the group or subgroup prefix.
> 
> From my research and testing, I believe a more reliable method would be to query the GitLab API directly for the project by its full path (group/subgroup/project) using the endpoint:
> 
> ```
> GET /projects/{url_encoded_full_path}
> ```
> 
> For example, the equivalent curl command is:
> 
> ```
> curl -H "PRIVATE-TOKEN: $TOKEN" "https://gitlab.example.com/api/v4/projects/group%2Fsubgroup%2Fproject"
> ```
> 
> I’ve prepared a sample Java method maybe you could do something like this:
> 
> ```
> public String getGitlabProjectIdByFullPath(String projectFullPath, String accessToken, String gitlabBaseUrl) throws IOException, InterruptedException {
>     String encodedProjectPath = URLEncoder.encode(projectFullPath, StandardCharsets.UTF_8);
>     String projectId = "";
> 
>     HttpClient client = HttpClient.newHttpClient();
>     HttpRequest request = HttpRequest.newBuilder()
>             .uri(URI.create(gitlabBaseUrl + "/projects/" + encodedProjectPath))
>             .header("Authorization", "Bearer " + accessToken)
>             .header("Content-Type", "application/json")
>             .GET()
>             .build();
> 
>     HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
> 
>     if (response.statusCode() == 200) {
>         ObjectMapper objectMapper = new ObjectMapper();
>         JsonNode jsonNode = objectMapper.readTree(response.body());
>         projectId = jsonNode.path("id").asText();
>     } else {
>         System.err.println("Failed to retrieve project. Status: " + response.statusCode());
>         System.err.println("Response: " + response.body());
>     }
> 
>     return projectId;
> }
> ```
> 
> Please let me know your thoughts.

This didn't work for me 

<img width="612" height="401" alt="Image" src="https://github.com/user-attachments/assets/1833bbf5-b02d-4c1e-abaf-e3aeec0c24af" />

## Comment by crs07 on 2025-07-11

I'm using Gitlab Enterprise, I mentioned at the beginning.

<img width="936" height="156" alt="Image" src="https://github.com/user-attachments/assets/7d9e0fda-5c46-4cfb-895d-f3e76a8b612c" />


On GitLab.com, searching with scope=projects may support more flexible matching, including path_with_namespace. However, in GitLab Enterprise (self-managed), the same endpoint only works when using the project name (not the full path like group/subgroup/project), which is why the project ID lookup is failing on my side.

To ensure compatibility across both GitLab.com and GitLab Enterprise environments, you should consider adding a conditional logic that detects the GitLab version or explicitly switches to querying the project by full path using /projects/:encoded_path, which is more reliable.

## Comment by alfespa17 on 2025-07-11

What do you think about using `https://gitlab.com/api/v4/projects?membership=true` and later just searching for `path_with_namespace` to match the correct repo? 

Maybe this can work for both gitlab and gitlab enterprise

## Comment by crs07 on 2025-07-11

Yes, I did some tests and it might work for both.

## Comment by alfespa17 on 2025-07-11

@crs07  you can test this version in some minutes

https://github.com/terrakube-io/terrakube/releases/tag/2.27.0-beta.4

## Comment by crs07 on 2025-07-11

Thanks mate I will give it a try.

## Comment by crs07 on 2025-07-11

@alfespa17 I tested it on two repositories. The first one succeeded, and the second failed due to missing pagination handling, it needs to iterate through all pages to find the correct project.

Additionally, I found another issue: when you delete a webhook from Terrakube, it creates a new one in GitLab, even though the UI shows that it's been deleted. The logs confirm that a new webhook is being created instead of properly removing it.

## Comment by alfespa17 on 2025-07-11

At least it is an improvement XD, do you know how to manage the pagination?

## Comment by crs07 on 2025-07-11

yes much better now :)

for pagination you would do something like this:

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Optional;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class GitLabProjectFetcher {

    public Optional<JsonNode> findProjectByPath(String gitlabBaseUrl, String accessToken, String targetPathWithNamespace) throws IOException, InterruptedException {
        int page = 1;
        int perPage = 100;
        HttpClient client = HttpClient.newHttpClient();
        ObjectMapper objectMapper = new ObjectMapper();

        while (true) {
            String url = String.format("%s/projects?membership=true&per_page=%d&page=%d", gitlabBaseUrl, perPage, page);
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Authorization", "Bearer " + accessToken)
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            JsonNode projects = objectMapper.readTree(response.body());

            if (!projects.isArray() || projects.size() == 0) {
                break; // No more results
            }

            for (JsonNode project : projects) {
                String pathWithNamespace = project.path("path_with_namespace").asText();
                if (targetPathWithNamespace.equals(pathWithNamespace)) {
                    return Optional.of(project); // Found the match, return it
                }
            }

            if (projects.size() < perPage) {
                break; // Last page
            }

            page++;
        }

        return Optional.empty(); // Not found
    }
}

## Comment by alfespa17 on 2025-07-15

This release should fix all of your issues with gitlab enterprise @crs07

https://github.com/terrakube-io/terrakube/releases/tag/2.27.0-beta.5

## Comment by crs07 on 2025-07-22

@alfespa17 thanks a lot it worked. I have another issue when trying to run the plan, this is the error:

[threadPoolTaskExecutor-1] ERROR org.springframework.aop.interceptor.SimpleAsyncUncaughtExceptionHandler - Unexpected exception occurred invoking async method: public void io.terrakube.executor.service.executor.ExecutorJobImpl.createJob(io.terrakube.executor.service.mode.TerraformJob)
feign.FeignException$Unauthorized: [401 ] during [GET] to [https://api.terrakube-dev.mydomain/api/v1/organization/d54ec5dc-5dj7-4ca4-8f2d-dfs56455sdf4/job/58?include=step] [TerrakubeClient#getJobById(String,String)]: []


I verified that the InternalSecret is valid matches across all the pods, also noticed that file ".terraformrc" is not being created. Can you help to debug this issue please?

## Comment by alfespa17 on 2025-07-22

> [@alfespa17](https://github.com/alfespa17) thanks a lot it worked. I have another issue when trying to run the plan, this is the error:
> 
> [threadPoolTaskExecutor-1] ERROR org.springframework.aop.interceptor.SimpleAsyncUncaughtExceptionHandler - Unexpected exception occurred invoking async method: public void io.terrakube.executor.service.executor.ExecutorJobImpl.createJob(io.terrakube.executor.service.mode.TerraformJob) feign.FeignException$Unauthorized: [401 ] during [GET] to [https://api.terrakube-dev.mydomain/api/v1/organization/d54ec5dc-5dj7-4ca4-8f2d-dfs56455sdf4/job/58?include=step] [TerrakubeClient#getJobById(String,String)]: []
> 
> I verified that the InternalSecret is valid matches across all the pods, also noticed that file ".terraformrc" is not being created. Can you help to debug this issue please?

Create a different issue for that and maybe you can add more context and logs because I didn't understand the problem
