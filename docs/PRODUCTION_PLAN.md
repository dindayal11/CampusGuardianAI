# Production conversion plan

## Target architecture

Browser/mobile client
        |
      HTTPS
        |
     Next.js
        |
     FastAPI
        |
    PostgreSQL
        |
  +-----+------+
  |            |
Local AI   Object storage

## Rules
1. PostgreSQL becomes the source of truth after migration.
2. The browser never talks directly to PostgreSQL.
3. Student and Institute Admin requests are tenant scoped.
4. Platform Admin is the only cross-institute role.
5. Existing SQLite records remain available until migration validation passes.
6. Public pages are separated from authenticated application screens.
7. Ads, when approved and configured, should stay away from login, reporting,
   security and administration workflows.
