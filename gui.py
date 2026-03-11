import tkinter as tk
from tkinter import messagebox
import threading
from organizer import (
    scan_desktop,
    plan_files_auto,
    plan_files_user_defined,
    plan_folders,
    validate_file_plan,
    validate_folder_plan,
    execute_file_plan,
    execute_folder_plan,
    undo_last,
    load_history,
    load_config,
    save_config,
    get_last_demo_meta,
    PROVIDERS,
)

# ── Theme colors ─────────────────────────────────────────────────────────────
BG = "#1e1e2e"           # dark background
BG_CARD = "#2a2a3d"      # card/section background
BG_INPUT = "#363650"     # input fields
FG = "#e0e0e0"           # main text
FG_DIM = "#8888aa"       # dimmed text
ACCENT = "#7c6ff7"       # purple accent
ACCENT_HOVER = "#9580ff" # purple hover
GREEN = "#50c878"        # execute button
GREEN_HOVER = "#66e090"
RED = "#e05565"          # undo button
RED_HOVER = "#f06878"
ORANGE = "#f0a050"       # warning color
BORDER = "#3a3a55"

# ── Translations ─────────────────────────────────────────────────────────────
STRINGS = {
    "en": {
        "title": "\U0001F5C2\uFE0F Desktop Organizer",
        "language": "\U0001F310 Language",
        "auto": "\U0001F916  Organize Files \u2014 Auto",
        "custom": "\U0001F4C1  Organize Files \u2014 Custom Folders",
        "folders": "\U0001F4C2  Organize Folders",
        "execute": "\u2705 Execute",
        "undo": "\u21A9\uFE0F  Undo",
        "plan_results": "\U0001F4CB Plan Results",
        "scanning": "\u23F3 Scanning desktop...",
        "status_fmt": "\U0001F4C1 {files} file(s)  \u2502  \U0001F4C2 {folders} folder(s) on desktop",
        "analyzing": "\u23F3 Analyzing with AI... please wait",
        "ai_thinking": "\n\n        \U0001F916 AI is thinking...\n",
        "plan_ready": "\u2705 Plan ready! Click Execute to apply.",
        "plan_error": "\u274C Failed to get plan from AI.",
        "done": "\U0001F389 Done! Changes applied. Click Undo to revert.",
        "undo_done": "\u21A9\uFE0F Undo complete. Desktop restored.",
        "no_files": "\U0001F4C1 No files found on desktop.",
        "no_folders": "\U0001F4C2 No folders found on desktop.",
        "no_changes": "\u2705 No folder changes proposed.",
        "custom_title": "\U0001F4C1 Custom Folders",
        "custom_header": "\U0001F4DD Enter folder names (one per field):",
        "next": "\u2795 Next",
        "done_btn": "\u2705 Done",
        "cancel": "\u274C Cancel",
        "fallback_notice": "\u26A0\uFE0F Claude limit reached \u2014 using free Gemini (results may vary)\n\n",
        "powered_by": "Powered by {provider} \u2022 {remaining} Claude requests left today",
    },
    "he": {
        "title": "\U0001F5C2\uFE0F \u05DE\u05E1\u05D3\u05E8 \u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4",
        "language": "\U0001F310 \u05E9\u05E4\u05D4",
        "auto": "\U0001F916  \u05E1\u05D9\u05D3\u05D5\u05E8 \u05E7\u05D1\u05E6\u05D9\u05DD \u2014 \u05D0\u05D5\u05D8\u05D5\u05DE\u05D8\u05D9",
        "custom": "\U0001F4C1  \u05E1\u05D9\u05D3\u05D5\u05E8 \u05E7\u05D1\u05E6\u05D9\u05DD \u2014 \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA \u05DE\u05D5\u05EA\u05D0\u05DE\u05D5\u05EA",
        "folders": "\U0001F4C2  \u05E1\u05D9\u05D3\u05D5\u05E8 \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA",
        "execute": "\u2705 \u05D1\u05D9\u05E6\u05D5\u05E2",
        "undo": "\u21A9\uFE0F  \u05D1\u05D9\u05D8\u05D5\u05DC",
        "plan_results": "\U0001F4CB \u05EA\u05D5\u05E6\u05D0\u05D5\u05EA \u05D4\u05EA\u05D5\u05DB\u05E0\u05D9\u05EA",
        "scanning": "\u23F3 \u05E1\u05D5\u05E8\u05E7 \u05D0\u05EA \u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4...",
        "status_fmt": "\U0001F4C1 {files} \u05E7\u05D1\u05E6\u05D9\u05DD  \u2502  \U0001F4C2 {folders} \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA \u05D1\u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4",
        "analyzing": "\u23F3 \u05DE\u05E0\u05EA\u05D7 \u05E2\u05DD AI... \u05D0\u05E0\u05D0 \u05D4\u05DE\u05EA\u05DF",
        "ai_thinking": "\n\n        \U0001F916 \u05D4-AI \u05D7\u05D5\u05E9\u05D1...\n",
        "plan_ready": "\u2705 \u05D4\u05EA\u05D5\u05DB\u05E0\u05D9\u05EA \u05DE\u05D5\u05DB\u05E0\u05D4! \u05DC\u05D7\u05E5 \u05D1\u05D9\u05E6\u05D5\u05E2 \u05DC\u05D4\u05E4\u05E2\u05DC\u05D4.",
        "plan_error": "\u274C \u05E0\u05DB\u05E9\u05DC \u05D1\u05E7\u05D1\u05DC\u05EA \u05EA\u05D5\u05DB\u05E0\u05D9\u05EA \u05DE\u05D4-AI.",
        "done": "\U0001F389 \u05D1\u05D5\u05E6\u05E2! \u05D4\u05E9\u05D9\u05E0\u05D5\u05D9\u05D9\u05DD \u05D4\u05D5\u05D7\u05DC\u05D5. \u05DC\u05D7\u05E5 \u05D1\u05D9\u05D8\u05D5\u05DC \u05DC\u05E9\u05D7\u05D6\u05D5\u05E8.",
        "undo_done": "\u21A9\uFE0F \u05D4\u05D1\u05D9\u05D8\u05D5\u05DC \u05D4\u05D5\u05E9\u05DC\u05DD. \u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4 \u05E9\u05D5\u05D7\u05D6\u05E8.",
        "no_files": "\U0001F4C1 \u05DC\u05D0 \u05E0\u05DE\u05E6\u05D0\u05D5 \u05E7\u05D1\u05E6\u05D9\u05DD \u05D1\u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4.",
        "no_folders": "\U0001F4C2 \u05DC\u05D0 \u05E0\u05DE\u05E6\u05D0\u05D5 \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA \u05D1\u05E9\u05D5\u05DC\u05D7\u05DF \u05D4\u05E2\u05D1\u05D5\u05D3\u05D4.",
        "no_changes": "\u2705 \u05DC\u05D0 \u05D4\u05D5\u05E6\u05E2\u05D5 \u05E9\u05D9\u05E0\u05D5\u05D9\u05D9\u05DD \u05D1\u05EA\u05D9\u05E7\u05D9\u05D5\u05EA.",
        "custom_title": "\U0001F4C1 \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA \u05DE\u05D5\u05EA\u05D0\u05DE\u05D5\u05EA",
        "custom_header": "\U0001F4DD \u05D4\u05D6\u05DF \u05E9\u05DE\u05D5\u05EA \u05EA\u05D9\u05E7\u05D9\u05D5\u05EA (\u05D0\u05D7\u05D3 \u05D1\u05DB\u05DC \u05E9\u05D3\u05D4):",
        "next": "\u2795 \u05D4\u05D1\u05D0",
        "done_btn": "\u2705 \u05E1\u05D9\u05D5\u05DD",
        "cancel": "\u274C \u05D1\u05D9\u05D8\u05D5\u05DC",
        "fallback_notice": "\u26A0\uFE0F \u05DE\u05DB\u05E1\u05EA Claude \u05D4\u05D2\u05D9\u05E2\u05D4 \u05DC\u05DE\u05D2\u05D1\u05DC\u05D4 \u2014 \u05DE\u05E9\u05EA\u05DE\u05E9 \u05D1-Gemini \u05D7\u05D9\u05E0\u05DE\u05D9 (\u05D9\u05D9\u05EA\u05DB\u05E0\u05D5 \u05E9\u05D2\u05D9\u05D0\u05D5\u05EA)\n\n",
        "powered_by": "\u05DE\u05D5\u05E4\u05E2\u05DC \u05E2\u05DC \u05D9\u05D3\u05D9 {provider} \u2022 \u05E0\u05D5\u05EA\u05E8\u05D5 {remaining} \u05D1\u05E7\u05E9\u05D5\u05EA Claude \u05D4\u05D9\u05D5\u05DD",
    },
}


def styled_button(parent, text, command, bg_color, hover_color, fg="white", **kwargs):
    """Create a flat styled button with hover effect."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg_color, fg=fg, activebackground=hover_color, activeforeground="white",
        relief="flat", cursor="hand2", font=("Segoe UI", 11, "bold"),
        bd=0, padx=16, pady=10, **kwargs
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_color) if btn["state"] != "disabled" else None)
    btn.bind("<Leave>", lambda e: btn.config(bg=bg_color) if btn["state"] != "disabled" else None)
    return btn


# ── Setup Dialog ─────────────────────────────────────────────────────────────

class SetupDialog(tk.Toplevel):
    """First-run setup: pick AI provider, model, and enter API key."""

    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.title("\U0001F511 AI Setup")
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=BG)
        self.on_complete = on_complete

        # Header
        header = tk.Frame(self, bg=ACCENT, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="\U0001F511 AI Provider Setup",
            bg=ACCENT, fg="white", font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=16)

        form = tk.Frame(self, bg=BG)
        form.pack(fill="both", expand=True, padx=30, pady=20)

        # Provider
        tk.Label(form, text="AI Provider", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
        self.provider_var = tk.StringVar(value=list(PROVIDERS.keys())[0])
        self.provider_menu = tk.OptionMenu(form, self.provider_var, *PROVIDERS.keys(), command=self._on_provider_change)
        self.provider_menu.config(
            bg=BG_INPUT, fg=FG, activebackground=BG_INPUT, activeforeground=FG,
            font=("Segoe UI", 11), relief="flat", highlightthickness=0, bd=0
        )
        self.provider_menu["menu"].config(bg=BG_INPUT, fg=FG, font=("Segoe UI", 10))
        self.provider_menu.pack(fill="x", pady=(2, 12))

        # Model
        tk.Label(form, text="Model", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
        self.model_var = tk.StringVar()
        self.model_menu = tk.OptionMenu(form, self.model_var, "")
        self.model_menu.config(
            bg=BG_INPUT, fg=FG, activebackground=BG_INPUT, activeforeground=FG,
            font=("Segoe UI", 11), relief="flat", highlightthickness=0, bd=0
        )
        self.model_menu["menu"].config(bg=BG_INPUT, fg=FG, font=("Segoe UI", 10))
        self.model_menu.pack(fill="x", pady=(2, 12))

        # API Key
        tk.Label(form, text="API Key", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
        self.key_entry = tk.Entry(
            form, bg=BG_INPUT, fg=FG, insertbackground=FG,
            font=("Segoe UI", 11), relief="flat", show="\u2022"
        )
        self.key_entry.pack(fill="x", ipady=6, pady=(2, 20))

        # Save button
        styled_button(form, "\u2705 Save & Start", self._on_save, GREEN, GREEN_HOVER).pack(fill="x")

        # Init model list
        self._on_provider_change(self.provider_var.get())

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_provider_change(self, provider):
        models = PROVIDERS[provider]["models"]
        menu = self.model_menu["menu"]
        menu.delete(0, "end")
        for m in models:
            menu.add_command(label=m, command=lambda v=m: self.model_var.set(v))
        self.model_var.set(models[0])

    def _on_save(self):
        provider = self.provider_var.get()
        model = self.model_var.get()
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Missing Key", "Please enter your API key.", parent=self)
            return
        save_config(provider, key, model)
        self.on_complete()
        self.destroy()

    def _on_close(self):
        if load_config() is None:
            self.master.destroy()
        else:
            self.destroy()

    def prefill(self, config: dict):
        """Pre-fill fields with existing config (for settings edit)."""
        self.provider_var.set(config["provider"])
        self._on_provider_change(config["provider"])
        self.model_var.set(config["model"])
        self.key_entry.insert(0, config["api_key"])


# ── Custom Folders Dialog ────────────────────────────────────────────────────

class CustomFoldersDialog(tk.Toplevel):
    """Dialog with dynamic folder name inputs. Press 'Next' or Tab to add more."""

    def __init__(self, parent, lang="en"):
        super().__init__(parent)
        s = STRINGS[lang]
        self.title(s["custom_title"])
        self.geometry("420x440")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=BG)

        self.result: list[str] | None = None
        self.entries: list[tk.Entry] = []

        # Header
        tk.Label(
            self, text=s["custom_header"],
            anchor="w", bg=BG, fg=FG, font=("Segoe UI", 11)
        ).pack(fill="x", padx=20, pady=(20, 8))

        # Scrollable area
        container = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        container.pack(fill="both", expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(container, bg=BG_CARD, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.inputs_frame = tk.Frame(self.canvas, bg=BG_CARD)

        self.inputs_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inputs_frame, anchor="nw", width=360)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=(8, 20))

        styled_button(btn_frame, s["next"], self._add_entry, ACCENT, ACCENT_HOVER).pack(side="left")
        styled_button(btn_frame, s["done_btn"], self._on_done, GREEN, GREEN_HOVER).pack(side="right")
        styled_button(btn_frame, s["cancel"], self._on_cancel, "#555566", "#666678").pack(side="right", padx=(0, 8))

        self._add_entry()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _add_entry(self):
        row = tk.Frame(self.inputs_frame, bg=BG_CARD)
        row.pack(fill="x", pady=3, padx=5)

        tk.Label(
            row, text=f"\U0001F4C2 {len(self.entries) + 1}.", width=5, anchor="e",
            bg=BG_CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        entry = tk.Entry(
            row, bg=BG_INPUT, fg=FG, insertbackground=FG,
            font=("Segoe UI", 11), relief="flat", bd=0
        )
        entry.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=4)
        entry.bind("<Tab>", self._on_tab)
        entry.bind("<Return>", self._on_tab)

        self.entries.append(entry)
        entry.focus_set()

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_tab(self, event):
        if event.widget == self.entries[-1]:
            self._add_entry()
            return "break"

    def _on_done(self):
        self.result = [e.get().strip() for e in self.entries if e.get().strip()]
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


# ── Main App ─────────────────────────────────────────────────────────────────

class DesktopOrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.geometry("620x680")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.files: list[str] = []
        self.folders: list[str] = []
        self.current_plan = None
        self.current_plan_type = None

        self.lang_var = tk.StringVar(value="en")

        self._build_ui()
        self._apply_lang()
        self._scan()

        self.lang_var.trace_add("write", self._apply_lang)

    def t(self, key: str) -> str:
        return STRINGS[self.lang_var.get()][key]

    def _build_ui(self):
        # ── Title bar ────────────────────────────────────────────────────
        title_frame = tk.Frame(self.root, bg=ACCENT, height=50)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        self.title_label = tk.Label(
            title_frame, text="",
            bg=ACCENT, fg="white", font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side="left", padx=20)

        # Settings gear button
        settings_btn = tk.Button(
            title_frame, text="\u2699\uFE0F", command=self._open_settings,
            bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, activeforeground="white",
            relief="flat", cursor="hand2", font=("Segoe UI", 14), bd=0
        )
        settings_btn.pack(side="right", padx=15)
        settings_btn.bind("<Enter>", lambda e: settings_btn.config(bg=ACCENT_HOVER))
        settings_btn.bind("<Leave>", lambda e: settings_btn.config(bg=ACCENT))

        # ── Language ─────────────────────────────────────────────────────
        lang_frame = tk.Frame(self.root, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        lang_frame.pack(fill="x", padx=15, pady=(15, 8))

        self.lang_label = tk.Label(
            lang_frame, text="", bg=BG_CARD, fg=FG_DIM,
            font=("Segoe UI", 9)
        )
        self.lang_label.pack(side="left", padx=(12, 5), pady=8)

        for text, val in [("\U0001F1EC\U0001F1E7 English", "en"), ("\U0001F1EE\U0001F1F1 \u05E2\u05D1\u05E8\u05D9\u05EA", "he")]:
            tk.Radiobutton(
                lang_frame, text=text, variable=self.lang_var, value=val,
                bg=BG_CARD, fg=FG, selectcolor=BG_INPUT, activebackground=BG_CARD,
                activeforeground=FG, font=("Segoe UI", 10), indicatoron=True
            ).pack(side="left", padx=10, pady=8)

        # ── Action buttons ───────────────────────────────────────────────
        action_frame = tk.Frame(self.root, bg=BG)
        action_frame.pack(fill="x", padx=15, pady=5)

        self.btn_auto = styled_button(
            action_frame, "", self._on_auto, ACCENT, ACCENT_HOVER
        )
        self.btn_auto.pack(fill="x", pady=3)

        self.btn_custom = styled_button(
            action_frame, "", self._on_custom, "#5a6acf", "#6b7ce0"
        )
        self.btn_custom.pack(fill="x", pady=3)

        self.btn_folders = styled_button(
            action_frame, "", self._on_folders, "#4a8c6f", "#5aa080"
        )
        self.btn_folders.pack(fill="x", pady=3)

        # ── Status ───────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="")
        tk.Label(
            self.root, textvariable=self.status_var, anchor="w",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 9)
        ).pack(fill="x", padx=18, pady=(8, 2))

        # ── Execute / Undo (pack BEFORE results so they always show) ────
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(side="bottom", fill="x", padx=15, pady=(5, 15))

        # ── Results ──────────────────────────────────────────────────────
        result_frame = tk.Frame(self.root, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.plan_results_label = tk.Label(
            result_frame, text="", bg=BG_CARD, fg=FG_DIM,
            font=("Segoe UI", 9), anchor="w"
        )
        self.plan_results_label.pack(fill="x", padx=10, pady=(8, 0))

        text_container = tk.Frame(result_frame, bg=BG_CARD)
        text_container.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.result_text = tk.Text(
            text_container, wrap="word", state="disabled",
            bg=BG_INPUT, fg=FG, insertbackground=FG,
            font=("Consolas", 10), relief="flat", bd=0, padx=10, pady=8
        )
        scrollbar = tk.Scrollbar(text_container, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_text.pack(fill="both", expand=True)

        self.btn_execute = styled_button(
            btn_frame, "", self._on_execute, GREEN, GREEN_HOVER, state="disabled"
        )
        self.btn_execute.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_undo = styled_button(
            btn_frame, "", self._on_undo, RED, RED_HOVER, state="disabled"
        )
        self.btn_undo.pack(side="right", fill="x", expand=True, padx=(5, 0))

    # ── Language switching ────────────────────────────────────────────────

    def _apply_lang(self, *_args):
        s = STRINGS[self.lang_var.get()]
        self.root.title(s["title"])
        self.title_label.config(text=s["title"])
        self.lang_label.config(text=s["language"])
        self.btn_auto.config(text=s["auto"])
        self.btn_custom.config(text=s["custom"])
        self.btn_folders.config(text=s["folders"])
        self.btn_execute.config(text=s["execute"])
        self.btn_undo.config(text=s["undo"])
        self.plan_results_label.config(text=s["plan_results"])
        self._update_status()

    def _update_status(self):
        s = STRINGS[self.lang_var.get()]
        self.status_var.set(
            s["status_fmt"].format(files=len(self.files), folders=len(self.folders))
        )

    # ── Settings ──────────────────────────────────────────────────────────

    def _open_settings(self):
        dialog = SetupDialog(self.root, on_complete=lambda: None)
        config = load_config()
        if config:
            dialog.prefill(config)

    # ── Helpers ──────────────────────────────────────────────────────────

    def _scan(self):
        self.files, self.folders = scan_desktop()
        self._update_status()
        if load_history():
            self.btn_undo.config(state="normal")

    def _set_results(self, text: str):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", text)
        self.result_text.config(state="disabled")

    def _set_buttons(self, analyzing: bool = False):
        state = "disabled" if analyzing else "normal"
        self.btn_auto.config(state=state)
        self.btn_custom.config(state=state)
        self.btn_folders.config(state=state)

    def _format_file_plan(self, plan: dict) -> str:
        lines = []
        for folder, flist in plan.items():
            lines.append(f"\U0001F4C1 {folder}")
            for f in flist:
                lines.append(f"   \u2514\u2500 {f}")
            lines.append("")
        return "\n".join(lines)

    def _format_folder_plan(self, plan: dict) -> str:
        lines = []
        for op in plan.get("merge", []):
            children = ", ".join(op["children"])
            lines.append(f"\U0001F504 MERGE: {children}")
            lines.append(f"   \u2514\u2500 \u27A1 new folder '{op['new_parent']}'")
            lines.append("")
        for op in plan.get("nest", []):
            lines.append(f"\U0001F4E5 NEST: {op['child']}/")
            lines.append(f"   \u2514\u2500 \u27A1 into {op['into']}/")
            lines.append("")
        if not lines:
            lines.append(self.t("no_changes"))
        return "\n".join(lines)

    # ── AI calls (threaded) ──────────────────────────────────────────────

    def _run_in_thread(self, target, *args):
        self._set_buttons(analyzing=True)
        self.btn_execute.config(state="disabled")
        self.status_var.set(self.t("analyzing"))
        self._set_results(self.t("ai_thinking"))

        def worker():
            try:
                result = target(*args)
                self.root.after(0, lambda: self._on_plan_ready(result))
            except Exception as e:
                self.root.after(0, lambda: self._on_plan_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _sort_plan(plan, plan_type):
        """Sort plan alphabetically — folders by name, files within each folder."""
        if plan_type == "file":
            return dict(
                sorted(
                    ((k, sorted(v, key=str.lower)) for k, v in plan.items()),
                    key=lambda item: item[0].lower(),
                )
            )
        # folder plan: sort merge/nest operations alphabetically
        sorted_plan = {}
        if "merge" in plan:
            sorted_plan["merge"] = sorted(
                plan["merge"], key=lambda op: op["new_parent"].lower()
            )
        if "nest" in plan:
            sorted_plan["nest"] = sorted(
                plan["nest"], key=lambda op: op["child"].lower()
            )
        return sorted_plan

    def _on_plan_ready(self, plan):
        self._set_buttons(analyzing=False)
        plan = self._sort_plan(plan, self.current_plan_type)

        if self.current_plan_type == "file":
            warnings = validate_file_plan(plan)
            text = self._format_file_plan(plan)
        else:
            warnings = validate_folder_plan(plan, self.folders)
            text = self._format_folder_plan(plan)

        if warnings:
            warning_text = "\u26A0\uFE0F WARNINGS:\n" + "\n".join(f"   \u2022 {w}" for w in warnings) + "\n\n"
            text = warning_text + text

        # Show fallback notice if demo mode used Gemini instead of Claude
        meta = get_last_demo_meta()
        if meta and meta.get("fallback"):
            text = self.t("fallback_notice") + text

        self.current_plan = plan
        self._set_results(text)
        self.btn_execute.config(state="normal")

        # Show provider info in status bar for demo mode
        if meta:
            self.status_var.set(self.t("powered_by").format(
                provider=meta.get("provider", "?").capitalize(),
                remaining=meta.get("claude_remaining", "?"),
            ))
        else:
            self.status_var.set(self.t("plan_ready"))

    def _on_plan_error(self, error: str):
        self._set_buttons(analyzing=False)
        self._set_results(f"\u274C Error:\n\n{error}")
        self.status_var.set(self.t("plan_error"))

    # ── Button handlers ──────────────────────────────────────────────────

    def _on_auto(self):
        if not self.files:
            messagebox.showinfo("Info", self.t("no_files"))
            return
        self.current_plan_type = "file"
        lang = self.lang_var.get()
        self._run_in_thread(plan_files_auto, self.files, lang)

    def _on_custom(self):
        if not self.files:
            messagebox.showinfo("Info", self.t("no_files"))
            return
        dialog = CustomFoldersDialog(self.root, lang=self.lang_var.get())
        self.root.wait_window(dialog)
        if not dialog.result:
            return
        self.current_plan_type = "file"
        self._run_in_thread(plan_files_user_defined, self.files, dialog.result)

    def _on_folders(self):
        if not self.folders:
            messagebox.showinfo("Info", self.t("no_folders"))
            return
        self.current_plan_type = "folder"
        lang = self.lang_var.get()
        self._run_in_thread(plan_folders, self.folders, lang)

    def _on_execute(self):
        if not self.current_plan:
            return
        if self.current_plan_type == "file":
            execute_file_plan(self.current_plan, dry_run=False)
        else:
            execute_folder_plan(self.current_plan, dry_run=False)

        self.btn_execute.config(state="disabled")
        self.btn_undo.config(state="normal")
        self.status_var.set(self.t("done"))
        self._scan()

    def _on_undo(self):
        undo_last()
        self.btn_undo.config(state="disabled")
        self.current_plan = None
        self.status_var.set(self.t("undo_done"))
        self._set_results("")
        self._scan()


def main():
    root = tk.Tk()

    config = load_config()
    if config is None:
        # First-run: show setup dialog in root
        root.title("\U0001F511 AI Setup")
        root.geometry("460x420")
        root.resizable(False, False)
        root.configure(bg=BG)

        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"460x420+{(sw - 460) // 2}+{(sh - 340) // 2}")

        _build_setup_in_root(root)
    else:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"620x680+{(sw - 620) // 2}+{(sh - 680) // 2}")
        DesktopOrganizerApp(root)

    root.mainloop()


def _build_setup_in_root(root):
    """Build the first-run setup UI directly inside the root window."""
    header = tk.Frame(root, bg=ACCENT, height=44)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(
        header, text="\U0001F511 AI Provider Setup",
        bg=ACCENT, fg="white", font=("Segoe UI", 14, "bold")
    ).pack(side="left", padx=16)

    form = tk.Frame(root, bg=BG)
    form.pack(fill="both", expand=True, padx=30, pady=20)

    # Provider
    tk.Label(form, text="AI Provider", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
    provider_var = tk.StringVar(value=list(PROVIDERS.keys())[0])
    provider_menu = tk.OptionMenu(form, provider_var, *PROVIDERS.keys())
    provider_menu.config(
        bg=BG_INPUT, fg=FG, activebackground=BG_INPUT, activeforeground=FG,
        font=("Segoe UI", 11), relief="flat", highlightthickness=0, bd=0
    )
    provider_menu["menu"].config(bg=BG_INPUT, fg=FG, font=("Segoe UI", 10))
    provider_menu.pack(fill="x", pady=(2, 12))

    # Model
    tk.Label(form, text="Model", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
    model_var = tk.StringVar()
    model_menu = tk.OptionMenu(form, model_var, "")
    model_menu.config(
        bg=BG_INPUT, fg=FG, activebackground=BG_INPUT, activeforeground=FG,
        font=("Segoe UI", 11), relief="flat", highlightthickness=0, bd=0
    )
    model_menu["menu"].config(bg=BG_INPUT, fg=FG, font=("Segoe UI", 10))
    model_menu.pack(fill="x", pady=(2, 12))

    def on_provider_change(*_args):
        models = PROVIDERS[provider_var.get()]["models"]
        menu = model_menu["menu"]
        menu.delete(0, "end")
        for m in models:
            menu.add_command(label=m, command=lambda v=m: model_var.set(v))
        model_var.set(models[0])

    provider_var.trace_add("write", on_provider_change)
    on_provider_change()

    # API Key
    tk.Label(form, text="API Key", bg=BG, fg=FG_DIM, font=("Segoe UI", 9), anchor="w").pack(fill="x")
    key_entry = tk.Entry(
        form, bg=BG_INPUT, fg=FG, insertbackground=FG,
        font=("Segoe UI", 11), relief="flat", show="\u2022"
    )
    key_entry.pack(fill="x", ipady=6, pady=(2, 20))

    def _launch_main(root):
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("620x680")
        root.resizable(False, False)
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"620x680+{(sw - 620) // 2}+{(sh - 680) // 2}")
        DesktopOrganizerApp(root)

    def on_save():
        key = key_entry.get().strip()
        if not key:
            messagebox.showwarning("Missing Key", "Please enter your API key.")
            return
        save_config(provider_var.get(), key, model_var.get())
        _launch_main(root)

    def on_demo():
        save_config("demo", "", "gemini-2.0-flash")
        _launch_main(root)

    styled_button(form, "\u2705 Save & Start", on_save, GREEN, GREEN_HOVER).pack(fill="x")

    # Separator
    tk.Label(form, text="- or -", bg=BG, fg=FG_DIM, font=("Segoe UI", 9)).pack(pady=(8, 4))

    # Demo mode button
    styled_button(
        form, "\U0001F680 Try without API key (demo)", on_demo, "#5a6acf", "#6b7ce0"
    ).pack(fill="x")


if __name__ == "__main__":
    main()
