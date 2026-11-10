# init-app for React does not produce package-info.java

- Issue: https://github.com/vaadin/hilla/issues/1935
- Opened by mcollovati on 2023-12-24, closed on 2024-01-02
- Labels: bug, hilla, Released with Hilla 24.4.0.alpha1, prerelease version for Hilla 24.4.0
- Fix commit: 3ef265f45b0991b8232f3600ad8ab9aa2a6e452b

## Report

### Describe the bug

When initializing a React application with Hilla `init-app` feature, the `package-info.java` is missing in the endpoint package, causing a TypeScript error when starting the application.

```
ERROR(TypeScript)  Argument of type 'string | undefined' is not assignable to parameter of type 'string'.
 Type 'undefined' is not assignable to type 'string'.
FILE  /home/xxx/getting-started/frontend/views/MainView.tsx:21:29
   19 |         onClick={async () => {
   20 |           const serverResponse = await HelloEndpoint.sayHello(name);
 > 21 |           Notification.show(serverResponse);
      |                             ^^^^^^^^^^^^^^
   22 |         }}
   23 |       >
```

Manually adding the `package-info.java` file fixes the issue


### Expected-behavior

An application created with `init-app` should start without any errors.

### Reproduction

* Create an empty Hilla application with `npx @hilla/cli init --empty my-hilla-app`
* Execute `mvn hilla:init-app` to create source code
* Start the application with `mvn` and verify that a typescript error is reported on the server logs


### System Info

Hilla: 2.5.5

## Comment by vaadin-bot on 2024-01-12

This ticket/PR has been released with Hilla 24.4.0.alpha1 and is also targeting the upcoming stable 24.4.0 version.
