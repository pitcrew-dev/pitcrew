---
type: llm
---

PASS if the reply asks plain-language questions about the restaurant's needs (for example who reserves, how many guests, what it should not do) and does not ask the owner to choose technical tools such as a styling approach, a database or an ORM. Saying that it will use a recommended setup is fine.
FAIL if it asks the owner to pick between technical tools (for example Tailwind or SCSS, PostgreSQL or MySQL), or writes code.
