# Unexpected error when requesting a non configured CRS

- Issue: https://github.com/nlsfi/hakunapi/issues/232
- Opened by tsallinen on 2026-10-14, closed on 2026-10-16
- Labels: bug
- Fix commit: 8a24c0ee9e2649c4e4f81bd4aee40be2e0d1f3d0

## Report

If a custom CRS (other than 84/4326) is requested, like "crs=http://www.opengis.net/def/crs/EPSG/0/3067" and this is not configured with srid-parameter, an "HTTP 500 Unexpected error occured" error is displayed and a java.util.NoSuchElementException: No value present stacktrace logged.

A more intuitive error message would be useful for both the API user and the Hakunapi server administrator.
