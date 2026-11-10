# Incorrect reading of the file with artifact key identifiers

- Issue: https://github.com/s4u/pgpverify-maven-plugin/issues/499
- Opened by freedom1b2830 on 2023-11-26, closed on 2024-04-11
- Labels: bug
- Fix commit: e12c20274871d47e41cfb5a43a0105ebdff7a599

## Report

**Describe the bug**
The plugin ignores the noSig instruction for the artifact, possibly due to the use of capital letters in the version.

**To Reproduce**
```xml
<repository>
	<id>papermc</id>
	<url>https://repo.papermc.io/repository/maven-public/</url>
</repository>
<dependency>
	<groupId>io.papermc.paper</groupId>
	<artifactId>paper-api</artifactId>
	<version>1.20.1-R0.1-SNAPSHOT</version>
	<scope>provided</scope>
</dependency>
```

pgp map key file:
```
io.papermc.paper:paper-api:jar:1.20.1-R0.1-SNAPSHOT = noSig
io.papermc.paper:paper-api:pom:1.20.1-R0.1-SNAPSHOT = noSig
```
see log 
[ERROR] Unsigned artifact not listed in keys map: io.papermc.paper:paper-api:jar:1.20.1-R0.1-SNAPSHOT
[ERROR] Unsigned artifact not listed in keys map: io.papermc.paper:paper-api:pom:1.20.1-R0.1-SNAPSHOT

**Expected behavior**
plugin version, goal
pgpverify-maven-plugin:1.17.0:check

## Comment by slawekjaranowski on 2024-04-11

@freedom1b2830 - thanks for reports
