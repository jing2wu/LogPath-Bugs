# Cloud Template folder name is used when validating if the record exists on the server, but the name in the details.json is used when creating/updating

- Issue: https://github.com/vmware/build-tools-for-vmware-aria/issues/210
- Opened by Michaelpalacce on 2024-01-04, closed on 2024-07-10
- Labels: kind/bug, area/artifact-manager
- Fix commit: 286f4b8db03211d963a611356092ec44bf3131ed

## Report

### Description

Perhaps we can think of a structure where only one or the other is used as a source of truth. A good option would be to only use the folder name and add it to the details.json. 

It would be beneficial if we take a similar approach to other resources to unify the logic as much as possible?

### Alternatives

An alternative solution would be to use the details.json, however that will conflict with how the resources are exported.

### Additional Context

N/A

## Comment by Michaelpalacce on 2024-01-08

We can submit a bugfix to use the information in the details.json exclusively, as well as add a quick check if the 2 are the same and fail if the details.json and the folder name are not the same.

## Comment by Michaelpalacce on 2024-02-01

@Nikson998 What is the progress on this one?

## Comment by Nikson998 on 2024-02-01

Will make a commit into the branch

On Thu, Feb 1, 2024 at 11:46 AM Stefan Genov ***@***.***>
wrote:

> @Nikson998 <https://github.com/Nikson998> What is the progress on this
> one?
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/vmware/build-tools-for-vmware-aria/issues/210#issuecomment-1920920593>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/BD2MJECN7S4H4RVA4MTMHYLYRNQA5AVCNFSM6AAAAABBMPZGD2VHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHMYTSMRQHEZDANJZGM>
> .
> You are receiving this because you were mentioned.Message ID:
> ***@***.***>
>

-- 
This electronic communication and the information and any files transmitted 
with it, or attached to it, are confidential and are intended solely for 
the use of the individual or entity to whom it is addressed and may contain 
information that is confidential, legally privileged, protected by privacy 
laws, or otherwise restricted from disclosure to anyone else. If you are 
not the intended recipient or the person responsible for delivering the 
e-mail to the intended recipient, you are hereby notified that any use, 
copying, distributing, dissemination, forwarding, printing, or copying of 
this e-mail is strictly prohibited. If you received this e-mail in error, 
please return the e-mail to the sender, delete it from your computer, and 
destroy any printed copy of it.

## Comment by github-actions[bot] on 2024-03-03

This issue is stale because it has been open 30 days with no activity. Remove stale label or comment or this will be closed in 7 days.

## Comment by github-actions[bot] on 2024-03-10

This issue was closed because it has been stalled for 7 days with no activity.
