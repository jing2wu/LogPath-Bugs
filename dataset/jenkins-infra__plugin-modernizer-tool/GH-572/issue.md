# UpdateBomVersionVisitor is failing when bom artifact id is non-standard

- Issue: https://github.com/jenkins-infra/plugin-modernizer-tool/issues/572
- Opened by jonesbusy on 2025-01-04, closed on 2025-01-08
- Labels: bug
- Fix commit: 583361308d028165531eea44dfc1594ffb3a6bcf

## Report

### Plugin Modernizer version

1145.v9716249cc13c

### What Operating System are you using

WSL2

### Reproduction steps

plugin-modernizer dry-run --plugins kubernetes-cli --recipe UpgradeToRecommendCoreVersion

### Expected Results

plugin-modernizer dry-run --plugins kubernetes-cli --recipe UpgradeToRecommendCoreVersion

```xml

  <properties>
    <!-- dependency versions -->
    <jenkins.version>2.401.3</jenkins.version>
    <bom.artifactId>bom-2.401.x</bom.artifactId>
    <bom.version>2555.v3190a_8a_c60c6</bom.version>
</properties>

...


  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>io.jenkins.tools.bom</groupId>
        <artifactId>${bom.artifactId}</artifactId>
        <version>${bom.version}</version>
        <scope>import</scope>
        <type>pom</type>
      </dependency>
  </dependencies>
</dependencyManagement>
```

```
25-01-04T16:16:10.699Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR] Failed to execute goal org.openrewrite.maven:rewrite-maven-plugin:5.47.3:run (default-cli) on project kubernetes-cli: Execution default-cli of goal org.openrewrite.maven:rewrite-maven-plugin:5.47.3:run failed: Error while visiting pom.xml: java.lang.IllegalArgumentException: Illegal character in path at index 57: https://repo.jenkins-ci.org/public/io/jenkins/tools/bom/${bom.artifactId}/maven-metadata.xml 
2025-01-04T16:16:10.699Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   java.base/java.net.URI.create(URI.java:906) 
2025-01-04T16:16:10.699Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.ipc.http.HttpSender$Request$Builder.<init>(HttpSender.java:146) 
2025-01-04T16:16:10.699Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.ipc.http.HttpSender.newRequest(HttpSender.java:70) 
2025-01-04T16:16:10.699Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.ipc.http.HttpSender.get(HttpSender.java:58) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.maven.internal.MavenPomDownloader.requestAsAuthenticatedOrAnonymous(MavenPomDownloader.java:917) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.maven.internal.MavenPomDownloader.downloadMetadata(MavenPomDownloader.java:276) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.maven.internal.MavenPomDownloader.downloadMetadata(MavenPomDownloader.java:226) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   io.jenkins.tools.pluginmodernizer.core.visitors.UpdateBomVersionVisitor.lambda$getLatestBomVersion$4(UpdateBomVersionVisitor.java:130) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.maven.table.MavenMetadataFailures.insertRows(MavenMetadataFailures.java:78) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   io.jenkins.tools.pluginmodernizer.core.visitors.UpdateBomVersionVisitor.getLatestBomVersion(UpdateBomVersionVisitor.java:129) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   io.jenkins.tools.pluginmodernizer.core.visitors.UpdateBomVersionVisitor.getLatestBomVersion(UpdateBomVersionVisitor.java:91) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   io.jenkins.tools.pluginmodernizer.core.visitors.UpdateBomVersionVisitor.visitDocument(UpdateBomVersionVisitor.java:72) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   io.jenkins.tools.pluginmodernizer.core.visitors.UpdateBomVersionVisitor.visitDocument(UpdateBomVersionVisitor.java:25) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.xml.tree.Xml$Document.acceptXml(Xml.java:149) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.xml.tree.Xml.accept(Xml.java:53) 
2025-01-04T16:16:10.700Z [INFO] [Thread=StreamPumper-systemOut] - i.j.t.p.core.impl.MavenInvoker # [ERROR]   org.openrewrite.TreeVisitor.visit(TreeVisitor.java:250) 
```

This deserve a test.

Better to not fail and skip if we cannot do anything
