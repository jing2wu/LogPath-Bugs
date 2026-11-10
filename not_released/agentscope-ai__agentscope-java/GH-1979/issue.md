# [Bug]: ClasspathSkillRepository failed to load skills in jar application

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/1979
- Opened by benko233 on 2026-07-01, closed on 2026-07-06
- Labels: bug
- Fix commit: 284186307c510d2490621fe1815fc619f8d53aba

## Report

**<u>AgentScope-Java is an open-source project. To involve a broader community, we recommend asking your questions in English.</u>**

**Describe the bug**
ClasspathSkillRepository failed to load skills in jar application

**To Reproduce**
the second ClasspathSkillRepository instance throws FileSystemAlreadyExistsException cause by the file system has already been created by the first ClasspathSkillRepository instance. 

<img width="1035" height="626" alt="Image" src="https://github.com/user-attachments/assets/af88b04a-0c78-44e9-82b6-006724c255cc" />

**Expected behavior**
reuse FileSystem like this:


     
            if ("jar".equals(uri.getScheme())) {
                this.isJar = true;

                FileSystem fs;
                try {
                    fs = FileSystems.getFileSystem(uri);
                } catch (FileSystemNotFoundException e) {
                    fs = FileSystems.newFileSystem(uri, Collections.emptyMap());
                }
                this.fileSystem = fs;
                String schemeSpecificUriPath = uri.getSchemeSpecificPart();
                String actualResourcePath =
                        schemeSpecificUriPath.substring(schemeSpecificUriPath.lastIndexOf("!") + 1);
                logger.info("Actual resource path: {}", actualResourcePath);
                this.skillBasePath = fileSystem.getPath(actualResourcePath);
            } else {



**Error messages**
Caused by: org.springframework.beans.BeanInstantiationException: Failed to instantiate [io.agentscope.core.skill.SkillBox]: Factory method 'skillBox' threw exception with message: Failed to load skills from classpath
	at org.springframework.beans.factory.support.SimpleInstantiationStrategy.instantiate(SimpleInstantiationStrategy.java:178)
	at org.springframework.beans.factory.support.ConstructorResolver.instantiate(ConstructorResolver.java:644)
	... 130 common frames omitted
Caused by: java.lang.IllegalStateException: Failed to load skills from classpath
	at com.ruoyi.agent.core.config.SkillBoxConfig.skillBox(SkillBoxConfig.java:34)
	at com.ruoyi.agent.core.config.SkillBoxConfig$$SpringCGLIB$$0.CGLIB$skillBox$0(<generated>)
	at com.ruoyi.agent.core.config.SkillBoxConfig$$SpringCGLIB$$FastClass$$1.invoke(<generated>)
	at org.springframework.cglib.proxy.MethodProxy.invokeSuper(MethodProxy.java:258)
	at org.springframework.context.annotation.ConfigurationClassEnhancer$BeanMethodInterceptor.intercept(ConfigurationClassEnhancer.java:348)
	at com.ruoyi.agent.core.config.SkillBoxConfig$$SpringCGLIB$$0.skillBox(<generated>)
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(Unknown Source)
	at java.base/java.lang.reflect.Method.invoke(Unknown Source)
	at org.springframework.beans.factory.support.SimpleInstantiationStrategy.instantiate(SimpleInstantiationStrategy.java:146)
	... 131 common frames omitted
Caused by: java.nio.file.FileSystemAlreadyExistsException: null
	at jdk.zipfs/jdk.nio.zipfs.ZipFileSystemProvider.newFileSystem(Unknown Source)
	at java.base/java.nio.file.FileSystems.newFileSystem(Unknown Source)
	at java.base/java.nio.file.FileSystems.newFileSystem(Unknown Source)
	at io.agentscope.core.skill.repository.ClasspathSkillRepository.<init>(ClasspathSkillRepository.java:142)
	at io.agentscope.core.skill.repository.ClasspathSkillRepository.<init>(ClasspathSkillRepository.java:93)
	at com.ruoyi.agent.core.config.SkillBoxConfig.skillBox(SkillBoxConfig.java:27)
	... 139 common frames omitted

**Environment (please complete the following information):**

- AgentScope-Java Version: 2.0.0-RC4
- Java Version: 21
- OS: [e.g. macos, windows]

**Additional context**
Add any other context about the problem here.
