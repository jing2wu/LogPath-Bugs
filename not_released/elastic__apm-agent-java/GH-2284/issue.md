# About hostname

- Issue: https://github.com/elastic/apm-agent-java/issues/2284
- Opened by zt9788 on 2021-11-24, closed on 2021-11-25
- Labels: bug, agent-java, community, triage
- Fix commit: 3752548664bcd88bd8ee65e798688d089e5f8fee

## Report

My server name is service type+IP, which was correct in kibana before version 1.26. The new version 1.27 omits the part
The name is  like `business-10.0.0.1`,now the kibana display `business-10`
so ,How can the apm to display the full name? or I need to set property apm.hostname?

## Comment by eyalkoren on 2021-11-24

This should be fixed by #2286 and expected to be released soon.
In the mean time, if can you verify the fix by trying the [snapshot build](https://apm-ci.elastic.co/blue/organizations/jenkins/apm-agent-java%2Fapm-agent-java-mbp/detail/PR-2286/1/artifacts), that would be great.

## Comment by zt9788 on 2021-11-25

I have try the snapshot version ,
that is OK. kibana has show full name
