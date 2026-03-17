"""
One-time script to obfuscate your API keys for embedding in the EXE.
Run this ONCE locally:  python generate_keys.py
It creates embedded_keys.py (gitignored) which gets bundled into the EXE.
"""
import base64
import os

print("=== API Key Obfuscator ===\n")
claude_key = input("Enter your Claude (Anthropic) API key: ").strip()
gemini_key = input("Enter your Gemini API key: ").strip()

# Simple obfuscation — base64 + reverse. Not cryptographic security,
# just enough so keys aren't plain text in the binary.
def obfuscate(key: str) -> str:
    return base64.b64encode(key[::-1].encode()).decode()

out = f'''# Auto-generated — do NOT commit this file
_C = "{obfuscate(claude_key)}"
_G = "{obfuscate(gemini_key)}"
'''

path = os.path.join(os.path.dirname(__file__), "embedded_keys.py")
with open(path, "w") as f:
    f.write(out)

print(f"\nSaved to {path}")
print("Now rebuild the EXE: python -m PyInstaller --onefile --windowed --name DesktopOrganizer gui.py")
