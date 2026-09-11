# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. Featuring prominent whole-word focus, bold typography, double-spaced layout, Monkeytype-style faded words, character-by-character precision, and clickable mouse support.

---

## 🔍 Visibility & Typography

* **🔍 Increased Word Font (Words Only):** The active whole word currently being typed is rendered in a dedicated 2-row increased font with guide letters directly above, making the words easy to see and type without altering your terminal's normal font.
* **📏 Double Line Spacing:** Generous empty lines between text rows for effortless reading and natural eye tracking.
* **✨ High-Contrast Color Palette:**
  * **Vibrant Bold Neon Green:** Correct letters.
  * **Vivid Bold Red:** Mistyped letters.
  * **Crisp Bold Light Slate Gray:** Upcoming letters (always clearly readable, never muddy or invisible).
* **🖥️ Centered Canvas:** Text area automatically centers horizontally and vertically in your terminal window.

---

## 🎮 Game Modes

### 1. ⚡ Sprint Mode (WPM Test)
* **Goal:** Quick benchmark of your typing speed in 1–2 minutes.
* **Content:** Clean, natural everyday sentences (25–40 words).
* **Finish:** Concludes when the sentence is typed, presenting an end-of-round card with your exact **WPM**, **Accuracy**, and **Time**.

### 2. ♾️ Endless Mode (Balanced Practice)
* **Goal:** A comfortable typing session you can maintain for hours while steadily building muscle memory.
* **Balanced Pacing:**
  * 🔤 **Arbitrary Vocabulary:** 96%+ clean, varied English words.
  * ✍️ **Commas & Full Stops:** Appear once every **~35 words** (under 50 words) for natural punctuation cadence.
  * 🔢 **Numbers:** Appear once every **100 words** to practice the number row.
  * ⚙️ **Special Symbols & Code:** Appear once every **200 words** for occasional dexterity challenges.

---

## 🕹️ Mode Selection

1. **🖱️ Mouse:** Click directly on `[ 1: ⚡ Sprint ]` or `[ 2: ♾️ Endless ]` on the top bar.
2. **⌨️ Keyboard:**
   * **`1` / `2`:** Switch between Sprint and Endless modes.
   * **`TAB`:** Cycle modes.
3. **💻 CLI Flags:**
   ```bash
   ttyping --sprint     # Launch in Sprint Mode (or: ttyping -1)
   ttyping --endless    # Launch in Endless Mode (or: ttyping -2)
   ```

---

## ⌨️ Controls & Precision

* **Character Precision:** Space is treated like any regular key—it never skips words.
* **Color Feedback:** Correct letters are **Green**, mistyped letters are **Red (underlined)**, and upcoming letters are **Light Slate Gray**.
* **Backspace:** Delete any typos and fix characters on the fly.
* **`Ctrl + R` / `F5`:** Reset current session.
* **`ESC` or `Ctrl + C`:** Quit and view your summary stats card.
* **Terminal Zoom:** Press **`Ctrl + (+)`** in your terminal emulator to scale up overall font size anytime.

---

## 🛠 Project Structure

```
├── ttyping        # Executable launcher script
├── main.py        # Core curses game loop, big font, and modes
├── install.sh     # Quick setup script
├── .gitignore     # Git ignore rules
└── readme.md      # Documentation
```
