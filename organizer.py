import os
import sys
import json
import shutil
import platform
import subprocess


def _get_desktop_path() -> str:
    """Detect the desktop path across Windows, macOS, and Linux."""
    system = platform.system()

    if system == "Windows":
        # Use the Windows Shell to get the actual Desktop path
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            desktop, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            return desktop
        except Exception:
            pass

    elif system == "Darwin":
        # macOS — always ~/Desktop
        return os.path.join(os.path.expanduser("~"), "Desktop")

    else:
        # Linux — read XDG user-dirs config for the real desktop folder
        try:
            result = subprocess.run(
                ["xdg-user-dir", "DESKTOP"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass

    # Fallback for all platforms
    return os.path.join(os.path.expanduser("~"), "Desktop")


DESKTOP_PATH = _get_desktop_path()

# Resolve base dir — works for both script and PyInstaller EXE
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(__file__)

HISTORY_PATH = os.path.join(_BASE_DIR, "move_history.json")
CONFIG_PATH = os.path.join(_BASE_DIR, "config.json")

# ── Provider / model options ─────────────────────────────────────────────────
PROVIDERS = {
    "claude": {
        "label": "Claude (Anthropic)",
        "models": ["claude-sonnet-4-5-20250929"],
    },
    "openai": {
        "label": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini"],
    },
    "gemini": {
        "label": "Gemini (Google)",
        "models": ["gemini-2.0-flash", "gemini-2.5-pro"],
    },
}

# ── Config ───────────────────────────────────────────────────────────────────

def load_config() -> dict | None:
    """Load config from disk. Returns None if not set up yet."""
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(provider: str, api_key: str, model: str) -> None:
    """Save provider config to disk."""
    with open(CONFIG_PATH, "w") as f:
        json.dump({"provider": provider, "api_key": api_key, "model": model}, f, indent=2)


# ── Language config ──────────────────────────────────────────────────────────
LANG_INSTRUCTION = {
    "en": "All folder names MUST be in English.",
    "he": "All folder names MUST be in Hebrew (עברית).",
}

# ── Prompt templates (use {lang_rule} placeholder) ───────────────────────────
PROMPT_FILES_AUTO = """You are a file organizer. You receive a list of filenames from a user's desktop.
Categorize each file into a logical folder based on its name and extension.
- If your confidence that a file belongs to an existing/proposed folder is below 85%,
  create a new, clearly-named folder for it.
- Use short, clear folder names.
- Do not create a folder for a single file unless it clearly belongs to its own category.
- Ignore system files like desktop.ini, thumbs.db, or .DS_Store.
- Every file must appear exactly once.
- {lang_rule}

Return ONLY valid JSON with this structure:
{{
  "FolderName": ["file1.ext", "file2.ext"],
  "AnotherFolder": ["file3.ext"]
}}
"""

PROMPT_FILES_USER_DEFINED = """You are a file organizer. You receive a list of filenames and a list of target folder names.
Move every file into the folder from the provided list that has the highest contextual match.
- You may NOT create folders outside the provided list.
- Every file MUST be placed into exactly one of the given folders.
- Ignore system files like desktop.ini, thumbs.db, or .DS_Store.

Return ONLY valid JSON with this structure:
{{
  "FolderName": ["file1.ext", "file2.ext"],
  "AnotherFolder": ["file3.ext"]
}}
"""

PROMPT_FOLDERS = """You are a desktop folder organizer. You receive a list of existing folder names from a user's desktop.
Identify folders that are contextually related and propose restructuring:

(a) MERGE: Group related folders under a NEW parent folder.
(b) NEST: Move one existing folder inside another existing folder when one
    is clearly a subset of the other.

- Folders with no clear relationship should be left alone.
- Never propose moving a folder into itself or creating circular nesting.
- {lang_rule}

Return ONLY valid JSON with this structure:
{{
  "merge": [
    {{
      "new_parent": "Parent Folder Name",
      "children": ["ExistingFolder1", "ExistingFolder2"]
    }}
  ],
  "nest": [
    {{
      "child": "FolderToMove",
      "into": "ExistingDestinationFolder"
    }}
  ]
}}
If no relationships are found, return: {{"merge": [], "nest": []}}
"""


def scan_desktop() -> tuple[list[str], list[str]]:
    """Return separate lists of files and folders on the desktop."""
    files = []
    folders = []
    for item in os.listdir(DESKTOP_PATH):
        full_path = os.path.join(DESKTOP_PATH, item)
        if os.path.isfile(full_path):
            files.append(item)
        elif os.path.isdir(full_path):
            folders.append(item)
    return files, folders


def get_prompt(template: str, lang: str) -> str:
    """Fill in the language rule in a prompt template."""
    lang_rule = LANG_INSTRUCTION.get(lang, LANG_INSTRUCTION["en"])
    return template.format(lang_rule=lang_rule)


# ── Multi-provider AI call ───────────────────────────────────────────────────

def _parse_json_response(response_text: str) -> dict:
    """Extract JSON from AI response, handling markdown fences."""
    if "```" in response_text:
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    return json.loads(response_text.strip())


def _call_claude(system_prompt: str, user_message: str, config: dict) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=config["api_key"])
    message = client.messages.create(
        model=config["model"],
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def _call_openai(system_prompt: str, user_message: str, config: dict) -> str:
    import openai
    client = openai.OpenAI(api_key=config["api_key"])
    response = client.chat.completions.create(
        model=config["model"],
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _call_gemini(system_prompt: str, user_message: str, config: dict) -> str:
    from google import genai
    client = genai.Client(api_key=config["api_key"])
    response = client.models.generate_content(
        model=config["model"],
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=2048,
        ),
    )
    return response.text


# ── Demo mode (proxy server) ─────────────────────────────────────────────────
DEMO_SERVER_URL = os.environ.get(
    "DEMO_SERVER_URL", "https://desktop-organizer-api.onrender.com"
)


def _call_demo(system_prompt: str, user_message: str) -> dict:
    """Call the proxy server for demo mode (no API key needed)."""
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "system_prompt": system_prompt,
        "user_message": user_message,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{DEMO_SERVER_URL}/api/organize",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("error", body)
        except Exception:
            msg = body
        raise RuntimeError(msg)


def call_ai(system_prompt: str, user_message: str, config: dict | None = None) -> dict:
    """Send a prompt to the configured AI provider and parse the JSON response."""
    if config is None:
        config = load_config()

    # Demo mode — no config needed, use proxy server
    if config is None or config.get("provider") == "demo":
        return _call_demo(system_prompt, user_message)

    provider = config["provider"]
    if provider == "claude":
        text = _call_claude(system_prompt, user_message, config)
    elif provider == "openai":
        text = _call_openai(system_prompt, user_message, config)
    elif provider == "gemini":
        text = _call_gemini(system_prompt, user_message, config)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return _parse_json_response(text)


# ── Plan functions ───────────────────────────────────────────────────────────

def plan_files_auto(files: list[str], lang: str, config: dict | None = None) -> dict:
    """Auto-categorize files into AI-chosen folders."""
    prompt = get_prompt(PROMPT_FILES_AUTO, lang)
    user_msg = f"Categorize these desktop files into folders:\n{json.dumps(files, indent=2)}"
    return call_ai(prompt, user_msg, config)


def plan_files_user_defined(files: list[str], target_folders: list[str], config: dict | None = None) -> dict:
    """Categorize files into user-provided folders only."""
    user_msg = (
        f"Files:\n{json.dumps(files, indent=2)}\n\n"
        f"Target folders (use ONLY these): {json.dumps(target_folders)}"
    )
    return call_ai(PROMPT_FILES_USER_DEFINED, user_msg, config)


def plan_folders(folders: list[str], lang: str, config: dict | None = None) -> dict:
    """Analyze existing folders and propose merge/nest operations."""
    prompt = get_prompt(PROMPT_FOLDERS, lang)
    user_msg = f"Analyze these desktop folders:\n{json.dumps(folders, indent=2)}"
    result = call_ai(prompt, user_msg, config)
    result.setdefault("merge", [])
    result.setdefault("nest", [])
    return result


# ── Validation ───────────────────────────────────────────────────────────────

def validate_file_plan(file_plan: dict) -> list[str]:
    warnings = []
    planned_files = []
    for folder, file_list in file_plan.items():
        for f in file_list:
            planned_files.append(f)
            if not os.path.isfile(os.path.join(DESKTOP_PATH, f)):
                warnings.append(f"File '{f}' in plan does not exist on desktop.")
    if len(planned_files) != len(set(planned_files)):
        warnings.append("Some files appear in multiple folders.")
    return warnings


def validate_folder_plan(folder_plan: dict, existing_folders: list[str]) -> list[str]:
    warnings = []
    existing = set(existing_folders)
    for nest_op in folder_plan.get("nest", []):
        if nest_op["child"] not in existing:
            warnings.append(f"Nest source '{nest_op['child']}' does not exist.")
        if nest_op["into"] not in existing:
            warnings.append(f"Nest target '{nest_op['into']}' does not exist.")
        if nest_op["child"] == nest_op["into"]:
            warnings.append(f"Cannot nest folder '{nest_op['child']}' into itself.")
    for merge_op in folder_plan.get("merge", []):
        for child in merge_op["children"]:
            if child not in existing:
                warnings.append(f"Merge child '{child}' does not exist.")
    return warnings


# ── History (for undo) ───────────────────────────────────────────────────────

def save_history(moves: list[dict], created_dirs: list[str]) -> None:
    history = {"moves": moves, "created_dirs": created_dirs}
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def load_history() -> dict | None:
    if not os.path.isfile(HISTORY_PATH):
        return None
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)


def undo_last() -> None:
    history = load_history()
    if not history:
        return
    moves = history.get("moves", [])
    created_dirs = history.get("created_dirs", [])
    for move in reversed(moves):
        src = move["dst"]
        dst = move["src"]
        if not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
    for d in reversed(created_dirs):
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    os.remove(HISTORY_PATH)


# ── Execution ────────────────────────────────────────────────────────────────

def execute_file_plan(file_plan: dict, dry_run: bool = True) -> None:
    moves = []
    created_dirs = []
    for folder_name, file_list in file_plan.items():
        target_dir = os.path.join(DESKTOP_PATH, folder_name)
        if not dry_run:
            if not os.path.isdir(target_dir):
                created_dirs.append(target_dir)
            os.makedirs(target_dir, exist_ok=True)
        for filename in file_list:
            src = os.path.join(DESKTOP_PATH, filename)
            dst = os.path.join(target_dir, filename)
            if not os.path.isfile(src):
                continue
            if not dry_run:
                shutil.move(src, dst)
                moves.append({"src": src, "dst": dst})
    if not dry_run and moves:
        save_history(moves, created_dirs)


def execute_folder_plan(folder_plan: dict, dry_run: bool = True) -> None:
    moves = []
    created_dirs = []
    for merge_op in folder_plan.get("merge", []):
        parent = merge_op["new_parent"]
        parent_path = os.path.join(DESKTOP_PATH, parent)
        if not dry_run:
            if not os.path.isdir(parent_path):
                created_dirs.append(parent_path)
            os.makedirs(parent_path, exist_ok=True)
        for child in merge_op["children"]:
            src = os.path.join(DESKTOP_PATH, child)
            dst = os.path.join(parent_path, child)
            if not os.path.isdir(src):
                continue
            if not dry_run:
                shutil.move(src, dst)
                moves.append({"src": src, "dst": dst})
    for nest_op in folder_plan.get("nest", []):
        child = nest_op["child"]
        into = nest_op["into"]
        src = os.path.join(DESKTOP_PATH, child)
        dst = os.path.join(DESKTOP_PATH, into, child)
        if not os.path.isdir(src):
            continue
        if not os.path.isdir(os.path.join(DESKTOP_PATH, into)):
            continue
        if not dry_run:
            shutil.move(src, dst)
            moves.append({"src": src, "dst": dst})
    if not dry_run and moves:
        save_history(moves, created_dirs)
