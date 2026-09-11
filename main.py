#!/usr/bin/env python3
"""
Terminal Typing Game (ttyping)
A responsive terminal typing game featuring real-time word streaming,
faded ghost/target words, live WPM, CPM, and accuracy tracking.
"""

import sys
import time
import random
import curses

# Common English and programming words for the typing stream
WORD_POOL = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "any", "these", "give", "day", "most", "us", "code", "game", "system",
    "terminal", "type", "fast", "speed", "test", "run", "key", "press",
    "screen", "world", "write", "read", "build", "play", "great", "cool",
    "light", "line", "word", "hand", "mind", "learn", "quick", "clean",
    "create", "focus", "flow", "open", "input", "start", "stop", "power"
]

QUOTES = [
    "The quick brown fox jumps over the lazy dog.",
    "Talk is cheap. Show me the code.",
    "First, solve the problem. Then, write the code.",
    "Simplicity is the soul of efficiency.",
    "Programs must be written for people to read, and only incidentally for machines to execute.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "In programming, the best code is no code at all.",
    "Experience is the name everyone gives to their mistakes.",
    "Knowledge is power, but practice makes perfect."
]

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"

class WordTypingGame:
    def __init__(self, words=None, mode="WORDS"):
        self.mode = mode
        self.preset_words = words
        self.reset()

    def reset(self):
        if self.preset_words:
            self.words = list(self.preset_words)
        elif self.mode == "WORDS":
            self.words = random.sample(WORD_POOL, 35)
        elif self.mode == "QUOTES":
            quote = random.choice(QUOTES)
            self.words = quote.split()
        else:
            self.words = []

        self.current_word_idx = 0
        self.current_input = ""
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.correct_keystrokes = 0
        self.word_results = {}  # idx -> True (correct) / False (incorrect)
        self.completed = False

    def add_char(self, char):
        if self.completed:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1

        if self.mode in ("WORDS", "QUOTES"):
            if self.current_word_idx < len(self.words):
                target_word = self.words[self.current_word_idx]
                target_char_idx = len(self.current_input)
                if target_char_idx < len(target_word) and char == target_word[target_char_idx]:
                    self.correct_keystrokes += 1
                self.current_input += char
        else:
            # Free typing mode
            self.current_input += char
            self.correct_keystrokes += 1

    def handle_space(self):
        if self.completed or self.mode not in ("WORDS", "QUOTES"):
            return

        if not self.current_input:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1
        target_word = self.words[self.current_word_idx]
        is_match = (self.current_input == target_word)
        if is_match:
            self.correct_keystrokes += 1

        self.word_results[self.current_word_idx] = is_match
        self.current_word_idx += 1
        self.current_input = ""

        if self.current_word_idx >= len(self.words):
            self.completed = True
            self.end_time = time.time()

    def backspace(self):
        if self.completed:
            return
        if self.current_input:
            self.current_input = self.current_input[:-1]
        elif self.current_word_idx > 0 and self.mode in ("WORDS", "QUOTES"):
            # Allow backspacing into previous word if it was marked incorrect
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

        # Completed words chars + current input chars
        completed_chars = sum(len(self.words[i]) + 1 for i in range(self.current_word_idx))
        total_typed_chars = completed_chars + len(self.current_input)

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
            "total_words": len(self.words),
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

def run_game(stdscr, custom_text=None):
    try:
        curses.curs_set(1)
    except curses.error:
        pass

    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Color configuration
    c_cyan = c_green = c_red = c_yellow = c_faded = c_bold_white = 0
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
            curses.init_pair(5, curses.COLOR_YELLOW, -1)
            curses.init_pair(6, curses.COLOR_WHITE, -1)

            # High quality faded color (dark gray)
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
            c_bold_white = curses.color_pair(6) | curses.A_BOLD
        except curses.error:
            pass

    # Default fallback for faded text
    if not c_faded:
        c_faded = curses.A_DIM

    preset = custom_text.split() if custom_text else None
    game = WordTypingGame(words=preset, mode="WORDS" if not preset else "CUSTOM")
    last_stats = None

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 12 or max_x < 50:
            safe_addstr(stdscr, 1, 2, "Please enlarge terminal window...", curses.A_BOLD)
            stdscr.refresh()
            time.sleep(0.1)
            try:
                ch = stdscr.getch()
                if ch in (27, 3):
                    break
            except curses.error:
                pass
            continue

        stats = game.get_stats()
        last_stats = stats

        # Top Header Banner
        header = " TERMINAL TYPING GAME "
        safe_addstr(stdscr, 0, (max_x - len(header)) // 2, header, curses.A_BOLD | c_cyan)
        safe_addstr(stdscr, 1, 2, "═" * (max_x - 4), c_cyan)

        # Mode & Live Stats Bar
        mode_badge = f" {game.mode} "
        safe_addstr(stdscr, 2, 2, mode_badge, curses.A_REVERSE | c_yellow)

        time_str = f"⏱ Time: {format_time(stats['elapsed'])}"
        wpm_str = f"⚡ WPM: {stats['wpm']}"
        cpm_str = f"CPM: {stats['cpm']}"
        acc_str = f"Acc: {stats['accuracy']}%"
        prog_str = f"Word: {stats['words_completed']}/{stats['total_words']}"

        stat_bar = f"{time_str}   {wpm_str}   {cpm_str}   {acc_str}   {prog_str}"
        safe_addstr(stdscr, 2, 14, stat_bar, curses.A_BOLD)
        safe_addstr(stdscr, 3, 2, "─" * (max_x - 4), c_faded)

        # Word stream area with faded upcoming words
        start_row = 5
        wrap_width = max(30, max_x - 8)
        padding_left = 4

        # Calculate word wrapping and coordinates
        lines = []
        current_line = []
        current_len = 0
        word_positions = {}

        for idx, w in enumerate(game.words):
            w_len = len(w) + 1  # word length plus trailing space
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

        # Determine scroll offset so current word is always visible on line 1 or 2
        active_row = word_positions.get(game.current_word_idx, (0, 0))[0]
        scroll_offset = max(0, active_row - 1)
        visible_lines = min(max_y - 9, len(lines) - scroll_offset)

        cursor_y = start_row
        cursor_x = padding_left

        # Render visible word lines
        for line_idx in range(scroll_offset, scroll_offset + visible_lines):
            screen_y = start_row + (line_idx - scroll_offset)
            if line_idx >= len(lines):
                break

            line_items = lines[line_idx]
            for w_idx, w_text in line_items:
                w_row, w_col = word_positions[w_idx]
                screen_x = padding_left + w_col

                if w_idx < game.current_word_idx:
                    # Completed word
                    is_correct = game.word_results.get(w_idx, True)
                    color = c_green if is_correct else c_red
                    safe_addstr(stdscr, screen_y, screen_x, w_text, color)
                    safe_addstr(stdscr, screen_y, screen_x + len(w_text), " ", c_faded)

                elif w_idx == game.current_word_idx:
                    # Current active word being typed
                    curr_input = game.current_input
                    typed_len = len(curr_input)
                    target_len = len(w_text)

                    # Characters already typed
                    for char_idx in range(typed_len):
                        draw_x = screen_x + char_idx
                        if char_idx < target_len:
                            if curr_input[char_idx] == w_text[char_idx]:
                                safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_green | curses.A_BOLD)
                            else:
                                safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_red | curses.A_UNDERLINE | curses.A_BOLD)
                        else:
                            # Overflow characters beyond word length
                            safe_addstr(stdscr, screen_y, draw_x, curr_input[char_idx], c_red | curses.A_BOLD)

                    # Remaining untyped characters of current word (FADED)
                    for char_idx in range(typed_len, target_len):
                        draw_x = screen_x + char_idx
                        safe_addstr(stdscr, screen_y, draw_x, w_text[char_idx], c_faded)

                    # Space after current word (FADED)
                    trailing_space_x = screen_x + max(typed_len, target_len)
                    safe_addstr(stdscr, screen_y, trailing_space_x, " ", c_faded)

                    # Position cursor right after the typed character
                    cursor_y = screen_y
                    cursor_x = screen_x + typed_len

                else:
                    # Upcoming words ("another word but with a little bit faded")
                    safe_addstr(stdscr, screen_y, screen_x, w_text, c_faded)
                    safe_addstr(stdscr, screen_y, screen_x + len(w_text), " ", c_faded)

        # Completion Banner
        if game.completed:
            congrats = "🎉 Round Finished! Press [ENTER] for new words, or [ESC] to view final stats."
            safe_addstr(stdscr, start_row + visible_lines + 2, 4, congrats, c_yellow | curses.A_BOLD)

        # Bottom Bar & Controls
        footer_y = max_y - 2
        safe_addstr(stdscr, footer_y - 1, 2, "─" * (max_x - 4), c_faded)
        controls = "[ESC] Quit   [Space] Next Word   [Backspace] Delete   [Ctrl+R] Reset   [TAB] Mode"
        if game.completed:
            controls = "[ENTER] New Round   " + controls
        safe_addstr(stdscr, footer_y, 4, controls, c_cyan)

        # Move terminal cursor to current typing position
        try:
            if 0 <= cursor_y < max_y and 0 <= cursor_x < max_x:
                stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass

        stdscr.refresh()

        # Non-blocking input loop
        try:
            ch = stdscr.getch()
        except curses.error:
            ch = -1

        if ch == -1:
            time.sleep(0.02)
            continue

        # Handle user input
        if ch in (27, 3):  # ESC or Ctrl+C
            break
        elif ch == 9:  # TAB -> Switch mode
            new_mode = "QUOTES" if game.mode == "WORDS" else "WORDS"
            game.mode = new_mode
            game.reset()
        elif ch in (18, 263, curses.KEY_F5):  # Ctrl+R or F5
            game.reset()
        elif ch in (curses.KEY_BACKSPACE, 127, 8, ord('\b')):
            game.backspace()
        elif ch == 32:  # Spacebar -> advances to next word
            game.handle_space()
        elif ch in (10, 13, curses.KEY_ENTER):
            if game.completed:
                game.reset()
        elif 32 < ch <= 126:  # Printable ASCII characters
            game.add_char(chr(ch))

    return last_stats

def main():
    custom_text = None
    if len(sys.argv) > 1:
        custom_text = " ".join(sys.argv[1:])

    try:
        final_stats = curses.wrapper(run_game, custom_text)
    except KeyboardInterrupt:
        final_stats = None

    # Print clean post-game exit summary to terminal
    print("\n" + "=" * 48)
    print("           TERMINAL TYPING GAME           ")
    print("=" * 48)
    if final_stats:
        print(f"  ⏱  Time Elapsed     : {format_time(final_stats['elapsed'])}")
        print(f"  📝 Words Completed  : {final_stats['words_completed']} / {final_stats['total_words']}")
        print(f"  ⚡ Typing Speed     : {final_stats['wpm']} WPM ({final_stats['cpm']} CPM)")
        print(f"  🎯 Accuracy         : {final_stats['accuracy']}%")
        print(f"  ⌨️  Keystrokes      : {final_stats['keystrokes']}")
    print("=" * 48)
    print("Thanks for playing! Run 'ttyping' anytime to play again.\n")

if __name__ == "__main__":
    main()
