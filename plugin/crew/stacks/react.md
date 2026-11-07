# Stack guide: React

For React apps without Next.js, usually built with Vite. For Next.js, read `nextjs.md`, which uses §4 of this guide.

## 1. Official guidance first

- **react.dev** is the reference for the installed React version (check it in the lock file). Older patterns, such as class components or `useEffect` for data that could be derived, are not the default.
- If the project uses the **React Compiler**, don't add `useMemo`, `useCallback` or `memo` by hand unless the project already does.
- If the project has Vercel's `react-best-practices` skill installed, follow it for performance.
- **Follow the project's own choices** for routing, state, data fetching and styling. Never add a second library for the same job.

## 2. Who owns which files

A React app is all frontend, so **`frontend-developer`** owns `src/**`, components, styles and tests. Calls to the server go **only through the project's existing API layer** (for example `src/api/**` or `src/lib/api.ts`). When that API is in this repo, its code is backend-owned, and the shape of each request and response is the seam (`standards/code-ownership.md` §3).

## 3. Tests

- Use the project's own tools: usually **Vitest** or **Jest** with **React Testing Library**, plus **Playwright** for flows.
- Test what the user sees and does: find elements by role and label, not by class names or internal state.
- Every new component gets a test for its main behavior, its empty state and its error state.

## 4. React rules (also used by Next.js)

- Follow the **rules of hooks**. If the project has `eslint-plugin-react-hooks`, its warnings are errors for new code.
- Derive values while rendering. Don't copy props into state, and don't use an effect to sync something that could be computed.
- Lists need stable `key`s, from the data, never the array index when items can move.
- Accessibility is required: real `<button>` and `<label>` elements, visible focus, and the whole flow usable with a keyboard.

## 5. Security floor for React

- **Only `VITE_` variables (or the bundler's public prefix) reach the browser.** Everything in the bundle is public, so no secrets.
- No `dangerouslySetInnerHTML` with user content, unless it's sanitized with the project's sanitizer.
- Never build URLs for `href` or `src` from user input without checking the scheme, because `javascript:` URLs run code.
- Login tokens are stored the way the project already stores them. Don't change that inside a feature task: raise it with the PM as a finding.

## 6. Review and QA checklist

- [ ] No secret is in client code or uses a public variable prefix
- [ ] No unsanitized `dangerouslySetInnerHTML`, and no unchecked user URLs in `href` or `src`
- [ ] Follows the rules of hooks, and adds no new library that duplicates an existing one
- [ ] Tests find elements by role or label, and cover the empty and error states
- [ ] Usable with a keyboard, with visible focus and labelled inputs
- [ ] The check command passes, including the type check and the build
