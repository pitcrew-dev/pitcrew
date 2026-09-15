# Standard — Coding Standards

**Default profile:** PHP 8.2+ / Laravel 11+ / MySQL 8 · Blade + SCSS + jQuery, bundled by Vite — i.e. **Profile A** in [`stack-profiles.md`](stack-profiles.md).
**Applies to:** `backend-developer`, `frontend-developer`, `full-stack-developer`
**Enforced by:** `code-reviewer` at the review gate. A change violating a MUST is rejected, not negotiated.

> ### ⚠ This file is rung 4
>
> [`engagement-modes.md`](engagement-modes.md) governs. This file applies **in full only to greenfield projects on Profile A**.
>
> In an existing project, the project's own config and observed conventions (`.claude/project/conventions.md`) outrank everything below, and `stack-profiles.md` says which of these sections are suspended entirely — §2, §3, and §4 do not apply outside Laravel at all.
>
> **Code consistent with the surrounding codebase and inconsistent with this file is correct.** The reverse is a defect.
>
> The exception is **§7, the security baseline**, which applies everywhere, always, in every profile and every mode.

---

## 1. PHP — general

- **PSR-12** formatting. Run Laravel Pint before every commit: `./vendor/bin/pint`. Unformatted code fails review.
- `declare(strict_types=1);` at the top of every PHP file under `app/`.
- **Type everything.** Parameter types, return types, and typed properties are mandatory. Use `?Type` for nullable, never an untyped default of `null`. Where a native type is insufficient, add a PHPDoc generic: `@return Collection<int, User>`.
- Constructor property promotion for dependencies. Inject via the constructor; do not resolve out of the container inside a method (`app()`, `resolve()`) except in framework bootstrapping.
- **No `env()` outside `config/`.** Config is cached in production and `env()` returns `null` there. Read `config('services.foo.key')`.
- Prefer early returns to nested conditionals. A method nesting more than two levels deep is a refactor signal.
- No commented-out code, no `dd()`, `dump()`, `var_dump()`, `ray()`, or stray `Log::debug()` in a commit.

## 2. Laravel structure

**Controllers are thin.** A controller method may: authorize, accept a validated request, call one service or action, and return a response. It may not contain business rules, query building, or data shaping.

```php
public function store(StoreUserRequest $request, CreateUser $createUser): RedirectResponse
{
    $user = $createUser->handle($request->validated());

    return to_route('users.show', $user)->with('status', __('user.created'));
}
```

- **Validation lives in FormRequests**, never inline in a controller. Authorization lives in Policies, invoked via `authorize()` or a `can` middleware — never an inline role check.
- **Business logic lives in** `app/Services/` (stateful, multi-step) **or** `app/Actions/` (one public `handle()` method, one job). Pick one per operation; do not split logic across both.
- **Eloquent belongs in models and query scopes**, not in controllers or Blade. Complex reads go in a dedicated query class or a scope, not an inline chain in a controller.
- **Resource controllers use the seven standard actions** with conventional route names (`users.index`, `users.store`, …). A verb outside the seven (`activate`, `publish`) becomes its own single-action controller rather than a custom method bolted onto the resource.
- Anything slow, external, or retryable is a **queued job**, not inline work in a request. Email, third-party API calls, image processing, and report generation are all queued.
- Wrap multi-write operations in `DB::transaction()`. A partial write is a defect even when every individual statement succeeded.

## 3. Database

- **Migrations are append-only once merged.** Editing a merged migration is prohibited; correct it with a new migration. Every migration has a working `down()`.
- Tables plural snake_case (`order_items`); columns snake_case; foreign keys `<singular>_id`; pivots singular-alphabetical (`role_user`).
- Declare foreign keys with `constrained()` and an explicit `onDelete` behavior. Index every foreign key and every column used in a `where` or `orderBy` on a table expected to exceed ~10k rows.
- Money is `decimal(<precision>, 2)` or an integer of minor units — **never** `float`. Timestamps are UTC in storage; conversion to local time is a presentation concern.
- **N+1 queries are defects.** Eager-load with `with()`. Keep `Model::preventLazyLoading()` enabled in non-production environments so violations fail loudly.
- Never interpolate user input into `DB::raw()`. Bind parameters.

## 4. Blade

- **No business logic in templates.** Permitted: loops, conditionals on already-computed values, formatting, and `route()`/`__()` calls. Prohibited: queries, `->save()`, arithmetic on domain values, and re-deriving anything the controller could have passed.
- Escape by default with `{{ }}`. `{!! !!}` requires a comment on the line above stating why the content is trusted and where it was sanitized.
- Every form carries `@csrf`. Non-POST verbs use `@method`.
- Reuse via `<x-component>` and layout inheritance. A block of markup appearing three times becomes a component.
- **No user-facing string literals in templates** — everything through `__()` / `@lang`, with keys in `lang/`.
- **No `<style>` or `<script>` blocks in templates.** Styles go to SCSS, behavior goes to JS modules. The single exception is passing server data to JS (§6).

## 5. SCSS

- Files live in `resources/sass/`, organized as `abstracts/` (variables, mixins, functions), `base/`, `components/`, `layouts/`, `pages/`, with `app.scss` importing them in that order. Partials are `_name.scss` and are imported, never linked directly.
- **BEM naming**: `.block`, `.block__element`, `.block--modifier`. One block per component file, and the file is named for the block.
- **Nesting depth is capped at 3.** Deeper nesting means the markup is fighting the naming; fix the naming. Use `&__element` for BEM, not descendant nesting.
- **No magic numbers and no raw hex outside `abstracts/_variables.scss`.** Colors, spacing, breakpoints, radii, and z-index tiers are variables. A z-index that is not on the declared scale is rejected.
- **`!important` is prohibited** except to override a third-party stylesheet, and then only with an explanatory comment.
- Mobile-first: base styles are the small viewport; widen with `min-width` media queries via the breakpoint mixin.
- No IDs as style hooks and no styling off `js-` hooks or `data-*` attributes.

## 6. jQuery

- **All JS is a module under `resources/js/`, bundled by Vite.** No `<script>` blocks in Blade beyond the data bridge below, and no CDN `<script>` tags — dependencies come through `package.json`.
- **No inline event handlers.** `onclick="doThing()"` in markup is rejected on sight.
- **Bind behavior to `js-` classes or `data-*` attributes, never to styling classes.** A designer renaming `.btn-primary` must not break behavior.
  ```js
  $(document).on('click', '.js-user-delete', function (e) { … });
  ```
- **Delegate events** from a stable ancestor so dynamically inserted markup works without rebinding.
- **Scope every lookup.** `$('.item')` inside a component searches the whole document; use `$root.find('.item')`. Cache repeated selections in a variable rather than re-querying.
- **Server data reaches JS through `data-*` attributes or one JSON script tag** — never by templating values into a JS file or expression:
  ```blade
  <div class="js-user-table" data-endpoint="{{ route('users.search') }}"></div>
  ```
  ```blade
  <script type="application/json" id="page-data">@json($payload)</script>
  ```
- **AJAX**: send the CSRF token, handle the failure branch, and disable the trigger while the request is in flight. A request with no error handling and no double-submit guard is incomplete.
- **Never build HTML from user input by string concatenation.** Use `.text()` for text, or render a server-side partial and insert it. `.html()` with interpolated user data is an XSS defect.
- Each page or component gets one entry module with an idempotent `init()` guarded by a presence check, so it is inert on pages that do not use it.

## 7. Security baseline

Non-negotiable, and checked at review regardless of what the task asked for.

**Why this section is stricter than it looks.** Independent 2026 testing found roughly **45% of AI-generated code samples introduce an OWASP Top 10 vulnerability**, with 86% failing to defend against XSS and 88% vulnerable to log injection — while syntax correctness exceeds 95%. Generated code looks right far more reliably than it *is* right, so the defence has to sit downstream of generation, in this list and at the review gate.

- No secrets in code, config, or commits — `.env` only, and `.env` is never committed. A `PostToolUse` hook scans every written file; treat a flag as real until you have proved otherwise.
- Every write route authorizes; never trust a hidden form field or a client-supplied ID to establish permission.
- Mass assignment is guarded: `$fillable` declared explicitly, never `$guarded = []` on a model reachable from user input.
- Uploads validate MIME type and size, are stored outside the webroot, and are served through a route that authorizes.
- Redirects to user-supplied URLs are validated against an allowlist.
- Any change touching authentication, authorization, payment, PII, file upload or migrations is a **Sensitive** task. It gets the threat check (§7.6), Claude Code's `/security-review`, and the user's approval before merge. There is no `security-engineer` role yet; this is never simply skipped.

### 7.1 Dependencies — verify existence before installing

Language models invent packages that do not exist, and attackers register those invented names to serve malware ("slopsquatting"). Before adding **any** dependency:

- [ ] **Confirm the package actually exists** on Packagist or npm. Never install a name you recalled rather than read.
- [ ] Check its age, download count, and last release. A package matching your need exactly but published last week is a red flag, not a lucky find.
- [ ] Confirm the maintainer and repository are the ones you expect — typosquats differ by a character.
- [ ] Justify it: what in the project cannot do this already?
- [ ] Get architect approval and security sign-off (`engagement-modes.md` §4). In brownfield, a new dependency may be impossible for deployment reasons that are not visible in the code.
- [ ] After any dependency change, run `composer audit` / `npm audit`. A known-vulnerable version is blocking.

Never install a package to resolve an import you wrote from memory. Fix the import.

### 7.2 Logging

- **Never log secrets, tokens, passwords, full card numbers, or personal data.** Log identifiers, not payloads.
- **Sanitize newlines out of user-controlled values before logging them.** Untreated, a user submitting `\n` forges log entries — this is log injection, and generated code fails it about 88% of the time.
- **Log what matters for security:** failed logins, permission denials, password resets and admin actions, with the actor's ID and never the payload.
- Log exceptions with context, never raw request bodies.
- Error responses shown to users must not leak stack traces, SQL, file paths, or internal identifiers.

### 7.3 What is enforced automatically, and what is not

The installer adds two deterministic layers that no agent can forget or skip:

- **Permission rules** in `settings.json`. Agents can never read or write `.env` files. `migrate:fresh`, `db:wipe` and force-push are denied. Pushes, hard resets and branch deletions ask the user first.
- **Hooks** in `~/.claude/hooks/agent-company/`. They:
  - block writes to dependencies, build output, secrets, private keys, WordPress core and lock files
  - stop irreversible shell and PowerShell commands
  - scan every written file for credentials
  - run the project's own Pint on PHP files, but only where that can't cause a drive-by reformat

**Everything else in this section is still on you.** Neither layer can see an authorization branch you failed to write, an unescaped variable, or a missing CSRF token. They are a floor, not a gate.

### 7.4 OWASP Top 10:2025 — what new code must do

| # | Risk | New code must |
|---|---|---|
| A01 | Broken access control (now includes SSRF) | Authorize **reads** as well as writes: scope queries to the user (`$user->orders()->findOrFail($id)`), never trust an ID from the request alone. A URL the server fetches must be `http`/`https`, public hosts only, with private and link-local IP ranges refused. |
| A02 | Security misconfiguration | In production: `APP_DEBUG=false`; security headers (CSP, HSTS, `frame-ancestors`, `X-Content-Type-Options`); session cookies `Secure`, `HttpOnly`, `SameSite=Lax`; a CORS allowlist, never `*` with credentials. |
| A03 | Software supply chain | §7.1: packages verified to exist, lock files committed, audit clean. |
| A04 | Cryptographic failures | HTTPS only. Personal data at rest through the `encrypted` cast. Tokens from `Str::random()` / `random_bytes()`. Passwords through `Hash::make()` / `password_hash()`. Never home-made crypto. |
| A05 | Injection | The floor above. XML is parsed **without** external entities (never `LIBXML_NOENT`), tested with a hostile document. |
| A06 | Insecure design | Sensitive tasks answer the threat check (§7.6) before implementation. |
| A07 | Authentication failures | Rate-limit login, password reset and one-time-code routes; regenerate the session on login; use `Password::defaults()` or equivalent; give one message for "no such user" and "wrong password"; offer 2FA for admin accounts where the project supports it. |
| A08 | Data integrity failures | Verify webhook signatures; use signed URLs for sensitive links; never deserialize untrusted data. |
| A09 | Logging and alerting failures | §7.2. |
| A10 | Mishandling exceptional conditions | §7.5. |

**Code that calls an AI model** (prompt injection is the #1 risk on OWASP's list for LLM applications):
- Text sent to a model (user input, fetched pages, feed items) is **data, never instructions**.
- The model's output is untrusted input. Validate it against a schema (structured output), and never let it alone decide what a business rule must decide: publishing, permissions, spending.
- Test with a hostile input: *"ignore your instructions and…"*

### 7.5 Error handling — fail closed

- When a security decision errors, **deny**. An exception in an authorization check, a signature check or a rate limiter must never end in "allow".
- Catch specific exceptions, only where you can act on them. No empty `catch`, and no catch-and-continue in silence.
- Every external call has a timeout, a failure branch and a message for the user. Retry only transient errors, with a cap.
- Users see a plain message; the log gets the context (§7.2).

### 7.6 Threat check — every Sensitive task, before implementation

The PM writes five short answers into the task record; review checks the code against them:

1. **Who can reach this?** Which roles, and anonymous visitors?
2. **What could they read or change that isn't theirs?**
3. **What if they lie?** A forged ID, a tampered field, a replayed request, an oversized upload.
4. **What gets logged?** Does any of it leak secrets or personal data?
5. **What happens when something it depends on fails?** Does it fail closed?

## 8. Naming

| Thing | Convention | Example |
|---|---|---|
| Class | StudlyCase, singular | `OrderItem` |
| Method / variable | camelCase | `calculateTotal()` |
| Constant / config key | UPPER_SNAKE / lower.dot | `MAX_RETRIES`, `services.stripe.key` |
| Route name | dot, resource-first | `orders.items.store` |
| Blade view | dot, lowercase | `orders.items.index` |
| Translation key | dot, namespaced | `order.status.pending` |
| SCSS block | kebab-case BEM | `order-card__title--muted` |
| JS behavior hook | `js-` prefix, kebab-case | `js-order-submit` |
| DB table / column | snake_case | `order_items`, `shipped_at` |

Names state intent, not type or mechanism: `$activeUsers`, not `$data`, `$arr`, or `$temp`. Booleans read as assertions — `$isPublished`, `$hasStock`, `$canEdit`.
