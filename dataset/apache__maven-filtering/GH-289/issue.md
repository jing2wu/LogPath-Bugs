# File name filtering does not work when the escapeString is the same as the file separator

- Issue: https://github.com/apache/maven-filtering/issues/289
- Opened by pbarnes-tibco on 2025-07-15, closed on 2026-09-24
- Labels: bug
- Fix commit: 270585b4d8cdec5cb6e1026af3bc7de625d5234b

## Report

### Affected version

3.3.1

### Bug description

On Windows, configure the maven-resources-plugin with `fileNameFiltering=true` and `escapeString=\`. Attempt to copy a resource from a subfolder of a resource directory, where the filename begins with a maven property. For example, use the following pom.xml:

    <?xml version="1.0" encoding="UTF-8"?>

    <project xmlns="http://maven.apache.org/POM/4.0.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>

      <groupId>com.test</groupId>
      <artifactId>FileNameFiltering</artifactId>
      <version>0.0.1-SNAPSHOT</version>

      <name>FileNameFiltering</name>
      <description>Reproduction of file name filtering bug</description>

      <properties>
        <file.name>myFileName</file.name>
      </properties>

      <build>
        <pluginManagement>
          <plugins>
            <plugin>
              <artifactId>maven-resources-plugin</artifactId>
              <version>3.3.1</version>
            </plugin>
          </plugins>
        </pluginManagement>
        <plugins>
          <plugin>
            <artifactId>maven-resources-plugin</artifactId>
            <executions>
              <execution>
                <id>copy-resources-filter-filename</id>
                <phase>process-resources</phase>
                <goals>
                  <goal>copy-resources</goal>
                </goals>
                <configuration>
                  <outputDirectory>${project.build.outputDirectory}</outputDirectory>
                  <fileNameFiltering>true</fileNameFiltering>
                  <escapeString>\</escapeString>
                  <resources>
                    <resource>
                      <directory>${project.basedir}/src/main/custom-resources</directory>
                      <filtering>false</filtering>
                    </resource>
                  </resources>
                </configuration>
              </execution>
            </executions>
          </plugin>
        </plugins>
      </build>
    </project>

and create empty file `src\main\custom-resources\folder\${file.name}.txt`. Expected result is the file `target\classes\folder\myFileName.txt` is created. Instead, `target\classes\folder${file.name}.txt` is created, where the subdirectory is lost and becomes part of the file name, which is not filtered.

It appears the filtering is applied to the relative path name as a whole, `folder\${file.name}.txt`, and the file separator is treated as an escape. The filtering should be applied to each file component separately, to remove the conflict with the file separator.

Presumably this can also be reproduced on linux/mac by setting `escapeString=/`, tho this is more likely to be an issue on Windows, since using `escapeString=\` is a common practice.

See the reproduction in this [GitHub repo](https://github.com/pbarnes-tibco/maven-resources-plugin-issue)

## Comment by pratx08 on 2026-01-30

Hey @pbarnes-tibco, I was able to reproduce this issue locally and i think the path separator '' is getting overlapped with escapeString. I have a probable fix where the collision of '' in DefaultMavenResourcesFiltering.getDestinationFile() retains the directory structure. I have raised a [Pull Request](https://github.com/apache/maven-filtering/pull/320) with the fix and a test please look into it when you find time.

## Comment by pbarnes-tibco on 2026-02-13

Thanks for looking into this @pratx08. I took a look at your PR. It looks like that would fix the issue on Windows. But it would probably fail on linux/mac if the escape string was set to '/'. Though, admittedly, that would be unusual. I too have a PR open since last July, but no activity on it.

## Comment by cstamas on 2026-02-27

Please agree on proper fix and make a PR against 3.x branch, as release is to happen soon (ie next week or so)

## Comment by pbarnes-tibco on 2026-02-27

@cstamas My fix works on all platforms. I've created a PR on the maven-filtering-3.x branch. Note that the original PR on master still exists. Let me know if I need to do anything with it.

## Comment by cstamas on 2026-02-27

Thanks, will look at it over the weekend. I plan release (3.x) somewhere on next week (along with m-resources-p) and m-shade-p.

## Comment by gnodet on 2026-09-24

Fixed in:

- **master (4.x)**: PR apache/maven-filtering#290 — merged 2026-09-24
- **maven-filtering-3.x**: included in the batch backport PR apache/maven-filtering#396 — merged 2026-09-24

The fix filters each path component independently instead of the full relative path, so the `escapeString` (e.g. `\` on Windows, or `/` on any platform) can no longer be confused with a path separator.

The fix will ship with **3.5.2** (draft release already staged) and the upcoming 4.0.0-beta-2.
