# Standard — Design Approach

**Applies to:** every implementation role, whenever a task needs new logic.
**Read with:** [`engagement-modes.md`](engagement-modes.md). In an existing project, the project's own patterns outrank everything here.
**Checked by:** `code-reviewer`, as part of conformance.

The most common failures of generated code are not syntax errors. They are **code that didn't need to exist** and **abstractions built for a future that never comes**. This standard is the antidote. Most tasks never get past §1.

---

## 1. The ladder — before writing any code

Go down in order and **stop at the first "yes"**.

| # | Ask | If yes |
|---|---|---|
| 1 | Does this need to exist at all? | Don't build it. Say so in your report. |
| 2 | Does this codebase already do it? | Reuse it. Grep before you write. |
| 3 | Does the language's standard library do it? | Use it. |
| 4 | Does the framework or platform do it? | Use it. Laravel: validation rules, policies and gates, `Str`, `Arr`, `Collection`, `Pipeline`, `Http`, `Cache`, `RateLimiter`, casts, enums, notifications. WordPress: the core API. Browser: native HTML (`<details>`, `<dialog>`, form validation) and CSS before JavaScript. |
| 5 | Does an **already installed** dependency do it? | Use it. |
| 6 | Is it one line? | Write one line. |
| 7 | Only now | Write the minimum that works, shaped by §2. |

A **new** dependency is never a rung. It needs the checks in `coding-standards.md` §7.1 and approval (`engagement-modes.md` §4).

## 2. Choosing a shape — only at rung 7

| The problem you actually have | Use | Laravel form | Instead of |
|---|---|---|---|
| Several interchangeable ways to do one thing (payment gateways, shipping rates, export formats) | **Strategy** | Interface + container binding, or a `Manager` class | A growing `if`/`switch` on a type |
| Creating objects that vary by type or config | **Factory** | Named static constructor, or `Manager::driver()` | `new` scattered across callers |
| One business operation used from several places (controller, job, command) | **Action** | One class, one public `handle()` | Logic copied between controllers |
| Multi-step processing where steps come and go | **Pipeline** | `Pipeline::send($x)->through([...])` | One 200-line method |
| "When X happens, also do Y and Z" | **Events** | Event + (queued) listeners | Side effects packed into the controller |
| Talking to an external service | **Adapter** | Your own small interface, one class per provider; `Http::fake()` in tests | The vendor SDK called from everywhere |
| A complex or reused query | **Scope / query object** | `scopeActive()`, or a dedicated query class | The same query chain in several places |
| A value with rules (money, email, a status) | **Value object / enum** | Backed enum (PHP 8.1+), small readonly class | Raw strings, and floats for money |

Check the PHP version ceiling before using an enum or `readonly` (`stack-profiles.md`).

## 3. Rules

- **Rule of two.** No interface, base class or pattern until two real implementations exist **today**. One implementation is a plain class.
- **The project's pattern wins.** If it uses repositories, you use repositories. If it puts logic in `app/Lib/`, yours goes there.
- **No speculative flexibility.** No config options, flags, hooks or extension points the task didn't ask for.
- **Readable in one sitting.** A reader should follow a function without opening four files.
- **Errors fail closed.** See `coding-standards.md` §7.5.

## 4. What review checks

- A lower rung was skipped, rebuilding something the codebase, the standard library or the framework already has → **should-fix**.
- An abstraction with a single use → **should-fix**.
- A new dependency, or a new architectural layer, without approval → **blocking**.
