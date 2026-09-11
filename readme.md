# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. Featuring real-time Monkeytype-style faded words, character-by-character accuracy, clickable mouse support, and balanced difficulty pacing.

---

## 🎮 Game Modes

### 1. ⚡ Sprint Mode (WPM Test)
* **Goal:** Quick benchmark of your typing speed in 1–2 minutes.
* **Content:** Clean, natural everyday sentences (25–40 words).
* **Finish:** Concludes when the sentence is typed, presenting an end-of-round card with your exact **WPM**, **Accuracy**, and **Time**.

### 2. ♾️ Endless Mode (Balanced Practice)
* **Goal:** A comfortable typing session you can maintain for hours while steadily building muscle memory.
* **Balanced Pacing:**
  * 🔤 **Arbitrary Vocabulary:** 96%+ of words are clean, varied English words (no annoying symbol clutter).
  * ✍️ **Commas & Full Stops:** Appear once every **~35 words** (under 50 words) for natural punctuation cadence.
  * 🔢 **Numbers:** Appear once every **100 words** to practice the number row.
  * ⚙️ **Special Symbols & Code:** Appear once every **200 words** for occasional dexterity challenges.
* **Continuous Flow:** Words generate dynamically without stopping—type for as long as you want!

---

## 🕹️ Mode Selection

1. **🖱️ Mouse:** Click directly on `[ 1: ⚡ Sprint ]` or `[ 2: ♾️ Endless ]` on the top bar.
2. **⌨️ Keyboard:** Press **`1`** or **`2`** (or **`TAB`**) to switch modes.
3. **💻 CLI Flags:**
   ```bash
   ttyping --sprint     # Launch directly in Sprint Mode (or: ttyping -1)
   ttyping --endless    # Launch directly in Endless Mode (or: ttyping -2)
   ```

---

## ⌨️ Controls & Precision

* **Character Precision:** Space is treated like any regular key—it never skips words.
* **Color Feedback:** Correct letters are **Green**, mistyped letters are **Red (underlined)**, and upcoming letters are **Faded**.
* **Backspace:** Delete any typos and fix characters on the fly.
* **`Ctrl + R` / `F5`:** Reset current session.
* **`ESC` or `Ctrl + C`:** Quit and view your summary stats card.

---

## 🛠 Project Structure

```
├── ttyping        # Executable launcher script
├── main.py        # Core curses game loop, pacing, and modes
├── install.sh     # Quick setup script
├── .gitignore     # Git ignore rules
└── readme.md      # Documentation
```
