# Frontend System E2E Test Plan

## Scope

This Cypress suite drives the real Vue frontend pages and records all backend API traffic to prevent UI-to-API contract regressions.

## Covered Flows

- Front guest flow: home, login redirect, register, front login, user center, logout.
- Admin flow: admin login, dynamic menu loading, all main admin routes.
- User management: create user, edit base fields, reset password, admin super role removal guard.
- Role management: create role, edit role, replace role permissions, replace role menus, delete role.
- Permission management: create/edit permission, create/edit/delete API permission binding.
- Menu management: create/edit/delete menu, with update payload contract assertions.
- Rate limit and Swagger: rate-limit stats, whitelist/blacklist operations, Swagger iframe availability.

## Contract Assertions

- `/users/register` must not receive `role_codes`.
- `/users/update/{id}` must not receive `role_codes` or `password`.
- `/users/assign-roles/{id}` is the only tested user role replacement path.
- Default `admin` cannot be saved without `ROLE_SUPER_ADMIN`.
- `/roles/{id}` updates must not receive `permission_ids` or `menu_ids`.
- `/menus/{id}` updates must not receive `menu_code` or `created_by`.
- No tested frontend flow may produce a 5xx backend response.

## Network Report

Each run writes a network report to:

```text
frontend/cypress/reports/full-system-network-<RUN_ID>.json
```

The report includes test name, HTTP method, API path, status code, request body, response code, and response message.
