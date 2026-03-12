#!/bin/bash
# ============================================================
# Run this on a Mac to build DesktopOrganizer.app
# Then uploads it to the GitHub release.
#
# Usage:  bash build_mac.sh
# ============================================================
set -e

echo "=== Desktop Organizer — Mac Builder ==="
echo ""

# 1. Clone the repo
if [ ! -d "DesktopOrganizer" ]; then
    git clone https://github.com/dor29494/DesktopOrganizer.git
fi
cd DesktopOrganizer

# 2. Install dependencies
pip3 install pyinstaller anthropic openai google-genai

# 3. Generate embedded keys
echo ""
echo "=== API Key Setup ==="
read -p "Enter Claude (Anthropic) API key: " CLAUDE_KEY
read -p "Enter Gemini API key: " GEMINI_KEY

python3 -c "
import base64
def obfuscate(key):
    return base64.b64encode(key[::-1].encode()).decode()
with open('embedded_keys.py', 'w') as f:
    f.write(f'# Auto-generated\n_C = \"{obfuscate(\"$CLAUDE_KEY\")}\"\n_G = \"{obfuscate(\"$GEMINI_KEY\")}\"\n')
print('embedded_keys.py created!')
"

# 4. Build .app
echo ""
echo "=== Building .app ==="
pyinstaller --onefile --windowed --name "DesktopOrganizer" --hidden-import embedded_keys gui.py

# 5. Zip the .app for upload
cd dist
zip -r DesktopOrganizer-Mac.zip DesktopOrganizer.app
echo ""
echo "=== Build complete! ==="
echo "File: $(pwd)/DesktopOrganizer-Mac.zip"
echo ""

# 6. Upload to GitHub release
echo "To upload to GitHub, install gh CLI (brew install gh) and run:"
echo "  gh auth login"
echo "  gh release upload v1.0.0 DesktopOrganizer-Mac.zip --repo dor29494/DesktopOrganizer"
echo ""
read -p "Want to upload now? (requires gh CLI) [y/N]: " UPLOAD
if [ "$UPLOAD" = "y" ] || [ "$UPLOAD" = "Y" ]; then
    gh release upload v1.0.0 DesktopOrganizer-Mac.zip --repo dor29494/DesktopOrganizer
    echo "Uploaded! Check: https://github.com/dor29494/DesktopOrganizer/releases/tag/v1.0.0"
fi
