# Pre-launch checklist

## Infrastructure
- [ ] Managed PostgreSQL created and backed up
- [ ] Backend deployed with HTTPS
- [ ] Frontend deployed with HTTPS
- [ ] Domain + DNS configured
- [ ] `NEXT_PUBLIC_SITE_URL` set to canonical HTTPS domain
- [ ] Exact `CORS_ORIGINS` configured
- [ ] Strong random `SECRET_KEY`
- [ ] `COOKIE_SECURE=true`

## Data
- [ ] Original SQLite file copied to a safe backup
- [ ] Migration dry-run reviewed
- [ ] Row counts compared after migration
- [ ] Sample student/admin/complaint/announcement records verified
- [ ] Existing IDs remain unchanged

## Security
- [ ] No default Platform Admin password used
- [ ] Platform Admin created with a unique password
- [ ] HTTPS active
- [ ] Error responses checked for secret leakage
- [ ] Attachment upload tested with valid/invalid JPG/PNG
- [ ] Rate limiting / WAF / CDN policy added for public traffic
- [ ] Backups and restore test completed

## Product
- [ ] Student login tested
- [ ] Institute registration tested
- [ ] Platform approval tested
- [ ] Student creation/status tested
- [ ] Complaint report + duplicate detection tested
- [ ] Complaint status/department/SLA/history tested
- [ ] Feedback tested
- [ ] Announcements/notifications tested
- [ ] Campus locations/map tested
- [ ] Reports CSV tested
- [ ] Analytics tested
- [ ] Audit tested
- [ ] System health tested

## SEO / AdSense-conscious public site
- [ ] Privacy, Terms and Contact pages are live
- [ ] Public pages contain original useful content
- [ ] Navigation is clear on mobile and desktop
- [ ] `robots.txt` and `sitemap.xml` work
- [ ] Search Console property added
- [ ] No deceptive ad placement
- [ ] Ads kept away from login/report/admin controls
- [ ] Support email and organization details configured
- [ ] 404/error pages work
- [ ] Performance tested on mobile

AdSense approval cannot be guaranteed by this codebase alone; final eligibility depends on Google's review and policy compliance.
