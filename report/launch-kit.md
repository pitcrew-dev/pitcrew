# PitCrew launch kit

Everything to copy and paste, in the order to do it. Version 2.3.2, repo https://github.com/pitcrew-dev/pitcrew.

| # | Step | Who | Time |
|---|---|---|---|
| 1 | Repo "About" box and topics | You (or me, with your OK) | 2 min |
| 2 | GitHub Release v2.3.2 | You (or me, with your OK) | 3 min |
| 3 | Anthropic plugin directory | **You** (needs your claude.ai account) | 10 min |
| 4 | awesome-claude-code | **You** (they only accept forms filled by a person) | 5 min |
| 5 | awesome-claude-plugins | You or me, as a pull request | 5 min |
| 6 | Record the demo GIF | You | 15 min |
| 7 | Launch posts | **You** | a day, spread out |

Do 1 to 3 first. Post (step 7) once the release and demo exist, so visitors see a finished page.

---

## 1. Repo "About" box

On the repo page, click the gear next to **About**.

- **Description:** `An AI dev team inside Claude Code: a project manager plans, developers build, review, QA and security check, and safety hooks guard every step. PHP, Laravel, WordPress, React, Next.js.`
- **Website:** leave empty (or the Anthropic directory listing, once live)
- **Topics:** `claude-code` `claude-code-plugin` `claude` `ai-agents` `multi-agent` `developer-tools` `laravel` `wordpress` `php` `nextjs` `react` `prisma` `code-review` `project-management`

## 2. GitHub Release

Repo page → **Releases** → **Draft a new release**.

- **Tag:** `v2.3.2` (create on `main`)
- **Title:** `PitCrew 2.3.2: an AI dev team for Claude Code`
- **Notes:**

```markdown
PitCrew turns Claude Code into a small software company. You talk to a project manager in plain words; it plans the work in small pieces, hands each piece to the right agent, gets it checked, and stops for your OK after every piece, with what it cost.

**Install**

    /plugin marketplace add pitcrew-dev/pitcrew
    /plugin install pit@pitcrew

Then say `/pit:start` and describe what you want built, or point it at an existing project.

**The crew:** project manager · backend, frontend and full-stack developers · devops engineer · code reviewer · QA engineer · security engineer.

**What's in it**
- **Your code wins:** on an existing project it reads first and follows the project's own conventions and versions.
- **Independent checks:** review, QA and (for risky work) security can't edit code, so they can't cover up a problem.
- **Effort matched to risk:** a typo costs nothing extra; logins, payments, personal data, migrations and going live always get the full checks and your approval.
- **Safety hooks:** agents can't read `.env`, wipe a database, force-push or deploy without asking you.
- **Cost control:** every agent run is logged with its cost, with a budget per piece and per project.
- **Stacks:** Laravel, plain PHP, WordPress, React and Next.js, with PostgreSQL or MySQL through Prisma.

See the [changelog](CHANGELOG.md) for the full history.
```

## 3. Anthropic plugin directory

Form: https://www.claude.com/docs/plugins/submit (needs a paid claude.ai plan). **Check the icon first: it can be set only once.**

| Field | Answer |
|---|---|
| Repository | `pitcrew-dev/pitcrew` |
| Plugin path | `plugin` |
| Branch or tag | leave empty (follows `main`) |
| Reads or stores personal data? | No |
| Sends data to services other than declared connectors? | No |
| Data retention | None. Project files and the cost log stay in the user's project folder |
| Intended for people under 18? | No |
| Contact email | your email |

If validation shows a **hold** on `hooks/run`, that's expected: it's the launcher that finds Python, and the plugin README explains it.

## 4. awesome-claude-code (57k stars)

Form (web only, no pull requests, must be filled by you): https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml

| Field | Answer |
|---|---|
| Display Name | `PitCrew` |
| Category | **Agent Orchestration** (choose SDLC if it asks for a sub-category) |
| Link | `https://github.com/pitcrew-dev/pitcrew` |
| Author Name | `Muhammad Kashif` |
| Author Link | `https://github.com/kasshif01` |
| Description | `A Claude Code plugin that runs a project like a small software company: the main session acts as project manager and dispatches developer, code-review, QA, security and devops agents, with risk-based checks, per-story cost budgets, and hooks that block destructive commands. Supports Laravel, WordPress, React and Next.js.` |

Their rules: no emojis, no "you", not promotional, one resource per form. The repo meets the 14-day age rule (first commit 4 Sept 2026).

## 5. awesome-claude-plugins (Composio)

A pull request that adds one line to `README.md`, under **### Developer Productivity**:

```markdown
- [PitCrew](https://github.com/pitcrew-dev/pitcrew) - An AI dev team: a project manager plans and dispatches developer, review, QA, security and devops agents, with cost budgets and safety hooks.
```

- **PR title:** `Add PitCrew (AI dev team plugin)`
- **PR text:** `Adds PitCrew, a Claude Code plugin that runs projects like a small dev team (PM, developers, code review, QA, security, devops). Install: /plugin marketplace add pitcrew-dev/pitcrew, then /plugin install pit@pitcrew. MIT licensed, tested in CI on Windows, macOS and Linux.`

## 6. Demo GIF (the most important thing on the README)

Record about 40 seconds with ScreenToGif (Windows, free). Speed up the waiting.

1. An empty folder. Type: `/pit:start I want a booking site for my hair salon`
2. Show the 3 to 5 questions with defaults; pick the defaults.
3. Show the plan: goals, pieces, budget. Type `go`.
4. Show the agent status line: developer working, then QA.
5. End on the PM's report: "what you can now see and do", and the cost line.
6. Open the page in the browser.

Save as `docs/demo.gif` and put it under the title in the README. I can add it once you have it.

## 7. Launch posts

Post one or two a day, not all at once, and answer every comment. Costs are API-equivalent: say so if asked.

### Hacker News ("Show HN")

**Title:** `Show HN: PitCrew – a Claude Code plugin that runs your project like a small dev team`

**Text:**
> I kept getting AI code that looked right and wasn't, so I built a plugin that adds the checks a real team has. The main Claude Code session becomes a project manager: it asks a few questions, plans the work in small pieces, and dispatches developer agents. Separate review and QA agents check each piece and can't edit code, so they can't paper over a problem. Risky work (auth, payments, personal data, migrations, going live) also gets a security agent and stops for your approval.
>
> Hooks enforce a safety floor in every project: no reading .env, no migrate:fresh or prisma migrate reset, no force-push, and every deploy asks first. Every agent run is logged with its cost against a budget.
>
> On its first real project (a Laravel news site) review caught a `javascript:` URL that could be saved as a link, the hook stopped a `migrate:fresh`, and the PM caught a developer claiming a check it never ran.
>
> Works with Laravel, plain PHP, WordPress, React and Next.js. MIT. Feedback welcome, especially on what it gets wrong.
> https://github.com/pitcrew-dev/pitcrew

### Reddit, r/ClaudeAI

**Title:** `I built a Claude Code plugin that gives you a PM, developers, code review, QA and security agents`

**Text:** use the HN text, then add the install lines:
```
/plugin marketplace add pitcrew-dev/pitcrew
/plugin install pit@pitcrew
```

### Reddit, r/laravel

**Title:** `A Claude Code plugin that respects your existing Laravel codebase (and refuses migrate:fresh)`

**Text:**
> Most AI tools "modernise" your code as a side effect. PitCrew reads the project first (versions, conventions, structure) and follows them: code that matches its neighbours is correct even when it breaks the plugin's own style guide. It formats with your own Pint config, never on old unformatted files.
>
> A PM agent plans, developer agents build, review and QA agents check. Migrations, auth and payments always get the full checks plus your approval, and the hooks block migrate:fresh, db:wipe and reading .env. Piloted on a Laravel 12 news site. MIT: https://github.com/pitcrew-dev/pitcrew

### Reddit, r/nextjs

**Title:** `Claude Code plugin for Next.js + Prisma that reads your installed version's own docs`

**Text:**
> PitCrew detects your stack from package.json and the lock file, and points its agents at the docs bundled with your installed Next.js version instead of stale rules. It blocks `prisma migrate reset`, data-loss `db push` and setting Prisma's AI-consent variable, and asks before `vercel --prod`. A PM agent plans, developers build, review, QA and security check, and you approve risky work. MIT: https://github.com/pitcrew-dev/pitcrew

### X or LinkedIn

> Built PitCrew: an AI dev team inside Claude Code.
>
> 🧭 a project manager that talks in plain words
> 🛠️ developers that see their tests fail first
> 🔍 review, QA and security that can't edit code
> 🛡️ hooks that block .env reads, database wipes and unapproved deploys
> 💰 a budget for every piece of work
>
> Laravel, WordPress, React, Next.js. Free, MIT.
> https://github.com/pitcrew-dev/pitcrew
