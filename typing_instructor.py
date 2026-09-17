#!/usr/bin/env python3
r"""
Vintage Typing Instructor - Hands-on-Keyboard Terminal CLI Application
Features:
  - Full-window ANSI canvas centering a mechanical keyboard and realistic typing hands.
  - Large multi-line ASCII block keycaps with 3x3 block letter glyphs.
  - Layered density-shaded ASCII hands (█, ▓, ▒, ░, (, ), /, \) with realistic anatomy.
  - Dynamic finger reach, keycap depression, and retraction animation cycle.
  - 24-bit TrueColor ANSI palette (flesh tones, vintage beige/slate keycaps, neon active keys).
  - Interactive touch-typing mode + automated demo typing tutor mode (toggle with TAB).
  - Flicker-free double-buffered atomic rendering engine.
"""

import sys
import os
import time
import math
import tty
import termios
import select
import signal
import atexit
import shutil
import random
from typing import Dict, List, Tuple, Optional, Any

# ============================================================================
# 24-Bit TrueColor ANSI Helpers & Color Palette
# ============================================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

def fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"

# Palette: Retro Mechanical Keyboard (IBM Model M Style)
COLOR_DESK_BG         = (16, 18, 22)        # Dark desk backdrop
COLOR_CHASSIS_BG      = (36, 39, 46)        # Outer enclosure
COLOR_CHASSIS_BORDER  = (82, 88, 102)       # Enclosure top bevel highlight
COLOR_CHASSIS_SHADOW  = (22, 24, 28)        # Enclosure drop shadow
COLOR_PLATE_BG        = (24, 26, 30)        # Switch mounting plate well

# Keycaps (Matte Vintage PBT Dye-Sub Beige & Modifiers)
COLOR_ALPHA_BG        = (220, 216, 206)     # Retro off-white / light cream
COLOR_ALPHA_FG        = (32, 35, 42)        # Dark charcoal legend
COLOR_ALPHA_TOP       = (245, 243, 238)     # Highlight bevel
COLOR_ALPHA_BOT       = (155, 150, 140)     # Bottom shadow bevel
COLOR_ALPHA_SIDE      = (192, 188, 178)     # Lateral bevel

COLOR_MOD_BG          = (138, 134, 128)     # Warm vintage slate grey
COLOR_MOD_FG          = (240, 240, 240)     # Off-white modifier text
COLOR_MOD_TOP         = (170, 166, 160)
COLOR_MOD_BOT         = (98, 94, 90)
COLOR_MOD_SIDE        = (124, 120, 115)

# Active Depressed Key (Vibrant Electric Neon Cyan / Amber)
COLOR_ACTIVE_BG       = (0, 235, 255)       # Glowing neon cyan
COLOR_ACTIVE_FG       = (10, 16, 26)        # Deep obsidian legend
COLOR_ACTIVE_BORDER   = (0, 180, 220)       # Depressed border highlight
COLOR_TARGET_BORDER   = (255, 205, 40)      # Target key border (tutor hint)

# Anatomy: Realistic Shaded Hands & Fingers
SKIN_HIGHLIGHT        = (248, 214, 188)     # Dorsal/knuckle sheen
SKIN_MID              = (222, 170, 132)     # Natural warm flesh
SKIN_LOW              = (172, 118, 84)      # Contour shadow
SKIN_DARK             = (115, 72, 46)       # Deep outline shadow
NAIL_COLOR            = (252, 232, 220)     # Fingernail pearlescent sheen
NAIL_STRIKE           = (255, 255, 255)     # Fingernail pressure flare

# Top Status HUD Accents
COLOR_HUD_BG          = (24, 27, 34)
COLOR_HUD_BORDER      = (60, 66, 80)
COLOR_ACCENT_CYAN     = (0, 235, 255)
COLOR_ACCENT_GREEN    = (70, 235, 120)
COLOR_ACCENT_AMBER    = (255, 185, 40)
COLOR_ACCENT_PINK     = (255, 90, 140)

# ============================================================================
# Large Block Figlet Glyph Sets (3x3 and 2x3 Compact)
# ============================================================================

GLYPHS_3X3: Dict[str, List[str]] = {
    'A': ["▄▀▄", "█▀█", "▀ ▀"],
    'B': ["█▀▄", "█▀▄", "▀▀▀"],
    'C': ["█▀▀", "█  ", "▀▀▀"],
    'D': ["█▀▄", "█ █", "▀▀▀"],
    'E': ["█▀▀", "█▀▀", "▀▀▀"],
    'F': ["█▀▀", "█▀▀", "▀  "],
    'G': ["█▀▀", "█ ▀", "▀▀▀"],
    'H': ["█ █", "█▀█", "▀ ▀"],
    'I': ["▀█▀", " █ ", "▀▀▀"],
    'J': ["  █", "  █", "▀▀ "],
    'K': ["█ █", "██ ", "▀ ▀"],
    'L': ["█  ", "█  ", "▀▀▀"],
    'M': ["█▄█", "█ █", "▀ ▀"],
    'N': ["█▄█", "███", "▀ ▀"],
    'O': ["█▀█", "█ █", "▀▀▀"],
    'P': ["█▀█", "█▀▀", "▀  "],
    'Q': ["█▀█", "█▀█", "▀▀█"],
    'R': ["█▀█", "██▀", "▀ ▀"],
    'S': ["█▀▀", "▀▀█", "▀▀▀"],
    'T': ["▀█▀", " █ ", " ▀ "],
    'U': ["█ █", "█ █", "▀▀▀"],
    'V': ["█ █", "█ █", " ▀ "],
    'W': ["█ █", "█▄█", "▀ ▀"],
    'X': ["▀▄▀", " █ ", "▄▀▄"],
    'Y': ["█ █", " █ ", " ▀ "],
    'Z': ["▀▀█", " █ ", "█▀▀"],
    '0': ["█▀█", "█/█", "▀▀▀"],
    '1': [" ▄█", "  █", "  ▀"],
    '2': ["▀▀█", "█▀▀", "▀▀▀"],
    '3': ["▀▀█", " ▀█", "▀▀▀"],
    '4': ["█ █", "▀▀█", "  ▀"],
    '5': ["█▀▀", "▀▀█", "▀▀▀"],
    '6': ["█▀▀", "█▀█", "▀▀▀"],
    '7': ["▀▀█", "  █", "  ▀"],
    '8': ["█▀█", "█▀█", "▀▀▀"],
    '9': ["█▀█", "▀▀█", "▀▀▀"],
    '`': ["▀  ", "   ", "   "],
    '~': ["▄▀▄", "   ", "   "],
    '!': [" █ ", " █ ", " ▄ "],
    '@': ["█▀█", "█▀█", "▀▀▀"],
    '#': ["█▄█", "▀█▀", "█▄█"],
    '$': ["▄█▄", "▀█▀", "▄█▄"],
    '%': ["█ █", " ▀ ", "█ █"],
    '^': [" ▄ ", "▀ ▀", "   "],
    '&': ["▄▀▄", "▀▄█", "▀ ▀"],
    '*': [" █ ", "▀█▀", " █ "],
    '(': [" ▄▀", " █ ", " ▀▄"],
    ')': ["▀▄ ", " █ ", "▄▀ "],
    '-': ["   ", "▀▀▀", "   "],
    '_': ["   ", "   ", "▀▀▀"],
    '=': ["▀▀▀", "   ", "▀▀▀"],
    '+': [" ▄ ", "▀█▀", " ▀ "],
    '[': ["▀▀ ", "█  ", "▀▀ "],
    ']': [" ▀▀", "  █", " ▀▀"],
    '{': [" ▀█", "▀█ ", " ▀█"],
    '}': ["█▀ ", " █▀", "█▀ "],
    '\\': ["█  ", " █ ", "  █"],
    '|': [" █ ", " █ ", " █ "],
    ';': [" ▄ ", "   ", " █ "],
    ':': [" ▄ ", "   ", " ▀ "],
    '\'': [" █ ", " ▀ ", "   "],
    '"': ["█ █", "▀ ▀", "   "],
    ',': ["   ", "   ", " █ "],
    '<': ["  █", " █ ", "  █"],
    '.': ["   ", "   ", " ▄ "],
    '>': ["█  ", " █ ", "█  "],
    '/': ["  █", " █ ", "█  "],
    '?': ["▀▀█", " ▀ ", " ▄ "],
    ' ': ["   ", "   ", "   "],
}

GLYPHS_2X3: Dict[str, List[str]] = {
    'A': ["▄▀▄", "█ █"],
    'B': ["█▀▄", "█▄▀"],
    'C': ["█▀▀", "▀▀▀"],
    'D': ["█▀▄", "▀▀▀"],
    'E': ["█▀▀", "▀▀▀"],
    'F': ["█▀▀", "▀  "],
    'G': ["█▀▀", "▀▀█"],
    'H': ["█ █", "█▀█"],
    'I': ["▀█▀", "▀▀▀"],
    'J': ["  █", "▀▀ "],
    'K': ["█ █", "▀ ▀"],
    'L': ["█  ", "▀▀▀"],
    'M': ["█▄█", "▀ ▀"],
    'N': ["█▄█", "▀ ▀"],
    'O': ["█▀█", "▀▀▀"],
    'P': ["█▀█", "▀  "],
    'Q': ["█▀█", "▀▀█"],
    'R': ["█▀█", "▀ ▀"],
    'S': ["█▀▀", "▀▀▀"],
    'T': ["▀█▀", " ▀ "],
    'U': ["█ █", "▀▀▀"],
    'V': ["█ █", " ▀ "],
    'W': ["█ █", "▀ ▀"],
    'X': ["▀▄▀", "▄▀▄"],
    'Y': ["█ █", " ▀ "],
    'Z': ["▀▀█", "█▀▀"],
    '0': ["█▀█", "▀▀▀"],
    '1': [" ▄█", "  ▀"],
    '2': ["▀▀█", "▀▀▀"],
    '3': ["▀▀█", "▀▀▀"],
    '4': ["█ █", "  ▀"],
    '5': ["█▀▀", "▀▀▀"],
    '6': ["█▀▀", "▀▀▀"],
    '7': ["▀▀█", "  ▀"],
    '8': ["█▀█", "▀▀▀"],
    '9': ["█▀█", "▀▀▀"],
    '`': ["▀  ", "   "],
    '-': ["   ", "▀▀▀"],
    '=': ["▀▀▀", "▀▀▀"],
    '[': ["▀▀ ", "▀▀ "],
    ']': [" ▀▀", " ▀▀"],
    '\\': ["█  ", "  █"],
    ';': [" ▄ ", " █ "],
    '\'': [" █ ", " ▀ "],
    ',': ["   ", " █ "],
    '.': ["   ", " ▄ "],
    '/': ["  █", "█  "],
    ' ': ["   ", "   "],
}

# ============================================================================
# Keyboard Layout & Ergonomic Finger Assignments
# ============================================================================

ROW_LAYOUT_SPEC = [
    # Row 0 (Number row, 15.0 Units total)
    [("`", 1.0, "`"), ("1", 1.0, "1"), ("2", 1.0, "2"), ("3", 1.0, "3"), ("4", 1.0, "4"),
     ("5", 1.0, "5"), ("6", 1.0, "6"), ("7", 1.0, "7"), ("8", 1.0, "8"), ("9", 1.0, "9"),
     ("0", 1.0, "0"), ("-", 1.0, "-"), ("=", 1.0, "="), ("BACKSPACE", 2.0, "BKSP")],
    # Row 1 (QWERTY, 15.0 Units total)
    [("TAB", 1.5, "TAB"), ("Q", 1.0, "Q"), ("W", 1.0, "W"), ("E", 1.0, "E"), ("R", 1.0, "R"),
     ("T", 1.0, "T"), ("Y", 1.0, "Y"), ("U", 1.0, "U"), ("I", 1.0, "I"), ("O", 1.0, "O"),
     ("P", 1.0, "P"), ("[", 1.0, "["), ("]", 1.0, "]"), ("\\", 1.5, "\\")],
    # Row 2 (Home row, 15.0 Units total)
    [("CAPS", 1.75, "CAPS"), ("A", 1.0, "A"), ("S", 1.0, "S"), ("D", 1.0, "D"), ("F", 1.0, "F"),
     ("G", 1.0, "G"), ("H", 1.0, "H"), ("J", 1.0, "J"), ("K", 1.0, "K"), ("L", 1.0, "L"),
     (";", 1.0, ";"), ("'", 1.0, "'"), ("ENTER", 2.25, "ENTER")],
    # Row 3 (ZXCV row, 15.0 Units total)
    [("SHIFT_L", 2.25, "SHIFT"), ("Z", 1.0, "Z"), ("X", 1.0, "X"), ("C", 1.0, "C"), ("V", 1.0, "V"),
     ("B", 1.0, "B"), ("N", 1.0, "N"), ("M", 1.0, "M"), (",", 1.0, ","), (".", 1.0, "."),
     ("/", 1.0, "/"), ("SHIFT_R", 2.75, "SHIFT")],
    # Row 4 (Space row, 15.0 Units total)
    [("CTRL_L", 1.75, "CTRL"), ("ALT_L", 1.75, "ALT"), ("SPACE", 7.0, "SPACE"),
     ("ALT_R", 1.75, "ALT"), ("CTRL_R", 2.75, "CTRL")],
]

# Standard touch-typing finger assignment (0 to 9)
# 0: Left Pinky,  1: Left Ring,   2: Left Middle,   3: Left Index,   4: Left Thumb
# 5: Right Thumb, 6: Right Index, 7: Right Middle,  8: Right Ring,   9: Right Pinky
FINGER_NAMES = [
    "Left Pinky", "Left Ring", "Left Middle", "Left Index", "Left Thumb",
    "Right Thumb", "Right Index", "Right Middle", "Right Ring", "Right Pinky"
]

KEY_TO_FINGER: Dict[str, int] = {
    # Left Pinky (Home: A)
    '`': 0, '~': 0, '1': 0, '!': 0, 'Q': 0, 'A': 0, 'Z': 0, 'TAB': 0, 'CAPS': 0, 'SHIFT_L': 0,
    # Left Ring (Home: S)
    '2': 1, '@': 1, 'W': 1, 'S': 1, 'X': 1,
    # Left Middle (Home: D)
    '3': 2, '#': 2, 'E': 2, 'D': 2, 'C': 2,
    # Left Index (Home: F)
    '4': 3, '$': 3, '5': 3, '%': 3, 'R': 3, 'T': 3, 'F': 3, 'G': 3, 'V': 3, 'B': 3,
    # Left Thumb
    'CTRL_L': 0, 'ALT_L': 4,
    # Right Thumb
    ' ': 5, 'SPACE': 5, 'ALT_R': 5,
    # Right Index (Home: J)
    '6': 6, '^': 6, '7': 6, '&': 6, 'Y': 6, 'U': 6, 'H': 6, 'J': 6, 'N': 6, 'M': 6,
    # Right Middle (Home: K)
    '8': 7, '*': 7, 'I': 7, 'K': 7, ',': 7, '<': 7,
    # Right Ring (Home: L)
    '9': 8, '(': 8, 'O': 8, 'L': 8, '.': 8, '>': 8,
    # Right Pinky (Home: ;)
    '0': 9, ')': 9, '-': 9, '_': 9, '=': 9, '+': 9, 'BACKSPACE': 9,
    'P': 9, '[': 9, '{': 9, ']': 9, '}': 9, '\\': 9, '|': 9,
    ';': 9, ':': 9, '\'': 9, '"': 9, 'ENTER': 9, '/': 9, '?': 9, 'SHIFT_R': 9, 'CTRL_R': 9,
}

SHIFTED_MAP: Dict[str, str] = {
    '~': '`', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
    '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', '_': '-',
    '+': '=', '{': '[', '}': ']', '|': '\\', ':': ';', '"': '\'',
    '<': ',', '>': '.', '?': '/'
}

# ============================================================================
# 2D Screen Canvas Buffer
# ============================================================================

class Canvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.chars = [[' ' for _ in range(width)] for _ in range(height)]
        self.fg = [[COLOR_ALPHA_FG for _ in range(width)] for _ in range(height)]
        self.bg = [[COLOR_DESK_BG for _ in range(width)] for _ in range(height)]
        self.bold = [[False for _ in range(width)] for _ in range(height)]

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.chars[y][x] = ' '
                self.fg[y][x] = COLOR_ALPHA_FG
                self.bg[y][x] = COLOR_DESK_BG
                self.bold[y][x] = False

    def set_cell(self, x: int, y: int, ch: str,
                 fg_col: Optional[Tuple[int, int, int]] = None,
                 bg_col: Optional[Tuple[int, int, int]] = None,
                 bold: bool = False):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.chars[y][x] = ch
            if fg_col is not None:
                self.fg[y][x] = fg_col
            if bg_col is not None:
                self.bg[y][x] = bg_col
            self.bold[y][x] = bold

    def draw_text(self, x: int, y: int, text: str,
                  fg_col: Optional[Tuple[int, int, int]] = None,
                  bg_col: Optional[Tuple[int, int, int]] = None,
                  bold: bool = False):
        for i, ch in enumerate(text):
            self.set_cell(x + i, y, ch, fg_col, bg_col, bold)

    def render(self) -> str:
        """Converts canvas into an optimized ANSI escape sequence string."""
        lines = []
        cur_fg: Optional[Tuple[int, int, int]] = None
        cur_bg: Optional[Tuple[int, int, int]] = None
        cur_bold: bool = False

        for y in range(self.height):
            row_parts = []
            for x in range(self.width):
                c = self.chars[y][x]
                f = self.fg[y][x]
                b = self.bg[y][x]
                bo = self.bold[y][x]

                code = ""
                if bo != cur_bold:
                    code += BOLD if bo else "\033[22m"
                    cur_bold = bo
                if f != cur_fg:
                    code += f"\033[38;2;{f[0]};{f[1]};{f[2]}m"
                    cur_fg = f
                if b != cur_bg:
                    code += f"\033[48;2;{b[0]};{b[1]};{b[2]}m"
                    cur_bg = b

                row_parts.append(code + c)
            lines.append("".join(row_parts) + RESET)
            cur_fg = None
            cur_bg = None
            cur_bold = False

        return "\033[H" + "\n".join(lines)


# ============================================================================
# Finger Animation State Machine
# ============================================================================

class FingerState:
    REST = 0
    REACH = 1
    STRIKE = 2
    RETRACT = 3

class AnimatedFinger:
    def __init__(self, finger_id: int, name: str, home_x: float, home_y: float, knuckle_x: float, knuckle_y: float):
        self.finger_id = finger_id
        self.name = name
        self.home_x = home_x
        self.home_y = home_y
        self.knuckle_x = knuckle_x
        self.knuckle_y = knuckle_y

        self.cur_x = home_x
        self.cur_y = home_y
        self.target_x = home_x
        self.target_y = home_y

        self.state = FingerState.REST
        self.state_start_time = 0.0
        self.reach_duration = 0.06
        self.strike_duration = 0.09
        self.retract_duration = 0.07

        self.struck_key_id: Optional[str] = None
        self.is_striking = False

    def strike_target(self, target_x: float, target_y: float, key_id: str):
        self.target_x = target_x
        self.target_y = target_y
        self.struck_key_id = key_id
        self.state = FingerState.REACH
        self.state_start_time = time.time()
        self.is_striking = False

    def update(self, now: float) -> Optional[str]:
        """Returns the key_id when depressed during STRIKE."""
        active_key = None
        elapsed = now - self.state_start_time

        if self.state == FingerState.REST:
            self.cur_x = self.home_x
            self.cur_y = self.home_y
            self.is_striking = False

        elif self.state == FingerState.REACH:
            t = min(1.0, elapsed / max(0.01, self.reach_duration))
            # Smooth ease-out
            ease = math.sin(t * math.pi / 2.0)
            self.cur_x = self.home_x + (self.target_x - self.home_x) * ease
            self.cur_y = self.home_y + (self.target_y - self.home_y) * ease
            if t >= 1.0:
                self.state = FingerState.STRIKE
                self.state_start_time = now
                self.is_striking = True
                active_key = self.struck_key_id

        elif self.state == FingerState.STRIKE:
            self.cur_x = self.target_x
            self.cur_y = self.target_y
            self.is_striking = True
            active_key = self.struck_key_id
            if elapsed >= self.strike_duration:
                self.state = FingerState.RETRACT
                self.state_start_time = now
                self.is_striking = False

        elif self.state == FingerState.RETRACT:
            t = min(1.0, elapsed / max(0.01, self.retract_duration))
            # Smooth ease-in-out
            ease = (1.0 - math.cos(t * math.pi)) / 2.0
            self.cur_x = self.target_x + (self.home_x - self.target_x) * ease
            self.cur_y = self.target_y + (self.home_y - self.target_y) * ease
            if t >= 1.0:
                self.state = FingerState.REST
                self.cur_x = self.home_x
                self.cur_y = self.home_y
                self.struck_key_id = None

        return active_key


# ============================================================================
# Main Application Engine
# ============================================================================

class TypingInstructorApp:
    DEMO_DRILLS = [
        "the quick brown fox jumps over the lazy dog",
        "touch typing with vintage ibm model m buckling springs",
        "sphinx of black quartz judge my vow pack my box with five dozen jugs",
        "how vexingly quick daft zebras jump while jackdaws love big quartz",
        "classic mechanical keyboard typing instructor rendered in full ascii",
        "proper finger placement asdf and jkl semi builds speed and accuracy",
    ]

    def __init__(self):
        self.term_w, self.term_h = shutil.get_terminal_size((110, 42))
        self.canvas = Canvas(self.term_w, self.term_h)

        # Dynamic layout parameters
        self._calculate_dimensions()

        self.keys: Dict[str, Dict[str, Any]] = {}
        self.fingers: List[AnimatedFinger] = []

        # Modes & Metrics
        self.demo_mode = True
        self.current_drill_idx = 0
        self.drill_char_idx = 0
        self.last_demo_strike_time = 0.0
        self.demo_char_delay = 0.16

        self.active_depressed_keys: set[str] = set()
        self.target_key: Optional[str] = None
        self.last_pressed_finger_name: str = "Ready"

        # Typing stats
        self.total_keypresses = 0
        self.correct_keypresses = 0
        self.streak = 0
        self.start_time = time.time()
        self.wpm = 0.0

        # Termios backup
        self.old_termios = None
        self.running = True

        self._build_keyboard_geometry()
        self._init_fingers()

    def _calculate_dimensions(self):
        """Calculates optimal key width, key height, and canvas centering."""
        # Width scaling
        if self.term_w >= 115:
            self.unit_w = 7
        elif self.term_w >= 85:
            self.unit_w = 5
        else:
            self.unit_w = max(4, (self.term_w - 6) // 15)

        # Height scaling
        if self.term_h >= 36:
            self.unit_h = 5
        elif self.term_h >= 28:
            self.unit_h = 4
        else:
            self.unit_h = 3

        self.kbd_w = 15 * self.unit_w
        self.kbd_h = 5 * self.unit_h
        self.kbd_x = max(2, (self.term_w - self.kbd_w) // 2)

        # Top padding
        if self.term_h >= 36:
            self.kbd_y = 5
        elif self.term_h >= 28:
            self.kbd_y = 4
        else:
            self.kbd_y = 3

    def _build_keyboard_geometry(self):
        """Constructs rectangular keycap geometry and center coordinates."""
        self.keys.clear()
        for r_idx, row in enumerate(ROW_LAYOUT_SPEC):
            cur_u = 0.0
            for raw_id, u_len, display_label in row:
                x1 = self.kbd_x + int(cur_u * self.unit_w)
                x2 = self.kbd_x + int((cur_u + u_len) * self.unit_w)
                w = x2 - x1
                y1 = self.kbd_y + r_idx * self.unit_h
                h = self.unit_h
                cur_u += u_len

                is_modifier = raw_id in (
                    "BACKSPACE", "TAB", "CAPS", "ENTER",
                    "SHIFT_L", "SHIFT_R", "CTRL_L", "CTRL_R", "ALT_L", "ALT_R"
                )

                key_data = {
                    'id': raw_id,
                    'label': display_label,
                    'x': x1,
                    'y': y1,
                    'w': w,
                    'h': h,
                    'center_x': x1 + w / 2.0,
                    'center_y': y1 + h / 2.0,
                    'is_modifier': is_modifier,
                    'is_space': raw_id == "SPACE",
                    'finger': KEY_TO_FINGER.get(raw_id, -1)
                }
                self.keys[raw_id] = key_data

    def _init_fingers(self):
        """Initializes home resting coordinates and knuckle anchors for 10 fingers."""
        self.fingers.clear()

        # Left Hand: Home row keys A, S, D, F, Space-left
        key_a = self.keys["A"]
        key_s = self.keys["S"]
        key_d = self.keys["D"]
        key_f = self.keys["F"]
        key_sp = self.keys["SPACE"]

        tip_offset_y = max(1.5, self.unit_h * 0.6)

        home_L = [
            (key_a['center_x'], key_a['y'] + tip_offset_y),
            (key_s['center_x'], key_s['y'] + tip_offset_y),
            (key_d['center_x'], key_d['y'] + tip_offset_y),
            (key_f['center_x'], key_f['y'] + tip_offset_y),
            (key_sp['x'] + key_sp['w'] * 0.32, key_sp['y'] + tip_offset_y * 0.7),
        ]

        # Knuckle arch on palm below row 3
        row3_y = self.keys["SHIFT_L"]['y'] + self.unit_h
        knuckle_gap = max(0.5, self.unit_h * 0.15)
        knuckles_L = [
            (key_a['center_x'] - 0.5, row3_y + knuckle_gap * 1.6),
            (key_s['center_x'] - 0.3, row3_y + knuckle_gap * 0.5),
            (key_d['center_x'], row3_y - knuckle_gap * 0.3),
            (key_f['center_x'] + 0.5, row3_y + knuckle_gap * 0.5),
            (key_sp['x'] + key_sp['w'] * 0.22, row3_y + knuckle_gap * 3.5),
        ]

        # Right Hand: Space-right, J, K, L, ;
        key_j = self.keys["J"]
        key_k = self.keys["K"]
        key_l = self.keys["L"]
        key_semi = self.keys[";"]

        home_R = [
            (key_sp['x'] + key_sp['w'] * 0.68, key_sp['y'] + tip_offset_y * 0.7),
            (key_j['center_x'], key_j['y'] + tip_offset_y),
            (key_k['center_x'], key_k['y'] + tip_offset_y),
            (key_l['center_x'], key_l['y'] + tip_offset_y),
            (key_semi['center_x'], key_semi['y'] + tip_offset_y),
        ]

        knuckles_R = [
            (key_sp['x'] + key_sp['w'] * 0.78, row3_y + knuckle_gap * 3.5),
            (key_j['center_x'] - 0.5, row3_y + knuckle_gap * 0.5),
            (key_k['center_x'], row3_y - knuckle_gap * 0.3),
            (key_l['center_x'] + 0.3, row3_y + knuckle_gap * 0.5),
            (key_semi['center_x'] + 0.5, row3_y + knuckle_gap * 1.6),
        ]

        # Assemble all 10 fingers
        for f_id in range(5):
            hx, hy = home_L[f_id]
            kx, ky = knuckles_L[f_id]
            self.fingers.append(AnimatedFinger(f_id, FINGER_NAMES[f_id], hx, hy, kx, ky))

        for f_id in range(5):
            hx, hy = home_R[f_id]
            kx, ky = knuckles_R[f_id]
            self.fingers.append(AnimatedFinger(f_id + 5, FINGER_NAMES[f_id + 5], hx, hy, kx, ky))

    def on_terminal_resize(self):
        """Re-computes canvas and positions when user resizes terminal window."""
        self.term_w, self.term_h = shutil.get_terminal_size((110, 42))
        self.canvas = Canvas(self.term_w, self.term_h)
        self._calculate_dimensions()
        self._build_keyboard_geometry()
        self._init_fingers()

    # ------------------------------------------------------------------------
    # Animation & Key Action Triggers
    # ------------------------------------------------------------------------

    def trigger_key_strike(self, char_or_key: str):
        """Triggers the corresponding finger to reach, depress, and retract."""
        norm_key = char_or_key.upper()
        # Check shifted symbols
        if char_or_key in SHIFTED_MAP:
            norm_key = SHIFTED_MAP[char_or_key]
        elif char_or_key == ' ':
            norm_key = "SPACE"
        elif char_or_key in ('\r', '\n'):
            norm_key = "ENTER"
        elif char_or_key in ('\x7f', '\x08'):
            norm_key = "BACKSPACE"

        target_data = self.keys.get(norm_key)
        if not target_data:
            return

        finger_idx = target_data['finger']
        if 0 <= finger_idx < len(self.fingers):
            finger = self.fingers[finger_idx]
            # Strike at key center
            tx = target_data['center_x']
            ty = target_data['center_y']
            finger.strike_target(tx, ty, norm_key)
            self.last_pressed_finger_name = finger.name
            self.total_keypresses += 1
            self.streak += 1

            # Update stats
            elapsed_m = max(0.05, (time.time() - self.start_time) / 60.0)
            self.wpm = (self.total_keypresses / 5.0) / elapsed_m

    # ------------------------------------------------------------------------
    # Drawing Pipeline
    # ------------------------------------------------------------------------

    def draw_hud(self):
        """Renders top vintage status HUD, indicators, and metrics."""
        # Title bar
        title = " ⌨  VINTAGE TYPING INSTRUCTOR  //  IBM MODEL M MECHANICAL  "
        mode_str = "[ AUTOMATED DEMO (TAB to switch) ]" if self.demo_mode else "[ INTERACTIVE USER TYPING (TAB to demo) ]"

        self.canvas.draw_text(self.kbd_x, 0, title, COLOR_ACCENT_AMBER, COLOR_HUD_BG, bold=True)
        self.canvas.draw_text(self.kbd_x + len(title) + 2, 0, mode_str,
                              COLOR_ACCENT_GREEN if self.demo_mode else COLOR_ACCENT_CYAN,
                              COLOR_HUD_BG, bold=True)

        # Status & Metrics
        hud_line2 = (
            f"  WPM: {self.wpm:5.1f}  │  STREAK: {self.streak:3d}  │  "
            f"TOTAL KEYS: {self.total_keypresses:4d}  │  "
            f"LAST FINGER: {self.last_pressed_finger_name:<12}  │  [ESC/Q] Quit"
        )
        self.canvas.draw_text(self.kbd_x, 1, hud_line2, (200, 205, 215), COLOR_HUD_BG)

        # Drill sentence display (in Demo mode)
        drill_text = self.DEMO_DRILLS[self.current_drill_idx]
        drill_prompt = "  DRILL:  " + drill_text
        self.canvas.draw_text(self.kbd_x, 2, drill_prompt, (170, 180, 195), COLOR_DESK_BG)

        # Highlight current target character
        if self.demo_mode:
            target_col = self.kbd_x + 10 + self.drill_char_idx
            ch = drill_text[self.drill_char_idx] if self.drill_char_idx < len(drill_text) else " "
            self.canvas.draw_text(target_col, 2, ch, (10, 20, 30), COLOR_ACTIVE_BG, bold=True)

    def draw_keyboard_chassis(self):
        """Renders outer beveled frame, badge, and LEDs for retro mechanical chassis."""
        kx = self.kbd_x
        ky = self.kbd_y
        kw = self.kbd_w
        kh = self.kbd_h

        # Switch plate well (dark recessed backing)
        for y in range(ky - 1, ky + kh + 1):
            for x in range(kx - 1, kx + kw + 1):
                self.canvas.set_cell(x, y, ' ', None, COLOR_PLATE_BG)

        # Beveled chassis enclosure
        bx1 = kx - 2
        by1 = ky - 1
        bx2 = kx + kw + 1
        by2 = ky + kh

        # Horizontal borders
        for x in range(bx1, bx2 + 1):
            self.canvas.set_cell(x, by1, '═', COLOR_CHASSIS_BORDER, COLOR_CHASSIS_BG)
            self.canvas.set_cell(x, by2, '═', COLOR_CHASSIS_SHADOW, COLOR_CHASSIS_BG)

        # Vertical borders
        for y in range(by1, by2 + 1):
            self.canvas.set_cell(bx1, y, '║', COLOR_CHASSIS_BORDER, COLOR_CHASSIS_BG)
            self.canvas.set_cell(bx2, y, '║', COLOR_CHASSIS_SHADOW, COLOR_CHASSIS_BG)

        # Corners
        self.canvas.set_cell(bx1, by1, '╔', COLOR_CHASSIS_BORDER, COLOR_CHASSIS_BG)
        self.canvas.set_cell(bx2, by1, '╗', COLOR_CHASSIS_BORDER, COLOR_CHASSIS_BG)
        self.canvas.set_cell(bx1, by2, '╚', COLOR_CHASSIS_BORDER, COLOR_CHASSIS_BG)
        self.canvas.set_cell(bx2, by2, '╝', COLOR_CHASSIS_SHADOW, COLOR_CHASSIS_BG)

        # Vintage IBM Badge & Status LEDs
        badge = " [ IBM MODEL M ] "
        self.canvas.draw_text(bx1 + 3, by1, badge, (190, 195, 205), COLOR_CHASSIS_BG, bold=True)

        leds = " [ NUM ⬤ ] [ CAPS ◯ ] [ SCROLL ◯ ] "
        if bx2 - len(leds) - 2 > bx1 + len(badge) + 6:
            self.canvas.draw_text(bx2 - len(leds) - 1, by1, leds, (140, 220, 160), COLOR_CHASSIS_BG)

    def draw_keycaps(self):
        """Renders large multi-line ASCII block keycaps with centered block font glyphs."""
        glyph_set = GLYPHS_3X3 if self.unit_h >= 5 else GLYPHS_2X3

        for key_id, k in self.keys.items():
            x, y, w, h = k['x'], k['y'], k['w'], k['h']
            label = k['label']
            is_mod = k['is_modifier']
            is_space = k['is_space']
            is_pressed = key_id in self.active_depressed_keys
            is_target = (key_id == self.target_key) and not is_pressed

            # Color styling
            if is_pressed:
                bg_col = COLOR_ACTIVE_BG
                fg_col = COLOR_ACTIVE_FG
                top_b = COLOR_ACTIVE_BORDER
                bot_b = COLOR_ACTIVE_BORDER
                side_b = COLOR_ACTIVE_BORDER
            elif is_mod:
                bg_col = COLOR_MOD_BG
                fg_col = COLOR_MOD_FG
                top_b = COLOR_MOD_TOP
                bot_b = COLOR_MOD_BOT
                side_b = COLOR_MOD_SIDE
            else:
                bg_col = COLOR_ALPHA_BG
                fg_col = COLOR_ALPHA_FG
                top_b = COLOR_TARGET_BORDER if is_target else COLOR_ALPHA_TOP
                bot_b = COLOR_ALPHA_BOT
                side_b = COLOR_ALPHA_SIDE

            # Physical 3D keycap beveling
            if not is_pressed:
                # Idle high bevel
                self.canvas.set_cell(x, y, '┌', top_b, COLOR_PLATE_BG)
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y, '─', top_b, COLOR_PLATE_BG)
                self.canvas.set_cell(x + w - 1, y, '┐', top_b, COLOR_PLATE_BG)

                self.canvas.set_cell(x, y + h - 1, '└', bot_b, COLOR_PLATE_BG)
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y + h - 1, '─', bot_b, COLOR_PLATE_BG)
                self.canvas.set_cell(x + w - 1, y + h - 1, '┘', bot_b, COLOR_PLATE_BG)
            else:
                # Depressed physical state (keycap sunken into plate)
                self.canvas.set_cell(x, y, '▗', bot_b, COLOR_PLATE_BG)
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y, '▄', bot_b, COLOR_PLATE_BG)
                self.canvas.set_cell(x + w - 1, y, '▖', bot_b, COLOR_PLATE_BG)

                self.canvas.set_cell(x, y + h - 1, '▝', top_b, COLOR_PLATE_BG)
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y + h - 1, '▀', top_b, COLOR_PLATE_BG)
                self.canvas.set_cell(x + w - 1, y + h - 1, '▘', top_b, COLOR_PLATE_BG)

            # Keycap interior body & lateral borders
            glyph = glyph_set.get(label, None)
            max_glyph_lines = len(glyph) if glyph else 0

            for dy in range(1, h - 1):
                cur_y = y + dy
                self.canvas.set_cell(x, cur_y, '│' if not is_pressed else '▌', side_b, COLOR_PLATE_BG)
                self.canvas.set_cell(x + w - 1, cur_y, '│' if not is_pressed else '▐', side_b, COLOR_PLATE_BG)

                # Fill keycap face
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, cur_y, ' ', fg_col, bg_col)

                # Render block font glyph
                gy = dy - 1
                if glyph and gy < max_glyph_lines:
                    glyph_row = glyph[gy]
                    pad_l = max(0, (w - 2 - len(glyph_row)) // 2)
                    for ci, ch in enumerate(glyph_row[:w-2]):
                        self.canvas.set_cell(x + 1 + pad_l + ci, cur_y, ch, fg_col, bg_col, bold=True)
                elif is_mod and dy == max(1, (h - 2) // 2):
                    lbl = label[:w-2]
                    pad_l = max(0, (w - 2 - len(lbl)) // 2)
                    for ci, ch in enumerate(lbl):
                        self.canvas.set_cell(x + 1 + pad_l + ci, cur_y, ch, fg_col, bg_col, bold=True)
                elif is_space and dy == max(1, (h - 2) // 2):
                    bar_w = max(1, w - 6)
                    pad_l = max(0, (w - 2 - bar_w) // 2)
                    for ci in range(bar_w):
                        self.canvas.set_cell(x + 1 + pad_l + ci, cur_y, '━', (170, 165, 155), bg_col)

    def draw_hands_and_fingers(self):
        """Renders shaded ASCII palms, wrists, and animated fingers layered over keyboard."""
        kx = self.kbd_x
        row4_bot = self.kbd_y + self.kbd_h
        screen_bot = self.term_h

        # 1. Left Palm & Wrist (Anatomically sculpted)
        left_wrist_x1 = kx + int(self.unit_w * 1.1)
        left_wrist_x2 = kx + int(self.unit_w * 5.2)

        for y in range(row4_bot - 1, screen_bot):
            prog = (y - (row4_bot - 1)) / max(1, (screen_bot - (row4_bot - 1)))
            x_min = int(left_wrist_x1 + 4 * prog)
            x_max = int(left_wrist_x2 - 2 * prog)

            for x in range(x_min, x_max + 1):
                dist_edge = min(x - x_min, x_max - x)
                if dist_edge == 0:
                    ch = '│' if (x == x_min or x == x_max) else '░'
                    col = SKIN_LOW
                elif dist_edge == 1:
                    ch = '▒'
                    col = SKIN_MID
                else:
                    ch = '█'
                    # Thenar eminence highlight (thumb pad muscle)
                    col = SKIN_HIGHLIGHT if (x - x_min) in (4, 5, 6, 7) and prog < 0.6 else SKIN_MID
                self.canvas.set_cell(x, y, ch, col, None)

        # 2. Right Palm & Wrist
        right_wrist_x1 = kx + int(self.unit_w * 7.2)
        right_wrist_x2 = kx + int(self.unit_w * 11.8)

        for y in range(row4_bot - 1, screen_bot):
            prog = (y - (row4_bot - 1)) / max(1, (screen_bot - (row4_bot - 1)))
            x_min = int(right_wrist_x1 + 2 * prog)
            x_max = int(right_wrist_x2 - 4 * prog)

            for x in range(x_min, x_max + 1):
                dist_edge = min(x - x_min, x_max - x)
                if dist_edge == 0:
                    ch = '│' if (x == x_min or x == x_max) else '░'
                    col = SKIN_LOW
                elif dist_edge == 1:
                    ch = '▒'
                    col = SKIN_MID
                else:
                    ch = '█'
                    col = SKIN_HIGHLIGHT if (x_max - x) in (4, 5, 6, 7) and prog < 0.6 else SKIN_MID
                self.canvas.set_cell(x, y, ch, col, None)

        # 3. Draw All 10 Fingers (Shafts + Fingertips)
        for finger in self.fingers:
            self._draw_single_finger(finger)

    def _draw_single_finger(self, f: AnimatedFinger):
        """Draws finger shaft from knuckle to fingertip and shaped nail/pad."""
        bx, by = f.knuckle_x, f.knuckle_y
        tx, ty = f.cur_x, f.cur_y
        striking = f.is_striking

        # Linear shaft traversal
        length = math.hypot(tx - bx, ty - by)
        steps = max(1, int(length * 2.2))

        for s in range(steps):
            t = s / steps
            cx = bx + (tx - bx) * t
            cy = by + (ty - by) * t
            ix = int(round(cx))
            iy = int(round(cy))

            # Draw 3-character wide finger shaft with lateral contour
            self.canvas.set_cell(ix - 1, iy, '▒', SKIN_LOW, None)
            self.canvas.set_cell(ix, iy, '█', SKIN_HIGHLIGHT if s % 4 == 0 else SKIN_MID, None)
            self.canvas.set_cell(ix + 1, iy, '▒', SKIN_LOW, None)

        # Draw Distinct Fingertip (Nail, Cuticle, Pad Cushion)
        itx = int(round(tx))
        ity = int(round(ty))
        nail_col = NAIL_STRIKE if striking else NAIL_COLOR

        # Fingertip upper arch & nail
        self.canvas.set_cell(itx - 1, ity - 1, '╭', SKIN_LOW, None)
        self.canvas.set_cell(itx, ity - 1, '▀', nail_col, None, bold=striking)
        self.canvas.set_cell(itx + 1, ity - 1, '╮', SKIN_LOW, None)

        # Fingertip pad
        self.canvas.set_cell(itx - 2, ity, '(', SKIN_LOW, None)
        self.canvas.set_cell(itx - 1, ity, '▓', SKIN_MID, None)
        self.canvas.set_cell(itx, ity, '█', nail_col if striking else SKIN_HIGHLIGHT, None, bold=striking)
        self.canvas.set_cell(itx + 1, ity, '▓', SKIN_MID, None)
        self.canvas.set_cell(itx + 2, ity, ')', SKIN_LOW, None)

        # Fingertip lower joint
        self.canvas.set_cell(itx - 1, ity + 1, '│', SKIN_LOW, None)
        self.canvas.set_cell(itx, ity + 1, '█', SKIN_MID, None)
        self.canvas.set_cell(itx + 1, ity + 1, '│', SKIN_LOW, None)

    # ------------------------------------------------------------------------
    # Simulation & State Updates
    # ------------------------------------------------------------------------

    def update_simulation(self, now: float):
        """Updates finger animation states and automated typing demo cadence."""
        self.active_depressed_keys.clear()

        # Update all 10 fingers
        for finger in self.fingers:
            struck = finger.update(now)
            if struck:
                self.active_depressed_keys.add(struck)

        # Update automated typing demo loop
        if self.demo_mode:
            drill_text = self.DEMO_DRILLS[self.current_drill_idx]
            if self.drill_char_idx < len(drill_text):
                next_char = drill_text[self.drill_char_idx]
                target_norm = next_char.upper()
                if next_char in SHIFTED_MAP:
                    target_norm = SHIFTED_MAP[next_char]
                elif next_char == ' ':
                    target_norm = "SPACE"
                self.target_key = target_norm

                if now - self.last_demo_strike_time >= self.demo_char_delay:
                    self.trigger_key_strike(next_char)
                    self.drill_char_idx += 1
                    self.last_demo_strike_time = now
                    # Natural typing cadence jitter
                    self.demo_char_delay = random.uniform(0.12, 0.20)
            else:
                # Advance to next drill after brief pause
                if now - self.last_demo_strike_time >= 1.2:
                    self.current_drill_idx = (self.current_drill_idx + 1) % len(self.DEMO_DRILLS)
                    self.drill_char_idx = 0
                    self.last_demo_strike_time = now
        else:
            self.target_key = None

    def render_frame(self):
        """Assembles all layers onto canvas and performs atomic zero-flicker flush."""
        self.canvas.clear()
        self.draw_hud()
        self.draw_keyboard_chassis()
        self.draw_keycaps()
        self.draw_hands_and_fingers()
        output = self.canvas.render()
        sys.stdout.write(output)
        sys.stdout.flush()

    # ------------------------------------------------------------------------
    # Terminal Setup / Teardown & Event Loop
    # ------------------------------------------------------------------------

    def setup_terminal(self):
        """Puts terminal in cbreak raw mode and hides cursor."""
        if sys.stdin.isatty():
            self.old_termios = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        # Hide cursor & clear screen once
        sys.stdout.write("\033[?25l\033[2J")
        sys.stdout.flush()

    def restore_terminal(self):
        """Restores terminal settings, cursor, and normal text attributes."""
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()
        if self.old_termios and sys.stdin.isatty():
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_termios)

    def handle_input(self):
        """Reads non-blocking user keystrokes."""
        if not sys.stdin.isatty():
            return

        r, _, _ = select.select([sys.stdin], [], [], 0)
        if not r:
            return

        ch = sys.stdin.read(1)
        if not ch:
            return

        # Exit controls
        if ch in ('\x03', 'q', 'Q'):  # Ctrl+C or Q
            self.running = False
            return
        elif ch == '\x1b':  # ESC sequence
            r_seq, _, _ = select.select([sys.stdin], [], [], 0.02)
            if not r_seq:
                self.running = False
                return
            else:
                _ = sys.stdin.read(2)
                return

        elif ch == '\t':  # TAB toggles Demo Mode
            self.demo_mode = not self.demo_mode
            self.drill_char_idx = 0
            self.last_demo_strike_time = time.time()
            return

        # Interactive typing mode
        if not self.demo_mode:
            self.trigger_key_strike(ch)

    def run(self, max_frames: Optional[int] = None):
        """Main 60 FPS double-buffered event loop."""
        self.setup_terminal()
        signal.signal(signal.SIGWINCH, lambda sig, frame: self.on_terminal_resize())

        target_dt = 1.0 / 60.0  # 60 FPS
        frames_rendered = 0

        try:
            while self.running:
                t_start = time.time()
                self.handle_input()
                self.update_simulation(t_start)
                self.render_frame()

                frames_rendered += 1
                if max_frames and frames_rendered >= max_frames:
                    break

                t_end = time.time()
                sleep_time = target_dt - (t_end - t_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        finally:
            self.restore_terminal()


# ============================================================================
# Entry Point
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Vintage Typing Instructor Hands-on-Keyboard CLI")
    parser.add_argument("--interactive", action="store_true", help="Start directly in interactive typing mode")
    parser.add_argument("--frames", type=int, default=None, help="Run for N frames and exit (for automated testing)")
    args = parser.parse_args()

    app = TypingInstructorApp()
    if args.interactive:
        app.demo_mode = False

    atexit.register(app.restore_terminal)
    app.run(max_frames=args.frames)

if __name__ == "__main__":
    main()
