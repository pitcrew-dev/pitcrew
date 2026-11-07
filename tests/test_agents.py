"""Checks on the agent files in plugin/agents/.

The gates (review, security, QA) must never be able to change the code they
judge, so their tool lists are pinned here.
"""
import os
import re
import unittest

AGENTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugin", "agents")


def frontmatter(name):
    with open(os.path.join(AGENTS, name + ".md"), encoding="utf-8") as handle:
        text = handle.read()  # text mode turns Windows line endings into \n
    block = re.match(r"---\n(.*?)\n---\n", text, re.S).group(1)
    return dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)


class AgentFilesTest(unittest.TestCase):
    def test_each_agent_is_named_after_its_file(self):
        for file in os.listdir(AGENTS):
            name = file[:-3]
            meta = frontmatter(name)
            self.assertEqual(name, meta["name"], file)
            self.assertTrue(meta.get("description"), file)

    def test_gates_cannot_edit_code(self):
        for name in ("code-reviewer", "security-engineer"):
            tools = [t.strip() for t in frontmatter(name)["tools"].split(",")]
            self.assertNotIn("Edit", tools, name)
            self.assertNotIn("Write", tools, name)
        qa_tools = [t.strip() for t in frontmatter("qa-engineer")["tools"].split(",")]
        self.assertNotIn("Edit", qa_tools)

    def test_the_security_engineer_ends_with_a_line_the_activity_log_reads(self):
        with open(os.path.join(AGENTS, "security-engineer.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("VERDICT: PASS", text)
        self.assertIn("STATUS: DONE", text)


if __name__ == "__main__":
    unittest.main()
