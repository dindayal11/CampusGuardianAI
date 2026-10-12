# Deployment

Next.js 16 requires Node.js 20.9+.

Recommended public topology:
- `www.example.com` -> Next.js
- `api.example.com` (or `/api`) -> FastAPI
- managed PostgreSQL
- object storage for uploaded complaint images

Deployment sequence:
1. Create a private GitHub repository.
2. Configure production environment variables.
3. Provision PostgreSQL.
4. Run the SQLite migration against a backup copy.
5. Compare row counts and critical records.
6. Deploy the API.
7. Deploy the Next.js website.
8. Configure HTTPS and DNS.
9. Run end-to-end Student/Admin tests.
10. Configure Search Console and sitemap.
11. Replace starter legal pages with the real policies.
12. Add AdSense only after the site has substantial original useful content and
    the actual publisher ID is available.

Never commit credentials or a production database into Git.
