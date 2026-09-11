# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. No external dependencies required!

---

## 🚀 Features

- **Instant Terminal Launch:** Start typing immediately by running `ttyping` in your terminal.
- **Two Game Modes:**
  - **Free Typing Mode:** Type anything you want in the terminal freely! Track your words, characters, elapsed time, and real-time WPM.
  - **Challenge Mode:** Practice against built-in quotes or supply your own custom sentence/text.
- **Live Performance Dashboard:**
  - ⏱ Elapsed Timer
  - ⚡ Real-Time WPM (Words Per Minute)
  - 📊 CPM (Characters Per Minute)
  - 📝 Word Count & Character Count
  - 🎯 Accuracy Percentage (Challenge Mode)
- **Fluid Terminal Controls:** Backspace, text wrapping, terminal resizing support, and clean session exit summary.

---

## 📦 Quick Installation

Run the install script to add `ttyping` to your local PATH (`~/.local/bin`):

```bash
chmod +x install.sh
./install.sh
```

Ensure `~/.local/bin` is in your `$PATH` (standard on most Linux distributions).

---

## 🎮 How to Play

### 1. Launch Free Typing Mode
Type anything in the terminal freely:
```bash
ttyping
```

### 2. Launch with Custom Practice Text
Pass any custom text as an argument to test your typing speed against it:
```bash
ttyping "The quick brown fox jumps over the lazy dog."
```

### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| **`TAB`** | Toggle between **Free Typing** and **Challenge** modes |
| **`Backspace`** | Delete previous character |
| **`Ctrl + R`** / **`F5`** | Reset current typing session |
| **`ENTER`** | Start next challenge quote (when finished) / Newline |
| **`ESC`** or **`Ctrl + C`** | Finish and view summary stats |

---

## 🛠 Project Structure

```
├── ttyping        # Executable launcher script
├── main.py        # Core curses game loop and logic
├── install.sh     # Quick setup script
├── .gitignore     # Git ignore rules
└── readme.md      # Documentation
```
