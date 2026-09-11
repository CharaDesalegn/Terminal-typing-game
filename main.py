#!/usr/bin/env python3
"""
Terminal Typing Game (ttyping)
Features:
- Prominent Whole-Word Visibility: Clear, bold typography with active whole-word highlighting.
- Spacious Centered Layout: Double line spacing, high-contrast colors, and generous margins.
- High-Contrast Palette: Crisp light gray for upcoming text, bright bold white for the active
  word, vibrant neon green for correct characters, and vivid bold red for errors.
- Character Precision: Space is treated just like any other key (never skips words).
- Mode 1 (Sprint): Simple sentences to test your WPM in 1-2 minutes.
- Mode 2 (Endless): Continuous practice with controlled difficulty pacing:
    * Comma / Full stop: once every ~35 words (<= 50 words)
    * Numbers: once every 100 words
    * Special characters / symbols: once every 200 words
    * All other words: arbitrary clean vocabulary
- Interactive Top Bar: Clickable via mouse and selectable with keys [1], [2], or [TAB].
- CLI Flags: --sprint (-1), --endless (-2), or custom practice text.
"""

import sys
import time
import random
import argparse
import curses

# Mode 1: Clean, natural English sentences for 1-2 minute WPM tests
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

# Mode 2 (Endless): Arbitrary English words (pure letters, varied lengths)
BASE_WORDS_POOL = [
    "system", "method", "network", "stream", "thread", "buffer", "server", "packet",
    "socket", "engine", "device", "screen", "cursor", "signal", "filter", "matrix",
    "vector", "string", "number", "symbol", "action", "result", "status", "target",
    "source", "window", "border", "layout", "canvas", "player", "reward", "domain",
    "record", "column", "header", "footer", "script", "binary", "branch", "commit",
    "origin", "master", "remote", "portal", "access", "secure", "cipher", "secret",
    "future", "memory", "syntax", "parser", "render", "update", "reload", "listen",
    "events", "notify", "prompt", "dialog", "option", "toggle", "button", "metric",
    "timing", "smooth", "energy", "flight", "vision", "nature", "planet", "cosmos",
    "galaxy", "season", "spring", "summer", "autumn", "winter", "forest", "valley",
    "canyon", "bridge", "castle", "island", "harbor", "beacon", "anchor", "summit",
    "shadow", "riddle", "wonder", "silence", "whisper", "journey", "courage", "balance",
    "clarity", "freedom", "passion", "harmony", "purpose", "triumph", "destiny", "horizon",
    "dynamic", "illuminate", "understand", "experience", "appreciate", "collaborate",
    "discipline", "coordinate", "articulate", "synthesize", "strengthen", "accelerate",
    "navigation", "generation", "foundation", "resolution", "connection", "expression",
    "reflection", "dedication", "innovation", "atmosphere", "temperature", "equilibrium",
    "resilience", "phenomenon", "leadership", "fellowship", "creativity", "curiosity",
    "simplicity", "efficiency", "confidence", "perseverance", "inspiration", "fascinating",
    "extraordinary", "magnificent", "comprehensive", "philosophical", "metamorphosis",
    "synchronization", "perspicacity", "serendipity", "unprecedented", "crystallization",
    "algorithm", "knowledge", "practice", "challenge", "discovery", "performance", "focus"
]

# Numbers: Appears once every 100 words
NUMBER_WORDS = [
    "100", "2026", "42", "365", "1984", "500", "24", "7", "1000",
    "version2", "level5", "page12", "top10", "stage3", "rank1",
    "step4", "room101", "route66", "year2030", "chapter8"
]

# Special characters and symbols: Appears once every 200 words
SYMBOL_WORDS = [
    "calculate_sum()", "UserAuth.verify()", "data_stream.pipe()", "item_list[index]",
    "lambda_handler()", "read_buffer_bytes()", "key:value", "total_count+=1",
    "process_id#99", "config_options", "Vector3D.normalize()", "format_output()",
    "is_valid_token?", "get_connection()", "print(\"hello\")", "result!=None"
]

# 2-row clean font for increased word visibility
FONT_2X = {
    'a': ['▄▀▄', '█▄█'], 'b': ['█▀▄', '█▄▀'], 'c': [' ▄▀▀', ' ▀▄▄'], 'd': ['▄▀█', '▀▄█'],
    'e': ['█▀▀', '▀▀▀'], 'f': ['▄█▀', ' █ '], 'g': ['▄▀█', ' ▀█'], 'h': ['█ █', '█▀█'],
    'i': ['█', '█'],     'j': ['  █', '▀▄▀'], 'k': ['█ ▄', '█▀ '], 'l': ['█ ', '▀▀'],
    'm': ['█▀█', '█ █'], 'n': ['█▀▄', '█ █'], 'o': ['▄▀▄', '▀▄▀'], 'p': ['█▀▄', '█▀ '],
    'q': ['▄▀█', '  ▀'], 'r': ['█▀▄', '█  '], 's': ['▄▀ ', ' ▀▄'], 't': ['▀█▀', ' █ '],
    'u': ['█ █', '▀▄▀'], 'v': ['█ █', ' ▀ '], 'w': ['█ █ █', '▀▄█▄▀'], 'x': ['▀▄▀', '▄▀▄'],
    'y': ['█ █', ' ▀█'], 'z': ['▀▀█', '█▀▀'],
    ' ': ['   ', '   '], '␣': ['   ', '▀▀▀'],
    '.': [' ', '▄'],     ',': [' ', '▀'],     ':': ['▄', '▄'],     ';': ['▄', '▀'],
    '-': ['▀▀', '  '],   '_': ['  ', '▀▀'],   '!': ['█', '▄'],     '?': ['▀█', ' ▄'],
    '(': ['▄▀', '▀▄'],   ')': ['▀▄', '▄▀'],   '[': ['█▀', '█▄'],   ']': ['▀█', '▄█'],
    '+': [' ▄ ', '▀█▀'], '=': ['▀▀', '▀▀'],   '/': [' ▄', '▄ '],   '\"': ['█ █', '   '],
    '\'': ['█', ' '],    '#': ['█▀█', '▀█▀'],
    '0': ['▄▀▄', '▀▄▀'], '1': ['▄█', ' █'],   '2': ['▀▀█', '█▀▀'], '3': ['▀▀█', '▀▀█'],
    '4': ['█ █', '▀▀█'], '5': ['█▀▀', '▀▀█'], '6': ['█▀▀', '█▄█'], '7': ['▀▀█', '  █'],
    '8': ['█▀█', '█▄█'], '9': ['█▀█', ' ▀█'],
}

def get_glyph(c):
    return FONT_2X.get(c.lower(), [c, ' '])

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"

class TypingEngine:
    def __init__(self, mode="SPRINT", custom_text=None):
        self.mode = mode
        self.custom_text = custom_text
        self.endless_word_counter = 0
        self.reset()

    def _generate_endless_word(self, index):
        word_num = index + 1
        if word_num % 200 == 0:
            return random.choice(SYMBOL_WORDS)
        elif word_num % 100 == 0:
            return random.choice(NUMBER_WORDS)

        base = random.choice(BASE_WORDS_POOL)
        if word_num % 35 == 0:
            punct = random.choice([",", "."])
            return base + punct

        return base

    def generate_endless_batch(self, count=35):
        words = []
        for _ in range(count):
            w = self._generate_endless_word(self.endless_word_counter)
            self.endless_word_counter += 1
            words.append(w)
        return " ".join(words)

    def reset(self):
        self.endless_word_counter = 0

        if self.custom_text:
            self.target_text = self.custom_text.strip()
        elif self.mode == "SPRINT":
            self.target_text = random.choice(SPRINT_SENTENCES)
        elif self.mode == "ENDLESS":
            self.target_text = self.generate_endless_batch(40)
        else:
            self.target_text = ""

        self.typed_chars = []
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
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
        self.typed_chars.append(char)

        if self.mode == "ENDLESS":
            if len(self.typed_chars) > len(self.target_text) - 120:
                more_words = " " + self.generate_endless_batch(25)
                self.target_text += more_words

        elif self.mode == "SPRINT":
            if len(self.typed_chars) >= len(self.target_text):
                self.completed = True
                self.end_time = time.time()

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

        correct_count = 0
        mistakes_count = 0

        for i, typed_ch in enumerate(self.typed_chars):
            if i < len(self.target_text):
                if typed_ch == self.target_text[i]:
                    correct_count += 1
                else:
                    mistakes_count += 1
            else:
                mistakes_count += 1

        if minutes > 0:
            wpm = (correct_count / 5.0) / minutes
            cpm = correct_count / minutes
        else:
            wpm = 0.0
            cpm = 0.0

        typed_len = len(self.typed_chars)
        accuracy = (correct_count / typed_len * 100.0) if typed_len > 0 else 100.0

        completed_words = 0
        current_text_typed = self.target_text[:typed_len]
        words_in_typed_part = current_text_typed.split(' ')
        if len(words_in_typed_part) > 1:
            completed_words = len(words_in_typed_part) - 1

        total_words = len(self.target_text.split(' ')) if self.mode != "ENDLESS" else "∞"

        return {
            "elapsed": elapsed,
            "wpm": round(wpm, 1),
            "cpm": round(cpm, 1),
            "accuracy": round(accuracy, 1),
            "correct_chars": correct_count,
            "mistakes": mistakes_count,
            "words_completed": completed_words,
            "total_words": total_words,
            "completed": self.completed,
            "keystrokes": self.total_keystrokes,
            "typed_len": typed_len,
            "target_len": len(self.target_text)
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

def build_char_positions(text, wrap_width):
    char_positions = {}
    words = text.split(' ')
    cur_row = 0
    cur_col = 0
    global_idx = 0

    for w_idx, word in enumerate(words):
        if cur_col + len(word) > wrap_width and cur_col > 0:
            cur_row += 1
            cur_col = 0

        for ch in word:
            if cur_col >= wrap_width:
                cur_row += 1
                cur_col = 0
            char_positions[global_idx] = (cur_row, cur_col)
            cur_col += 1
            global_idx += 1

        if w_idx < len(words) - 1:
            if cur_col >= wrap_width:
                cur_row += 1
                cur_col = 0
            char_positions[global_idx] = (cur_row, cur_col)
            cur_col += 1
            global_idx += 1

    return char_positions, cur_row + 1

def run_game(stdscr, initial_mode="SPRINT", custom_text=None):
    try:
        curses.curs_set(1)
    except curses.error:
        pass

    stdscr.nodelay(True)
    stdscr.keypad(True)

    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    except curses.error:
        pass

    # High-contrast, easy-to-see color palette
    c_cyan = c_green = c_red = c_yellow = c_faded = c_white = c_highlight = 0
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(5, curses.COLOR_YELLOW, -1)
            curses.init_pair(6, curses.COLOR_WHITE, -1)

            if curses.COLORS >= 256:
                # Vibrant 256 colors:
                # Color 46: Neon bright green
                # Color 196: Vivid red
                # Color 250: Crisp light slate gray (high contrast, clearly visible)
                # Color 226: Bright gold
                curses.init_pair(2, 46, -1)
                curses.init_pair(3, 196, -1)
                curses.init_pair(4, 250, -1)
                curses.init_pair(7, 226, -1)
            else:
                curses.init_pair(2, curses.COLOR_GREEN, -1)
                curses.init_pair(3, curses.COLOR_RED, -1)
                curses.init_pair(4, curses.COLOR_WHITE, -1)
                curses.init_pair(7, curses.COLOR_YELLOW, -1)

            c_cyan = curses.color_pair(1) | curses.A_BOLD
            c_green = curses.color_pair(2) | curses.A_BOLD
            c_red = curses.color_pair(3) | curses.A_BOLD
            c_faded = curses.color_pair(4) | curses.A_BOLD  # Crisp, readable light gray (bold)
            c_yellow = curses.color_pair(5) | curses.A_BOLD
            c_white = curses.color_pair(6) | curses.A_BOLD  # Bright bold white for whole active word
            c_highlight = curses.color_pair(7) | curses.A_BOLD
        except curses.error:
            pass

    if not c_faded:
        c_faded = curses.A_BOLD

    engine = TypingEngine(mode=initial_mode, custom_text=custom_text)
    last_stats = None

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 10 or max_x < 38:
            safe_addstr(stdscr, 1, 2, "Please enlarge terminal window to play...", curses.A_BOLD)
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
        # 1. TOP BAR (Clickable with mouse, 1, 2)
        # ==========================================
        btn_sprint = "[ 1: Sprint ]" if max_x < 55 else "[ 1: ⚡ Sprint ]"
        btn_endless = "[ 2: Endless ]" if max_x < 55 else "[ 2: ♾️ Endless ]"

        top_buttons = []
        cur_btn_x = 1 if max_x < 55 else 2

        # Button 1: Sprint
        is_sprint = (engine.mode == "SPRINT")
        sprint_attr = (curses.A_REVERSE | c_green) if is_sprint else c_white
        safe_addstr(stdscr, 0, cur_btn_x, btn_sprint, sprint_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_sprint), "SPRINT"))
        cur_btn_x += len(btn_sprint) + 1

        # Button 2: Endless
        is_endless = (engine.mode == "ENDLESS")
        endless_attr = (curses.A_REVERSE | c_yellow) if is_endless else c_white
        safe_addstr(stdscr, 0, cur_btn_x, btn_endless, endless_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_endless), "ENDLESS"))

        # Right-aligned exit button
        exit_label = "[ESC]" if max_x < 55 else "[ESC: Exit]"
        exit_x = max(cur_btn_x + len(btn_endless) + 1, max_x - len(exit_label) - 1)
        safe_addstr(stdscr, 0, exit_x, exit_label, c_cyan)

        # Header divider
        safe_addstr(stdscr, 1, 2, "═" * (max_x - 4), c_cyan)

        # ==========================================
        # 2. PROMINENT STATS DASHBOARD
        # ==========================================
        time_str = f"⏱  {format_time(stats['elapsed'])}"
        wpm_str = f"⚡ {stats['wpm']} WPM"
        cpm_str = f"CPM: {stats['cpm']}"
        acc_str = f"🎯 {stats['accuracy']}%"
        err_str = f"❌ {stats['mistakes']} err"
        prog_str = f"📝 {stats['words_completed']}/{stats['total_words']}"

        if max_x >= 75:
            stat_bar = f"{time_str}     {wpm_str}     {cpm_str}     {acc_str}     {err_str}     {prog_str}"
        elif max_x >= 58:
            stat_bar = f"{time_str}   {wpm_str}   {acc_str}   {err_str}   {prog_str}"
        else:
            stat_bar = f"{time_str}  {wpm_str}  {acc_str}  {err_str}"

        stat_x = max(2, (max_x - len(stat_bar)) // 2)
        safe_addstr(stdscr, 2, stat_x, stat_bar, curses.A_BOLD | c_highlight)
        safe_addstr(stdscr, 3, 2, "─" * (max_x - 4), c_faded)

        # ==========================================
        # 3. TYPING CANVAS (Active Word in Increased Font + Flowing Context)
        # ==========================================
        curr_idx = len(engine.typed_chars)
        target = engine.target_text

        # Determine active whole word boundaries
        if curr_idx < len(target) and target[curr_idx] == ' ':
            word_start = curr_idx
            word_end = curr_idx + 1
            active_word = "␣"
            letter_in_word = 0
            is_space_active = True
        else:
            word_start = target.rfind(' ', 0, curr_idx) + 1 if curr_idx > 0 else 0
            word_end = target.find(' ', curr_idx)
            if word_end == -1:
                word_end = len(target)
            active_word = target[word_start:word_end]
            letter_in_word = curr_idx - word_start
            is_space_active = False

        # --- A. Render the Active Word in Increased Size (Guide + 2-Row Font) ---
        char_entries = []
        for char_pos, ch in enumerate(active_word):
            g = get_glyph(ch)
            gw = max(len(g[0]), len(g[1]), 1)
            char_entries.append((ch, g, gw))

        total_word_w = sum(gw for _, _, gw in char_entries) + max(0, len(char_entries) - 1)
        word_start_x = max(2, (max_x - total_word_w) // 2)
        word_start_y = 4 if max_y < 22 else 5

        draw_x = word_start_x
        cursor_screen_x = word_start_x
        cursor_screen_y = word_start_y + 1

        for char_pos, (ch, g, gw) in enumerate(char_entries):
            if char_pos < letter_in_word:
                typed_ch = engine.typed_chars[word_start + char_pos]
                if typed_ch == ch:
                    col = c_green
                    guide_char = ch
                else:
                    col = c_red
                    guide_char = typed_ch if typed_ch != ' ' else '_'
            elif char_pos == letter_in_word:
                col = c_white
                guide_char = ch if not is_space_active else '␣'
                cursor_screen_x = draw_x + (gw // 2)
                cursor_screen_y = word_start_y + 1
            else:
                col = c_faded
                guide_char = ch

            guide_str = guide_char.center(gw)
            if draw_x < max_x - 2:
                safe_addstr(stdscr, word_start_y, draw_x, guide_str, col | curses.A_BOLD)
                safe_addstr(stdscr, word_start_y + 1, draw_x, g[0].ljust(gw), col | curses.A_BOLD)
                safe_addstr(stdscr, word_start_y + 2, draw_x, g[1].ljust(gw), col | curses.A_BOLD)

            draw_x += gw + 1

        # --- B. Sentence Flow Context ---
        context_divider_y = word_start_y + 3
        safe_addstr(stdscr, context_divider_y, 2, "─" * (max_x - 4), c_faded)

        text_start_y = context_divider_y + 1
        wrap_width = max(24, min(max_x - 6, 80))
        box_x = max(2, (max_x - wrap_width) // 2)

        char_positions, total_rows = build_char_positions(engine.target_text, wrap_width)

        if curr_idx in char_positions:
            active_row = char_positions[curr_idx][0]
        elif curr_idx > 0 and (curr_idx - 1) in char_positions:
            active_row = char_positions[curr_idx - 1][0]
        else:
            active_row = 0

        scroll_offset = max(0, active_row - 1)
        visible_rows = max(1, (max_y - text_start_y - 4) // 2)

        for i, target_ch in enumerate(engine.target_text):
            if i not in char_positions:
                continue

            r, c = char_positions[i]
            line_offset = r - scroll_offset
            if line_offset < 0 or line_offset >= visible_rows:
                continue

            screen_y = text_start_y + (line_offset * 2)  # Double-spaced rows!
            screen_x = box_x + c

            if i < curr_idx:
                typed_ch = engine.typed_chars[i]
                if typed_ch == target_ch:
                    safe_addstr(stdscr, screen_y, screen_x, target_ch, c_green)
                else:
                    if typed_ch == ' ':
                        safe_addstr(stdscr, screen_y, screen_x, "_", c_red | curses.A_REVERSE)
                    else:
                        safe_addstr(stdscr, screen_y, screen_x, typed_ch, c_red | curses.A_UNDERLINE)
            elif word_start <= i < word_end:
                safe_addstr(stdscr, screen_y, screen_x, target_ch, c_white)
            else:
                safe_addstr(stdscr, screen_y, screen_x, target_ch, c_faded)

        # Completion Card (Sprint Mode)
        if engine.completed:
            card_y = max_y - 5
            congrats = f"🏆 Sprint Finished! Speed: {stats['wpm']} WPM | Accuracy: {stats['accuracy']}% | Errors: {stats['mistakes']}"
            prompt = "Press [ENTER] for next sentence, [1] / [2] to change mode, or [ESC] to quit."
            safe_addstr(stdscr, card_y, 4, congrats, c_yellow)
            safe_addstr(stdscr, card_y + 1, 4, prompt, c_white)

        # ==========================================
        # 4. FOOTER & SHORTCUTS
        # ==========================================
        footer_y = max_y - 2
        safe_addstr(stdscr, footer_y - 1, 2, "─" * (max_x - 4), c_faded)
        if max_x < 50:
            controls = "[1/2] Mode  [Back] Fix  [ESC] Exit"
        elif max_x < 65:
            controls = "[1/2] Mode  [Back] Fix  [Ctrl+R] Reset  [ESC] Exit"
        else:
            controls = "[1/2] Mode   [Space] Key   [Backspace] Fix   [Ctrl+R] Reset   [ESC] Exit"
        if engine.completed:
            controls = "[ENTER] Next  " + controls
        safe_addstr(stdscr, footer_y, 2, controls, c_cyan)


        # Move terminal cursor to active position
        try:
            if 0 <= cursor_screen_y < max_y and 0 <= cursor_screen_x < max_x:
                stdscr.move(cursor_screen_y, cursor_screen_x)
        except curses.error:
            pass

        stdscr.refresh()

        # Input handling
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
                if my == 0 and (bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED)):
                    for x_start, x_end, action in top_buttons:
                        if x_start <= mx <= x_end:
                            if action == "SPRINT":
                                engine.switch_mode("SPRINT")
                            elif action == "ENDLESS":
                                engine.switch_mode("ENDLESS")
                            break
            except curses.error:
                pass
            continue

        # Keyboard shortcuts
        if ch in (27, 3):  # ESC or Ctrl+C
            break
        elif ch == ord('1') and (len(engine.typed_chars) == 0 or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '1')):
            engine.switch_mode("SPRINT")
        elif ch == ord('2') and (len(engine.typed_chars) == 0 or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '2')):
            engine.switch_mode("ENDLESS")
        elif ch == 9:  # TAB -> toggle mode
            next_mode = "ENDLESS" if engine.mode == "SPRINT" else "SPRINT"
            engine.switch_mode(next_mode)
        elif ch in (18, 263, curses.KEY_F5):  # Ctrl+R or F5 -> Reset
            engine.reset()
        elif ch in (curses.KEY_BACKSPACE, 127, 8, ord('\b')):
            engine.backspace()
        elif ch in (10, 13, curses.KEY_ENTER):
            if engine.completed:
                engine.reset()
        elif 32 <= ch <= 126:  # Printable ASCII characters (INCLUDING SPACE 32!)
            engine.add_char(chr(ch))

    return last_stats, engine.mode

def main():
    parser = argparse.ArgumentParser(
        prog="ttyping",
        description="Terminal Typing Game - Sprint WPM testing & Endless key mastery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Modes:
  1: Sprint   - Simple, natural sentences you finish in 1-2 minutes to test your WPM.
  2: Endless  - Endless session with controlled frequency:
                * Numbers appear once every 100 words
                * Special symbols appear once every 200 words
                * Comma and fullstop appear once every ~35 words
                * Clean arbitrary words in between
"""
    )
    parser.add_argument("-1", "--sprint", action="store_true", help="Launch directly in Sprint Mode (1-2 min WPM test)")
    parser.add_argument("-2", "--endless", action="store_true", help="Launch directly in Endless Mode (controlled practice)")
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

    # Summary
    print("\n" + "=" * 50)
    print("             TERMINAL TYPING SUMMARY              ")
    print("=" * 50)
    print(f"  🎮 Mode             : {final_mode}")
    if final_stats:
        print(f"  ⏱  Time Elapsed     : {format_time(final_stats['elapsed'])}")
        print(f"  📝 Words Completed  : {final_stats['words_completed']}")
        print(f"  ⚡ Typing Speed     : {final_stats['wpm']} WPM ({final_stats['cpm']} CPM)")
        print(f"  🎯 Accuracy         : {final_stats['accuracy']}%")
        print(f"  ❌ Errors Made      : {final_stats['mistakes']}")
        print(f"  ⌨️  Total Keystrokes : {final_stats['keystrokes']}")
    print("=" * 50)
    print("Thanks for playing! Run 'ttyping' anytime to play again.\n")

if __name__ == "__main__":
    main()

