# ⌨️ Terminal Typing Game (`ttyping`)

A lightweight, responsive, and distraction-free terminal typing speed and practice game built in Python using standard `curses`. Featuring prominent whole-word focus, bold typography, double-spaced layout, Monkeytype-style faded words, character-by-character precision, and clickable mouse support.

---

## 🔍 Visibility & Typography

* **🔍 Increased Word Font (Words Only):** The active whole word currently being typed is rendered in a dedicated 2-row increased font with guide letters directly above, making the words easy to see and type without altering your terminal's normal font.
* **📏 Double Line Spacing:** Generous empty lines between text rows for effortless reading and natural eye tracking.
* **✨ High-Contrast Color Palette:**
  * **Vibrant Bold Neon Green:** Correct letters.
  * **Vivid Bold Red:** Mistyped letters.
  * **Prominent Reverse Gold:** Current active letter being typed.
  * **Crisp Bold Light Slate Gray:** Upcoming letters (always clearly readable, never muddy or invisible).
* **🖥️ Centered Canvas:** Layout maintains consistent orientation and automatically centers both horizontally and vertically across all screen sizes.

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

### 3. 🖐️ Touch Typing Tutor (Finger Guide Mode)
* **Goal:** Master proper 10-finger touch typing mechanics with visual keyboard and hand guidance.
* **⌨️ Full QWERTY Layout:** Displays every key in true ANSI QWERTY alignment with centered spacebar and home row resting position indicators (`[A] [S] [D] [F]` and `[J] [K] [L] [;]`).
* **🖐️ Faded Hand & Finger Positions:** Renders Left and Right hands with all 10 fingers (*Pinky*, *Ring*, *Middle*, *Index*, *Thumb*) faded in subtle gray.
* **✨ Real-Time Finger Highlighting:** When a key needs to be typed, the key on the keyboard and its corresponding finger on the hand diagram light up in bright bold neon green.
* **🎯 Prospective Finger Guidance:** Tells you exactly what to do before every keystroke (e.g. `👉 Press [ E ] with LEFT MIDDLE finger (Reach up from [D])`). If a mistake is made, it alerts you which finger you used vs which was expected, and prompts you to fix it.
* **📚 6 Built-in Drills:**
  1. **🏠 Home Row Mastery:** Rest position practice (`ASDF` and `JKL;`).
  2. **⬆️ Top Row Reach:** Upward reaches (`QWERTY UIOP`).
  3. **⬇️ Bottom Row Reach:** Downward reaches (`ZXCV BNM`).
  4. **🦊 Pangram:** Full alphabet drill covering all 26 letters across both hands.
  5. **🔢 Numbers & Symbols:** Number row and punctuation drills.
  6. **⌨️ Free Key Explorer:** Press ANY key on your keyboard to instantly see which finger and hand to use!

### 4. 📊 Error & Mistake Board (Confusion Matrix & Analytics)
* **Goal:** Understand your personal typing mistakes and target your weak keys for rapid improvement.
* **🔍 Mistake Tracking:** Tracks every single mistyped character (e.g., typing `E` instead of `D`, or `R` instead of `T`).
* **📋 Confusion Matrix Board:** Displays a clean table showing:
  * **Target Key:** The letter you were supposed to type.
  * **Total Errors:** How many times you've mistyped that letter.
  * **Mistyped With (Count):** Exactly which keys your fingers accidentally hit (e.g. `'e' (3x), 's' (1x)`).
  * **Accuracy Rate:** Precision percentage per key.
  * **Finger & Root Cause Analysis:** Explains whether you used the same finger (reached off-target), an adjacent finger on the same hand, or the wrong hand entirely.
* **🎯 Practice Weak Keys [P]:** Generates a custom practice session filled with words specifically containing your most mistyped letters!
* **🔄 Scope Toggle [S]:** Switch between your current session's mistakes and all-time persistent stats saved in `~/.config/ttyping/mistakes.json`.
* **🧹 Clear Stats [C]:** Reset your mistake history whenever you want to measure fresh progress.

---

## 🕹️ Mode Selection

1. **🖱️ Mouse:** Click directly on `[ 1: ⚡ Sprint ]`, `[ 2: ♾️ Endless ]`, `[ 3: 🖐️ Tutor ]`, or `[ 4: 📊 Error Board ]` on the top bar.
2. **⌨️ Keyboard:**
   * **`1` / `2` / `3` / `4`:** Switch directly to Sprint, Endless, Tutor, or Error Board mode.
   * **`TAB`:** Cycle through all modes (`Sprint` ➔ `Endless` ➔ `Tutor` ➔ `Board`).
   * **`ENTER` / `F2`:** Advance to the next drill in Tutor mode.
   * **`P`:** On the Error Board, generate and launch a targeted drill for your weak letters.
   * **`S`:** On the Error Board, toggle between Session and All-Time stats.
   * **`C`:** On the Error Board, clear mistake statistics.
   * **`↑` / `↓` / `PgUp` / `PgDn`:** Scroll through the mistake table.
3. **💻 CLI Flags:**
   ```bash
   ttyping --sprint     # Launch in Sprint Mode (or: ttyping -1)
   ttyping --endless    # Launch in Endless Mode (or: ttyping -2)
   ttyping --tutor      # Launch in Touch Typing Tutor Mode (or: ttyping -3)
   ttyping --board      # Launch directly into the Error Board (or: ttyping -4)
   ```

---

## ⌨️ Controls & Precision

* **Character Precision:** Space is treated like any regular key—it never skips words. When pressed correctly, it lights up in vibrant green (`␣`).
* **Color Feedback:** Correct letters and spaces are **Green (`␣`)**, current letter is **Prominently Highlighted (Reverse Gold)**, mistyped letters are **Red (underlined)**, and upcoming letters are **Light Slate Gray**.
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
