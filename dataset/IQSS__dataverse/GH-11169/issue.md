# Shape files with upper upper case extensions are not re-zipped

- Issue: https://github.com/IQSS/dataverse/issues/11169
- Opened by jo-pol on 2025-01-20, closed on 2025-02-03
- Labels: Type: Bug
- Fix commit: 040ba43f9562e88a306e9459250c9b16f0ddc811

## Report

<!--
Thank you for contributing to the Dataverse Project through the creation of a bug report!

WARNING: If this is a security issue it should be reported privately to security@dataverse.org

More information on bug issues and contributions can be found in the "Contributing to Dataverse" page:
https://guides.dataverse.org/en/latest/contributor/index.html

Please fill out as much of the template as you can.
Start below this comment section.
-->
**What steps does it take to reproduce the issue?**

Upload a zip with a set of shape files with one or more upper case extensions.

* When does this issue occur?


* Which page(s) does it occurs on?


* What happens?

Only the shape files with lower case extensions are re-zipped. If a mandatory zip file had an upper case extensions, none are zipped

* To whom does it occur (all users, curators, superusers)?

all

* What did you expect to happen?

Shape files with upper case extension should be in the re-zipped file.

**Which version of Dataverse are you using?**



**Any related open or closed issues to this bug report?**


**Screenshots:**

No matter the issue, screenshots are always welcome.

To add a screenshot, please use one of the following formats and/or methods described here:

* https://help.github.com/en/articles/file-attachments-on-issues-and-pull-requests
*


**Are you thinking about creating a pull request for this issue?**
Yes
