#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.local/bin"

mkdir -p "$TARGET_DIR"
chmod +x "$DIR/ttyping" "$DIR/main.py"

ln -sf "$DIR/ttyping" "$TARGET_DIR/ttyping"

echo "============================================="
echo "  Terminal Typing Game (ttyping) Installed!  "
echo "============================================="
echo "You can now run 'ttyping' anywhere in your terminal."
echo "Usage:"
echo "  ttyping                  # Open game in Free Typing mode"
echo "  ttyping \"Custom text\"    # Open challenge mode with custom text"
echo "============================================="
