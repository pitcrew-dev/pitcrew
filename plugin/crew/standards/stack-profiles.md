# Standard — Stack Profiles

**Applies to:** every implementation role.
**Read with:** [`engagement-modes.md`](engagement-modes.md) — the precedence ladder governs everything here. In a brownfield project, `.claude/project/conventions.md` outranks this file.

A profile says which rules apply, which are suspended, and where the code lives. The PM names the profile in every assignment record. When the profile is unclear, that is a blocker, not a guess.

| Profile | When it applies |
|---|---|
| **A — Modern Laravel** | Laravel 9+ on PHP 8.1+. The company default for greenfield. |
| **B — Legacy Laravel** | Laravel 5.x–8.x, or any Laravel on PHP < 8.1. |
| **C — Plain PHP** | No framework, or a bespoke/in-house one. |
| **D — WordPress** | Themes, child themes, plugins, or WP-based sites. |
| **E — Other framework** | Symfony, CodeIgniter, Yii, Slim, etc. Survey-driven; no company defaults apply. |

---

## The rule that spans every profile

**The language level is a hard ceiling, verified at survey time, never assumed.**

Check the PHP version from the runtime *and* from `composer.json`'s platform constraint, and take the lower. Writing syntax the target cannot parse is a deployment-breaking defect, and it is the single most common way an agent damages a legacy project.

| Feature | Requires |
|---|---|
| `match`, constructor promotion, named arguments, nullsafe `?->` | PHP 8.0 |
| Enums, `readonly` properties, `never`, pure intersection types | PHP 8.1 |
| `readonly` classes, DNF types, `null`/`false` as standalone types | PHP 8.2 |
| Typed properties, arrow functions, null coalescing assignment | PHP 7.4 |
| Return types, nullable types, `void` | PHP 7.0–7.1 |

The same applies to the framework: an API added in Laravel 9 does not exist in Laravel 6. Verify against the installed version's documentation, not against memory of the current release.

---

## Profile A — Modern Laravel

The full company standard applies as written:

- [`coding-standards.md`](coding-standards.md) §1–8 in full
- [`code-ownership.md`](code-ownership.md) path map as written
- [`testing-standards.md`](testing-standards.md) — Pest, the full mandatory coverage set
- [`git-workflow.md`](git-workflow.md) — trunk-based, Conventional Commits

**Greenfield toolchain (the scaffold task):**
- Pint
- Pest with architecture tests (`arch()->preset()->laravel()` and `->security()`)
- Larastan, starting at level 5
- `composer audit`
- the check command recorded in `conventions.md` (`testing-standards.md` §5)

Use Pest 5 when the platform allows it (it needs PHP 8.4+). **Laravel Boost**, the Laravel team's guidelines matched to your installed versions, is recommended; ask the sponsor first, since it adds a dev dependency.

Frontend default is Blade + SCSS + jQuery via Vite. Where an existing Modern Laravel project uses Livewire, Inertia, or Mix instead, that is what you use — rung 3 beats rung 4.

---

## Profile B — Legacy Laravel

The structure is familiar; the capabilities are not. Assume nothing from Profile A.

**Suspended or adapted:**

| Company default | In legacy Laravel |
|---|---|
| PHP 8.2 syntax, `strict_types`, full typing | Only what the platform version supports. Match the file's existing level of typing — do not add types to an untyped file. |
| Pint | Only if the project already has it. Otherwise match formatting by hand; do not introduce a formatter. |
| Pest | Use the project's PHPUnit setup and its existing test style. |
| Vite | Use Laravel Mix, Gulp, or whatever is there. **Never migrate the build as a side effect.** |
| `app/Actions/`, service-layer conventions | Use wherever the project actually puts logic — often `app/Http/Controllers/` or `app/Repositories/`. |
| Route model binding, invokable controllers, modern helpers | Only if the version supports them and the project already uses them. |

**Still applies:** the security floor, migrations append-only once merged, tests ship with code, no drive-by changes.

**Watch for:** a `laravel/framework` constraint that pins an old version for a reason; `composer.lock` committed with vendored patches; helpers removed or renamed between versions (`str_slug` → `Str::slug`, `array_get` → `Arr::get`); `$dates` vs `$casts`; middleware and kernel registration differing sharply across versions.

---

## Profile C — Plain PHP

No framework means no assumed structure. The survey's directory tree *is* the architecture.

**Suspended:** everything in `coding-standards.md` §2 (Laravel structure), §3's migration rules, §4 (Blade), and the `code-ownership.md` path map. All of it is framework-specific and does not apply.

**Applies:** §1 (general PHP — to the extent the platform version and local style allow), §5–6 (SCSS and jQuery, if the project uses them), §7 (**security floor, in full**), and §8 naming — adapted to the project's actual naming.

**Ownership** is derived per project during the survey and recorded in `conventions.md`. There is no default map.

**Rules specific to this profile:**

1. **Do not introduce a framework, router, ORM, or build step.** Architect and sponsor approval only. "This would be cleaner in Laravel" is not a task.
2. **Match the include and bootstrap pattern.** If pages `require` a shared header, yours does too.
3. **If there is no autoloader, do not add one** as part of a feature task.
4. Where PHP and HTML are interleaved in one file, keep the project's existing separation — do not impose a template layer.
5. **This profile carries the highest security risk.** Plain PHP projects commonly predate prepared statements, CSRF tokens, and output escaping. Your new code meets the floor absolutely; pre-existing violations are reported, not fixed in place (`engagement-modes.md` §6).
6. Database access matches the project's existing layer — `mysqli`, PDO, or a hand-rolled wrapper — **but always parameterized**, regardless of what surrounds it.

---

## Profile D — WordPress

WordPress has its own coding standards, and they **contradict PSR-12 deliberately**. Follow WordPress, not the company default.

### Never touch

- **Core** — `wp-admin/`, `wp-includes/`, root `wp-*.php`. Never edited, for any reason. Core updates overwrite it.
- **Third-party themes and plugins** — never modified in place. Extend via a child theme, hooks, or a custom plugin. A modified plugin is destroyed by its next update.

### Where work happens

| Work | Location |
|---|---|
| Presentation, templates, theme styles | `wp-content/themes/<child-theme>/` |
| Custom functionality | `wp-content/plugins/<custom-plugin>/` |
| Must-use, site-critical code | `wp-content/mu-plugins/` |
| Uploads | `wp-content/uploads/` — never committed |

**Extend through hooks.** `add_action()` and `add_filter()` are the integration mechanism; overriding a template file is a last resort and is recorded in `conventions.md`.

### WordPress conventions (these override `coding-standards.md` §1 and §8)

- **Tabs for indentation**, not spaces.
- `snake_case` for functions and variables; `Class_Name_With_Underscores` for classes; file names `class-my-thing.php`, `my-template-part.php`.
- **Yoda conditions**: `if ( 'value' === $var )`.
- Spaces inside parentheses: `if ( $condition ) {`. `elseif`, never `else if`.
- **Prefix everything global** — functions, classes, options, post types, hooks — with a project-specific slug. WordPress has one global namespace, and a collision breaks the site.

### WordPress security — mandatory, and stricter than the general floor

- **Escape on output, every time**: `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()` for permitted HTML.
- **Sanitize on input**: `sanitize_text_field()`, `sanitize_email()`, `absint()`, and the rest of the family.
- **Nonces on every form and state-changing request**: `wp_nonce_field()`, verified with `check_admin_referer()` or `wp_verify_nonce()`.
- **Capability checks, not role checks**: `current_user_can( 'edit_posts' )`.
- **`$wpdb->prepare()` for every query with a variable.** No exceptions.
- Prefer the WP API over raw SQL: `WP_Query`, `get_posts()`, `wp_insert_post()`, the options and meta APIs.

### WordPress mechanics

- **Enqueue assets** with `wp_enqueue_script()` / `wp_enqueue_style()`, versioned, with declared dependencies. Never a hardcoded `<script>` or `<link>` in a template.
- **jQuery is bundled with WordPress.** Enqueue the core handle `jquery` as a dependency; never load a second copy from a CDN. WordPress runs jQuery in `noConflict` mode — use `jQuery(function ($) { … })`, not a bare `$`.
- **i18n**: every user-facing string through `__()`, `_e()`, `esc_html__()` with the project text domain.
- **Never write to the filesystem or database directly** where a WP API exists.
- Options, transients, and post meta are the storage APIs; custom tables need architect approval.

### WordPress testing

`testing-standards.md` largely does not apply as written. WordPress projects frequently have no test suite, and adding one is its own project. Where testing exists or is introduced, it is typically WP-CLI-driven PHPUnit with the WP test scaffold. Otherwise verification is a documented manual test plan owned by `qa-engineer` — recorded in the task, not skipped.

---

## Profile E — Other framework

No company defaults apply beyond the security floor and the no-drive-by rule.

1. The survey is deeper than usual: identify the framework's own conventions and its documented project layout.
2. Follow the framework's official standards as rung 5, beneath the project's actual conventions.
3. `solution-architect` records in `decisions.md` which company standards are suspended and what replaces them.
4. Where the framework version is unsupported or the docs are gone, record that as a project risk in `decisions.md` (`## Risks`).
