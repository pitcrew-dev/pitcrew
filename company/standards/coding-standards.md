# Standard — Coding Standards

**Default profile:** PHP 8.2+ / Laravel 11+ / MySQL 8 · Blade + SCSS + jQuery, bundled by Vite — i.e. **Profile A** in [`stack-profiles.md`](stack-profiles.md).
**Applies to:** `backend-developer`, `frontend-developer`, `full-stack-developer`
**Enforced by:** `code-reviewer` at the review gate. A change violating a MUST is rejected, not negotiated.

> ### ⚠ This file is rung 4
>
> [`engagement-modes.md`](engagement-modes.md) governs. This file applies **in full only to greenfield projects on Profile A**.
>
> In an existing project, the project's own config and observed conventions (`projects/<name>/conventions.md`) outrank everything below, and `stack-profiles.md` says which of these sections are suspended entirely — §2, §3, and §4 do not apply outside Laravel at all.
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

Non-negotiable, and checked at review regardless of what the task asked for:

- No secrets in code, config, or commits — `.env` only, and `.env` is never committed.
- Every write route authorizes; never trust a hidden form field or a client-supplied ID to establish permission.
- Mass assignment is guarded: `$fillable` declared explicitly, never `$guarded = []` on a model reachable from user input.
- Uploads validate MIME type and size, are stored outside the webroot, and are served through a route that authorizes.
- Redirects to user-supplied URLs are validated against an allowlist.
- Any change touching authentication, authorization, payment, PII, or file upload is routed to `security-engineer` before merge.

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
