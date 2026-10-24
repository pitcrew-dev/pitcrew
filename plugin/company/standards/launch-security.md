# Standard — Launch Security Checklist

**Applies to:** every story that deploys a site or takes it live, and every major release after that.
**Read with:** [`coding-standards.md`](coding-standards.md) §7, which covers the code. This file covers the running site.
**Owned by:** the PM puts it in the acceptance criteria of the deploy or launch story; the developer does it; QA verifies every box with evidence; **the user approves the launch** (Sensitive lane).

No checklist makes a site unhackable. This one closes the doors attackers try first and makes sure you'd notice, and recover, if something got through.

---

## 1. Before going live

**Configuration**
- [ ] `APP_ENV=production`, `APP_DEBUG=false`. Error pages are generic, with no stack traces, SQL or file paths.
- [ ] `APP_KEY` is set and unique to this environment. `.env` sits outside the web root: only `public/` is served.
- [ ] HTTPS everywhere: HTTP redirects to HTTPS, and HSTS is on.
- [ ] Security headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors` (or `X-Frame-Options`), `Permissions-Policy`.
- [ ] Session cookies are `Secure`, `HttpOnly` and `SameSite=Lax` (`SESSION_SECURE_COOKIE=true`).
- [ ] No debug tools in production (Telescope, Debugbar, and the like). Install with `composer install --no-dev`.

**Nothing private is reachable.** Open each URL; each must return 403 or 404:
- [ ] `/.env`, `/.git/config`, `/composer.json`, `/storage/logs/laravel.log`, `/vendor/`, and any backup files (`*.sql`, `*.zip`). Directory listing is off.

**Accounts and access**
- [ ] No default, demo or test users, and no seeded passwords. The admin account is created by a command, with a strong password.
- [ ] Login, password reset and one-time-code routes are rate-limited. Admins use 2FA where the project supports it.
- [ ] The database user has only the rights the app needs, and the database isn't reachable from the internet.
- [ ] File permissions: only `storage/` and `bootstrap/cache/` are writable, and nothing is world-writable.

**Dependencies**
- [ ] `composer audit` and `npm audit` are clean. The PHP and framework versions still get security fixes.

**Data**
- [ ] Automatic backups of the database and uploads, stored off the server, and **one restore actually tested**.
- [ ] Only the personal data the site needs is collected, and the privacy page matches what really happens.

**Noticing trouble**
- [ ] Failed logins, permission denials and admin actions are logged (`coding-standards.md` §7.2). Errors alert a person.
- [ ] Uptime monitoring is on.

## 2. Test it like an attacker — on staging, before launch

Scan **only sites the user owns**, or has written permission to test.

| Check | Free tool | Pass |
|---|---|---|
| Common web weaknesses | OWASP ZAP baseline scan: `docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://<staging-url>` | No High findings. Medium findings fixed, or accepted by the user in `decisions.md` |
| Security headers | Mozilla HTTP Observatory, or securityheaders.com | Grade A or B |
| HTTPS setup | SSL Labs server test | Grade A |
| Private files | The URL list in §1 | All 403 or 404 |

## 3. After launch

- **Security updates arrive automatically:** GitHub Dependabot security updates (or a scheduled `composer audit`) raise a pull request when a package gets a fix.
- **Patch quickly:** security releases of PHP, the framework and packages are applied within a week.
- **Watch the logs** for failed logins and errors, weekly for the first month.
- **A one-page incident plan** in the project: who to call, how to take the site offline (`php artisan down`), how to rotate keys and passwords, and how to restore the last backup.
