# MultiPid UI selector incorrect for sub-collections

- Issue: https://github.com/IQSS/dataverse/issues/10390
- Opened by qqmyers on 2024-03-19, closed on 2024-03-27
- Labels: Type: Bug
- Fix commit: 8915dad0b41b79293cb3f7b97db30757fb0e322c

## Report

The existing code doesn't handle the case where a non-default inherited PID Provider exists - the entry shows the default which is not what will be used. This is only an issue in sub-collections (where an inherited PID provider can exist).

**What steps does it take to reproduce the issue?**

* When does this issue occur?


* Which page(s) does it occurs on?


* What happens?


* To whom does it occur (all users, curators, superusers)?


* What did you expect to happen?
As with other UI selections, the UI should show what will be used (the default or the inherited value if it exists), e.g. 
![image](https://github.com/IQSS/dataverse/assets/6731983/ad2eeb76-8ca4-42eb-aba0-93597ec34c2e)

**Which version of Dataverse are you using?**
develop


**Any related open or closed issues to this bug report?**



**Screenshots:**

No matter the issue, screenshots are always welcome.

To add a screenshot, please use one of the following formats and/or methods described here:

* https://help.github.com/en/articles/file-attachments-on-issues-and-pull-requests
*
