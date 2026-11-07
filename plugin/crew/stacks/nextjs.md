# Stack guide: Next.js

For Next.js projects, App Router or Pages Router. React rules in `react.md` §4 apply too.

## 1. Official guidance first

- **Next.js 16.2 and later ship their docs inside the package:** `node_modules/next/dist/docs/`. Read the page for what you're building **before** writing code. Your training data may describe an older Next.js.
- `AGENTS.md` (and `CLAUDE.md`) may hold a **block managed by Next.js**. Never edit that block. Next.js rewrites it on upgrade.
- **Next.js 16.1 or older has no bundled docs.** The PM may offer the user Next's official codemod (`npx @next/codemod@canary agents-md`), which adds them. It's never run without the user's yes.
- If the project has Vercel's `react-best-practices` skill installed, follow it for performance.
- **Follow the router and patterns already in use.** Don't move Pages Router code to the App Router, or add a second data-fetching style, unless the task says so.

## 2. Who owns which files

Server and UI code mix in Next.js, so **`full-stack-developer` is the default**. Split only for a big task, or in Careful mode, using this map:

| Paths | Owner |
|---|---|
| `prisma/**`, database and data-access modules (`lib/db/**`, `lib/dal/**`, `server/**`), anything marked `import "server-only"` | backend |
| `app/api/**/route.ts`, files with `"use server"` (server actions), `middleware.ts` / `proxy.ts`, auth config | backend |
| `components/**`, page markup (`page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`), styles, `public/**` | frontend |
| `next.config.*`, `package.json`, the lock file, `tsconfig.json` | the PM decides, per task |

**The seam:** a page gets data only through a backend-owned data-access function that returns a typed object with only the fields the page needs. The frontend never queries the database or imports Prisma.

## 3. Tests

- Use the project's own tools. Typical setups: **Vitest** or **Jest** with **React Testing Library** for components, and **Playwright** for pages and flows.
- **Async Server Components can't be unit-tested in Vitest yet** (Next.js docs). Test them with Playwright, and unit-test the data-access function on its own.
- A server action or route handler gets a test for: invalid input rejected, a user without permission rejected, and the happy path.
- New project defaults: Vitest with React Testing Library, plus Playwright.

## 4. Security floor for Next.js

- **Every server action and route handler is a public endpoint.** Validate the input (with the project's schema library, for example zod), and check the user's permission **inside** it. Hiding a button is not a check.
- **Middleware (called proxy in Next.js 16) is never the only auth check.** Check again in the data-access layer or the action.
- **Only `NEXT_PUBLIC_` variables reach the browser.** A secret never gets that prefix. Server-only modules import `"server-only"`, so a client import fails the build.
- **Never pass a whole database row to a client component.** Pass only the fields it shows, because props are sent to the browser.
- No `dangerouslySetInnerHTML` with user content, unless it's sanitized with the project's sanitizer.
- Redirects take only relative paths or an allow-list, never a raw `?next=` URL.

## 5. Dangerous commands

None that are specific to Next.js. `.next/` is build output, and the hooks block writes to it. Database commands are in `prisma.md` §5.

## 6. Review and QA checklist

- [ ] Every new server action and route handler validates input and checks permission inside itself
- [ ] No secret uses a `NEXT_PUBLIC_` name, and server modules import `"server-only"`
- [ ] Client components receive only the fields they show
- [ ] It follows the router, data fetching and caching style already in the project
- [ ] Tests cover the rejection cases, and async Server Components are covered by Playwright
- [ ] The check command passes, **including `build`**, because type and server/client boundary errors only appear there
