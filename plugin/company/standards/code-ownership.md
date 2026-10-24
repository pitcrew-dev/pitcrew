# Standard — Code Ownership Map

**Applies to:** all implementation roles
**Purpose:** make the PM charter's rule *"two active tasks may not own the same component"* mechanically checkable.

Blade gives no tooling-enforced boundary between server and client work. This map is that boundary. Before assigning a task, the PM checks its declared in-scope paths against this table; before starting a task, the developer confirms every path they intend to touch is theirs.

> ### ⚠ The table below is the Laravel default map
>
> It is the ownership map for **Profile A and B** projects with a conventional Laravel layout. It is **not** universal.
>
> - **Plain PHP, WordPress, and other frameworks have no default map.** One is derived during the codebase survey and recorded in `.claude/project/conventions.md`, which then replaces this table for that project.
> - **A Laravel project with a non-standard layout** uses its actual structure, not this one. If logic lives in `app/Lib/`, the map says `app/Lib/`.
> - **§2 (Rules) and §3 (the seam contract) are profile-independent** — they hold for every project, whatever the paths turn out to be. Only the table changes.
>
> See [`engagement-modes.md`](engagement-modes.md) §3 and [`stack-profiles.md`](stack-profiles.md).

---

## 1. Ownership table

| Path | Owner | Notes |
|---|---|---|
| `app/Http/Controllers/**` | `backend-developer` | Thin. Delegates to services; returns a view-data array. |
| `app/Http/Requests/**` | `backend-developer` | All input validation lives here, never in controllers. |
| `app/Http/Middleware/**` | `backend-developer` | Security-sensitive changes require `security-engineer` review. |
| `app/Models/**` | `backend-developer` | |
| `app/Services/**`, `app/Actions/**` | `backend-developer` | Business logic. |
| `app/Jobs/**`, `app/Events/**`, `app/Listeners/**`, `app/Console/**` | `backend-developer` | |
| `app/View/Components/**` | `backend-developer` | The PHP class only. Its Blade template is frontend-owned. |
| `routes/**` | `backend-developer` | Route *names* are a published contract (§3). |
| `database/migrations/**`, `database/seeders/**`, `database/factories/**` | `backend-developer` | Migrations are append-only (see `coding-standards.md`). |
| `config/**` | `backend-developer` | `devops-engineer` co-owns environment-driven values. |
| `resources/views/**` | `frontend-developer` | Including component templates and layouts. |
| `resources/sass/**` | `frontend-developer` | |
| `resources/js/**` | `frontend-developer` | |
| `public/images/**`, `public/fonts/**` | `frontend-developer` | Static assets. |
| `vite.config.js`, `package.json` | `frontend-developer` | `devops-engineer` consulted on build output paths. |
| `tests/Unit/**`, `tests/Feature/**` | `backend-developer` | Written with the code under test, not after. |
| `tests/Browser/**` | `qa-engineer` | Frontend dev consulted on selectors. |
| `composer.json` | `backend-developer` | Adding a dependency requires `security-engineer` sign-off. |
| `.github/**`, `Dockerfile`, deploy config | `devops-engineer` | |
| `public/build/**`, `vendor/**`, `node_modules/**` | *nobody* | Generated. Never edited, never committed. |

Anything not listed is unowned. **Encountering an unowned path is a blocker, not a judgment call** — raise it to the PM, who assigns ownership and records the decision.

---

## 2. Rules

1. **A task may only change paths its role owns.** Needing to change another role's path means the task was sliced wrong. Stop and return it to the PM for re-decomposition — do not "just make the small change".
2. **One owner per path, always.** Where two roles appear above (`config/`, `vite.config.js`), the first named is the owner and the second is Consulted.
3. **The full-stack developer owns both columns**, but only for tasks the PM has explicitly designated full-stack. It is not a licence to cross the boundary on a task assigned to a specialist role. See `full-stack-developer.md` §3 for when that designation is allowed.
4. **Generated output is never hand-edited.** If compiled CSS or JS is wrong, the source is wrong.
5. **Serialized access.** When two tasks genuinely must touch one path, the PM sequences them and records the order in both task records. They never run concurrently.

---

## 3. The seam contract

The backend/frontend interface is **the view-data array**, and it is a contract in both directions.

```php
// backend-developer owns this file and this array
return view('users.index', [
    'users'   => $users,        // LengthAwarePaginator<User>
    'filters' => $filters,      // array{search: ?string, role: ?string}
    'canEdit' => $canEdit,      // bool
]);
```

```blade
{{-- frontend-developer owns this file and consumes exactly those keys --}}
@foreach ($users as $user)
    ...
@endforeach
```

Rules for the seam:

- **The backend declares the shape.** Every key gets a name, a type, and — where it is a collection — the element type. Declare it in the task record before the frontend task starts.
- **The frontend consumes only declared keys.** Reaching for an undeclared property, or calling a model method from a template to fetch data the controller did not pass, breaks the contract.
- **Changing a key is a breaking change.** Renaming, removing, or retyping a key requires the paired frontend task to be updated in the same sequence. The PM links them as dependencies.
- **Route names, not URLs.** Templates reference `route('users.edit', $user)`. A hardcoded `/users/1/edit` couples the frontend to a path the backend owns.
- **No business logic crosses the seam.** Formatting is frontend; deciding *what is true* is backend. `$user->isEligible()` is computed server-side and passed as a boolean, not re-derived in a template or in jQuery.
- **AJAX endpoints are seam surface too.** A jQuery request against a backend route is bound by the same contract: the backend declares the JSON shape and status codes, the frontend consumes exactly that.

### The seam in other profiles

The principle is profile-independent — *the server declares the shape, the template consumes only what was declared* — but its concrete form changes:

| Profile | The seam is |
|---|---|
| Laravel (A, B) | The view-data array passed to `view()` |
| Plain PHP (C) | The variables in scope when the template is `include`d, or the array passed to a render helper. Declare them; do not let a template reach into globals or superglobals. |
| WordPress (D) | The query vars, template-part `$args`, and the return shape of custom functions. `get_template_part( 'parts/card', null, $args )` passes `$args` — declare its keys the same way. |
| Other (E) | Whatever the framework's controller-to-view mechanism is. Identify it in the survey and record it in `conventions.md`. |

Where a project genuinely has no server/template separation — logic and markup interleaved in one file — say so in `conventions.md`. That project cannot support the backend/frontend role split at file granularity, and the PM assigns `full-stack-developer` instead of splitting tasks that would collide.
