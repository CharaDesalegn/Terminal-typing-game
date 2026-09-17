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
* **Goal:** Master proper 10-finger touch typing mechanics with realistic mechanical keyboard and hand guidance.
* **⌨️ Mechanical Keyboard Layout:** Displays an authentic 60% ANSI mechanical keyboard with cool grey chassis borders, off-white keycaps, two-tone modifiers, and home row resting position indicators (`[A] [S] [D] [F]` and `[J] [K] [L] [;]`).
* **🖐️ Stylized Shaded Hands & Finger Guidance:** Renders Left and Right hands with shaded ASCII blocks (`█, ▓, ▒, ░`), stippled knuckles, and fingernails in warm peach/beige skin tones resting on the keyboard and spacebar.
* **✨ Real-Time Finger Highlighting:** When a key needs to be typed, the key on the keyboard lights up in bright contrasting highlight and its corresponding finger shaft and knuckle glow in warm active gold.
* **🎯 Prospective Finger Guidance:** Tells you exactly what to do before every keystroke (e.g. `👉 Press [ E ] with LEFT MIDDLE finger (Reach up from [D])`). If a mistake is made, it alerts you which finger was pressed vs which was expected.
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
* **✨ Real-Time Physical Key Highlighting:**
  * **Press ANY key on your physical keyboard** (e.g. `[A]`, `[E]`, `[R]`, `[Space]`): that key is instantly highlighted in bold reverse video in the Error Board list with `➔ [A]`.
  * **Auto-Scroll:** Automatically scrolls the list to bring the pressed key directly into view.
  * **Zero-Mistake Confirmation:** If you press a key with 0 errors, a confirmation banner displays your clean record (e.g. `✅ Key [ A ]: 0 mistakes recorded! (57/57 clean hits)`).
* **📊 Error & Press Count Tracking `(10/57)`:**
  * Whenever errors are displayed, the Error Board includes the total number of times you have pressed that key in the format `(errors/presses)`, such as `10 (10/57)`.
  * The top overview stat row summarizes total errors and total keystrokes: `❌ Total Mistakes: 10 (10/57)`.
  * Key inspection banner displays errors vs total attempts: `❌ Mistakes: 10 (10/57)`.
* **🎯 High-Density Focused Practice Mode (Error Board Protected):**
  * While highlighting any key, press **`[ENTER]`** (or click the practice button) to enter a focused drill where words are heavily saturated with that letter (including words with 2, 3, or more occurrences of that target key).
  * **Protected Stats:** Errors made during focused key practice drills are **not added to the Error Board**, keeping your real-world typing metrics pure and uninflated.
  * Prominent target drill banner displayed throughout practice.
  * Hitting **`[ENTER]`** upon drill completion immediately serves a fresh set of high-density practice words for that same key!
* **📋 Confusion Matrix Table:**
  * **TARGET:** The letter you were supposed to type.
  * **ERRORS (ERR/PRESSES):** Number of typos vs total times pressed, formatted as `10 (10/57)`.
  * **ACCURACY:** Precision percentage for that specific key.
  * **MISTYPED WITH (COUNT):** Exactly which keys your fingers accidentally hit (e.g. `'e' (8x), 's' (2x)`).
* **🎯 Practice Weak Keys [ENTER / F2]:** Generates a custom practice session filled with words specifically containing your most mistyped letters!
* **🔄 Scope Toggle [F1]:** Switch between your current session's mistakes and all-time persistent stats saved in `~/.config/ttyping/mistakes.json`.
* **🧹 Clear Stats [F3]:** Reset your mistake history whenever you want to measure fresh progress.

---

## 🕹️ Mode Selection

1. **🖱️ Mouse:** Click directly on `[ 1: ⚡ Sprint ]`, `[ 2: ♾️ Endless ]`, `[ 3: 🖐️ Tutor ]`, or `[ 4: 📊 Error Board ]` on the top bar, or click any table row / action button on the Board.
2. **⌨️ Keyboard:**
   * **`1` / `2` / `3` / `4`:** Switch directly to Sprint, Endless, Tutor, or Error Board mode.
   * **`TAB`:** Cycle through all modes (`Sprint` ➔ `Endless` ➔ `Tutor` ➔ `Board`).
   * **`ENTER` / `F2`:** Advance to next drill in Tutor mode.
   * **On Error Board:**
      * **Press ANY key on physical keyboard (e.g. `A`, `D`, `E`, `Space`):** Highlights that key in the list and shows its mistake count vs attempts `(10/57)`.
      * **`↑` / `↓`:** Navigate and highlight keys through the list.
      * **`ENTER`:** Practice words densely packed with the highlighted key (or practice top weak keys if none highlighted).
      * **`Backspace` / `ESC`:** Clear key highlight and return to overall summary.
      * **`F1`:** Toggle between Session and All-Time stats.
      * **`F2`:** Practice top weak keys drill.
      * **`F3` / `Delete`:** Clear mistake statistics.
      * **`PgUp` / `PgDn`:** Scroll through the mistake table.
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
