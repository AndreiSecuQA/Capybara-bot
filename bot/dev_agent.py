"""
Dev Agent — lets the bot owner make code changes via Telegram.
Usage: /dev <describe the change you want>
Only works for ADMIN_TELEGRAM_ID.
"""
import os
import json
import logging
import base64
import httpx
import anthropic

from config import ADMIN_TELEGRAM_ID, ANTHROPIC_API_KEY, GITHUB_TOKEN, GITHUB_REPO

logger = logging.getLogger(__name__)

# GitHub API base
GH_API = "https://api.github.com"
GH_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
OWNER, REPO = GITHUB_REPO.split("/")
BRANCH = "main"

# Claude model for dev tasks
DEV_MODEL = "claude-sonnet-4-6"

# ── GitHub helper functions ──────────────────────────────────────────────────

def gh_list_files(path: str = "") -> list[dict]:
    """List files/dirs at path in the repo."""
    url = f"{GH_API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = httpx.get(url, headers=GH_HEADERS, params={"ref": BRANCH})
    if r.status_code == 200:
        items = r.json()
        return [{"name": i["name"], "path": i["path"], "type": i["type"]} for i in items]
    return [{"error": f"HTTP {r.status_code}: {r.text[:200]}"}]

def gh_read_file(path: str) -> str:
    """Read a file's content from the repo."""
    url = f"{GH_API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = httpx.get(url, headers=GH_HEADERS, params={"ref": BRANCH})
    if r.status_code == 200:
        data = r.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8")
        return data.get("content", "")
    return f"ERROR: HTTP {r.status_code}: {r.text[:300]}"

def gh_write_file(path: str, content: str, commit_message: str) -> dict:
    """Create or update a file in the repo."""
    url = f"{GH_API}/repos/{OWNER}/{REPO}/contents/{path}"
    # Get current SHA if file exists (needed for update)
    sha = None
    existing = httpx.get(url, headers=GH_HEADERS, params={"ref": BRANCH})
    if existing.status_code == 200:
        sha = existing.json().get("sha")

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    r = httpx.put(url, headers=GH_HEADERS, json=payload)
    if r.status_code in (200, 201):
        commit = r.json().get("commit", {})
        return {"success": True, "sha": commit.get("sha", "")[:7], "path": path}
    return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}

def gh_search_code(query: str) -> list[dict]:
    """Search for a string pattern across repo files."""
    url = f"{GH_API}/search/code"
    r = httpx.get(url, headers=GH_HEADERS, params={"q": f"{query} repo:{OWNER}/{REPO}"})
    if r.status_code == 200:
        items = r.json().get("items", [])
        return [{"path": i["path"], "url": i["html_url"]} for i in items[:10]]
    return [{"error": f"HTTP {r.status_code}"}]

# ── Tool definitions for Claude ───────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_files",
        "description": "List files and directories in the GitHub repo at a given path. Use '' for root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (e.g. '' for root, 'bot' for bot/ folder, 'bot/handlers' for handlers)"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the full content of a file from the GitHub repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root (e.g. 'bot/food.py', 'config.py')"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Create or update a file in the GitHub repo. This immediately commits and pushes. Railway will auto-redeploy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path (e.g. 'bot/food.py')"},
                "content": {"type": "string", "description": "Complete new file content"},
                "commit_message": {"type": "string", "description": "Git commit message describing the change"}
            },
            "required": ["path", "content", "commit_message"]
        }
    },
    {
        "name": "search_code",
        "description": "Search for a pattern/string across all files in the repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term or pattern"}
            },
            "required": ["query"]
        }
    }
]

SYSTEM_PROMPT = """You are an expert Python developer and the autonomous coding agent for the Capybara Bot — a Telegram health tracking bot.

The bot is deployed on Railway and auto-redeploys on every GitHub push. The repo is AndreiSecuQA/Capybara-bot.

Tech stack: Python 3.11, python-telegram-bot 20.7, google-genai (Gemini), aiosqlite, APScheduler.

When the owner gives you a coding task:
1. Use list_files and read_file to understand the current code thoroughly
2. Plan the minimal, focused changes needed
3. Use write_file to apply changes (you can write multiple files)
4. Always write complete file content — never partial snippets
5. After all changes, summarize what you did concisely

Be careful: the bot is live. Make targeted, correct changes. Preserve all existing functionality."""


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if tool_name == "list_files":
            result = gh_list_files(tool_input.get("path", ""))
        elif tool_name == "read_file":
            result = gh_read_file(tool_input["path"])
        elif tool_name == "write_file":
            result = gh_write_file(tool_input["path"], tool_input["content"], tool_input["commit_message"])
        elif tool_name == "search_code":
            result = gh_search_code(tool_input["query"])
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        return json.dumps({"error": str(e)})


async def run_dev_agent(task: str, progress_callback=None) -> str:
    """
    Run Claude as a coding agent to complete the task.
    progress_callback(msg) is called with status updates.
    Returns final summary string.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = [{"role": "user", "content": task}]
    files_changed = []
    iterations = 0
    max_iterations = 20

    while iterations < max_iterations:
        iterations += 1

        response = client.messages.create(
            model=DEV_MODEL,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Add assistant message to history
        messages.append({"role": "assistant", "content": response.content})

        # Check stop reason
        if response.stop_reason == "end_turn":
            # Extract final text
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text + (f"\n\n📁 Files changed: {', '.join(files_changed)}" if files_changed else "")
            return "✅ Task completed." + (f"\n📁 Files changed: {', '.join(files_changed)}" if files_changed else "")

        if response.stop_reason != "tool_use":
            break

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input

            # Notify progress
            if progress_callback:
                if tool_name == "read_file":
                    await progress_callback(f"📖 Reading `{tool_input.get('path')}`...")
                elif tool_name == "write_file":
                    path = tool_input.get('path')
                    await progress_callback(f"✏️ Writing `{path}`...")
                    files_changed.append(path)
                elif tool_name == "list_files":
                    await progress_callback(f"📂 Listing `{tool_input.get('path', '/')}`...")
                elif tool_name == "search_code":
                    await progress_callback(f"🔍 Searching for `{tool_input.get('query')}`...")

            result = run_tool(tool_name, tool_input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    return "⚠️ Agent reached iteration limit. Partial changes may have been applied."


# ── Telegram handler ──────────────────────────────────────────────────────────

async def dev_command(update, context):
    """Handle /dev command — only for admin."""
    user_id = update.effective_user.id

    if not ADMIN_TELEGRAM_ID or user_id != ADMIN_TELEGRAM_ID:
        return  # silently ignore non-admin

    task = " ".join(context.args) if context.args else ""
    if not task:
        await update.message.reply_text(
            "🛠️ *Dev Agent*\n\nUsage: `/dev <describe the change>`\n\nExample:\n`/dev add a /weight command that lets users update their current weight`",
            parse_mode="Markdown"
        )
        return

    status_msg = await update.message.reply_text("🤖 Claude is working on it...")

    async def progress_callback(msg: str):
        try:
            await status_msg.edit_text(f"🤖 {msg}")
        except Exception:
            pass

    try:
        result = await run_dev_agent(task, progress_callback)
        await status_msg.edit_text(
            f"✅ *Done!*\n\n{result}\n\n🚀 Railway is redeploying automatically.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Dev agent error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)[:300]}")
