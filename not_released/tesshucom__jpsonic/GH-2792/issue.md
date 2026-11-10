# NoResourceFoundException: No static resource logout

- Issue: https://github.com/tesshucom/jpsonic/issues/2792
- Opened by tesshucom on 2025-11-09, closed on 2025-11-11
- Labels: type: bug, in: web
- Fix commit: e64286cd37342bf4481fb942b8f8cbe6c468ea10

## Report

Prerequisites:  #2764

## Problem description

When accessing /logout, Spring attempts to resolve it as a static resource instead of handling it as a Spring Security endpoint.

### Steps to reproduce

Logout

## System information

 * **Jpsonic version**: DEVELOP

### Cause

In Spring Security 6+, logout handling is no longer automatically mapped to /logout unless explicitly configured.
If requestMatchers("/logout") is not included in the security configuration, the request is passed to ResourceHttpRequestHandler, resulting in NoResourceFoundException.

### Current Implementation

GlobalSecurityConfig does not explicitly configure a logout endpoint. As a result, /logout is not matched by the security filter chain and is treated as a static resource path.

### Recommended Fix

Explicitly define logout handling in the Spring Security configuration, for example:

```
http
    .logout(logout -> logout
        .logoutUrl("/logout")
        .logoutSuccessUrl("/")
        .permitAll()
    );
```

Alternatively, if /logout should be handled by a REST controller, disable Spring Security’s default logout and map /logout manually.
