# Scan Policy Manager Policy multiplies while modifying the name

- Issue: https://github.com/zaproxy/zaproxy/issues/7134
- Opened by muX1337 on 2022-03-10, closed on 2022-10-07
- Labels: bug, Component-UI
- Fix commit: b53b57f0e831b0e54f858f5a84ec29a8b417aef9

## Report

### Describe the bug

When you change the Policy Name more than two Time(e.g. from upper Case to Lower-Case) then the item got duplicated, after removing one item the other cannot be modified anymore but removed.

### Steps to reproduce the behavior

1. Start Zap
2. Open Scan Policy Manager (CTRL-P)/ Analyse -> Scan Policy Manager
3. Add a new Policy
4. Name it "scan"
5. Press Ok
6. Modify the "scan"-item
7. Change Policy-Name to "Scan" and press okay again
8. Modify the item again (notice that the Policy-Name is already "scan" instead of "Scan") change the name again to "sCan" and press okay
9. Repeating step 8 to different Names creates even more Items and all of them seems to be the one which we have created first.
10. Remove one item and you cannot modify the other ones.

Attached a video how to reproduce the bug
[2022-03-10 09-59-46.zip](https://github.com/zaproxy/zaproxy/files/8221998/2022-03-10.09-59-46.zip)


### Expected behavior

The policy name is changed and no other item is created.

### Software versions

Version 2.11.1

### Screenshots

![zap_policy_name_bug](https://user-images.githubusercontent.com/9527130/157630814-c8b15f18-42b4-44dd-a4b6-4dc0db9df674.png)


### Errors from the zap.log file

_No response_

### Additional context

_No response_

### Would you like to help fix this issue?

- [X] Yes

## Comment by psiinon on 2022-03-10

Ooops yeah, I can reproduce that here :)
The code for the dialog is https://github.com/zaproxy/zaproxy/blob/main/zap/src/main/java/org/zaproxy/zap/extension/ascan/PolicyManagerDialog.java
@marvUta would you like this issue assigned to you?

## Comment by muX1337 on 2022-03-10

@psiinon  Yeap I can take a look at it this weekend, shouldn't be big problem and I can fresh up my Java Skills :D

## Comment by psiinon on 2022-03-10

Great - I've assigned it to you.
If you need any help or advice then just ask here.
If you havnt set up a ZAP Dev environment yet then see https://www.zaproxy.org/docs/developer/

## Comment by kingthorin on 2022-04-12

@marvUta any progress?

## Comment by muX1337 on 2022-04-12

@kingthorin Sorry I haven't updated the ticket. So far I've settep up everything, checkout a new branch and done some quick debugging but haven't found the issue yet.

## Comment by muX1337 on 2022-05-16

@kingthorin @psiinon 
Sorry again for the late update. 
I've fixed it so far by deleting the old-policy-file in case of a namechange but I have two questions:

1. How can I push my branch? Right now I got rejected with a 403.
2. What about the testcoverage? I can extend the ScanPolicyUnitTest with some checks if a new file was created and the old one deleted.

## Comment by kingthorin on 2022-05-16

1. Push to your fork not zaproxy's.
2. That would be perfect.

## Comment by thc202 on 2022-05-16

Take into account that some file systems are case insensitive.

## Comment by github-actions[bot] on 2023-01-06

This issue has been automatically locked since there has not been any recent activity after it was closed. Please open a new issue for related bugs.
