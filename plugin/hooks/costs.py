"""Cost reader shared by the activity log and the budget check.

Reads a Claude Code transcript (.jsonl) and prices every model call in
API-equivalent dollars. One message can appear on several lines while it
streams; only its last line has the final token counts, so each message id
is counted once, from its last line.

Not a hook itself: imported by log_activity.py and check_budget.py.
"""
import json
import os
import re

# Dollars per million tokens: input, output, cache read.
# Cache writes cost 1.25x input (5-minute cache) or 2x input (1-hour cache).
# Checked against Anthropic's price list on 2026-10-24.
PRICES = {
    "claude-fable-5-1": (10.00, 50.00, 0.25),
    "claude-mythos-5-1": (10.00, 50.00, 0.25),
    "claude-fable-5": (10.00, 50.00, 1.00),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-opus-5": (5.00, 25.00, 0.50),
    "claude-opus-4-8": (5.00, 25.00, 0.50),
    "claude-opus-4-7": (5.00, 25.00, 0.50),
    "claude-opus-4-6": (5.00, 25.00, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20),
    "claude-sonnet-5": (2.00, 10.00, 0.20),
    "claude-sonnet-4-6": (3.00, 15.00, 0.30),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-haiku-4-5": (1.00, 5.00, 0.10),
}
# Task IDs as the PM writes them: PVN-E01-S02-T01, SHOP-S03, PVN-D03.
TASK_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-E\d+)?-(?:S\d+(?:-T\d+)?|D\d+)\b")

# A model not in the table is priced as the default model.
FALLBACK = PRICES["claude-opus-5-5"]


def price(model):
    model = (model or "").split("[")[0]  # "claude-opus-5-5[1m]" -> "claude-opus-5-5"
    for name in sorted(PRICES, key=len, reverse=True):
        if model == name or model.startswith(name + "-"):
            return PRICES[name]
    return FALLBACK


def message_cost(model, usage):
    p_in, p_out, p_read = price(model)
    split = usage.get("cache_creation") or {}
    if split:
        write_5m = split.get("ephemeral_5m_input_tokens", 0) or 0
        write_1h = split.get("ephemeral_1h_input_tokens", 0) or 0
    else:
        write_5m, write_1h = usage.get("cache_creation_input_tokens", 0) or 0, 0
    dollars = ((usage.get("input_tokens", 0) or 0) * p_in
               + (usage.get("output_tokens", 0) or 0) * p_out
               + (usage.get("cache_read_input_tokens", 0) or 0) * p_read
               + write_5m * p_in * 1.25
               + write_1h * p_in * 2.0)
    return dollars / 1_000_000


def transcript_cost(path, since="", main=False):
    """Dollars for the messages in `path` newer than the timestamp `since`.

    Returns (dollars, newest timestamp seen), so the caller can pass that
    back next time and never count a message twice. With main=True,
    side-conversation lines are skipped and only the main session is priced.
    """
    last = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") != "assistant" or (main and entry.get("isSidechain")):
                continue
            message = entry.get("message") or {}
            if message.get("id") and message.get("usage"):
                last[message["id"]] = (entry.get("timestamp") or "", message)
    dollars, newest = 0.0, since
    for stamp, message in last.values():
        if stamp > since:
            dollars += message_cost(message.get("model"), message["usage"])
            newest = max(newest, stamp)
    return dollars, newest


def story_of(task):
    """PVN-E01-S02-T01 -> PVN-E01-S02. Defects (PVN-D03) are their own story."""
    return re.sub(r"-T\d+$", "", task)


def logged(log_path, since=""):
    """Costs already in activity.md: ({story: dollars}, all stories' dollars).

    Lines without a task count toward the project total only. With `since`
    ("2026-10-01"), only lines from that date on are counted.
    """
    stories, total = {}, 0.0
    try:
        with open(log_path, encoding="utf-8") as handle:
            for line in handle:
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(cells) != 7 or cells[1] == "Task" or cells[0] < since:
                    continue
                try:
                    dollars = float(cells[4]) + float(cells[5])
                except ValueError:
                    continue
                total += dollars
                if cells[1] != "-":
                    story = story_of(cells[1])
                    stories[story] = stories.get(story, 0.0) + dollars
    except OSError:
        pass
    return stories, total


# Budgets: .claude/project/budget.md, else the plugin settings, else these.
DEFAULT_STORY = 25.0
SETTING = re.compile(r"^\W*(story|project) budget\W*:\W*(\$?\s*[\d.]+|none)", re.I | re.M)
AMOUNT = re.compile(r"^\$?\s*(\d+(?:\.\d+)?)$")


def find_project(start):
    current = os.path.abspath(start)
    while True:
        folder = os.path.join(current, ".claude", "project")
        if os.path.isdir(folder):
            return folder
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def option(name):
    try:
        value = float(os.environ.get("CLAUDE_PLUGIN_OPTION_" + name, ""))
    except ValueError:
        return None
    return value if value > 0 else None


MODE = re.compile(r"^\W*mode\W*:\W*(careful|quick)\b", re.I | re.M)


def mode(folder):
    """(mode name, where it came from): budget.md, else the plugin setting, else Quick."""
    if folder:
        try:
            with open(os.path.join(folder, "budget.md"), encoding="utf-8") as handle:
                found = MODE.findall(handle.read())
        except OSError:
            found = []
        if found:
            return found[-1].capitalize(), "from .claude/project/budget.md"
    if os.environ.get("CLAUDE_PLUGIN_OPTION_CAREFUL_MODE", "").strip().lower() in ("true", "1", "yes", "on"):
        return "Careful", "from the plugin setting"
    return "Quick", "the default"


def budgets(folder):
    """(story budget, project budget or None, {story or 'project': approved top-ups})."""
    story, project, topups = option("STORY_BUDGET") or DEFAULT_STORY, option("PROJECT_BUDGET"), {}
    try:
        with open(os.path.join(folder, "budget.md"), encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return story, project, topups
    for kind, value in SETTING.findall(text):
        number = None if value.lower() == "none" else float(value.lstrip("$ "))
        if kind.lower() == "story" and number:
            story = number
        elif kind.lower() == "project":
            project = number
    for line in text.splitlines():
        cells = [cell.strip().strip("*`") for cell in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|") or len(cells) < 3:
            continue
        who = next((c for c in cells if TASK_ID.fullmatch(c) or c.lower() == "project"), None)
        amount = next((float(AMOUNT.match(c).group(1)) for c in cells if AMOUNT.match(c)), None)
        if who and amount:
            key = "project" if who.lower() == "project" else story_of(who)
            topups[key] = topups.get(key, 0.0) + amount
    return story, project, topups
