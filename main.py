#!/usr/bin/env python3
"""
Terminal Typing Game (ttyping)
Features:
- Mode 1 (Sprint): Simple sentences to test your WPM in 1-2 minutes.
- Mode 2 (Endless): Continuous endless practice with complex vocabulary, code syntax, and symbol keys.
- Interactive Top Bar: Clickable via mouse and selectable with keys [1], [2], or [TAB].
- CLI Flags: --sprint (-1), --endless (-2), or custom practice text.
- Monkeytype-style faded ghost words.
"""

import sys
import time
import random
import argparse
import curses

# Mode 1: Natural, everyday English sentences for fast 1-2 minute WPM benchmarking
SPRINT_SENTENCES = [
    "Success is not final, failure is not fatal: it is the courage to continue that counts. Keep your focus forward and learn from every step.",
    "The early morning sun broke through the clouds, warming the quiet city streets as people slowly began their daily routines with coffee.",
    "Reading books every day opens doors to new worlds, sharpens your critical thinking skills, and helps you communicate with confidence.",
    "Technology is at its best when it brings people together and solves problems that genuinely matter in our everyday lives.",
    "Learning to code is like gaining a superpower. With just a keyboard and your imagination, you can build tools that change the world.",
    "A journey of a thousand miles begins with a single step. Be patient with your progress and celebrate the small victories along the way.",
    "Simplicity is not about having less, it is about making room for what truly matters in your work and your thoughts.",
    "The best way to predict the future is to create it. Stay curious, ask good questions, and never stop exploring new possibilities.",
    "Great things are not done by impulse, but by a series of small things brought together over time through steady dedication.",
    "Clear writing usually reflects clear thinking. When you take the time to organize your ideas, others will understand your vision."
]

# Mode 2: Advanced vocabulary, technical jargon, mixed casing, and symbols to train all fingers and keys
COMPLEX_WORDS_POOL = [
    # Complex multisyllabic vocabulary
    "extraordinary", "juxtaposition", "serendipity", "unprecedented", "crystallization",
    "idiosyncratic", "equilibrium", "heterogeneous", "magnificent", "comprehensive",
    "susceptibility", "counterintuitive", "acknowledgement", "quintessential", "resilience",
    "infrastructure", "philosophical", "metamorphosis", "synchronization", "perspicacity",
    "conscientious", "disproportionate", "incompatibility", "characteristically", "anachronism",
    "ubiquitous", "circumlocution", "idiosyncrasy", "reconnaissance", "photosynthesis",
    # Computer science & software engineering
    "asynchronous", "polymorphism", "concurrency", "cryptography", "microservices",
    "virtualization", "encapsulation", "reconciliation", "authentication", "authorization",
    "multithreading", "serialization", "containerization", "backpropagation", "hyperparameter",
    "orchestration", "deterministic", "subroutines", "idempotent", "decoupling",
    "observability", "maintainability", "declarative", "imperative", "distributed",
    "algorithm", "bandwidth", "cache_miss", "deadlock", "event_loop",
    # Key-reaching constructs (symbols, underscores, casing, dots)
    "calculate_sum()", "UserAuth.verify()", "data_stream.pipe()", "item_list[index]",
    "config_options", "max_capacity_limit", "response.status_code", "process_id#99",
    "lambda_handler()", "matrix_multiply()", "format_output()", "query_param:value",
    "is_valid_token?", "read_buffer_bytes()", "retry_interval_ms", "get_connection_pool()",
    "Vector3D.normalize()", "filter_records()", "total_count+=1", "error_message.strip()",
    "TypeScript", "PostgreSQL", "Kubernetes", "WebSockets", "JavaScript"
]

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"

class TypingEngine:
    def __init__(self, mode="SPRINT", custom_text=None):
        self.mode = mode
        self.custom_text = custom_text
        self.reset()

    def reset(self):
        if self.custom_text:
            self.words = self.custom_text.split()
        elif self.mode == "SPRINT":
            sentence = random.choice(SPRINT_SENTENCES)
            self.words = sentence.split()
        elif self.mode == "ENDLESS":
            self.words = random.sample(COMPLEX_WORDS_POOL, min(35, len(COMPLEX_WORDS_POOL)))
        else:
            self.words = []

        self.current_word_idx = 0
        self.current_input = ""
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.correct_keystrokes = 0
        self.word_results = {}  # idx -> bool (is_correct)
        self.streak = 0
        self.completed = False

    def switch_mode(self, new_mode):
        if self.mode != new_mode:
            self.mode = new_mode
            self.custom_text = None
            self.reset()

    def add_char(self, char):
        if self.completed:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1

        if self.current_word_idx < len(self.words):
            target_word = self.words[self.current_word_idx]
            target_char_idx = len(self.current_input)
            if target_char_idx < len(target_word) and char == target_word[target_char_idx]:
                self.correct_keystrokes += 1
            self.current_input += char

    def handle_space(self):
        if self.completed or not self.current_input:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1
        target_word = self.words[self.current_word_idx]
        is_match = (self.current_input == target_word)

        if is_match:
            self.correct_keystrokes += 1
            self.streak += 1
        else:
            self.streak = 0

        self.word_results[self.current_word_idx] = is_match
        self.current_word_idx += 1
        self.current_input = ""

        # Endless Mode: Dynamically stream new complex words without end
        if self.mode == "ENDLESS":
            if self.current_word_idx > len(self.words) - 15:
                next_batch = random.sample(COMPLEX_WORDS_POOL, 20)
                self.words.extend(next_batch)
        else:
            # Sprint Mode: Finish when all words in the sentence are typed
            if self.current_word_idx >= len(self.words):
                self.completed = True
                self.end_time = time.time()

    def backspace(self):
        if self.completed:
            return
        if self.current_input:
            self.current_input = self.current_input[:-1]
        elif self.current_word_idx > 0:
            # Backspace into previous word if it was marked incorrect
            prev_idx = self.current_word_idx - 1
            if not self.word_results.get(prev_idx, True):
                self.current_word_idx = prev_idx
                self.current_input = self.words[prev_idx]
                del self.word_results[prev_idx]

    def get_elapsed_time(self):
        if self.start_time is None:
            return 0.0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_stats(self):
        elapsed = self.get_elapsed_time()
        minutes = elapsed / 60.0 if elapsed > 0 else 0.0

        if minutes > 0:
            wpm = (self.correct_keystrokes / 5.0) / minutes
            cpm = self.correct_keystrokes / minutes
        else:
            wpm = 0.0
            cpm = 0.0

        accuracy = (self.correct_keystrokes / self.total_keystrokes * 100.0) if self.total_keystrokes > 0 else 100.0

        return {
            "elapsed": elapsed,
            "wpm": round(wpm, 1),
            "cpm": round(cpm, 1),
            "accuracy": round(accuracy, 1),
            "words_completed": self.current_word_idx,
            "total_words": len(self.words) if self.mode != "ENDLESS" else "∞",
            "streak": self.streak,
            "completed": self.completed,
            "keystrokes": self.total_keystrokes
        }

def safe_addstr(stdscr, y, x, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x >= max_x:
        return
    max_len = max_x - x
    if max_len <= 0:
        return
    try:
        stdscr.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass

def run_game(stdscr, initial_mode="SPRINT", custom_text=None):
    try:
        curses.curs_set(1)
    except curses.error:
        pass

    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Enable mouse tracking for interactive top-bar clicks
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    except curses.error:
        pass

    # Colors
    c_cyan = c_green = c_red = c_yellow = c_faded = c_white = 0
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
            curses.init_pair(5, curses.COLOR_YELLOW, -1)
            curses.init_pair(6, curses.COLOR_WHITE, -1)

            if curses.COLORS >= 256:
                curses.init_pair(4, 244, -1)
                c_faded = curses.color_pair(4)
            else:
                curses.init_pair(4, curses.COLOR_BLACK, -1)
                c_faded = curses.color_pair(4) | curses.A_BOLD | curses.A_DIM

            c_cyan = curses.color_pair(1)
            c_green = curses.color_pair(2)
            c_red = curses.color_pair(3)
            c_yellow = curses.color_pair(5)
            c_white = curses.color_pair(6)
        except curses.error:
            pass

    if not c_faded:
        c_faded = curses.A_DIM

    engine = TypingEngine(mode=initial_mode, custom_text=custom_text)
    last_stats = None

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 13 or max_x < 55:
            safe_addstr(stdscr, 1, 2, "Please expand terminal window to play...", curses.A_BOLD)
            stdscr.refresh()
            time.sleep(0.1)
            try:
                ch = stdscr.getch()
                if ch in (27, 3):
                    break
            except curses.error:
                pass
            continue

        stats = engine.get_stats()
        last_stats = stats

        # ==========================================
        # 1. TOP BAR (Clickable with mouse or 1/2)
        # ==========================================
        btn_sprint = "[ 1: ⚡ Sprint (WPM Test) ]"
        btn_endless = "[ 2: ♾️ Endless (Mastery) ]"

        top_buttons = []
        cur_btn_x = 2

        # Button 1: Sprint
        is_sprint = (engine.mode == "SPRINT")
        sprint_attr = (curses.A_REVERSE | curses.A_BOLD | c_green) if is_sprint else (curses.A_BOLD | c_white)
        safe_addstr(stdscr, 0, cur_btn_x, btn_sprint, sprint_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_sprint), "SPRINT"))
        cur_btn_x += len(btn_sprint) + 2

        # Button 2: Endless
        is_endless = (engine.mode == "ENDLESS")
        endless_attr = (curses.A_REVERSE | curses.A_BOLD | c_yellow) if is_endless else (curses.A_BOLD | c_white)
        safe_addstr(stdscr, 0, cur_btn_x, btn_endless, endless_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_endless), "ENDLESS"))

        # Right-aligned exit hint
        exit_label = "[ESC: Exit]"
        safe_addstr(stdscr, 0, max_x - len(exit_label) - 2, exit_label, c_cyan)

        # Header divider
        safe_addstr(stdscr, 1, 2, "═" * (max_x - 4), c_cyan)

        # ==========================================
        # 2. STATS BAR
        # ==========================================
        time_str = f"⏱ Time: {format_time(stats['elapsed'])}"
        wpm_str = f"⚡ WPM: {stats['wpm']}"
        cpm_str = f"CPM: {stats['cpm']}"
        acc_str = f"Acc: {stats['accuracy']}%"
        
        if engine.mode == "ENDLESS":
            prog_str = f"Words: {stats['words_completed']} | Streak: {stats['streak']}"
        else:
            prog_str = f"Words: {stats['words_completed']}/{stats['total_words']}"

        stat_bar = f"{time_str}    {wpm_str}    {cpm_str}    {acc_str}    {prog_str}"
        safe_addstr(stdscr, 2, 4, stat_bar, curses.A_BOLD)
        safe_addstr(stdscr, 3, 2, "─" * (max_x - 4), c_faded)

        # ==========================================
        # 3. WORD STREAM & FADED WORDS AREA
        # ==========================================
        start_row = 5
        wrap_width = max(30, max_x - 8)
        padding_left = 4

        # Wrap words into display rows
        lines = []
        current_line = []
        current_len = 0
        word_positions = {}

        for idx, w in enumerate(engine.words):
            w_len = len(w) + 1
            if current_len + len(w) > wrap_width and current_line:
                lines.append(current_line)
                current_line = []
                current_len = 0

            row = len(lines)
            col = current_len
            word_positions[idx] = (row, col)
            current_line.append((idx, w))
            current_len += w_len

        if current_line:
            lines.append(current_line)

        # Smooth vertical scroll to keep current word centered
        active_row = word_positions.get(engine.current_word_idx, (0, 0))[0]
        scroll_offset = max(0, active_row - 1)
        visible_lines = min(max_y - 9, len(lines) - scroll_offset)

        cursor_y = start_row
        cursor_x = padding_left

        for line_idx in range(scroll_offset, scroll_offset + visible_lines):
            screen_y = start_row + (line_idx - scroll_offset)
            if line_idx >= len(lines):
                break

            for w_idx, w_text in lines[line_idx]:
                w_row, w_col = word_positions[w_idx]
                screen_x = padding_left + w_col

                if w_idx < engine.current_word_idx:
                    # Completed words
                    is_correct = engine.word_results.get(w_idx, True)
                    color = c_green if is_correct else c_red
                    safe_addstr(stdscr, screen_y, screen_x, w_text, color)
                    safe_addstr(stdscr, screen_y, screen_x + len(w_text), " ", c_faded)

                elif w_idx == engine.current_word_idx:
                    # Current active word being typed
                    curr_input = engine.current_input
                    typed_len = len(curr_input)
                    target_len = len(w_text)

                    # Typed letters
                    for char_idx in range(typed_len):
                        draw_x = screen_x + char_idx
                        if char_idx < target_len:
                            if curr_input[char_idx] == w_text[char_idx]:
                                safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_green | curses.A_BOLD)
                            else:
                                safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_red | curses.A_UNDERLINE | curses.A_BOLD)
                        else:
                            # Extra letters beyond target length
                            safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_red | curses.A_BOLD)

                    # Untyped characters of current word (FADED)
                    for char_idx in range(typed_len, target_len):
                        draw_x = screen_x + char_idx
                        safe_addstr(stdscr, screen_y, draw_x, w_text[char_idx], c_faded)

                    # Trailing space (FADED)
                    trailing_space_x = screen_x + max(typed_len, target_len)
                    safe_addstr(stdscr, screen_y, trailing_space_x, " ", c_faded)

                    # Cursor position right after typed input
                    cursor_y = screen_y
                    cursor_x = screen_x + typed_len

                else:
                    # Upcoming words (ANOTHER WORD FADED)
                    safe_addstr(stdscr, screen_y, screen_x, w_text, c_faded)
                    safe_addstr(stdscr, screen_y, screen_x + len(w_text), " ", c_faded)

        # Completion Card (Sprint Mode)
        if engine.completed:
            card_y = min(max_y - 5, start_row + visible_lines + 1)
            congrats = f"🏆 Sprint Finished! Speed: {stats['wpm']} WPM | Accuracy: {stats['accuracy']}%"
            prompt = "Press [ENTER] for next sentence, [1] / [2] to change mode, or [ESC] to quit."
            safe_addstr(stdscr, card_y, 4, congrats, c_yellow | curses.A_BOLD)
            safe_addstr(stdscr, card_y + 1, 4, prompt, curses.A_BOLD)

        # ==========================================
        # 4. FOOTER & SHORTCUTS
        # ==========================================
        footer_y = max_y - 2
        safe_addstr(stdscr, footer_y - 1, 2, "─" * (max_x - 4), c_faded)
        controls = "[1/2 or Click] Switch Mode   [Space] Next Word   [Backspace] Delete   [Ctrl+R] Reset   [ESC] Exit"
        if engine.completed:
            controls = "[ENTER] Next Sentence   " + controls
        safe_addstr(stdscr, footer_y, 4, controls, c_cyan)

        # Place physical blinking cursor
        try:
            if 0 <= cursor_y < max_y and 0 <= cursor_x < max_x:
                stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass

        stdscr.refresh()

        # Event input handling
        try:
            ch = stdscr.getch()
        except curses.error:
            ch = -1

        if ch == -1:
            time.sleep(0.02)
            continue

        # Mouse click handling
        if ch == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                # Check top bar row (row 0)
                if my == 0 and (bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED)):
                    for x_start, x_end, target_mode in top_buttons:
                        if x_start <= mx <= x_end:
                            engine.switch_mode(target_mode)
                            break
            except curses.error:
                pass
            continue

        # Keyboard shortcuts
        if ch in (27, 3):  # ESC or Ctrl+C
            break
        elif ch == ord('1'):
            # Switch to Sprint mode if not already on it
            if engine.mode != "SPRINT":
                engine.switch_mode("SPRINT")
            else:
                engine.add_char('1')
        elif ch == ord('2'):
            # Switch to Endless mode if not already on it
            if engine.mode != "ENDLESS":
                engine.switch_mode("ENDLESS")
            else:
                engine.add_char('2')
        elif ch == 9:  # TAB -> toggle mode
            next_mode = "ENDLESS" if engine.mode == "SPRINT" else "SPRINT"
            engine.switch_mode(next_mode)
        elif ch in (18, 263, curses.KEY_F5):  # Ctrl+R or F5
            engine.reset()
        elif ch in (curses.KEY_BACKSPACE, 127, 8, ord('\b')):
            engine.backspace()
        elif ch == 32:  # Spacebar
            engine.handle_space()
        elif ch in (10, 13, curses.KEY_ENTER):
            if engine.completed:
                engine.reset()
        elif 32 < ch <= 126:
            engine.add_char(chr(ch))

    return last_stats, engine.mode

def main():
    parser = argparse.ArgumentParser(
        prog="ttyping",
        description="Terminal Typing Game - Sprint WPM testing & Endless key mastery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Modes:
  1: Sprint   - Simple, natural sentences you finish in 1-2 minutes to test your WPM.
  2: Endless  - Endless complex words, technical symbols, and tricky keys to build speed.

Interactive Controls:
  Click [1] or [2] on the Top Bar with your mouse, or press 1 / 2 on your keyboard!
"""
    )
    parser.add_argument("-1", "--sprint", action="store_true", help="Launch directly in Sprint Mode (1-2 min WPM test)")
    parser.add_argument("-2", "--endless", action="store_true", help="Launch directly in Endless Mode (complex words practice)")
    parser.add_argument("custom", nargs="*", help="Optional custom text or sentence to practice")

    args = parser.parse_args()

    mode = "SPRINT"
    if args.endless:
        mode = "ENDLESS"
    elif args.sprint:
        mode = "SPRINT"

    custom_text = " ".join(args.custom) if args.custom else None

    try:
        result = curses.wrapper(run_game, mode, custom_text)
        final_stats, final_mode = result if result else (None, mode)
    except KeyboardInterrupt:
        final_stats, final_mode = None, mode

    # Post-session summary
    print("\n" + "=" * 50)
    print("             TERMINAL TYPING SUMMARY              ")
    print("=" * 50)
    print(f"  🎮 Mode             : {final_mode}")
    if final_stats:
        print(f"  ⏱  Time Elapsed     : {format_time(final_stats['elapsed'])}")
        print(f"  📝 Words Completed  : {final_stats['words_completed']}")
        print(f"  ⚡ Typing Speed     : {final_stats['wpm']} WPM ({final_stats['cpm']} CPM)")
        print(f"  🎯 Accuracy         : {final_stats['accuracy']}%")
        print(f"  ⌨️  Total Keystrokes : {final_stats['keystrokes']}")
        if final_mode == "ENDLESS":
            print(f"  🔥 Best Streak      : {final_stats['streak']} words")
    print("=" * 50)
    print("Thanks for playing! Run 'ttyping' anytime to play again.\n")

if __name__ == "__main__":
    main()
