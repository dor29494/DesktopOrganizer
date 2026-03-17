#!/bin/bash
# ============================================================
# Run this on a Mac to build DesktopOrganizer.app
#
# Usage:  bash build_mac.sh <CLAUDE_KEY> <GEMINI_KEY>
#   or:   bash build_mac.sh   (will prompt for keys)
#
# After it finishes, send the DesktopOrganizer-Mac.zip file
# back to the repo owner to upload to GitHub Releases.
# ============================================================
set -e

echo "=== Desktop Organizer — Mac Builder ==="
echo ""

# 1. Get API keys (from args or prompt)
CLAUDE_KEY="${1}"
GEMINI_KEY="${2}"
if [ -z "$CLAUDE_KEY" ]; then
    read -p "Enter Claude (Anthropic) API key: " CLAUDE_KEY
fi
if [ -z "$GEMINI_KEY" ]; then
    read -p "Enter Gemini API key: " GEMINI_KEY
fi

# 2. Clone the repo (or pull latest)
if [ ! -d "DesktopOrganizer" ]; then
    git clone https://github.com/dor29494/DesktopOrganizer.git
fi
cd DesktopOrganizer
git pull origin main

# 3. Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install pyinstaller anthropic openai google-genai

# 4. Generate embedded keys
python3 << PYEOF
import base64
def obfuscate(key):
    return base64.b64encode(key[::-1].encode()).decode()
claude_key = "${CLAUDE_KEY}"
gemini_key = "${GEMINI_KEY}"
with open("embedded_keys.py", "w") as f:
    f.write(f'# Auto-generated\\n_C = "{obfuscate(claude_key)}"\\n_G = "{obfuscate(gemini_key)}"\\n')
print("embedded_keys.py created!")
PYEOF

# 5. Build .app
echo ""
echo "=== Building .app ==="
pyinstaller --onefile --windowed --name "DesktopOrganizer" --hidden-import embedded_keys gui.py

# 6. Zip the .app and copy to Desktop for easy access
cd dist
zip -r DesktopOrganizer-Mac.zip DesktopOrganizer.app
cp DesktopOrganizer-Mac.zip ~/Desktop/

echo ""
echo "============================================"
echo "  BUILD COMPLETE!"
echo "  DesktopOrganizer-Mac.zip is on your Desktop"
echo "  Please send this file to Dor"
echo "============================================"
