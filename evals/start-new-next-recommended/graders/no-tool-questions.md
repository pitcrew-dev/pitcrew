---
type: llm
---

PASS if the reply asks plain-language questions about the restaurant's needs (for example who reserves, how many guests, what it should not do) and does not ask the owner to choose between technical tools. Telling the owner which tools it has already picked (for example "I'll use Next.js with PostgreSQL, the recommended setup") is fine and expected, and so is inviting them to change it.
FAIL if it asks the owner to pick between technical options (for example "Tailwind or SCSS?", "PostgreSQL or MySQL?"), or writes code.
