# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. Featuring giant 3-row Big Font mode, double-spaced layout, Monkeytype-style faded words, character-by-character precision, and clickable mouse support.

---

## 🔍 Visibility & Big Font Features

* **🔍 Giant 3-Row Big Font Mode:** Renders the active word in massive 3-row tall block letters (`[ B: Big Font ]`) so you never have to squint or strain your eyes.
* **📏 Double Line Spacing:** Generous empty lines between text rows for effortless reading.
* **✨ High-Contrast Color Palette:**
  * **Vibrant Neon Green:** Correct letters.
  * **Vivid Bold Red:** Mistyped letters.
  * **Crisp Light Slate Gray:** Upcoming letters (always clearly readable, never muddy or invisible).
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

## 🕹️ Mode & Size Selection

1. **🖱️ Mouse:** Click directly on `[ 1: ⚡ Sprint ]`, `[ 2: ♾️ Endless ]`, or `[ B: 🔍 Big Font ]` on the top bar.
2. **⌨️ Keyboard:**
   * **`1` / `2`:** Switch between Sprint and Endless modes.
   * **`B`:** Toggle Big Font on/off.
   * **`TAB`:** Cycle modes.
3. **💻 CLI Flags:**
   ```bash
   ttyping --big        # Launch directly in Big Font Mode (or: ttyping -b)
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
