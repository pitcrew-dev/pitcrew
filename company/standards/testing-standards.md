# Standard — Testing Standards

**Tooling:** Pest (PHPUnit underneath) · Laravel Dusk for browser tests · MySQL test schema, never SQLite-in-memory where the app uses MySQL-specific SQL
**Applies to:** `backend-developer`, `frontend-developer`, `full-stack-developer`, `qa-engineer`

The developer writes tests **with** the code, in the same commit and the same PR. "QA will test it later" is not a testing strategy — QA verifies behavior against acceptance criteria; it does not backfill the unit and feature tests the developer owed.

> ### ⚠ Brownfield adaptation
>
> This file describes **Profile A**. Existing projects frequently have a different framework, a different test style, or no tests at all. See [`engagement-modes.md`](engagement-modes.md) and [`stack-profiles.md`](stack-profiles.md), then §7 below.
>
> Use the project's test framework and its existing test style — PHPUnit rather than Pest, its own base classes, its own naming. Never introduce a test framework as a side effect of a feature task.

---

## 1. The test pyramid, as applied here

| Layer | Owner | What it covers | Speed |
|---|---|---|---|
| **Unit** (`tests/Unit/`) | developer | One class in isolation — services, actions, value objects, calculations. No DB, no HTTP, no queue. | ms |
| **Feature** (`tests/Feature/`) | developer | One HTTP route end to end — request → validation → authorization → persistence → response. Hits the DB. | Bulk of the suite. |
| **Browser** (`tests/Browser/`) | `qa-engineer` | Real interaction: jQuery behavior, AJAX flows, form submission in a browser. | Slow — reserve for flows that genuinely need a DOM. |

Write the cheapest test that can catch the defect. A calculation bug caught by a unit test does not also need a browser test.

## 2. Mandatory coverage

A task is not complete unless tests exist for:

- **The happy path** of every acceptance criterion in the task record.
- **Every validation rule** — one assertion per rule, checking the specific field error, not merely that the request failed.
- **Every authorization branch** — the permitted actor succeeds, the forbidden actor gets 403, the guest gets redirected. A write route without an authorization test is an incomplete task.
- **Every failure mode named in the task** — not found, conflict, external service down, empty state.
- **Boundaries** — zero, one, many; empty string; maximum length; the first and last valid value.
- **Every defect fixed.** A bug fix ships with a regression test that fails before the fix and passes after. No test, no fix.

Coverage percentage is not a target and is not reported as an achievement. Coverage of the criteria above is the bar.

## 3. Writing tests

- **Name the behavior, not the method.** `it('rejects an order when stock is insufficient')`, not `testStore()`. The name should read as a sentence describing a rule.
- **Arrange–Act–Assert**, visually separated. One behavior per test; a test asserting three unrelated things is three tests.
- **Build state with factories**, never with hand-written inserts or a shared seeded fixture. Each test creates exactly the state it needs.
- **Tests are independent and order-free.** No test may depend on another having run. Use `RefreshDatabase`.
- **Assert on outcomes, not implementation.** Check the response, the database row, the dispatched job — not that a private method was called.
- **Fake the boundaries**: `Mail::fake()`, `Queue::fake()`, `Event::fake()`, `Http::fake()`, `Storage::fake()`. A test suite that sends real mail or makes real HTTP calls is broken, not thorough.
- **No sleeps and no time dependence.** Freeze time with `travelTo()`; never assert against `now()` twice and hope.
- **No conditionals in tests.** An `if` in a test means it is testing two things or asserting nothing.

```php
it('forbids a viewer from deleting an order', function () {
    $viewer = User::factory()->viewer()->create();
    $order  = Order::factory()->create();

    $response = $this->actingAs($viewer)->delete(route('orders.destroy', $order));

    $response->assertForbidden();
    $this->assertDatabaseHas('orders', ['id' => $order->id]);
});
```

## 4. Frontend testing

With Blade + jQuery there is no component test layer, which changes where the risk sits:

- **Rendering is covered by feature tests.** Assert on the rendered response: `assertSee()`, `assertSeeText()`, `assertViewHas('users')`, `assertDontSee()` for the negative permission case.
- **The seam is asserted explicitly.** A feature test must assert `assertViewHas()` for every key in the view-data contract (`code-ownership.md` §3). This is what catches a backend rename before the frontend breaks in production.
- **jQuery behavior that carries real risk gets a Dusk test** — AJAX submission, dynamic insertion, dependent selects, anything with a loading or error state. Cosmetic behavior does not.
- **Dusk selectors use `@dusk` attributes**, never CSS classes. Styling changes must not break tests.
- **Every AJAX flow is tested on both branches** — success and failure. An untested error path is where the double-submit and the swallowed 500 live.

## 5. Running the suite

```bash
./vendor/bin/pest                          # full suite
./vendor/bin/pest --filter='rejects an order'   # one test by name
./vendor/bin/pest tests/Feature/OrderTest.php   # one file
./vendor/bin/pest --parallel               # fast local run
./vendor/bin/pest --coverage               # coverage report
php artisan dusk                           # browser suite
php artisan dusk --filter=OrderCheckoutTest
```

Before pushing: `./vendor/bin/pint` → `./vendor/bin/pest` → `npm run build`. All three clean, or the branch is not ready.

## 6. Rules

1. **A failing test is a stop condition.** Never commit on red, never mark a task complete on red, and never skip a test to get a build through. A test that must be disabled requires a defect record and PM sign-off.
2. **Never weaken a test to make it pass.** Loosening an assertion, deleting a case, or adding a conditional to dodge a failure is falsifying the gate. Fix the code or raise the defect.
3. **Flaky tests are defects with owners**, not background noise. Quarantine costs a ticket and a date.
4. **Tests are production code** — the standards in `coding-standards.md` apply to them: named clearly, no duplication, no dead code.
5. **The developer runs the full suite before handing off**, not just their own new tests. Breaking someone else's test is your task's defect.

---

## 7. Testing an existing codebase

### 7.1 Establish the baseline first

Part of the codebase survey (`engagement-modes.md` §3): **run the suite before anyone changes anything** and record the result in `conventions.md` — which tests pass, which fail, which are skipped, and how long it takes.

That baseline redefines §6 rule 1. The stop condition is not "the suite is green"; it is **"the suite is no worse than the baseline."** A test that was already failing on arrival is a pre-existing defect to report to the PM, not something your task inherited and must fix. A test that passed at baseline and fails now is your defect, without argument.

### 7.2 When there is no suite at all

Common in Profile C and D projects, and it does not excuse shipping unverified work.

1. **Do not build a test suite as part of a feature task.** Standing up a framework, bootstrap, and fixtures is its own project — raise it as tech debt and let the PM size it.
2. **Test your own change anyway** where anything can be tested in isolation — a pure function, a calculation, a new class with no framework coupling. A single test file added alongside your change is fine; a whole harness is not.
3. **Where automated testing is genuinely unavailable, verification becomes a written manual test plan** in the task record: exact steps, exact expected results, covering each acceptance criterion, each failure branch, and the states the change can produce. `qa-engineer` executes it and records evidence.
4. **A task is never accepted on "I checked and it looks fine."** Unverifiable is not the same as unverified — say which one it is.

### 7.3 Changing untested legacy code

**Characterization tests come first.** Before modifying behavior that has no test, write tests that capture what the code does *today* — including behavior that looks wrong. Then change it. In legacy code, today's apparent bug is sometimes a depended-upon feature, and the characterization test is what tells you which.

If characterization is impossible within the task's size, that is a blocker: return it to the PM to be re-sliced, with the risk stated.

### 7.4 Per-profile commands

The commands in §5 are Profile A. Record the project's actual commands in `conventions.md` — how to run the full suite, a single file, and a single test by name.

| Profile | Typical |
|---|---|
| A — Modern Laravel | `./vendor/bin/pest`, `php artisan dusk` |
| B — Legacy Laravel | `./vendor/bin/phpunit`, `php artisan test` (5.7+ only) |
| C — Plain PHP | `./vendor/bin/phpunit` if present; often nothing — see §7.2 |
| D — WordPress | WP-CLI scaffolded PHPUnit if present; usually a manual plan |
| E — Other framework | The framework's own runner |
