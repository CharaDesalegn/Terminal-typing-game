#!/usr/bin/env python3
r"""
Vintage Typing Instructor - Hands-on-Keyboard Terminal CLI Application
Features:
  - Full-window ANSI canvas centering a mechanical keyboard and realistic typing hands.
  - Large multi-line ASCII block keycaps with 3x3 block letter glyphs.
  - Layered density-shaded ASCII hands (█, ▓, ▒, ░, (, ), /, \) with realistic anatomy.
  - Dynamic finger reach, keycap depression, and retraction animation cycle.
  - 24-bit TrueColor ANSI palette with 4 selectable retro themes (IBM Model M, Cyberpunk, Phosphor CRT, Apple II).
  - 3 operating modes: Guided Lesson (interactive drill practice with real-time finger coaching),
    Free Key Explorer (type freely to see hands move), and Automated Demo (watch typing tutor).
  - Multi-category drill library (Home Row, E/I additions, Pangrams, Numbers & Symbols).
  - Real-time WPM, accuracy, streak, error highlighting, and flicker-free double buffering.
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
# 24-Bit TrueColor ANSI Helpers & Color Themes
# ============================================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

def fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"

# Theme Definitions
THEMES = [
    {
        "name": "IBM Model M (1985)",
        "desk_bg": (16, 18, 22),
        "chassis_bg": (36, 39, 46),
        "chassis_border": (82, 88, 102),
        "chassis_shadow": (22, 24, 28),
        "plate_bg": (24, 26, 30),
        "alpha_bg": (220, 216, 206),
        "alpha_fg": (32, 35, 42),
        "alpha_top": (245, 243, 238),
        "alpha_bot": (155, 150, 140),
        "alpha_side": (192, 188, 178),
        "mod_bg": (138, 134, 128),
        "mod_fg": (240, 240, 240),
        "mod_top": (170, 166, 160),
        "mod_bot": (98, 94, 90),
        "mod_side": (124, 120, 115),
        "active_bg": (0, 235, 255),      # Neon Cyan
        "active_fg": (10, 16, 26),
        "active_border": (0, 180, 220),
        "error_bg": (255, 50, 60),       # Error Red
        "target_border": (255, 205, 40), # Gold Target
        "skin_high": (248, 214, 188),
        "skin_mid": (222, 170, 132),
        "skin_low": (172, 118, 84),
        "nail_col": (252, 232, 220),
    },
    {
        "name": "Cyberpunk 2077 / Synthwave",
        "desk_bg": (12, 8, 22),
        "chassis_bg": (32, 16, 48),
        "chassis_border": (110, 45, 155),
        "chassis_shadow": (18, 8, 28),
        "plate_bg": (20, 10, 32),
        "alpha_bg": (48, 32, 68),
        "alpha_fg": (230, 210, 255),
        "alpha_top": (75, 52, 105),
        "alpha_bot": (30, 18, 45),
        "alpha_side": (58, 40, 82),
        "mod_bg": (80, 24, 75),
        "mod_fg": (255, 200, 240),
        "mod_top": (115, 42, 108),
        "mod_bot": (52, 14, 50),
        "mod_side": (90, 30, 85),
        "active_bg": (255, 30, 130),     # Hot Magenta Pink
        "active_fg": (255, 255, 255),
        "active_border": (255, 100, 180),
        "error_bg": (255, 30, 30),
        "target_border": (0, 245, 255),  # Electric Cyan Target
        "skin_high": (250, 200, 180),
        "skin_mid": (215, 150, 140),
        "skin_low": (155, 95, 100),
        "nail_col": (255, 220, 240),
    },
    {
        "name": "Retro Phosphor CRT (Matrix)",
        "desk_bg": (8, 14, 10),
        "chassis_bg": (18, 28, 22),
        "chassis_border": (45, 85, 55),
        "chassis_shadow": (10, 18, 12),
        "plate_bg": (12, 20, 15),
        "alpha_bg": (22, 45, 30),
        "alpha_fg": (75, 255, 130),
        "alpha_top": (38, 72, 50),
        "alpha_bot": (14, 30, 20),
        "alpha_side": (28, 55, 38),
        "mod_bg": (32, 60, 42),
        "mod_fg": (150, 255, 180),
        "mod_top": (50, 90, 65),
        "mod_bot": (20, 40, 28),
        "mod_side": (40, 75, 52),
        "active_bg": (50, 255, 90),      # Blinding Green
        "active_fg": (6, 20, 10),
        "active_border": (130, 255, 160),
        "error_bg": (255, 60, 40),
        "target_border": (255, 230, 50),
        "skin_high": (230, 220, 180),
        "skin_mid": (185, 175, 130),
        "skin_low": (130, 120, 85),
        "nail_col": (245, 240, 210),
    },
    {
        "name": "Apple Extended Keyboard II",
        "desk_bg": (22, 22, 22),
        "chassis_bg": (212, 206, 192),
        "chassis_border": (240, 235, 222),
        "chassis_shadow": (160, 154, 142),
        "plate_bg": (145, 140, 130),
        "alpha_bg": (242, 239, 232),
        "alpha_fg": (35, 35, 38),
        "alpha_top": (255, 255, 250),
        "alpha_bot": (195, 190, 180),
        "alpha_side": (225, 220, 212),
        "mod_bg": (185, 180, 170),
        "mod_fg": (40, 40, 45),
        "mod_top": (210, 205, 195),
        "mod_bot": (145, 140, 130),
        "mod_side": (170, 165, 155),
        "active_bg": (255, 165, 25),      # Vintage Amber
        "active_fg": (15, 15, 20),
        "active_border": (255, 200, 80),
        "error_bg": (240, 50, 50),
        "target_border": (0, 180, 240),
        "skin_high": (248, 214, 188),
        "skin_mid": (222, 170, 132),
        "skin_low": (172, 118, 84),
        "nail_col": (252, 232, 220),
    }
]

# HUD Accents
COLOR_HUD_BG          = (24, 27, 34)
COLOR_HUD_BORDER      = (60, 66, 80)
COLOR_ACCENT_CYAN     = (0, 235, 255)
COLOR_ACCENT_GREEN    = (70, 235, 120)
COLOR_ACCENT_AMBER    = (255, 185, 40)
COLOR_ACCENT_PINK     = (255, 90, 140)
COLOR_ACCENT_RED      = (255, 60, 60)

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
        self.fg = [[(200, 200, 200) for _ in range(width)] for _ in range(height)]
        self.bg = [[(16, 18, 22) for _ in range(width)] for _ in range(height)]
        self.bold = [[False for _ in range(width)] for _ in range(height)]

    def clear(self, desk_bg: Tuple[int, int, int]):
        for y in range(self.height):
            for x in range(self.width):
                self.chars[y][x] = ' '
                self.fg[y][x] = (200, 200, 200)
                self.bg[y][x] = desk_bg
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

class AppMode:
    GUIDED_LESSON = 0
    FREE_PLAY = 1
    AUTO_DEMO = 2

class TypingInstructorApp:
    DRILL_CATEGORIES = [
        ("Home Row Basics", "asdf jkl; a sad lad fall ask flask fall all salad"),
        ("Home Row + E & I", "fee side leaf lake slide jade deals alike safe fake deed"),
        ("Home Row + R & U", "dark surf fur rail run rural standard flare unfair dark"),
        ("Full Alphabet Pangram", "the quick brown fox jumps over the lazy dog"),
        ("Vintage Mechanical Drill", "touch typing with vintage ibm model m buckling springs"),
        ("Numbers & Symbols", "12345 67890 !@#$% ^&*() - = + _ [ ] { } ; : ' \" , . / ?"),
    ]

    def __init__(self):
        self.term_w, self.term_h = shutil.get_terminal_size((110, 42))
        self.canvas = Canvas(self.term_w, self.term_h)

        # Dynamic layout parameters
        self._calculate_dimensions()

        self.keys: Dict[str, Dict[str, Any]] = {}
        self.fingers: List[AnimatedFinger] = []

        # Modes & Themes
        self.mode = AppMode.AUTO_DEMO
        self.theme_idx = 0
        self.drill_cat_idx = 0
        self.drill_char_idx = 0
        self.last_demo_strike_time = 0.0
        self.demo_char_delay = 0.16

        self.active_depressed_keys: set[str] = set()
        self.mistyped_key: Optional[str] = None
        self.mistyped_until: float = 0.0
        self.target_key: Optional[str] = None
        self.last_pressed_finger_name: str = "Ready"
        self.tutor_feedback: str = "Welcome! Practice proper touch-typing technique."

        # Typing stats
        self.total_keypresses = 0
        self.correct_keypresses = 0
        self.streak = 0
        self.errors = 0
        self.start_time = time.time()
        self.wpm = 0.0
        self.accuracy = 100.0

        # Termios backup
        self.old_termios = None
        self.running = True

        self._build_keyboard_geometry()
        self._init_fingers()

    @property
    def theme(self) -> Dict[str, Any]:
        return THEMES[self.theme_idx]

    @property
    def current_drill_text(self) -> str:
        return self.DRILL_CATEGORIES[self.drill_cat_idx][1]

    @property
    def current_drill_name(self) -> str:
        return self.DRILL_CATEGORIES[self.drill_cat_idx][0]

    def _calculate_dimensions(self):
        """Calculates optimal key width, key height, and canvas centering."""
        if self.term_w >= 115:
            self.unit_w = 7
        elif self.term_w >= 85:
            self.unit_w = 5
        else:
            self.unit_w = max(4, (self.term_w - 6) // 15)

        if self.term_h >= 36:
            self.unit_h = 5
        elif self.term_h >= 28:
            self.unit_h = 4
        else:
            self.unit_h = 3

        self.kbd_w = 15 * self.unit_w
        self.kbd_h = 5 * self.unit_h
        self.kbd_x = max(2, (self.term_w - self.kbd_w) // 2)

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

    def _normalize_key(self, char_or_key: str) -> str:
        norm = char_or_key.upper()
        if char_or_key in SHIFTED_MAP:
            norm = SHIFTED_MAP[char_or_key]
        elif char_or_key == ' ':
            norm = "SPACE"
        elif char_or_key in ('\r', '\n'):
            norm = "ENTER"
        elif char_or_key in ('\x7f', '\x08'):
            norm = "BACKSPACE"
        return norm

    def trigger_key_strike(self, char_or_key: str):
        """Triggers the corresponding finger to reach, depress, and retract."""
        norm_key = self._normalize_key(char_or_key)
        target_data = self.keys.get(norm_key)
        if not target_data:
            return

        finger_idx = target_data['finger']
        if 0 <= finger_idx < len(self.fingers):
            finger = self.fingers[finger_idx]
            tx = target_data['center_x']
            ty = target_data['center_y']
            finger.strike_target(tx, ty, norm_key)
            self.last_pressed_finger_name = finger.name

    def handle_interactive_stroke(self, char_pressed: str):
        """Processes keystroke in Guided Lesson or Free Play mode."""
        self.total_keypresses += 1
        norm_pressed = self._normalize_key(char_pressed)

        # Trigger finger animation for whichever key was hit
        self.trigger_key_strike(char_pressed)

        if self.mode == AppMode.GUIDED_LESSON:
            drill_text = self.current_drill_text
            if self.drill_char_idx < len(drill_text):
                expected_char = drill_text[self.drill_char_idx]
                norm_expected = self._normalize_key(expected_char)

                if norm_pressed == norm_expected:
                    # Correct strike!
                    self.correct_keypresses += 1
                    self.streak += 1
                    self.drill_char_idx += 1
                    f_name = FINGER_NAMES[KEY_TO_FINGER.get(norm_expected, 0)]
                    self.tutor_feedback = f"Great! Hit '{expected_char}' with {f_name}."

                    if self.drill_char_idx >= len(drill_text):
                        self.drill_char_idx = 0
                        self.drill_cat_idx = (self.drill_cat_idx + 1) % len(self.DRILL_CATEGORIES)
                        self.tutor_feedback = f"Drill completed! Advanced to: {self.current_drill_name}"
                else:
                    # Mistake!
                    self.errors += 1
                    self.streak = 0
                    self.mistyped_key = norm_pressed
                    self.mistyped_until = time.time() + 0.22
                    exp_finger = FINGER_NAMES[KEY_TO_FINGER.get(norm_expected, 0)]
                    got_finger = FINGER_NAMES[KEY_TO_FINGER.get(norm_pressed, 0)]
                    self.tutor_feedback = f"Oops: Pressed '{char_pressed}' ({got_finger}) instead of '{expected_char}' ({exp_finger})!"

        elif self.mode == AppMode.FREE_PLAY:
            self.correct_keypresses += 1
            self.streak += 1
            f_name = FINGER_NAMES[KEY_TO_FINGER.get(norm_pressed, 0)]
            self.tutor_feedback = f"Key '{norm_pressed}' triggered {f_name}."

        # Update metrics
        elapsed_m = max(0.05, (time.time() - self.start_time) / 60.0)
        self.wpm = (self.correct_keypresses / 5.0) / elapsed_m
        if self.total_keypresses > 0:
            self.accuracy = (self.correct_keypresses / self.total_keypresses) * 100.0

    # ------------------------------------------------------------------------
    # Drawing Pipeline
    # ------------------------------------------------------------------------

    def draw_hud(self):
        """Renders top vintage status HUD, indicators, and metrics."""
        t = self.theme
        mode_labels = {
            AppMode.GUIDED_LESSON: ("[ MODE: GUIDED LESSON ]", COLOR_ACCENT_CYAN),
            AppMode.FREE_PLAY:     ("[ MODE: FREE KEY EXPLORER ]", COLOR_ACCENT_AMBER),
            AppMode.AUTO_DEMO:     ("[ MODE: AUTOMATED DEMO ]", COLOR_ACCENT_GREEN),
        }
        mode_str, mode_col = mode_labels[self.mode]

        # Line 0: Header & Controls
        title = " ⌨  VINTAGE TYPING INSTRUCTOR  //  IBM MODEL M MECHANICAL  "
        self.canvas.draw_text(self.kbd_x, 0, title, COLOR_ACCENT_AMBER, COLOR_HUD_BG, bold=True)
        self.canvas.draw_text(self.kbd_x + len(title) + 2, 0, mode_str, mode_col, COLOR_HUD_BG, bold=True)

        controls = f"  [TAB] Mode  │  [T] Theme: {t['name'][:14]}  │  [D] Drill  │  [ESC] Quit"
        self.canvas.draw_text(self.kbd_x, 1, controls, (180, 190, 205), COLOR_HUD_BG)

        # Line 2: Metrics Bar
        metrics = (
            f"  WPM: {self.wpm:5.1f}  │  ACCURACY: {self.accuracy:5.1f}%  │  "
            f"STREAK: {self.streak:3d}  │  ERRORS: {self.errors:2d}  │  "
            f"FINGER: {self.last_pressed_finger_name:<12}"
        )
        self.canvas.draw_text(self.kbd_x, 2, metrics, (215, 220, 230), COLOR_HUD_BG, bold=True)

        # Line 3: Drill Prompt or Feedback
        if self.mode in (AppMode.GUIDED_LESSON, AppMode.AUTO_DEMO):
            drill_text = self.current_drill_text
            prompt = f"  [{self.current_drill_name}]: " + drill_text
            self.canvas.draw_text(self.kbd_x, 3, prompt, (160, 175, 195), t["desk_bg"])

            # Highlight current target character
            target_col = self.kbd_x + len(f"  [{self.current_drill_name}]: ") + self.drill_char_idx
            ch = drill_text[self.drill_char_idx] if self.drill_char_idx < len(drill_text) else " "
            self.canvas.draw_text(target_col, 3, ch, t["active_fg"], t["active_bg"], bold=True)

        # Line 4: Tutor Coaching Tip
        tip_line = f"  👉 {self.tutor_feedback}"
        tip_col = COLOR_ACCENT_RED if "Oops" in self.tutor_feedback else COLOR_ACCENT_GREEN
        self.canvas.draw_text(self.kbd_x, 4, tip_line, tip_col, t["desk_bg"], bold=True)

    def draw_keyboard_chassis(self):
        """Renders outer beveled frame, badge, and LEDs for retro mechanical chassis."""
        t = self.theme
        kx = self.kbd_x
        ky = self.kbd_y
        kw = self.kbd_w
        kh = self.kbd_h

        # Switch plate well
        for y in range(ky - 1, ky + kh + 1):
            for x in range(kx - 1, kx + kw + 1):
                self.canvas.set_cell(x, y, ' ', None, t["plate_bg"])

        # Beveled chassis enclosure
        bx1 = kx - 2
        by1 = ky - 1
        bx2 = kx + kw + 1
        by2 = ky + kh

        for x in range(bx1, bx2 + 1):
            self.canvas.set_cell(x, by1, '═', t["chassis_border"], t["chassis_bg"])
            self.canvas.set_cell(x, by2, '═', t["chassis_shadow"], t["chassis_bg"])

        for y in range(by1, by2 + 1):
            self.canvas.set_cell(bx1, y, '║', t["chassis_border"], t["chassis_bg"])
            self.canvas.set_cell(bx2, y, '║', t["chassis_shadow"], t["chassis_bg"])

        self.canvas.set_cell(bx1, by1, '╔', t["chassis_border"], t["chassis_bg"])
        self.canvas.set_cell(bx2, by1, '╗', t["chassis_border"], t["chassis_bg"])
        self.canvas.set_cell(bx1, by2, '╚', t["chassis_border"], t["chassis_bg"])
        self.canvas.set_cell(bx2, by2, '╝', t["chassis_shadow"], t["chassis_bg"])

        # Vintage Badge & Status LEDs
        badge = " [ IBM MODEL M ] "
        self.canvas.draw_text(bx1 + 3, by1, badge, (190, 195, 205), t["chassis_bg"], bold=True)

        leds = " [ NUM ⬤ ] [ CAPS ◯ ] [ SCROLL ◯ ] "
        if bx2 - len(leds) - 2 > bx1 + len(badge) + 6:
            self.canvas.draw_text(bx2 - len(leds) - 1, by1, leds, (140, 220, 160), t["chassis_bg"])

    def draw_keycaps(self):
        """Renders large multi-line ASCII block keycaps with centered block font glyphs."""
        t = self.theme
        glyph_set = GLYPHS_3X3 if self.unit_h >= 5 else GLYPHS_2X3
        now = time.time()

        for key_id, k in self.keys.items():
            x, y, w, h = k['x'], k['y'], k['w'], k['h']
            label = k['label']
            is_mod = k['is_modifier']
            is_space = k['is_space']
            is_pressed = key_id in self.active_depressed_keys
            is_mistyped = (key_id == self.mistyped_key) and (now < self.mistyped_until)
            is_target = (key_id == self.target_key) and not is_pressed

            # Color styling
            if is_mistyped:
                bg_col = t["error_bg"]
                fg_col = (255, 255, 255)
                top_b = (255, 120, 120)
                bot_b = (180, 20, 20)
                side_b = (220, 40, 40)
            elif is_pressed:
                bg_col = t["active_bg"]
                fg_col = t["active_fg"]
                top_b = t["active_border"]
                bot_b = t["active_border"]
                side_b = t["active_border"]
            elif is_mod:
                bg_col = t["mod_bg"]
                fg_col = t["mod_fg"]
                top_b = t["mod_top"]
                bot_b = t["mod_bot"]
                side_b = t["mod_side"]
            else:
                bg_col = t["alpha_bg"]
                fg_col = t["alpha_fg"]
                top_b = t["target_border"] if is_target else t["alpha_top"]
                bot_b = t["alpha_bot"]
                side_b = t["alpha_side"]

            # Physical 3D keycap beveling
            if not is_pressed and not is_mistyped:
                self.canvas.set_cell(x, y, '┌', top_b, t["plate_bg"])
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y, '─', top_b, t["plate_bg"])
                self.canvas.set_cell(x + w - 1, y, '┐', top_b, t["plate_bg"])

                self.canvas.set_cell(x, y + h - 1, '└', bot_b, t["plate_bg"])
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y + h - 1, '─', bot_b, t["plate_bg"])
                self.canvas.set_cell(x + w - 1, y + h - 1, '┘', bot_b, t["plate_bg"])
            else:
                self.canvas.set_cell(x, y, '▗', bot_b, t["plate_bg"])
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y, '▄', bot_b, t["plate_bg"])
                self.canvas.set_cell(x + w - 1, y, '▖', bot_b, t["plate_bg"])

                self.canvas.set_cell(x, y + h - 1, '▝', top_b, t["plate_bg"])
                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, y + h - 1, '▀', top_b, t["plate_bg"])
                self.canvas.set_cell(x + w - 1, y + h - 1, '▘', top_b, t["plate_bg"])

            # Keycap interior body & lateral borders
            glyph = glyph_set.get(label, None)
            max_glyph_lines = len(glyph) if glyph else 0

            for dy in range(1, h - 1):
                cur_y = y + dy
                self.canvas.set_cell(x, cur_y, '│' if not (is_pressed or is_mistyped) else '▌', side_b, t["plate_bg"])
                self.canvas.set_cell(x + w - 1, cur_y, '│' if not (is_pressed or is_mistyped) else '▐', side_b, t["plate_bg"])

                for ix in range(x + 1, x + w - 1):
                    self.canvas.set_cell(ix, cur_y, ' ', fg_col, bg_col)

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
        t = self.theme
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
                    col = t["skin_low"]
                elif dist_edge == 1:
                    ch = '▒'
                    col = t["skin_mid"]
                else:
                    ch = '█'
                    col = t["skin_high"] if (x - x_min) in (4, 5, 6, 7) and prog < 0.6 else t["skin_mid"]
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
                    col = t["skin_low"]
                elif dist_edge == 1:
                    ch = '▒'
                    col = t["skin_mid"]
                else:
                    ch = '█'
                    col = t["skin_high"] if (x_max - x) in (4, 5, 6, 7) and prog < 0.6 else t["skin_mid"]
                self.canvas.set_cell(x, y, ch, col, None)

        # 3. Draw All 10 Fingers (Shafts + Fingertips)
        for finger in self.fingers:
            self._draw_single_finger(finger)

    def _draw_single_finger(self, f: AnimatedFinger):
        """Draws finger shaft from knuckle to fingertip and shaped nail/pad."""
        t = self.theme
        bx, by = f.knuckle_x, f.knuckle_y
        tx, ty = f.cur_x, f.cur_y
        striking = f.is_striking

        length = math.hypot(tx - bx, ty - by)
        steps = max(1, int(length * 2.2))

        for s in range(steps):
            prog = s / steps
            cx = bx + (tx - bx) * prog
            cy = by + (ty - by) * prog
            ix = int(round(cx))
            iy = int(round(cy))

            self.canvas.set_cell(ix - 1, iy, '▒', t["skin_low"], None)
            self.canvas.set_cell(ix, iy, '█', t["skin_high"] if s % 4 == 0 else t["skin_mid"], None)
            self.canvas.set_cell(ix + 1, iy, '▒', t["skin_low"], None)

        itx = int(round(tx))
        ity = int(round(ty))
        nail_col = (255, 255, 255) if striking else t["nail_col"]

        # Upper nail
        self.canvas.set_cell(itx - 1, ity - 1, '╭', t["skin_low"], None)
        self.canvas.set_cell(itx, ity - 1, '▀', nail_col, None, bold=striking)
        self.canvas.set_cell(itx + 1, ity - 1, '╮', t["skin_low"], None)

        # Pad
        self.canvas.set_cell(itx - 2, ity, '(', t["skin_low"], None)
        self.canvas.set_cell(itx - 1, ity, '▓', t["skin_mid"], None)
        self.canvas.set_cell(itx, ity, '█', nail_col if striking else t["skin_high"], None, bold=striking)
        self.canvas.set_cell(itx + 1, ity, '▓', t["skin_mid"], None)
        self.canvas.set_cell(itx + 2, ity, ')', t["skin_low"], None)

        # Lower joint
        self.canvas.set_cell(itx - 1, ity + 1, '│', t["skin_low"], None)
        self.canvas.set_cell(itx, ity + 1, '█', t["skin_mid"], None)
        self.canvas.set_cell(itx + 1, ity + 1, '│', t["skin_low"], None)

    # ------------------------------------------------------------------------
    # Simulation & State Updates
    # ------------------------------------------------------------------------

    def update_simulation(self, now: float):
        """Updates finger animation states and automated typing demo cadence."""
        self.active_depressed_keys.clear()

        for finger in self.fingers:
            struck = finger.update(now)
            if struck:
                self.active_depressed_keys.add(struck)

        # Automated demo mode
        if self.mode == AppMode.AUTO_DEMO:
            drill_text = self.current_drill_text
            if self.drill_char_idx < len(drill_text):
                next_char = drill_text[self.drill_char_idx]
                norm_key = self._normalize_key(next_char)
                self.target_key = norm_key
                f_name = FINGER_NAMES[KEY_TO_FINGER.get(norm_key, 0)]
                self.tutor_feedback = f"Automated Demo: '{next_char}' with {f_name}."

                if now - self.last_demo_strike_time >= self.demo_char_delay:
                    self.trigger_key_strike(next_char)
                    self.drill_char_idx += 1
                    self.correct_keypresses += 1
                    self.total_keypresses += 1
                    self.streak += 1
                    self.last_demo_strike_time = now
                    self.demo_char_delay = random.uniform(0.12, 0.19)
            else:
                if now - self.last_demo_strike_time >= 1.2:
                    self.drill_char_idx = 0
                    self.drill_cat_idx = (self.drill_cat_idx + 1) % len(self.DRILL_CATEGORIES)
                    self.last_demo_strike_time = now

        elif self.mode == AppMode.GUIDED_LESSON:
            drill_text = self.current_drill_text
            if self.drill_char_idx < len(drill_text):
                exp_char = drill_text[self.drill_char_idx]
                self.target_key = self._normalize_key(exp_char)
            else:
                self.target_key = None
        else:
            self.target_key = None

    def render_frame(self):
        """Assembles all layers onto canvas and performs atomic zero-flicker flush."""
        self.canvas.clear(self.theme["desk_bg"])
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

        elif ch == '\t':  # TAB cycles Modes (Guided Lesson -> Free Play -> Auto Demo)
            self.mode = (self.mode + 1) % 3
            self.drill_char_idx = 0
            self.last_demo_strike_time = time.time()
            return

        elif ch in ('t', 'T') and self.mode != AppMode.GUIDED_LESSON:  # T cycles Themes
            self.theme_idx = (self.theme_idx + 1) % len(THEMES)
            self.tutor_feedback = f"Switched theme to: {self.theme['name']}"
            return

        elif ch in ('d', 'D') and self.mode != AppMode.GUIDED_LESSON:  # D cycles Drills
            self.drill_cat_idx = (self.drill_cat_idx + 1) % len(self.DRILL_CATEGORIES)
            self.drill_char_idx = 0
            self.last_demo_strike_time = time.time()
            self.tutor_feedback = f"Selected drill: {self.current_drill_name}"
            return

        # Interactive typing stroke
        if self.mode != AppMode.AUTO_DEMO:
            self.handle_interactive_stroke(ch)

    def run(self, max_frames: Optional[int] = None):
        """Main 60 FPS double-buffered event loop."""
        self.setup_terminal()
        signal.signal(signal.SIGWINCH, lambda sig, frame: self.on_terminal_resize())

        target_dt = 1.0 / 60.0
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
    parser.add_argument("--interactive", action="store_true", help="Start directly in Guided Lesson interactive mode")
    parser.add_argument("--free", action="store_true", help="Start directly in Free Key Explorer mode")
    parser.add_argument("--theme", type=int, default=0, help="Theme index (0: IBM Model M, 1: Cyberpunk, 2: Phosphor, 3: Apple)")
    parser.add_argument("--frames", type=int, default=None, help="Run for N frames and exit (for automated testing)")
    args = parser.parse_args()

    app = TypingInstructorApp()
    if args.interactive:
        app.mode = AppMode.GUIDED_LESSON
    elif args.free:
        app.mode = AppMode.FREE_PLAY

    if 0 <= args.theme < len(THEMES):
        app.theme_idx = args.theme

    atexit.register(app.restore_terminal)
    app.run(max_frames=args.frames)

if __name__ == "__main__":
    main()
