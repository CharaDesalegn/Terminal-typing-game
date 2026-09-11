#!/usr/bin/env python3
"""
Terminal Typing Game (ttyping)
A lightweight, responsive terminal typing speed and practice game.
"""

import sys
import time
import random
import curses

QUOTES = [
    "The quick brown fox jumps over the lazy dog.",
    "Talk is cheap. Show me the code.",
    "First, solve the problem. Then, write the code.",
    "Simplicity is the soul of efficiency.",
    "Programs must be written for people to read, and only incidentally for machines to execute.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "In programming, the best code is no code at all.",
    "Experience is the name everyone gives to their mistakes.",
    "Knowledge is power, but practice makes perfect.",
    "Stay hungry, stay foolish."
]

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"

class TypingGame:
    def __init__(self, custom_text=None):
        self.custom_text = custom_text
        self.mode = "CHALLENGE" if custom_text else "FREE"
        self.reset()

    def reset(self):
        self.typed_chars = []
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.mistakes = 0
        self.completed = False

        if self.mode == "CHALLENGE":
            if self.custom_text:
                self.target_text = self.custom_text
            else:
                self.target_text = random.choice(QUOTES)
        else:
            self.target_text = ""

    def toggle_mode(self):
        self.mode = "CHALLENGE" if self.mode == "FREE" else "FREE"
        self.reset()

    def next_challenge(self):
        if not self.custom_text:
            choices = [q for q in QUOTES if q != self.target_text]
            self.target_text = random.choice(choices) if choices else random.choice(QUOTES)
        self.reset()

    def add_char(self, char):
        if self.completed:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1

        if self.mode == "CHALLENGE":
            expected_idx = len(self.typed_chars)
            if expected_idx < len(self.target_text):
                expected_char = self.target_text[expected_idx]
                if char != expected_char:
                    self.mistakes += 1
                self.typed_chars.append(char)
                if len(self.typed_chars) == len(self.target_text):
                    self.completed = True
                    self.end_time = time.time()
        else:
            self.typed_chars.append(char)

    def backspace(self):
        if self.completed:
            return
        if self.typed_chars:
            self.typed_chars.pop()

    def get_elapsed_time(self):
        if self.start_time is None:
            return 0.0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_stats(self):
        elapsed = self.get_elapsed_time()
        minutes = elapsed / 60.0 if elapsed > 0 else 0.0

        num_chars = len(self.typed_chars)
        text = "".join(self.typed_chars)
        words = len(text.split())

        if minutes > 0:
            wpm = (num_chars / 5.0) / minutes
            cpm = num_chars / minutes
        else:
            wpm = 0.0
            cpm = 0.0

        if self.mode == "CHALLENGE":
            correct_count = sum(
                1 for i, c in enumerate(self.typed_chars)
                if i < len(self.target_text) and c == self.target_text[i]
            )
            accuracy = (correct_count / self.total_keystrokes * 100.0) if self.total_keystrokes > 0 else 100.0
        else:
            accuracy = 100.0

        return {
            "elapsed": elapsed,
            "wpm": round(wpm, 1),
            "cpm": round(cpm, 1),
            "chars": num_chars,
            "words": words,
            "accuracy": round(accuracy, 1),
            "completed": self.completed
        }

def safe_addstr(stdscr, y, x, text, attr=0):
    """Safely write to curses screen within bounds without crashing on window edges."""
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

    # Initialize colors if terminal supports them
    c_cyan = c_green = c_red = c_yellow = c_gray = c_dim = 0
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
            curses.init_pair(4, curses.COLOR_YELLOW, -1)
            curses.init_pair(5, curses.COLOR_WHITE, -1)
            c_cyan = curses.color_pair(1)
            c_green = curses.color_pair(2)
            c_red = curses.color_pair(3)
            c_yellow = curses.color_pair(4)
            c_white = curses.color_pair(5)
            c_dim = c_white | curses.A_DIM
        except curses.error:
            pass

    game = TypingGame(custom_text)
    last_stats = None

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 12 or max_x < 50:
            safe_addstr(stdscr, 1, 2, "Please expand terminal window...", curses.A_BOLD)
            stdscr.refresh()
            time.sleep(0.1)
            try:
                ch = stdscr.getch()
                if ch in (27, 3):  # ESC or Ctrl+C
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
        mode_str = f" Mode: {game.mode} "
        safe_addstr(stdscr, 2, 2, mode_str, curses.A_REVERSE | (c_yellow if game.mode == 'FREE' else c_green))

        time_str = f"⏱ Time: {format_time(stats['elapsed'])}"
        wpm_str = f"⚡ WPM: {stats['wpm']}"
        cpm_str = f"CPM: {stats['cpm']}"
        chars_str = f"Chars: {stats['chars']}"
        words_str = f"Words: {stats['words']}"
        
        stat_line = f"{time_str}   {wpm_str}   {cpm_str}   {chars_str}   {words_str}"
        if game.mode == "CHALLENGE":
            stat_line += f"   Acc: {stats['accuracy']}%"

        safe_addstr(stdscr, 2, 18, stat_line, curses.A_BOLD)
        safe_addstr(stdscr, 3, 2, "─" * (max_x - 4), c_dim)

        # Content Area
        start_row = 5
        cursor_y = start_row
        cursor_x = 4

        if game.mode == "FREE":
            safe_addstr(stdscr, 4, 4, "Type anything you want below:", c_yellow | curses.A_BOLD)

            # Render typed text with line wrapping
            text = "".join(game.typed_chars)
            wrap_width = max(20, max_x - 8)

            curr_y = start_row
            curr_x = 4
            paragraphs = text.split("\n")
            for p_idx, paragraph in enumerate(paragraphs):
                if p_idx > 0:
                    curr_y += 1
                    curr_x = 4

                idx = 0
                if len(paragraph) == 0:
                    continue

                while idx < len(paragraph):
                    chunk = paragraph[idx:idx + wrap_width]
                    if curr_y < max_y - 4:
                        safe_addstr(stdscr, curr_y, curr_x, chunk, curses.A_BOLD)
                    curr_x = 4 + len(chunk)
                    idx += wrap_width
                    if idx < len(paragraph):
                        curr_y += 1
                        curr_x = 4

            cursor_y = curr_y
            cursor_x = curr_x

            # Placeholder prompt if nothing typed yet
            if not game.typed_chars:
                safe_addstr(stdscr, start_row, 4, "Start typing here...", c_dim)
                cursor_y = start_row
                cursor_x = 4

        elif game.mode == "CHALLENGE":
            safe_addstr(stdscr, 4, 4, "Target Text (type matching characters):", c_green | curses.A_BOLD)

            target = game.target_text
            typed = "".join(game.typed_chars)
            wrap_width = max(20, max_x - 8)

            row = start_row
            col = 4

            for i, ch in enumerate(target):
                # Calculate current position
                if i > 0 and (i % wrap_width) == 0:
                    row += 1
                    col = 4

                if row >= max_y - 4:
                    break

                if i < len(typed):
                    if typed[i] == ch:
                        safe_addstr(stdscr, row, col, ch, c_green | curses.A_BOLD)
                    else:
                        safe_addstr(stdscr, row, col, typed[i], c_red | curses.A_UNDERLINE | curses.A_BOLD)
                else:
                    safe_addstr(stdscr, row, col, ch, c_dim)

                if i == len(typed):
                    cursor_y = row
                    cursor_x = col

                col += 1

            if len(typed) >= len(target):
                cursor_y = row
                cursor_x = col

            if game.completed:
                congrats = "🎉 Challenge Completed! Press [ENTER] for next, or [ESC] to exit."
                safe_addstr(stdscr, row + 2, 4, congrats, c_yellow | curses.A_BOLD)

        # Bottom Bar & Controls
        footer_y = max_y - 2
        safe_addstr(stdscr, footer_y - 1, 2, "─" * (max_x - 4), c_dim)
        controls = "[ESC] Quit   [TAB] Switch Mode   [Ctrl+R] Reset   [Backspace] Delete"
        if game.completed and game.mode == "CHALLENGE":
            controls = "[ENTER] Next Challenge   " + controls
        safe_addstr(stdscr, footer_y, 4, controls, c_cyan)

        # Place the physical terminal cursor at active typing position
        try:
            if 0 <= cursor_y < max_y and 0 <= cursor_x < max_x:
                stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass

        stdscr.refresh()

        # Handle input with non-blocking timeout
        try:
            ch = stdscr.getch()
        except curses.error:
            ch = -1

        if ch == -1:
            time.sleep(0.02)
            continue

        # Check keys
        if ch in (27, 3):  # ESC or Ctrl+C
            break
        elif ch == 9:  # TAB -> toggle mode
            game.toggle_mode()
        elif ch in (18, 263, curses.KEY_F5):  # Ctrl+R or F5 -> reset
            game.reset()
        elif ch in (curses.KEY_BACKSPACE, 127, 8, ord('\b')):
            game.backspace()
        elif ch in (10, 13, curses.KEY_ENTER):  # Enter key
            if game.completed and game.mode == "CHALLENGE":
                game.next_challenge()
            elif game.mode == "FREE":
                game.add_char("\n")
        elif 32 <= ch <= 126:  # Printable ASCII characters
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

    # Print clean exit summary to terminal
    print("\n" + "=" * 48)
    print("           TERMINAL TYPING GAME           ")
    print("=" * 48)
    if final_stats:
        print(f"  ⏱  Time Elapsed     : {format_time(final_stats['elapsed'])}")
        print(f"  📝 Words Typed      : {final_stats['words']}")
        print(f"  ⌨️  Characters Typed : {final_stats['chars']}")
        print(f"  ⚡ Typing Speed     : {final_stats['wpm']} WPM ({final_stats['cpm']} CPM)")
        if "accuracy" in final_stats:
            print(f"  🎯 Accuracy         : {final_stats['accuracy']}%")
    print("=" * 48)
    print("Thanks for playing! Run 'ttyping' anytime to play again.\n")

if __name__ == "__main__":
    main()
