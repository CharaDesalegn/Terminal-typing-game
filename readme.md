# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. Featuring real-time Monkeytype-style faded words, clickable mouse support, and multiple game modes.

---

## 🎮 Game Modes

### 1. ⚡ Sprint Mode (WPM Test)
* **Goal:** Test your typing speed in 1–2 minutes.
* **Content:** Clean, natural everyday sentences (25–40 words).
* **Finish:** Automatically concludes when the sentence is typed, presenting a completion card with your exact **WPM**, **Accuracy**, and **Time**.

### 2. ♾️ Endless Mode (Mastery Practice)
* **Goal:** Build finger dexterity, speed, and muscle memory across every row of the keyboard.
* **Content:** An endless stream of complex vocabulary, technical terms, camelCase, snake_case, punctuation, and code constructs (e.g. `polymorphism`, `calculate_sum()`, `UserAuth.verify()`, `data_stream.pipe()`).
* **Continuous Flow:** Words generate dynamically without stopping—you can type for hours! Tracks running WPM, total words completed, and streaks.

---

## 🕹️ Mode Selection: 3 Easy Ways

1. **🖱️ Click with Your Mouse:** Click directly on `[ 1: ⚡ Sprint ]` or `[ 2: ♾️ Endless ]` on the top bar.
2. **⌨️ Press Numbers:** Press **`1`** or **`2`** on your keyboard (or press **`TAB`** to toggle).
3. **💻 CLI Flags:**
   ```bash
   ttyping --sprint     # Launch directly in Sprint Mode (or ttyping -1)
   ttyping --endless    # Launch directly in Endless Mode (or ttyping -2)
   ```

---

## 🚀 Quick Installation

Run the install script to add `ttyping` to your local PATH (`~/.local/bin`):

```bash
chmod +x install.sh
./install.sh
```

---

## ⌨️ Controls & Shortcuts

| Key / Input | Action |
| :--- | :--- |
| **Mouse Click** | Click on `[1]` or `[2]` in the top bar to switch modes |
| **`1` / `2`** | Switch immediately between Sprint and Endless modes |
| **`TAB`** | Toggle between modes |
| **`Space`** | Advance to next word |
| **`Backspace`** | Delete character / error |
| **`Ctrl + R`** / **`F5`** | Restart current round |
| **`ENTER`** | Start next sentence (after Sprint completion) |
| **`ESC`** or **`Ctrl + C`** | Quit and view session summary |

---

## 🛠 Project Structure

```
├── ttyping        # Executable launcher script
├── main.py        # Core curses game loop, top-bar, and modes
├── install.sh     # Quick setup script
├── .gitignore     # Git ignore rules
└── readme.md      # Documentation
```
