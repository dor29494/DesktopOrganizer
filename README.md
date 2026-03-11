# Desktop Organizer

An AI-powered desktop organizer that automatically sorts your files and folders into logical groups using Claude, OpenAI, or Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Auto Organize Files** — AI analyzes your desktop files and groups them into smart folders
- **Custom Folders** — Define your own folder names and let AI sort files into them
- **Organize Folders** — AI merges or nests related folders together
- **Multi-Language UI** — Full English and Hebrew interface support
- **Undo** — Revert the last operation with one click
- **Multi-Provider AI** — Choose between Claude, OpenAI, or Gemini
- **Cross-Platform** — Works on Windows, macOS, and Linux
- **Alphabetical Sorting** — Results are always sorted A-Z

## Screenshots

> _Add screenshots of the app here_

<!-- ![Setup Screen](screenshots/setup.png) -->
<!-- ![Main Screen](screenshots/main.png) -->
<!-- ![Plan Results](screenshots/results.png) -->

## Getting Started

### Option 1: Download the EXE (Windows)

1. Download `DesktopOrganizer.exe` from the [Releases](../../releases) page
2. Double-click to run
3. On first launch, pick your AI provider and enter your API key

### Option 2: Run from source

```bash
git clone https://github.com/dor29494/DesktopOrganizer.git
cd DesktopOrganizer
pip install anthropic openai google-genai
python gui.py
```

## API Keys

You'll need an API key from one of these providers:

| Provider | Get your key at |
|----------|----------------|
| Claude (Anthropic) | https://console.anthropic.com/ |
| OpenAI | https://platform.openai.com/api-keys |
| Gemini (Google) | https://aistudio.google.com/apikey |

## How It Works

1. The app scans your desktop for files and folders
2. You choose an organize mode (auto, custom folders, or folder merge)
3. AI generates a plan showing what will be moved where
4. You review the plan and click Execute to apply
5. If you don't like the result, click Undo to revert

## Build from Source

To create a standalone EXE:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "DesktopOrganizer" gui.py
```

The EXE will be in the `dist/` folder.

## Tech Stack

- **Python** — Core language
- **Tkinter** — Desktop GUI
- **Anthropic / OpenAI / Google GenAI SDKs** — AI providers

## License

MIT
