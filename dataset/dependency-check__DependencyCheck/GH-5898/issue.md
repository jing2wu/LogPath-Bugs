# Pip analyzer not showing vulnerabilities

- Issue: https://github.com/dependency-check/DependencyCheck/issues/5898
- Opened by stevieg27 on 2023-08-23, closed on 2023-10-05
- Labels: bug
- Fix commit: 949661be7154cae1923652928a8eaa0878e64fa5

## Report

**Describe the bug**
I was testing a python project using the experimental analyzer which has a requirements.txt file inside it. . While testing `cryptography~=1.8.2`  library present inside the requirements.txt , the result doesn't show any kind of vulnerabilities but `cryptography==1.8.2` shows three different vulnerabilities dating back from 2020. How can I properly test this scenario using dependency check to get those valid vulnerabilities?

**Version of dependency-check used**
CLI version 8.4.0



**To Reproduce**
Python project folder which contains requirements.txt file and has cryptography~=1.8.2 library defined. Then scan using latest cli
 ./dependency-check.sh -s ./ --enableExperimental 

**Expected behavior**
Since all the version above 1.9.0 has different vulnerabilities it should have resulted in showing that. Ref: https://security.snyk.io/package/pip/cryptography/1.9

**Additional context**
Add any other context about the problem here.
