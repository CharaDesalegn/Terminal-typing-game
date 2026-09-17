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
- Mode 3 (Tutor): Interactive touch typing tutor with full QWERTY keyboard layout, faded hand &
  finger positions, real-time key-to-finger guidance, and interactive key exploration.
- Mode 4 (Error Board): Track every mistyped letter (e.g., typing E instead of D), with
  comprehensive confusion matrix, finger analysis, all-time vs session stats, and weak-key drills.
- Interactive Top Bar: Clickable via mouse and selectable with keys [1], [2], [3], [4], or [TAB].
- CLI Flags: --sprint (-1), --endless (-2), --tutor (-3), --board (-4), or custom practice text.
"""

import os
import sys
import time
import json
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

# Rich multi-occurrence vocabulary for single-key targeted practice drills (high letter density)
KEY_WORDS_RICH = {
    "a": ["banana", "avalanche", "database", "advantage", "character", "alphabet", "apparatus", "available", "adaptation", "parade", "canal", "drama", "accuracy", "catalyst", "panorama"],
    "b": ["bubble", "barbecue", "bobcat", "bombastic", "backbone", "blackberry", "absorb", "bamboo", "baboon", "blubber", "bombard", "blueberry", "baseball", "billboard", "bluebird"],
    "c": ["circuit", "concrete", "calculate", "accuracy", "circle", "classic", "capacity", "occurred", "critic", "succinct", "eccentric", "concentric", "chocolate", "coincidence", "consequence"],
    "d": ["dedication", "discipline", "decided", "divided", "deadline", "demanded", "dashboard", "definition", "descended", "diamond", "ladder", "middle", "sudden", "redundant", "dependable"],
    "e": ["experience", "element", "reference", "excellence", "evidence", "effective", "enterprise", "teleconference", "settlement", "generate", "remember", "resilience", "equilibrium", "frequency"],
    "f": ["different", "effective", "firefighter", "fluffy", "fulfillment", "fearful", "fraction", "freefall", "offense", "traffic", "stiff", "coffee", "daffodil", "effortless", "cliffside"],
    "g": ["gigantic", "geography", "gargantuan", "language", "giggle", "gorging", "goggles", "gangway", "baggage", "luggage", "trigger", "aggregate", "gorgeous", "highlight", "debugging"],
    "h": ["highland", "heartthrob", "hitchhike", "haphazard", "health", "hypothesis", "heavens", "headache", "hotshot", "hatchback", "highchair", "handshake", "childhood", "thorough", "withstand"],
    "i": ["initiate", "infinite", "individual", "division", "visibility", "definition", "diminish", "illumination", "ignition", "criticism", "implicit", "simplicity", "discipline", "curiosity"],
    "j": ["jumpjack", "jeopardy", "junction", "rejoice", "journey", "judgment", "adjust", "project", "major", "enjoy", "inject", "object", "jungle", "jazz", "jacket", "joyful", "ninja"],
    "k": ["kickback", "knickknack", "knockout", "keyword", "knapsack", "knowledge", "keeper", "knuckle", "backtrack", "kickoff", "kingmaker", "kitchen", "breakneck", "handshake", "smokestack"],
    "l": ["parallel", "collection", "lullaby", "collaborate", "brilliant", "cellular", "level", "loyal", "flawless", "locally", "satellite", "lollipop", "fellowship", "philosophical", "clarity"],
    "m": ["maximum", "memorandum", "mammal", "monument", "movement", "mechanism", "summertime", "symmetry", "mammoth", "minimum", "monogram", "commence", "metamorphosis", "magnificent", "ceremony"],
    "n": ["connection", "nanosecond", "continent", "nonfiction", "announcement", "phenomenon", "ninepins", "nomination", "unknown", "cinnamon", "opponent", "navigation", "generation", "foundation"],
    "o": ["monopoly", "tomorrow", "condition", "cooperation", "composition", "protocol", "orthodox", "photograph", "colorado", "corridor", "octopus", "coordinate", "philosophical", "phenomenon"],
    "p": ["paperclip", "perpendicular", "perspective", "philosophy", "puppy", "pipeline", "popcorn", "passport", "peppercorn", "preposition", "pumpkin", "perspicacity", "appreciate", "performance"],
    "q": ["quantum", "sequence", "frequent", "liquidity", "conquest", "technique", "squadron", "quarantine", "quench", "equator", "quarter", "quick", "quiz", "equilibrium", "unique", "antique", "quality"],
    "r": ["remember", "particular", "resurrection", "recurrence", "mirror", "corridor", "reservoir", "restaurant", "rearward", "reporter", "warrior", "carrier", "perseverance", "orchestra", "structure"],
    "s": ["success", "session", "substance", "stressful", "expression", "statistics", "seamless", "suspension", "possess", "business", "senseless", "sensational", "simplicity", "resilience", "perspicacity"],
    "t": ["tatters", "totalitarian", "attitude", "statement", "constitute", "tentative", "turtleneck", "treatment", "titular", "attract", "texture", "protest", "temperature", "crystallization", "destiny"],
    "u": ["unusual", "ubiquitous", "curriculum", "ultimate", "vacuum", "unfortunate", "voluptuous", "status", "untrue", "sulfur", "autumn", "museum", "future", "curiosity", "unprecedented"],
    "v": ["vivid", "evolve", "survive", "vampire", "movement", "vibrative", "revival", "volvo", "valuable", "verve", "vocalist", "universe", "discovery", "victory", "adventure"],
    "w": ["wildwood", "worldwide", "willow", "backward", "warmwater", "whitewash", "withstand", "windswept", "showcase", "wallward", "woodwork", "wheelbarrow", "whisper", "wonder", "shadow"],
    "x": ["xerox", "maximum", "complex", "extraordinary", "syntax", "matrix", "context", "anxious", "oxygen", "reflex", "flexibility", "mixture", "expansion", "pixel", "exact", "exotic", "toxic"],
    "y": ["yesterday", "sympathy", "mystery", "synergy", "yearbyyear", "yellowy", "joyfully", "dynamically", "polyester", "symmetry", "mystify", "cyclically", "serendipity", "creativity", "curiosity"],
    "z": ["zigzag", "puzzling", "blizzard", "buzzard", "grizzly", "drizzle", "citizen", "horizontal", "haphazard", "dazzle", "bizarre", "piazza", "muzzle", "synchronization", "crystallization", "horizon"]
}

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

# ==============================================================================
# MODE 3 (TUTOR): FINGER GUIDE & TOUCH TYPING DATA STRUCTURES
# ==============================================================================

TUTOR_DRILLS = [
    {
        "name": "Home Row Mastery",
        "desc": "Practice resting home keys (ASDF and JKL;)",
        "text": "asdf jkl; sad dad fad lad ask fads flasks salads"
    },
    {
        "name": "Top Row Reach",
        "desc": "Reach upward from home row (QWERTY UIOP)",
        "text": "qwer tyui op quiet wipe tower wire pretty power"
    },
    {
        "name": "Bottom Row Reach",
        "desc": "Reach downward from home row (ZXCV BNM)",
        "text": "zxcv bnm, . zinc menu comb vexing cab move"
    },
    {
        "name": "Pangram (All 26 Letters)",
        "desc": "Covers every single letter on the keyboard across both hands",
        "text": "the quick brown fox jumps over the lazy dog."
    },
    {
        "name": "Numbers & Symbols",
        "desc": "Practice number keys and basic punctuation",
        "text": "12345 67890 level1 step2 100% (yes/no) item#4"
    },
    {
        "name": "Free Key Explorer",
        "desc": "Press ANY key on your keyboard to test which finger types it!",
        "text": ""
    }
]

FINGER_NAMES = {
    "LP": "Left Pinky",
    "LR": "Left Ring",
    "LM": "Left Middle",
    "LI": "Left Index",
    "LT": "Left Thumb",
    "RT": "Right Thumb",
    "THUMB": "Thumb (Left or Right)",
    "RI": "Right Index",
    "RM": "Right Middle",
    "RR": "Right Ring",
    "RP": "Right Pinky",
}

BASE_KEY_MAP = {
    "~": "`", "!": "1", "@": "2", "#": "3", "$": "4",
    "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
    "_": "-", "+": "=", "{": "[", "}": "]", "|": "\\",
    ":": ";", "\"": "\x27", "<": ",", ">": ".", "?": "/"
}

def get_base_key(ch):
    if not ch:
        return None
    if ch in (' ', 'SPACE'):
        return ' '
    if isinstance(ch, str) and ch.isupper():
        return ch.lower()
    return BASE_KEY_MAP.get(ch, ch)

def needs_shift(ch):
    return ch.isupper() or ch in BASE_KEY_MAP

def repr_ch(ch):
    if ch == ' ':
        return 'SPACE'
    return ch

KEY_FINGER_MAP = {
    # Left Pinky
    "`": ("LP", "Left Pinky", "Reach top-left corner"),
    "~": ("LP", "Left Pinky (with Right Shift)", "Reach top-left corner"),
    "1": ("LP", "Left Pinky", "Reach up from [A]"),
    "!": ("LP", "Left Pinky (with Right Shift)", "Reach up from [A]"),
    "q": ("LP", "Left Pinky", "Reach up-left from [A]"),
    "Q": ("LP", "Left Pinky (with Right Shift)", "Reach up-left from [A]"),
    "a": ("LP", "Left Pinky", "★ Home key (rest position)"),
    "A": ("LP", "Left Pinky (with Right Shift)", "★ Home key (rest position)"),
    "z": ("LP", "Left Pinky", "Reach down-left from [A]"),
    "Z": ("LP", "Left Pinky (with Right Shift)", "Reach down-left from [A]"),
    "Tab": ("LP", "Left Pinky", "Left edge of keyboard"),
    "Caps": ("LP", "Left Pinky", "Left edge of keyboard"),

    # Left Ring
    "2": ("LR", "Left Ring", "Reach up from [S]"),
    "@": ("LR", "Left Ring (with Right Shift)", "Reach up from [S]"),
    "w": ("LR", "Left Ring", "Reach up from [S]"),
    "W": ("LR", "Left Ring (with Right Shift)", "Reach up from [S]"),
    "s": ("LR", "Left Ring", "★ Home key (rest position)"),
    "S": ("LR", "Left Ring (with Right Shift)", "★ Home key (rest position)"),
    "x": ("LR", "Left Ring", "Reach down from [S]"),
    "X": ("LR", "Left Ring (with Right Shift)", "Reach down from [S]"),

    # Left Middle
    "3": ("LM", "Left Middle", "Reach up from [D]"),
    "#": ("LM", "Left Middle (with Right Shift)", "Reach up from [D]"),
    "e": ("LM", "Left Middle", "Reach up from [D]"),
    "E": ("LM", "Left Middle (with Right Shift)", "Reach up from [D]"),
    "d": ("LM", "Left Middle", "★ Home key (rest position)"),
    "D": ("LM", "Left Middle (with Right Shift)", "★ Home key (rest position)"),
    "c": ("LM", "Left Middle", "Reach down from [D]"),
    "C": ("LM", "Left Middle (with Right Shift)", "Reach down from [D]"),

    # Left Index
    "4": ("LI", "Left Index", "Reach up from [F]"),
    "$": ("LI", "Left Index (with Right Shift)", "Reach up from [F]"),
    "5": ("LI", "Left Index", "Reach up-right from [F]"),
    "%": ("LI", "Left Index (with Right Shift)", "Reach up-right from [F]"),
    "r": ("LI", "Left Index", "Reach up from [F]"),
    "R": ("LI", "Left Index (with Right Shift)", "Reach up from [F]"),
    "t": ("LI", "Left Index", "Reach up-right from [F]"),
    "T": ("LI", "Left Index (with Right Shift)", "Reach up-right from [F]"),
    "f": ("LI", "Left Index", "★ Home key with tactile bump [F]"),
    "F": ("LI", "Left Index (with Right Shift)", "★ Home key with tactile bump [F]"),
    "g": ("LI", "Left Index", "Reach right from [F]"),
    "G": ("LI", "Left Index (with Right Shift)", "Reach right from [F]"),
    "v": ("LI", "Left Index", "Reach down from [F]"),
    "V": ("LI", "Left Index (with Right Shift)", "Reach down from [F]"),
    "b": ("LI", "Left Index", "Reach down-right from [F]"),
    "B": ("LI", "Left Index (with Right Shift)", "Reach down-right from [F]"),

    # Thumbs (Spacebar)
    " ": ("THUMB", "Thumb (Left or Right)", "Rest on Spacebar"),

    # Right Index
    "6": ("RI", "Right Index", "Reach up-left from [J]"),
    "^": ("RI", "Right Index (with Left Shift)", "Reach up-left from [J]"),
    "7": ("RI", "Right Index", "Reach up from [J]"),
    "&": ("RI", "Right Index (with Left Shift)", "Reach up from [J]"),
    "y": ("RI", "Right Index", "Reach up-left from [J]"),
    "Y": ("RI", "Right Index (with Left Shift)", "Reach up-left from [J]"),
    "u": ("RI", "Right Index", "Reach up from [J]"),
    "U": ("RI", "Right Index (with Left Shift)", "Reach up from [J]"),
    "h": ("RI", "Right Index", "Reach left from [J]"),
    "H": ("RI", "Right Index (with Left Shift)", "Reach left from [J]"),
    "j": ("RI", "Right Index", "★ Home key with tactile bump [J]"),
    "J": ("RI", "Right Index (with Left Shift)", "★ Home key with tactile bump [J]"),
    "n": ("RI", "Right Index", "Reach down-left from [J]"),
    "N": ("RI", "Right Index (with Left Shift)", "Reach down-left from [J]"),
    "m": ("RI", "Right Index", "Reach down from [J]"),
    "M": ("RI", "Right Index (with Left Shift)", "Reach down from [J]"),

    # Right Middle
    "8": ("RM", "Right Middle", "Reach up from [K]"),
    "*": ("RM", "Right Middle (with Left Shift)", "Reach up from [K]"),
    "i": ("RM", "Right Middle", "Reach up from [K]"),
    "I": ("RM", "Right Middle (with Left Shift)", "Reach up from [K]"),
    "k": ("RM", "Right Middle", "★ Home key (rest position)"),
    "K": ("RM", "Right Middle (with Left Shift)", "★ Home key (rest position)"),
    ",": ("RM", "Right Middle", "Reach down from [K]"),
    "<": ("RM", "Right Middle (with Left Shift)", "Reach down from [K]"),

    # Right Ring
    "9": ("RR", "Right Ring", "Reach up from [L]"),
    "(": ("RR", "Right Ring (with Left Shift)", "Reach up from [L]"),
    "o": ("RR", "Right Ring", "Reach up from [L]"),
    "O": ("RR", "Right Ring (with Left Shift)", "Reach up from [L]"),
    "l": ("RR", "Right Ring", "★ Home key (rest position)"),
    "L": ("RR", "Right Ring (with Left Shift)", "★ Home key (rest position)"),
    ".": ("RR", "Right Ring", "Reach down from [L]"),
    ">": ("RR", "Right Ring (with Left Shift)", "Reach down from [L]"),

    # Right Pinky
    "0": ("RP", "Right Pinky", "Reach up from [;]"),
    ")": ("RP", "Right Pinky (with Left Shift)", "Reach up from [;]"),
    "-": ("RP", "Right Pinky", "Reach up-right from [;]"),
    "_": ("RP", "Right Pinky (with Left Shift)", "Reach up-right from [;]"),
    "=": ("RP", "Right Pinky", "Reach up-right from [;]"),
    "+": ("RP", "Right Pinky (with Left Shift)", "Reach up-right from [;]"),
    "p": ("RP", "Right Pinky", "Reach up from [;]"),
    "P": ("RP", "Right Pinky (with Left Shift)", "Reach up from [;]"),
    "[": ("RP", "Right Pinky", "Reach up-right from [;]"),
    "{": ("RP", "Right Pinky (with Left Shift)", "Reach up-right from [;]"),
    "]": ("RP", "Right Pinky", "Reach up-right from [;]"),
    "}": ("RP", "Right Pinky (with Left Shift)", "Reach up-right from [;]"),
    "\\": ("RP", "Right Pinky", "Far right of top row"),
    "|": ("RP", "Right Pinky (with Left Shift)", "Far right of top row"),
    ";": ("RP", "Right Pinky", "★ Home key (rest position)"),
    ":": ("RP", "Right Pinky (with Left Shift)", "★ Home key (rest position)"),
    "\x27": ("RP", "Right Pinky", "Reach right from [;]"),
    "\"": ("RP", "Right Pinky (with Left Shift)", "Reach right from [;]"),
    "/": ("RP", "Right Pinky", "Reach down from [;]"),
    "?": ("RP", "Right Pinky (with Left Shift)", "Reach down from [;]"),
    "Enter": ("RP", "Right Pinky", "Far right of home row"),
    "Bksp": ("RP", "Right Pinky", "Far right of number row"),
    "Ctrl_L": ("LP", "Left Pinky", "Bottom-left corner"),
    "Alt_L": ("LR", "Left Ring / Thumb", "Bottom row left"),
    "Alt_R": ("RR", "Right Ring / Thumb", "Bottom row right"),
    "Ctrl_R": ("RP", "Right Pinky", "Bottom-right corner"),
    "Shift_L": ("LP", "Left Pinky", "Left Shift key"),
    "Shift_R": ("RP", "Right Pinky", "Right Shift key"),
}

def finger_side(ch):
    info = KEY_FINGER_MAP.get(ch)
    if not info:
        return "LEFT"
    finger_code = info[0]
    if finger_code.startswith("L"):
        return "LEFT"
    elif finger_code.startswith("R"):
        return "RIGHT"
    return "THUMB"

def get_tutor_instruction(active_ch, last_pressed, was_correct, press_elapsed, target_exists, target_char_mistyped=None):
    if not target_exists:
        if last_pressed is not None and press_elapsed < 3.0:
            info = KEY_FINGER_MAP.get(last_pressed, ('THUMB', 'Thumb', 'Rest on Spacebar'))
            return f"👉 Key: [ {repr_ch(last_pressed)} ] ➔ Use {info[1].upper()}  |  {info[2]}", "highlight"
        return "👉 Press ANY key on your keyboard to test which finger and hand to use!", "cyan"

    if active_ch is None:
        return "🏆 Drill Finished! Press [ENTER] for next drill.", "yellow"

    info = KEY_FINGER_MAP.get(active_ch, ('THUMB', 'Thumb (Space)', 'Rest on Spacebar'))
    finger_code, finger_name, finger_hint = info
    disp_target = repr_ch(active_ch)
    shift = needs_shift(active_ch)
    side = finger_side(active_ch)

    if shift:
        shift_key = "RIGHT SHIFT" if side == "LEFT" else "LEFT SHIFT"
        shift_finger = "Right Pinky" if side == "LEFT" else "Left Pinky"
        action = f"Hold [ {shift_key} ] ({shift_finger}) + Press [ {disp_target} ] with {finger_name.upper()}"
    elif active_ch == ' ':
        action = f"Press [ SPACE ] with {finger_name.upper()}  |  {finger_hint}"
    else:
        action = f"Press [ {disp_target} ] with {finger_name.upper()}  |  {finger_hint}"

    # If there was a typo recently:
    if not was_correct and press_elapsed < 2.0 and last_pressed is not None:
        wrong_info = KEY_FINGER_MAP.get(last_pressed, ('?', 'Unknown', ''))
        disp_wrong = repr_ch(last_pressed)
        exp_ch = repr_ch(target_char_mistyped) if target_char_mistyped else disp_target
        return f"❌ Typo: pressed [ {disp_wrong} ] ({wrong_info[1]}) ➔ Expected [ {exp_ch} ]. Press [Back] to fix!", "red"

    # If there was a correct key recently:
    if was_correct and press_elapsed < 0.8 and last_pressed is not None:
        return f"✅ Nice!  👉 {action}", "green"

    return f"👉 {action}", "highlight"

# 60-column true ANSI QWERTY keyboard layout:
# Every row is exactly 60 characters wide with authentic key staggering
KEYBOARD_LAYOUT = [
    # Row 0 (60 cols): 13 keys * 4 = 52, plus [ Bksp ] (8) = 60
    [
        ("`", "LP", "[`]"), ("1", "LP", "[1]"), ("2", "LR", "[2]"), ("3", "LM", "[3]"),
        ("4", "LI", "[4]"), ("5", "LI", "[5]"), ("6", "RI", "[6]"), ("7", "RI", "[7]"),
        ("8", "RM", "[8]"), ("9", "RR", "[9]"), ("0", "RP", "[0]"), ("-", "RP", "[-]"),
        ("=", "RP", "[=]"), ("Bksp", "RP", "[ Bksp ]")
    ],
    # Row 1 (60 cols): [Tab] (5) + 1 gap + 12 keys * 4 (48) + [  \ ] (6) = 60
    [
        ("Tab", "LP", "[Tab]"), ("q", "LP", "[Q]"), ("w", "LR", "[W]"), ("e", "LM", "[E]"),
        ("r", "LI", "[R]"), ("t", "LI", "[T]"), ("y", "RI", "[Y]"), ("u", "RI", "[U]"),
        ("i", "RM", "[I]"), ("o", "RR", "[O]"), ("p", "RP", "[P]"), ("[", "RP", "[{]"),
        ("]", "RP", "[}]"), ("\\", "RP", "[  \\ ]")
    ],
    # Row 2 (60 cols): [ Caps ] (8) + 1 gap + 11 keys * 4 (44) + [Enter] (7) = 60
    [
        ("Caps", "LP", "[ Caps ]"), ("a", "LP", "[A]"), ("s", "LR", "[S]"), ("d", "LM", "[D]"),
        ("f", "LI", "[F]"), ("g", "LI", "[G]"), ("h", "RI", "[H]"), ("j", "RI", "[J]"),
        ("k", "RM", "[K]"), ("l", "RR", "[L]"), (";", "RP", "[;]"), ("\x27", "RP", "[']"),
        ("Enter", "RP", "[Enter]")
    ],
    # Row 3 (60 cols): [ Shift ] (9) + 1 gap + 10 keys * 4 (40) + [  Shift ] (10) = 60
    [
        ("Shift_L", "LP", "[ Shift ]"), ("z", "LP", "[Z]"), ("x", "LR", "[X]"), ("c", "LM", "[C]"),
        ("v", "LI", "[V]"), ("b", "LI", "[B]"), ("n", "RI", "[N]"), ("m", "RI", "[M]"),
        (",", "RM", "[,]"), (".", "RR", "[.]"), ("/", "RP", "[/]"), ("Shift_R", "RP", "[  Shift ]")
    ],
    # Row 4 (60 cols): [Ctrl] (6) + [Alt] (5) + Space (34) + [Alt] (5) + [Ctrl] (6) + 4 gaps = 60
    [
        ("Ctrl_L", "LP", "[Ctrl]"), ("Alt_L", "LR", "[Alt]"),
        (" ", "THUMB", "[             SPACE              ]"),
        ("Alt_R", "RR", "[Alt]"), ("Ctrl_R", "RP", "[Ctrl]")
    ]
]

# 9-line ASCII art hands (60 cols wide, fits comfortably on standard 24-row terminals)
_LH_ART = [
    " Pinky Ring Mid  Idx  Thb",
    "  [P]  [R]  [M]  [I]  [T] ",
    "   │    │   ╭─╮   │    │ ",
    "  ╭─╮  ╭─╮  │ │  ╭─╮   │ ",
    "  │ │  │ │  │ │  │ │  ╭─╮",
    "  │ │  │ │  │ │  │ │  │ │",
    "  │ ╰──┴─┴──┴─┴──┴─┴──┤ │",
    "  │     LEFT HAND     │ ╯",
    "  ╰───────────────────╯  "
]

_RH_ART = [
    " Thb  Idx  Mid Ring Pinky",
    " [T]  [I]  [M]  [R]  [P] ",
    "  │    │   ╭─╮   │    │  ",
    "  │   ╭─╮  │ │  ╭─╮  ╭─╮ ",
    " ╭─╮  │ │  │ │  │ │  │ │ ",
    " │ │  │ │  │ │  │ │  │ │ ",
    " │ ├──┴─┴──┴─┴──┴─┴──╯ │ ",
    " ╰ │     RIGHT HAND    │ ",
    "   ╰───────────────────╯ "
]

_LH_ART = [f"{line:<25}"[:25] for line in _LH_ART]
_RH_ART = [f"{line:<25}"[:25] for line in _RH_ART]
HAND_LINES = [f"{l}          {r}" for l, r in zip(_LH_ART, _RH_ART)]

FINGER_RANGES = {
    "LP": [(0, 6)],
    "LR": [(6, 11)],
    "LM": [(11, 16)],
    "LI": [(16, 21)],
    "LT": [(21, 26)],
    "RT": [(35, 40)],
    "RI": [(40, 45)],
    "RM": [(45, 50)],
    "RR": [(50, 55)],
    "RP": [(55, 60)],
    "THUMB": [(21, 26), (35, 40)]
}

# ==============================================================================
# MODE 4 (ERROR BOARD): MISTAKE TRACKER & CONFUSION MATRIX
# ==============================================================================

class MistakeTracker:
    def __init__(self, filepath=None):
        if filepath is None:
            config_dir = os.path.expanduser("~/.config/ttyping")
            self.filepath = os.path.join(config_dir, "mistakes.json")
        else:
            self.filepath = filepath
        self.all_time = {}   # {target_ch: {"correct": int, "mistypes": {wrong_ch: count}}}
        self.session = {}    # {target_ch: {"correct": int, "mistypes": {wrong_ch: count}}}
        self.load()

    def record(self, target_ch, typed_ch):
        if not target_ch or not typed_ch:
            return
        is_correct = (target_ch == typed_ch)
        for store in (self.all_time, self.session):
            if target_ch not in store:
                store[target_ch] = {"correct": 0, "mistypes": {}}
            if is_correct:
                store[target_ch]["correct"] += 1
            else:
                wrong_dict = store[target_ch]["mistypes"]
                wrong_dict[typed_ch] = wrong_dict.get(typed_ch, 0) + 1
        if not is_correct:
            self.save()

    def load(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.all_time = json.load(f)
        except Exception:
            self.all_time = {}

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.all_time, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def clear(self, all_time=True):
        self.session = {}
        if all_time:
            self.all_time = {}
            self.save()

    def get_summary_list(self, session_only=False):
        store = self.session if session_only else self.all_time
        entries = []
        for target_ch, data in store.items():
            mistypes = data.get("mistypes", {})
            total_errors = sum(mistypes.values())
            if total_errors == 0:
                continue
            correct = data.get("correct", 0)
            total_attempts = correct + total_errors
            accuracy = (correct / total_attempts * 100.0) if total_attempts > 0 else 0.0

            sorted_mistypes = dict(sorted(mistypes.items(), key=lambda item: item[1], reverse=True))
            most_common = next(iter(sorted_mistypes.keys())) if sorted_mistypes else None
            diagnosis = self.diagnose_confusion(target_ch, most_common)

            entries.append({
                "target": target_ch,
                "total_errors": total_errors,
                "correct": correct,
                "accuracy": round(accuracy, 1),
                "mistypes": sorted_mistypes,
                "most_common_wrong": most_common,
                "diagnosis": diagnosis
            })

        entries.sort(key=lambda x: x["total_errors"], reverse=True)
        return entries

    def get_totals(self, session_only=False):
        store = self.session if session_only else self.all_time
        total_errors = 0
        total_correct = 0
        for data in store.values():
            total_correct += data.get("correct", 0)
            total_errors += sum(data.get("mistypes", {}).values())
        total_keystrokes = total_correct + total_errors
        accuracy = (total_correct / total_keystrokes * 100.0) if total_keystrokes > 0 else 100.0
        return total_errors, total_correct, round(accuracy, 1)

    def diagnose_confusion(self, target_ch, wrong_ch):
        if not target_ch or not wrong_ch:
            return ""
        t_info = KEY_FINGER_MAP.get(target_ch)
        w_info = KEY_FINGER_MAP.get(wrong_ch)
        if not t_info or not w_info:
            return f"Mistyped as [{repr_ch(wrong_ch)}]"
        t_code, t_name, _ = t_info
        w_code, w_name, _ = w_info
        if t_code == w_code:
            return f"Same finger ({t_name})! Reached off-target"
        elif t_code[0] == w_code[0]:
            return f"Same hand: {t_name} slipped to {w_name}"
        else:
            return f"Wrong hand: expected {t_name}, pressed {w_name}"

    def get_key_detail(self, target_ch, session_only=False):
        store = self.session if session_only else self.all_time
        data = store.get(target_ch, {"correct": 0, "mistypes": {}})
        mistypes = data.get("mistypes", {})
        total_errors = sum(mistypes.values())
        correct = data.get("correct", 0)
        total_attempts = correct + total_errors
        accuracy = (correct / total_attempts * 100.0) if total_attempts > 0 else (100.0 if correct > 0 else 100.0)

        sorted_mistypes = dict(sorted(mistypes.items(), key=lambda item: item[1], reverse=True))
        most_common = next(iter(sorted_mistypes.keys())) if sorted_mistypes else None
        diagnosis = self.diagnose_confusion(target_ch, most_common) if most_common else "No typos recorded for this key!"
        finger_info = KEY_FINGER_MAP.get(target_ch, ("THUMB", "Thumb (Space)", "Rest on Spacebar"))

        return {
            "target": target_ch,
            "total_errors": total_errors,
            "correct": correct,
            "total_attempts": total_attempts,
            "accuracy": round(accuracy, 1),
            "mistypes": sorted_mistypes,
            "most_common_wrong": most_common,
            "diagnosis": diagnosis,
            "finger_info": finger_info
        }

    def generate_words_for_single_key(self, target_ch, count=25):
        if not target_ch:
            return self.generate_practice_words(count=count)

        target_lower = target_ch.lower()
        rich_pool = KEY_WORDS_RICH.get(target_lower, [])
        base_pool = [w for w in BASE_WORDS_POOL if target_lower in w.lower()]
        combined = list(set(rich_pool + base_pool))

        if not combined:
            if target_ch.isdigit():
                combined = [w for w in NUMBER_WORDS if target_ch in w] or NUMBER_WORDS
            elif target_ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~":
                combined = [w for w in SYMBOL_WORDS if target_ch in w] or SYMBOL_WORDS
            else:
                combined = [target_ch * 3, target_ch * 2, f"{target_ch}a{target_ch}"]

        weights = []
        for w in combined:
            occ = w.lower().count(target_lower)
            if occ >= 3:
                weights.append(8)
            elif occ >= 2:
                weights.append(4)
            else:
                weights.append(1)

        selected = random.choices(combined, weights=weights, k=count)
        return " ".join(selected)

    def generate_practice_words(self, count=25, session_only=False):
        entries = self.get_summary_list(session_only=session_only)
        if not entries:
            return None
        weak_letters = [e["target"].lower() for e in entries[:5] if e["target"].isalpha()]
        if not weak_letters:
            return None
        matched_words = [w for w in BASE_WORDS_POOL if any(ch in w.lower() for ch in weak_letters)]
        if not matched_words:
            matched_words = BASE_WORDS_POOL
        selected = random.choices(matched_words, k=count)
        return " ".join(selected)


# ==============================================================================
# TYPING ENGINE
# ==============================================================================

class TypingEngine:
    def __init__(self, mode="SPRINT", custom_text=None):
        self.mode = mode
        self.custom_text = custom_text
        self.practice_target_key = None
        self.is_practice_drill = False
        self.endless_word_counter = 0
        self.tutor_drill_idx = 0
        self.tracker = MistakeTracker()
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
        elif self.mode == "TUTOR":
            drill = TUTOR_DRILLS[self.tutor_drill_idx]
            self.target_text = drill["text"]
        elif self.mode == "BOARD":
            self.target_text = ""
        else:
            self.target_text = ""

        self.typed_chars = []
        self.start_time = None
        self.end_time = None
        self.total_keystrokes = 0
        self.completed = False

    def switch_mode(self, new_mode, keep_custom=False):
        if self.mode != new_mode:
            self.mode = new_mode
            if not keep_custom and new_mode != "BOARD":
                self.custom_text = None
                self.practice_target_key = None
                self.is_practice_drill = False
            self.reset()

    def next_drill(self):
        if self.mode == "TUTOR":
            self.tutor_drill_idx = (self.tutor_drill_idx + 1) % len(TUTOR_DRILLS)
            self.custom_text = None
            self.reset()

    def add_char(self, char):
        if self.completed:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.total_keystrokes += 1

        curr_idx = len(self.typed_chars)
        if self.target_text and curr_idx < len(self.target_text):
            target_ch = self.target_text[curr_idx]
            # Key requirement: When practicing a specific key (or in drill mode), mistakes are NOT added to the Error Board!
            if not self.practice_target_key and not self.is_practice_drill:
                self.tracker.record(target_ch, char)

        self.typed_chars.append(char)

        if self.mode == "ENDLESS":
            if len(self.typed_chars) > len(self.target_text) - 120:
                more_words = " " + self.generate_endless_batch(25)
                self.target_text += more_words

        elif self.mode in ("SPRINT", "TUTOR"):
            if self.target_text and len(self.typed_chars) >= len(self.target_text):
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

        if self.mode == "ENDLESS" or not self.target_text:
            total_words = "∞"
        else:
            total_words = len(self.target_text.split(' '))

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
            c_white = curses.color_pair(6) | curses.A_BOLD  # Bright bold white
            c_highlight = curses.color_pair(7) | curses.A_BOLD
        except curses.error:
            pass

    if not c_faded:
        c_faded = curses.A_BOLD

    engine = TypingEngine(mode=initial_mode, custom_text=custom_text)
    last_stats = None

    last_pressed_char = None
    last_key_press_time = 0.0
    last_press_was_correct = True
    last_target_mistyped = None
    drill_button_bounds = (0, 0)
    drill_button_row = 2

    # Mode 4 (Error Board) state
    board_session_only = False
    board_scroll = 0
    board_notice = None
    board_notice_time = 0.0
    board_action_buttons = []
    board_inspected_key = None
    board_table_rows_meta = []

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 20 or max_x < 62:
            msg1 = "Please enlarge terminal window to play ttyping"
            msg2 = f"Current size: {max_x}x{max_y}  |  Minimum required: 62x20"
            safe_addstr(stdscr, max_y // 2 - 1, max(2, (max_x - len(msg1)) // 2), msg1, curses.A_BOLD | c_yellow)
            safe_addstr(stdscr, max_y // 2, max(2, (max_x - len(msg2)) // 2), msg2, c_white)
            stdscr.refresh()
            time.sleep(0.05)
            try:
                ch = stdscr.getch()
                if ch in (27, 3):
                    break
            except curses.error:
                pass
            continue

        stats = engine.get_stats()
        last_stats = stats
        curr_idx = len(engine.typed_chars)
        target = engine.target_text

        # ==========================================
        # 1. TOP BAR (Clickable with mouse, 1, 2, 3, 4)
        # ==========================================
        if max_x < 78:
            btn_sprint = "[ 1: Sprint ]"
            btn_endless = "[ 2: Endless ]"
            btn_tutor = "[ 3: Tutor ]"
            btn_board = "[ 4: Board ]"
        else:
            btn_sprint = "[ 1: ⚡ Sprint ]"
            btn_endless = "[ 2: ♾️ Endless ]"
            btn_tutor = "[ 3: 🖐️ Tutor ]"
            btn_board = "[ 4: 📊 Error Board ]"

        top_buttons = []
        cur_btn_x = 1 if max_x < 78 else 2

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
        cur_btn_x += len(btn_endless) + 1

        # Button 3: Tutor
        is_tutor = (engine.mode == "TUTOR")
        tutor_attr = (curses.A_REVERSE | c_cyan) if is_tutor else c_white
        safe_addstr(stdscr, 0, cur_btn_x, btn_tutor, tutor_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_tutor), "TUTOR"))
        cur_btn_x += len(btn_tutor) + 1

        # Button 4: Error Board
        is_board = (engine.mode == "BOARD")
        board_attr = (curses.A_REVERSE | c_highlight) if is_board else c_white
        safe_addstr(stdscr, 0, cur_btn_x, btn_board, board_attr)
        top_buttons.append((cur_btn_x, cur_btn_x + len(btn_board), "BOARD"))

        # Right-aligned exit button
        exit_label = "[ESC]" if max_x < 78 else "[ESC: Exit]"
        exit_x = max(cur_btn_x + len(btn_board) + 1, max_x - len(exit_label) - 1)
        safe_addstr(stdscr, 0, exit_x, exit_label, c_cyan)

        # Header divider
        safe_addstr(stdscr, 1, 2, "═" * (max_x - 4), c_cyan)

        cursor_screen_x = 2
        cursor_screen_y = 2

        # ==========================================
        # MODES 1 & 2: SPRINT & ENDLESS
        # ==========================================
        if engine.mode in ("SPRINT", "ENDLESS"):
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

            # Vertical Centering (content height ~ 12 lines)
            content_height = 12
            avail_y = max(1, (max_y - 2) - 2)
            start_y = 2 + max(0, (avail_y - content_height) // 2)

            stat_x = max(2, (max_x - len(stat_bar)) // 2)
            if engine.practice_target_key and engine.mode == "SPRINT":
                tk_disp = repr_ch(engine.practice_target_key).upper()
                drill_banner = f"🎯 FOCUSED DRILL: Target Key [ {tk_disp} ] — Words Saturated with '{repr_ch(engine.practice_target_key)}'"
                ban_x = max(2, (max_x - len(drill_banner)) // 2)
                safe_addstr(stdscr, max(2, start_y - 1), ban_x, drill_banner, curses.A_BOLD | c_green)

            safe_addstr(stdscr, start_y, stat_x, stat_bar, curses.A_BOLD | c_highlight)
            safe_addstr(stdscr, start_y + 1, 2, "─" * (max_x - 4), c_faded)

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

            # Render Active Word in 2-Row Font
            char_entries = []
            for char_pos, ch in enumerate(active_word):
                g = get_glyph(ch)
                gw = max(len(g[0]), len(g[1]), 1)
                char_entries.append((ch, g, gw))

            total_word_w = sum(gw for _, _, gw in char_entries) + max(0, len(char_entries) - 1)
            word_start_x = max(2, (max_x - total_word_w) // 2)
            word_start_y = start_y + 2

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
                    guide_attr = col | curses.A_BOLD
                    glyph_attr = col | curses.A_BOLD
                elif char_pos == letter_in_word:
                    col = c_highlight
                    guide_char = ch if not is_space_active else '␣'
                    guide_attr = curses.A_REVERSE | c_highlight | curses.A_BOLD
                    glyph_attr = c_highlight | curses.A_BOLD
                    cursor_screen_x = draw_x + (gw // 2)
                    cursor_screen_y = word_start_y + 1
                else:
                    col = c_faded
                    guide_char = ch
                    guide_attr = col | curses.A_BOLD
                    glyph_attr = col | curses.A_BOLD

                guide_str = guide_char.center(gw)
                if draw_x < max_x - 2:
                    safe_addstr(stdscr, word_start_y, draw_x, guide_str, guide_attr)
                    safe_addstr(stdscr, word_start_y + 1, draw_x, g[0].ljust(gw), glyph_attr)
                    safe_addstr(stdscr, word_start_y + 2, draw_x, g[1].ljust(gw), glyph_attr)

                draw_x += gw + 1

            # Sentence Flow Context
            context_divider_y = word_start_y + 3
            safe_addstr(stdscr, context_divider_y, 2, "─" * (max_x - 4), c_faded)

            text_start_y = context_divider_y + 1
            wrap_width = min(max_x - 6, 68)
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

                screen_y = text_start_y + (line_offset * 2)
                screen_x = box_x + c

                if i < curr_idx:
                    typed_ch = engine.typed_chars[i]
                    if typed_ch == target_ch:
                        if target_ch == ' ':
                            safe_addstr(stdscr, screen_y, screen_x, "␣", c_green | curses.A_BOLD)
                        else:
                            safe_addstr(stdscr, screen_y, screen_x, target_ch, c_green)
                    else:
                        if typed_ch == ' ':
                            safe_addstr(stdscr, screen_y, screen_x, "_", c_red | curses.A_REVERSE)
                        else:
                            safe_addstr(stdscr, screen_y, screen_x, typed_ch, c_red | curses.A_UNDERLINE)
                elif i == curr_idx:
                    # Current letter being typed: prominently highlighted!
                    disp_ch = "␣" if target_ch == ' ' else target_ch
                    safe_addstr(stdscr, screen_y, screen_x, disp_ch, curses.A_REVERSE | c_highlight | curses.A_BOLD)
                elif word_start <= i < word_end:
                    # Rest of active word: bright bold white so upcoming letters stand out
                    safe_addstr(stdscr, screen_y, screen_x, target_ch, c_white)
                else:
                    # Upcoming future words: crisp faded gray
                    safe_addstr(stdscr, screen_y, screen_x, target_ch, c_faded)

            # Completion Card (Sprint Mode)
            if engine.completed:
                card_y = min(max_y - 5, text_start_y + (visible_rows * 2) + 1)
                if engine.practice_target_key:
                    tk_disp = repr_ch(engine.practice_target_key).upper()
                    congrats = f"🏆 Drill Finished for Key [ {tk_disp} ]! Speed: {stats['wpm']} WPM | Accuracy: {stats['accuracy']}% | Mistakes: {stats['mistakes']}"
                    prompt = f"Press [ENTER] to practice '[{tk_disp}]' again, [4] for Error Board, or [1/2/3] to change mode."
                else:
                    congrats = f"🏆 Sprint Finished! Speed: {stats['wpm']} WPM | Accuracy: {stats['accuracy']}% | Errors: {stats['mistakes']}"
                    if stats['mistakes'] > 0:
                        prompt = "Press [4] to view Error Board, [ENTER] for next sentence, or [1/2/3] to switch mode."
                    else:
                        prompt = "Press [ENTER] for next sentence, [1] / [2] / [3] / [4] to change mode, or [ESC] to quit."
                safe_addstr(stdscr, card_y, 4, congrats, c_yellow)
                safe_addstr(stdscr, card_y + 1, 4, prompt, c_white)

        # ==========================================
        # MODE 3: TOUCH TYPING TUTOR & FINGER GUIDE
        # ==========================================
        elif engine.mode == "TUTOR":
            drill_info = TUTOR_DRILLS[engine.tutor_drill_idx] if not engine.custom_text else {
                "name": "Custom Practice Text",
                "desc": "Custom text loaded from CLI",
                "text": engine.target_text
            }

            # Vertical Centering (Total content height = 19 lines: fits on standard 24-row terminals)
            content_height = 19
            avail_y = max(1, (max_y - 2) - 2)
            start_y = 2 + max(0, (avail_y - content_height) // 2)

            row_drill = start_y
            row_sentence = start_y + 1
            row_banner = start_y + 2
            row_divider = start_y + 3
            row_keyboard = start_y + 4
            row_hands = start_y + 10

            drill_button_row = row_drill

            # Row: Drill info button + stats
            drill_btn_text = f"[ 🔄 Drill ({engine.tutor_drill_idx + 1}/{len(TUTOR_DRILLS)}): {drill_info['name']} ]" if not engine.custom_text else "[ 🔄 Custom Text ]"
            if len(drill_btn_text) > max_x - 32:
                drill_btn_text = f"[ 🔄 Drill {engine.tutor_drill_idx + 1}: {drill_info['name'][:14]}.. ]"

            safe_addstr(stdscr, row_drill, 2, drill_btn_text, curses.A_BOLD | c_highlight)
            drill_button_bounds = (2, 2 + len(drill_btn_text))

            stats_info = f"🎯 {stats['accuracy']}%   ⚡ {stats['wpm']} WPM   ⏱ {format_time(stats['elapsed'])}"
            stats_x = max(2 + len(drill_btn_text) + 2, max_x - len(stats_info) - 2)
            safe_addstr(stdscr, row_drill, stats_x, stats_info, c_white)

            # Row: Practice Sentence Display or Free Key Explorer Prompt
            if target:
                wrap_w = min(max_x - 6, 60)
                text_start_x = max(2, (max_x - min(len(target), wrap_w)) // 2)
                scroll_start = max(0, curr_idx - (wrap_w // 2))
                visible_slice = target[scroll_start:scroll_start + wrap_w]

                for s_idx, ch in enumerate(visible_slice):
                    actual_idx = scroll_start + s_idx
                    draw_col = text_start_x + s_idx

                    if actual_idx < curr_idx:
                        typed_ch = engine.typed_chars[actual_idx]
                        if typed_ch == ch:
                            attr = c_green | curses.A_BOLD
                            disp_ch = ch if ch != ' ' else '␣'
                        else:
                            attr = c_red | curses.A_UNDERLINE | curses.A_BOLD
                            disp_ch = typed_ch if typed_ch != ' ' else '_'
                    elif actual_idx == curr_idx:
                        attr = curses.A_REVERSE | c_highlight | curses.A_BOLD
                        disp_ch = ch if ch != ' ' else '␣'
                        cursor_screen_x = draw_col
                        cursor_screen_y = row_sentence
                    else:
                        attr = c_faded
                        disp_ch = ch

                    safe_addstr(stdscr, row_sentence, draw_col, disp_ch, attr)
            else:
                explorer_msg = "⌨️  Free Key Explorer: Press ANY key to test which finger and hand to use!"
                exp_x = max(2, (max_x - len(explorer_msg)) // 2)
                safe_addstr(stdscr, row_sentence, exp_x, explorer_msg, curses.A_BOLD | c_cyan)

            # Determine active character to guide
            if target and curr_idx < len(target):
                active_ch = target[curr_idx]
            elif not target and last_pressed_char is not None:
                active_ch = last_pressed_char
            elif not target:
                active_ch = 'f'  # Default prompt to home key 'F'
            else:
                active_ch = None  # Drill completed

            now = time.time()
            press_elapsed = now - last_key_press_time

            # Prospective Instruction Banner (Always tells the user what key & finger to use)
            banner_text, banner_style = get_tutor_instruction(
                active_ch, last_pressed_char, last_press_was_correct, press_elapsed, bool(target), last_target_mistyped
            )
            attr_map = {
                "red": c_red | curses.A_BOLD,
                "green": c_green | curses.A_BOLD,
                "highlight": c_highlight | curses.A_BOLD,
                "yellow": c_yellow | curses.A_BOLD,
                "cyan": c_cyan | curses.A_BOLD
            }
            banner_attr = attr_map.get(banner_style, c_highlight | curses.A_BOLD)
            ban_x = max(2, (max_x - len(banner_text)) // 2)
            safe_addstr(stdscr, row_banner, ban_x, banner_text, banner_attr)

            # Divider before keyboard
            safe_addstr(stdscr, row_divider, 2, "─" * (max_x - 4), c_faded)

            # Centered Keyboard Layout (5 rows, 60 cols)
            kb_x = max(2, (max_x - 60) // 2)
            base_target = get_base_key(active_ch) if active_ch else None
            shift_needed = needs_shift(active_ch) if active_ch else False
            side = finger_side(active_ch) if active_ch else "LEFT"

            for r_idx, row_keys in enumerate(KEYBOARD_LAYOUT):
                ky = row_keyboard + r_idx
                kx = kb_x
                for key_id, k_finger, label in row_keys:
                    is_target = (base_target is not None and key_id == base_target)
                    is_shift = shift_needed and (
                        (key_id == "Shift_L" and side == "RIGHT") or
                        (key_id == "Shift_R" and side == "LEFT")
                    )
                    is_error = (
                        not last_press_was_correct and
                        (press_elapsed < 1.5) and
                        last_pressed_char is not None and
                        get_base_key(last_pressed_char) == key_id
                    )

                    if is_error:
                        k_attr = curses.A_REVERSE | c_red | curses.A_BOLD
                    elif is_target:
                        k_attr = curses.A_REVERSE | c_green | curses.A_BOLD
                    elif is_shift:
                        k_attr = curses.A_REVERSE | c_cyan | curses.A_BOLD
                    elif key_id in ("a", "s", "d", "f", "j", "k", "l", ";"):
                        k_attr = c_faded | curses.A_UNDERLINE
                    else:
                        k_attr = c_faded

                    safe_addstr(stdscr, ky, kx, label, k_attr)
                    kx += len(label) + 1

            # Hand Diagram (9 rows, 60 cols, perfectly aligned with keyboard)
            hx = kb_x
            finger_info = KEY_FINGER_MAP.get(active_ch, ('THUMB', 'Thumb', '')) if active_ch else ('THUMB', '', '')
            active_finger_code = finger_info[0]
            active_ranges = list(FINGER_RANGES.get(active_finger_code, []))
            if shift_needed:
                shift_finger = "RP" if side == "LEFT" else "LP"
                active_ranges.extend(FINGER_RANGES.get(shift_finger, []))

            for line_idx, line in enumerate(HAND_LINES):
                hy = row_hands + line_idx
                for col_idx, ch in enumerate(line):
                    in_active = any(s <= col_idx < e for s, e in active_ranges)
                    if in_active and ch != " " and line_idx < 7:
                        safe_addstr(stdscr, hy, hx + col_idx, ch, c_green | curses.A_BOLD)
                    else:
                        safe_addstr(stdscr, hy, hx + col_idx, ch, c_faded)

            # Completion Card (if drill completed)
            if engine.completed:
                card_y = max_y - 4
                congrats = f"🏆 Drill Finished! Speed: {stats['wpm']} WPM | Accuracy: {stats['accuracy']}%"
                if stats['mistakes'] > 0:
                    prompt = "Press [4] to view Error Board, [ENTER] for next drill, or [1/2/3] to change mode."
                else:
                    prompt = "Press [ENTER] for next drill, [1] / [2] / [4] to change mode, or [ESC] to quit."
                safe_addstr(stdscr, card_y, 4, congrats, c_yellow)
                safe_addstr(stdscr, card_y + 1, 4, prompt, c_white)

        # ==========================================
        # MODE 4: ERROR & MISTAKE BOARD
        # ==========================================
        elif engine.mode == "BOARD":
            board_action_buttons = []
            board_table_rows_meta = []
            entries = engine.tracker.get_summary_list(session_only=board_session_only)
            tot_errs, tot_corr, ovr_acc = engine.tracker.get_totals(session_only=board_session_only)

            # When a key is inspected (e.g. user pressed 'e'), ensure that key's error is placed at the very top!
            if board_inspected_key is not None:
                target_k = board_inspected_key.lower()
                found_idx = next((i for i, e in enumerate(entries) if e["target"].lower() == target_k), None)
                if found_idx is not None:
                    inspected_entry = entries.pop(found_idx)
                    entries.insert(0, inspected_entry)
                else:
                    detail_entry = engine.tracker.get_key_detail(board_inspected_key, session_only=board_session_only)
                    inspected_entry = {
                        "target": board_inspected_key,
                        "total_errors": detail_entry["total_errors"],
                        "correct": detail_entry["correct"],
                        "accuracy": detail_entry["accuracy"],
                        "mistypes": detail_entry["mistypes"],
                        "most_common_wrong": detail_entry["most_common_wrong"],
                        "diagnosis": detail_entry["diagnosis"]
                    }
                    entries.insert(0, inspected_entry)

            scope_title = "CURRENT SESSION" if board_session_only else "ALL-TIME"
            btn_scope = "[ F1: Scope: Session ]" if board_session_only else "[ F1: Scope: All-Time ]"
            btn_practice = "[ F2: 🎯 Practice Weak Keys ]"
            btn_clear = "[ F3: 🔄 Clear Stats ]"

            row_act = 2 if max_y >= 24 else 1
            ax = 2
            safe_addstr(stdscr, row_act, ax, btn_scope, curses.A_BOLD | c_cyan)
            board_action_buttons.append((row_act, ax, ax + len(btn_scope), "TOGGLE_SCOPE"))
            ax += len(btn_scope) + 2

            if entries:
                safe_addstr(stdscr, row_act, ax, btn_practice, curses.A_BOLD | c_green)
                board_action_buttons.append((row_act, ax, ax + len(btn_practice), "PRACTICE"))
                ax += len(btn_practice) + 2

            safe_addstr(stdscr, row_act, ax, btn_clear, curses.A_BOLD | c_yellow)
            board_action_buttons.append((row_act, ax, ax + len(btn_clear), "CLEAR"))

            if board_notice and (time.time() - board_notice_time < 3.0):
                not_x = max(ax + len(btn_clear) + 2, max_x - len(board_notice) - 2)
                safe_addstr(stdscr, row_act, not_x, board_notice, curses.A_BOLD | c_highlight)

            # Overview Stat Row
            stat_row_y = row_act + 1
            if board_inspected_key is not None:
                detail_top = engine.tracker.get_key_detail(board_inspected_key, session_only=board_session_only)
                tk_name = repr_ch(board_inspected_key).upper()
                f_name = detail_top["finger_info"][1]
                if detail_top["total_errors"] > 0:
                    summary_text = f"🔍 KEY [ {tk_name} ] ({f_name}): ❌ {detail_top['total_errors']} errors  |  🎯 {detail_top['accuracy']}% acc  |  ⚠️ Typed as: '{repr_ch(detail_top['most_common_wrong'])}'  |  Total Mistakes: {tot_errs}"
                else:
                    summary_text = f"🔍 KEY [ {tk_name} ] ({f_name}): ✅ 0 errors (100% accuracy)  |  Total Mistakes in {scope_title}: {tot_errs}"
                safe_addstr(stdscr, stat_row_y, 2, summary_text[:max_x - 4], curses.A_BOLD | c_highlight)
            else:
                weakest_str = ""
                if entries:
                    top_e = entries[0]
                    t_disp = repr_ch(top_e["target"])
                    w_disp = repr_ch(top_e["most_common_wrong"]) if top_e.get("most_common_wrong") else "none"
                    weakest_str = f"  |  ⚠️ Most Confused: [{t_disp}] ➔ typed [{w_disp}]"

                summary_text = f"📊 Scope: {scope_title}  |  ❌ Total Mistakes: {tot_errs}  |  🎯 Overall Accuracy: {ovr_acc}%{weakest_str}"
                safe_addstr(stdscr, stat_row_y, 2, summary_text[:max_x - 4], curses.A_BOLD | c_white)

            # ==========================================
            # KEYBOARD ERROR HEATMAP & KEY HIGHLIGHTER
            # ==========================================
            if max_y >= 26:
                row_kb_header = stat_row_y + 1
                kb_title = "⌨️  KEYBOARD HEATMAP (Press or click ANY key to highlight & inspect)"
                safe_addstr(stdscr, row_kb_header, max(2, (max_x - len(kb_title)) // 2), kb_title, curses.A_BOLD | c_cyan)
                row_keyboard = row_kb_header + 1
            else:
                row_keyboard = stat_row_y + 1

            kb_x = max(2, (max_x - 60) // 2)

            base_inspected = get_base_key(board_inspected_key) if board_inspected_key is not None else None
            base_pressed = get_base_key(last_pressed_char) if last_pressed_char is not None else None
            shift_req = needs_shift(board_inspected_key) if board_inspected_key is not None else False
            side = finger_side(board_inspected_key) if board_inspected_key is not None else "LEFT"
            is_recent_press = (time.time() - last_key_press_time < 0.4)

            # Details for inspected key (if any)
            inspected_mistypes = {}
            most_common_wrong = None
            if board_inspected_key is not None:
                inspected_detail = engine.tracker.get_key_detail(board_inspected_key, session_only=board_session_only)
                inspected_mistypes = {get_base_key(k): cnt for k, cnt in inspected_detail.get("mistypes", {}).items() if get_base_key(k)}
                most_common_wrong = get_base_key(inspected_detail.get("most_common_wrong"))

            # Current error store for coloring heatmap
            store = engine.tracker.session if board_session_only else engine.tracker.all_time

            for r_idx, row_keys in enumerate(KEYBOARD_LAYOUT):
                ky = row_keyboard + r_idx
                kx = kb_x
                for key_id, k_finger, label in row_keys:
                    is_active = (base_inspected is not None and key_id == base_inspected)
                    is_press_flash = (is_recent_press and base_pressed is not None and key_id == base_pressed)
                    is_shift = shift_req and (
                        (key_id == "Shift_L" and side == "RIGHT") or
                        (key_id == "Shift_R" and side == "LEFT")
                    )

                    # Check mistakes count for this key in store
                    k_errs = 0
                    k_corr = 0
                    for cand in (key_id, key_id.upper() if isinstance(key_id, str) else key_id):
                        if cand in store:
                            k_errs += sum(store[cand].get("mistypes", {}).values())
                            k_corr += store[cand].get("correct", 0)

                    # Highlight priority:
                    # 1. Pressed / Active Inspected key
                    if is_active or is_press_flash:
                        k_attr = curses.A_REVERSE | c_highlight | curses.A_BOLD
                    # 2. Shift key if needed
                    elif is_shift:
                        k_attr = curses.A_REVERSE | c_cyan | curses.A_BOLD
                    # 3. Mistyped / confused key for currently inspected key
                    elif base_inspected is not None and key_id in inspected_mistypes and key_id != base_inspected:
                        if key_id == most_common_wrong:
                            k_attr = curses.A_REVERSE | c_red | curses.A_BOLD
                        else:
                            k_attr = c_red | curses.A_BOLD
                    # 4. Error heatmap based on history
                    elif k_errs >= 3:
                        k_attr = c_red | curses.A_BOLD
                    elif k_errs >= 1:
                        k_attr = c_yellow | curses.A_BOLD
                    elif k_corr > 0 and k_errs == 0:
                        k_attr = c_green | curses.A_BOLD
                    # 5. Home row tactile indicators
                    elif key_id in ("a", "s", "d", "f", "j", "k", "l", ";"):
                        k_attr = c_faded | curses.A_UNDERLINE
                    # 6. Default
                    else:
                        k_attr = c_faded

                    safe_addstr(stdscr, ky, kx, label, k_attr)
                    board_action_buttons.append((ky, kx, kx + len(label), f"KEY_{key_id}"))
                    kx += len(label) + 1

            row_kb_divider = row_keyboard + 5
            safe_addstr(stdscr, row_kb_divider, 2, "─" * (max_x - 4), c_faded)
            content_start_y = row_kb_divider + 1

            # Key Inspection Card (if a key is inspected)
            if board_inspected_key is not None:
                detail = engine.tracker.get_key_detail(board_inspected_key, session_only=board_session_only)
                f_code, f_name, f_hint = detail["finger_info"]
                target_disp = repr_ch(board_inspected_key)

                card_w = min(max_x - 4, 76)
                card_x = max(2, (max_x - card_w) // 2)
                card_y = content_start_y

                # If screen height is tight (< 26), render compact 5-line card
                if max_y < 26:
                    title = f" 🔍 KEY: [ {target_disp.upper()} ]  |  🖐️ {f_name.upper()} "
                    pad = max(0, (card_w - 2 - len(title)) // 2)
                    top_border = "╭" + "─" * pad + title + "─" * max(0, card_w - 2 - pad - len(title)) + "╮"
                    safe_addstr(stdscr, card_y, card_x, top_border, curses.A_BOLD | c_cyan)

                    safe_addstr(stdscr, card_y + 1, card_x, "│", c_cyan)
                    if detail["total_attempts"] > 0:
                        if detail["total_errors"] > 0:
                            stat_txt = f"❌ Mistakes: {detail['total_errors']} | 🎯 Acc: {detail['accuracy']}% | 💡 {detail['diagnosis']}"
                        else:
                            stat_txt = f"✅ Clean Precision! 0 mistakes on [{target_disp}] (100% accuracy)"
                    else:
                        stat_txt = f"ℹ️  No keystrokes recorded yet for key [{target_disp}]."
                    safe_addstr(stdscr, card_y + 1, card_x + 2, stat_txt[:card_w - 4], curses.A_BOLD | (c_white if detail['total_errors'] > 0 else c_green))
                    safe_addstr(stdscr, card_y + 1, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 2, card_x, "│", c_cyan)
                    if detail["total_errors"] > 0:
                        parts = [f"'{repr_ch(w)}' ({cnt}x)" for w, cnt in detail["mistypes"].items()]
                        mistypes_txt = f"⚠️ Mistyped as: {', '.join(parts)}"
                        safe_addstr(stdscr, card_y + 2, card_x + 2, mistypes_txt[:card_w - 4], curses.A_BOLD | c_yellow)
                    else:
                        clean_txt = f"Rest on home row. Press [ENTER] to practice words with [{target_disp}]."
                        safe_addstr(stdscr, card_y + 2, card_x + 2, clean_txt[:card_w - 4], c_faded)
                    safe_addstr(stdscr, card_y + 2, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 3, card_x, "│", c_cyan)
                    btn_drill_txt = f"🎯 [ ENTER: Practice Words with '{target_disp}' ]"
                    btn_close_txt = "[ Backspace / ESC: Close ]"
                    safe_addstr(stdscr, card_y + 3, card_x + 2, btn_drill_txt, curses.A_BOLD | c_green)
                    board_action_buttons.append((card_y + 3, card_x + 2, card_x + 2 + len(btn_drill_txt), "PRACTICE_INSPECTED"))
                    cx_close = card_x + card_w - len(btn_close_txt) - 2
                    safe_addstr(stdscr, card_y + 3, cx_close, btn_close_txt, c_cyan)
                    board_action_buttons.append((card_y + 3, cx_close, cx_close + len(btn_close_txt), "CLOSE_INSPECTION"))
                    safe_addstr(stdscr, card_y + 3, card_x + card_w - 1, "│", c_cyan)

                    bot_border = "╰" + "─" * (card_w - 2) + "╯"
                    safe_addstr(stdscr, card_y + 4, card_x, bot_border, curses.A_BOLD | c_cyan)
                    card_bottom = card_y + 5
                else:
                    # Full 7-line card
                    title = f" 🔍 KEY INSPECTION: [ {target_disp.upper()} ] "
                    pad = max(0, (card_w - 2 - len(title)) // 2)
                    top_border = "╭" + "─" * pad + title + "─" * max(0, card_w - 2 - pad - len(title)) + "╮"
                    safe_addstr(stdscr, card_y, card_x, top_border, curses.A_BOLD | c_cyan)

                    finger_line = f"🖐️  Finger: {f_name.upper()}  |  {f_hint}"
                    safe_addstr(stdscr, card_y + 1, card_x, "│", c_cyan)
                    safe_addstr(stdscr, card_y + 1, card_x + 2, finger_line[:card_w - 4], curses.A_BOLD | c_highlight)
                    safe_addstr(stdscr, card_y + 1, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 2, card_x, "│", c_cyan)
                    if detail["total_attempts"] > 0:
                        if detail["total_errors"] > 0:
                            stat_txt = f"❌ Mistakes on [{target_disp}]: {detail['total_errors']}  |  ✅ Correct: {detail['correct']}  |  🎯 Accuracy: {detail['accuracy']}%"
                            safe_addstr(stdscr, card_y + 2, card_x + 2, stat_txt[:card_w - 4], curses.A_BOLD | c_white)
                        else:
                            stat_txt = f"✅ Clean Precision! 0 mistakes on [{target_disp}] ({detail['correct']} correct hits, 100% accuracy)"
                            safe_addstr(stdscr, card_y + 2, card_x + 2, stat_txt[:card_w - 4], curses.A_BOLD | c_green)
                    else:
                        stat_txt = f"ℹ️  No keystrokes recorded yet for key [{target_disp}] in {scope_title}."
                        safe_addstr(stdscr, card_y + 2, card_x + 2, stat_txt[:card_w - 4], c_white)
                    safe_addstr(stdscr, card_y + 2, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 3, card_x, "│", c_cyan)
                    if detail["total_errors"] > 0:
                        parts = [f"'{repr_ch(w)}' ({cnt}x)" for w, cnt in detail["mistypes"].items()]
                        mistypes_txt = f"⚠️ Mistyped as: {', '.join(parts)}"
                        safe_addstr(stdscr, card_y + 3, card_x + 2, mistypes_txt[:card_w - 4], curses.A_BOLD | c_yellow)
                    elif detail["correct"] > 0:
                        clean_txt = f"🎉 Perfect score on [{target_disp}]! You consistently hit this key accurately."
                        safe_addstr(stdscr, card_y + 3, card_x + 2, clean_txt[:card_w - 4], c_green)
                    else:
                        clean_txt = "Press [ENTER] to practice words containing this key and build muscle memory!"
                        safe_addstr(stdscr, card_y + 3, card_x + 2, clean_txt[:card_w - 4], c_faded)
                    safe_addstr(stdscr, card_y + 3, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 4, card_x, "│", c_cyan)
                    if detail["total_errors"] > 0:
                        diag_txt = f"💡 Diagnosis: {detail['diagnosis']}"
                        safe_addstr(stdscr, card_y + 4, card_x + 2, diag_txt[:card_w - 4], c_white)
                    else:
                        rec_txt = f"💡 Recommended Hand Position: Rest fingers on home row, strike [{target_disp}] lightly."
                        safe_addstr(stdscr, card_y + 4, card_x + 2, rec_txt[:card_w - 4], c_faded)
                    safe_addstr(stdscr, card_y + 4, card_x + card_w - 1, "│", c_cyan)

                    safe_addstr(stdscr, card_y + 5, card_x, "│", c_cyan)
                    btn_drill_txt = f"🎯 [ ENTER: Practice Words with '{target_disp}' ]"
                    btn_close_txt = "[ Backspace / ESC: Close ]"
                    safe_addstr(stdscr, card_y + 5, card_x + 2, btn_drill_txt, curses.A_BOLD | c_green)
                    board_action_buttons.append((card_y + 5, card_x + 2, card_x + 2 + len(btn_drill_txt), "PRACTICE_INSPECTED"))
                    cx_close = card_x + card_w - len(btn_close_txt) - 2
                    safe_addstr(stdscr, card_y + 5, cx_close, btn_close_txt, c_cyan)
                    board_action_buttons.append((card_y + 5, cx_close, cx_close + len(btn_close_txt), "CLOSE_INSPECTION"))
                    safe_addstr(stdscr, card_y + 5, card_x + card_w - 1, "│", c_cyan)

                    bot_border = "╰" + "─" * (card_w - 2) + "╯"
                    safe_addstr(stdscr, card_y + 6, card_x, bot_border, curses.A_BOLD | c_cyan)

                    card_bottom = card_y + 7
            else:
                card_bottom = content_start_y

            if not entries:
                if board_inspected_key is None:
                    card_y = content_start_y
                    box_w = min(max_x - 8, 64)
                    bx = max(2, (max_x - box_w) // 2)
                    safe_addstr(stdscr, card_y, bx, "╭" + "─" * (box_w - 2) + "╮", c_cyan)
                    msg1 = "🎯 NO MISTAKES RECORDED YET!"
                    msg2 = f"Your typing accuracy in {scope_title.lower()} is 100%."
                    msg3 = "Start typing in Sprint [1], Endless [2], or Tutor [3] mode."
                    msg4 = "Whenever you mistype, it will appear right here on the keyboard & table!"
                    msg5 = "👉 Press ANY key on your keyboard (e.g. [D]) to inspect & drill it!"
                    safe_addstr(stdscr, card_y + 1, max(bx + 1, bx + (box_w - len(msg1)) // 2), msg1, curses.A_BOLD | c_green)
                    safe_addstr(stdscr, card_y + 2, max(bx + 1, bx + (box_w - len(msg2)) // 2), msg2, c_white)
                    safe_addstr(stdscr, card_y + 3, max(bx + 1, bx + (box_w - len(msg3)) // 2), msg3, c_highlight)
                    safe_addstr(stdscr, card_y + 4, max(bx + 1, bx + (box_w - len(msg4)) // 2), msg4, c_faded)
                    safe_addstr(stdscr, card_y + 5, max(bx + 1, bx + (box_w - len(msg5)) // 2), msg5, curses.A_BOLD | c_yellow)
                    safe_addstr(stdscr, card_y + 6, bx, "╰" + "─" * (box_w - 2) + "╯", c_cyan)
            else:
                if board_inspected_key is None:
                    hint_line = "👉 Press ANY key on your keyboard or click a key above to inspect errors & drill it!"
                    safe_addstr(stdscr, content_start_y, 2, hint_line[:max_x - 4], curses.A_BOLD | c_highlight)
                    th_y = content_start_y + 1
                else:
                    th_y = card_bottom

                if th_y + 3 <= max_y - 2:
                    col_w_target = 8
                    col_w_errors = 8
                    col_w_mistypes = 24
                    col_w_acc = 10
                    avail_diag = max(10, max_x - (4 + col_w_target + col_w_errors + col_w_mistypes + col_w_acc + 5))

                    th_target = "TARGET".center(col_w_target)
                    th_errors = "ERRORS".center(col_w_errors)
                    th_mistypes = "MISTYPED WITH (COUNT)".ljust(col_w_mistypes)
                    th_acc = "ACCURACY".center(col_w_acc)
                    th_diag = "FINGER / ROOT CAUSE ANALYSIS".ljust(avail_diag)

                    th_line = f" {th_target}│{th_errors}│ {th_mistypes}│{th_acc}│ {th_diag}"
                    safe_addstr(stdscr, th_y, 2, th_line[:max_x - 4], curses.A_BOLD | c_highlight)

                    div_line = f"─{'─'*col_w_target}┼{'─'*col_w_errors}┼{'─'*(col_w_mistypes + 1)}┼{'─'*col_w_acc}┼{'─'*(avail_diag + 1)}"
                    safe_addstr(stdscr, th_y + 1, 2, div_line[:max_x - 4], c_faded)

                    table_start_y = th_y + 2
                    visible_table_rows = max(1, max_y - table_start_y - 3)

                    max_scroll = max(0, len(entries) - visible_table_rows)
                    board_scroll = min(board_scroll, max_scroll)

                    for r_idx in range(visible_table_rows):
                        entry_idx = board_scroll + r_idx
                        if entry_idx >= len(entries):
                            break

                        e = entries[entry_idx]
                        row_y = table_start_y + r_idx
                        board_table_rows_meta.append((row_y, e["target"]))

                        is_inspected = (board_inspected_key is not None and e["target"].lower() == board_inspected_key.lower())

                        t_disp = repr_ch(e["target"])
                        t_prefix = "➔ " if is_inspected else "  "
                        t_str = f"{t_prefix}[{t_disp}]".center(col_w_target)
                        err_str = str(e["total_errors"]).center(col_w_errors)

                        parts = []
                        for w_ch, count in e["mistypes"].items():
                            parts.append(f"'{repr_ch(w_ch)}' ({count}x)")
                        if parts:
                            mistypes_str = ", ".join(parts).ljust(col_w_mistypes)[:col_w_mistypes]
                        else:
                            mistypes_str = "(clean: 0 errors)".ljust(col_w_mistypes)[:col_w_mistypes]

                        acc_str = f"{e['accuracy']}%".center(col_w_acc)
                        diag_str = e["diagnosis"].ljust(avail_diag)[:avail_diag]

                        acc_val = e["accuracy"]
                        acc_color = c_green if acc_val >= 85 else (c_yellow if acc_val >= 70 else c_red)

                        row_base_attr = (curses.A_REVERSE | c_cyan) if is_inspected else 0

                        rx = 2
                        safe_addstr(stdscr, row_y, rx, f" {t_str}", row_base_attr or (curses.A_BOLD | c_highlight))
                        rx += len(t_str) + 1
                        safe_addstr(stdscr, row_y, rx, "│", c_faded)
                        rx += 1
                        safe_addstr(stdscr, row_y, rx, err_str, row_base_attr or (curses.A_BOLD | c_red))
                        rx += len(err_str)
                        safe_addstr(stdscr, row_y, rx, "│ ", c_faded)
                        rx += 2
                        safe_addstr(stdscr, row_y, rx, mistypes_str, row_base_attr or c_yellow)
                        rx += len(mistypes_str)
                        safe_addstr(stdscr, row_y, rx, "│", c_faded)
                        rx += 1
                        safe_addstr(stdscr, row_y, rx, acc_str, row_base_attr or (curses.A_BOLD | acc_color))
                        rx += len(acc_str)
                        safe_addstr(stdscr, row_y, rx, "│ ", c_faded)
                        rx += 2
                        safe_addstr(stdscr, row_y, rx, diag_str, row_base_attr or c_white)

                    if len(entries) > visible_table_rows:
                        scroll_info = f" [▼ Showing {board_scroll + 1}-{min(len(entries), board_scroll + visible_table_rows)} of {len(entries)} (Use ↑/↓ to scroll)] "
                        safe_addstr(stdscr, max_y - 3, max(2, (max_x - len(scroll_info)) // 2), scroll_info, c_cyan)

        # ==========================================
        # 4. FOOTER & SHORTCUTS
        # ==========================================
        footer_y = max_y - 2
        safe_addstr(stdscr, footer_y - 1, 2, "─" * (max_x - 4), c_faded)
        if engine.mode == "BOARD":
            if board_inspected_key is not None:
                controls = "[ENTER] 🎯 Practice Key   [Backspace/ESC] Close Inspection   [F1] Scope   [F3] Clear   [1/2/3] Modes"
            elif max_x < 70:
                controls = "[Press Key] Inspect   [ENTER/F2] Practice   [F1] Scope   [F3] Clear   [1/2/3] Modes"
            else:
                controls = "[Press ANY Key] Inspect Errors & Practice   [ENTER/F2] Practice Weak   [F1] Scope   [F3] Clear   [↑/↓] Scroll"
        elif engine.mode == "TUTOR":
            if max_x < 65:
                controls = "[1/2/3/4] Mode  [Enter] Next Drill  [Back] Fix  [ESC] Exit"
            else:
                controls = "[1/2/3/4] Mode   [Enter/F2] Next Drill   [Space] Key   [Back] Fix   [Ctrl+R] Reset   [ESC] Exit"
        else:
            if max_x < 50:
                controls = "[1/2/3/4] Mode  [Back] Fix  [ESC] Exit"
            elif max_x < 65:
                controls = "[1/2/3/4] Mode  [Back] Fix  [Ctrl+R] Reset  [ESC] Exit"
            else:
                controls = "[1/2/3/4] Mode   [Space] Key   [Backspace] Fix   [Ctrl+R] Reset   [ESC] Exit"
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
                            if action in ("SPRINT", "ENDLESS", "TUTOR", "BOARD"):
                                engine.switch_mode(action)
                            break
                elif engine.mode == "BOARD" and (bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED)):
                    handled_btn = False
                    for btn_y, x_start, x_end, action in board_action_buttons:
                        if my == btn_y and x_start <= mx <= x_end:
                            handled_btn = True
                            if action == "TOGGLE_SCOPE":
                                board_session_only = not board_session_only
                                board_scroll = 0
                                board_notice = "Switched to " + ("Session Stats" if board_session_only else "All-Time Stats")
                                board_notice_time = time.time()
                            elif action == "PRACTICE":
                                weak_words = engine.tracker.generate_practice_words(count=30, session_only=board_session_only)
                                if weak_words:
                                    engine.custom_text = weak_words
                                    engine.practice_target_key = None
                                    engine.switch_mode("SPRINT", keep_custom=True)
                                else:
                                    board_notice = "No weak letters recorded yet to practice!"
                                    board_notice_time = time.time()
                            elif action == "CLEAR":
                                engine.tracker.clear(all_time=not board_session_only)
                                board_notice = "Cleared " + ("Session Stats" if board_session_only else "All-Time Stats")
                                board_notice_time = time.time()
                                board_scroll = 0
                                board_inspected_key = None
                            elif action == "PRACTICE_INSPECTED":
                                if board_inspected_key:
                                    words = engine.tracker.generate_words_for_single_key(board_inspected_key, count=25)
                                    engine.custom_text = words
                                    engine.practice_target_key = board_inspected_key
                                    engine.is_practice_drill = True
                                    engine.switch_mode("SPRINT", keep_custom=True)
                            elif action == "CLOSE_INSPECTION":
                                board_inspected_key = None
                                board_scroll = 0
                            elif action.startswith("KEY_"):
                                k_id = action[4:]
                                if k_id == "Bksp":
                                    board_inspected_key = None
                                    last_pressed_char = "Bksp"
                                    last_key_press_time = time.time()
                                    board_scroll = 0
                                elif k_id == "Enter":
                                    last_pressed_char = "Enter"
                                    last_key_press_time = time.time()
                                    if board_inspected_key:
                                        words = engine.tracker.generate_words_for_single_key(board_inspected_key, count=25)
                                        engine.custom_text = words
                                        engine.practice_target_key = board_inspected_key
                                        engine.is_practice_drill = True
                                        engine.switch_mode("SPRINT", keep_custom=True)
                                elif k_id not in ("Shift_L", "Shift_R", "Ctrl_L", "Ctrl_R", "Alt_L", "Alt_R", "Caps", "Tab"):
                                    board_inspected_key = k_id
                                    last_pressed_char = k_id
                                    last_key_press_time = time.time()
                                    board_scroll = 0
                                    board_notice = None
                            break
                    if not handled_btn:
                        for r_y, t_ch in board_table_rows_meta:
                            if my == r_y:
                                board_inspected_key = t_ch
                                last_pressed_char = t_ch
                                last_key_press_time = time.time()
                                board_scroll = 0
                                break
                elif my == drill_button_row and engine.mode == "TUTOR" and (bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED)):
                    bx1, bx2 = drill_button_bounds
                    if bx1 <= mx <= bx2:
                        engine.next_drill()
                        last_pressed_char = None
                        last_target_mistyped = None
            except curses.error:
                pass
            continue

        # Keyboard shortcuts
        if ch in (27, 3):  # ESC or Ctrl+C
            if ch == 27 and engine.mode == "BOARD" and board_inspected_key is not None:
                board_inspected_key = None
                board_scroll = 0
                continue
            break
        elif ch == ord('1') and (len(engine.typed_chars) == 0 or engine.mode == "BOARD" or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '1')):
            engine.switch_mode("SPRINT")
        elif ch == ord('2') and (len(engine.typed_chars) == 0 or engine.mode == "BOARD" or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '2')):
            engine.switch_mode("ENDLESS")
        elif ch == ord('3') and (len(engine.typed_chars) == 0 or engine.mode == "BOARD" or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '3')):
            engine.switch_mode("TUTOR")
        elif ch == ord('4') and (len(engine.typed_chars) == 0 or engine.mode == "BOARD" or (curr_idx < len(engine.target_text) and engine.target_text[curr_idx] != '4')):
            engine.switch_mode("BOARD")
        elif ch == 9:  # TAB -> cycle modes SPRINT -> ENDLESS -> TUTOR -> BOARD -> SPRINT
            mode_cycle = {"SPRINT": "ENDLESS", "ENDLESS": "TUTOR", "TUTOR": "BOARD", "BOARD": "SPRINT"}
            engine.switch_mode(mode_cycle.get(engine.mode, "SPRINT"))
        elif ch in (18, 263, curses.KEY_F5):  # Ctrl+R or F5 -> Reset
            engine.reset()
            last_pressed_char = None
            last_target_mistyped = None
        elif ch in (curses.KEY_BACKSPACE, 127, 8, ord('\b')):
            last_pressed_char = "Bksp"
            last_key_press_time = time.time()
            if engine.mode == "BOARD" and board_inspected_key is not None:
                board_inspected_key = None
                board_scroll = 0
                continue
            engine.backspace()
            last_target_mistyped = None
            last_press_was_correct = True
        elif ch in (10, 13, curses.KEY_ENTER):
            last_pressed_char = "Enter"
            last_key_press_time = time.time()
            if engine.mode == "BOARD":
                if board_inspected_key is not None:
                    words = engine.tracker.generate_words_for_single_key(board_inspected_key, count=25)
                    engine.custom_text = words
                    engine.practice_target_key = board_inspected_key
                    engine.is_practice_drill = True
                    engine.switch_mode("SPRINT", keep_custom=True)
                    continue
                else:
                    weak_words = engine.tracker.generate_practice_words(count=30, session_only=board_session_only)
                    if weak_words:
                        engine.custom_text = weak_words
                        engine.practice_target_key = None
                        engine.is_practice_drill = True
                        engine.switch_mode("SPRINT", keep_custom=True)
                        continue
                    else:
                        board_notice = "No weak letters recorded yet! Press any key (e.g. [D]) to drill it."
                        board_notice_time = time.time()
                        continue
            elif engine.mode == "TUTOR":
                if engine.completed or not engine.target_text:
                    engine.next_drill()
                    last_pressed_char = None
                    last_target_mistyped = None
            elif engine.completed:
                if engine.practice_target_key:
                    engine.custom_text = engine.tracker.generate_words_for_single_key(engine.practice_target_key, count=25)
                    engine.is_practice_drill = True
                    engine.reset()
                else:
                    engine.reset()
        elif ch == curses.KEY_F2:
            if engine.mode == "TUTOR":
                engine.next_drill()
                last_pressed_char = None
                last_target_mistyped = None

        # Board Mode navigation
        if engine.mode == "BOARD":
            if ch in (curses.KEY_F1,):
                board_session_only = not board_session_only
                board_scroll = 0
                board_notice = "Switched to " + ("Session Stats" if board_session_only else "All-Time Stats")
                board_notice_time = time.time()
                continue
            elif ch in (curses.KEY_F2,):
                weak_words = engine.tracker.generate_practice_words(count=30, session_only=board_session_only)
                if weak_words:
                    engine.custom_text = weak_words
                    engine.practice_target_key = None
                    engine.is_practice_drill = True
                    engine.switch_mode("SPRINT", keep_custom=True)
                else:
                    board_notice = "No weak letters recorded yet to practice!"
                    board_notice_time = time.time()
                continue
            elif ch in (curses.KEY_F3, curses.KEY_DC):
                engine.tracker.clear(all_time=not board_session_only)
                board_scroll = 0
                board_notice = "Cleared " + ("Session Stats" if board_session_only else "All-Time Stats")
                board_notice_time = time.time()
                board_inspected_key = None
                continue
            elif ch in (curses.KEY_UP, curses.KEY_PPAGE):
                board_scroll = max(0, board_scroll - 1)
                continue
            elif ch in (curses.KEY_DOWN, curses.KEY_NPAGE):
                board_scroll += 1
                continue

        elif 32 <= ch <= 126:  # Printable ASCII characters (INCLUDING SPACE 32!)
            pressed_char = chr(ch)

            if engine.mode == "BOARD":
                # User pressed a key on the Error Board: inspect that specific key and place it at the top!
                inspected = pressed_char.lower() if pressed_char.isalpha() else pressed_char
                board_inspected_key = inspected
                last_pressed_char = inspected
                last_key_press_time = time.time()
                board_scroll = 0
                board_notice = None
                continue

            last_pressed_char = pressed_char
            last_key_press_time = time.time()

            if engine.mode == "TUTOR":
                if not engine.target_text:
                    # Free Key Explorer
                    engine.total_keystrokes += 1
                    last_press_was_correct = True
                    last_target_mistyped = None
                else:
                    if curr_idx < len(engine.target_text):
                        if pressed_char == engine.target_text[curr_idx]:
                            last_press_was_correct = True
                            last_target_mistyped = None
                        else:
                            last_press_was_correct = False
                            last_target_mistyped = engine.target_text[curr_idx]
                        engine.add_char(pressed_char)
            else:
                engine.add_char(pressed_char)

    return last_stats, engine.mode, engine.tracker

def main():
    parser = argparse.ArgumentParser(
        prog="ttyping",
        description="Terminal Typing Game - Sprint WPM testing, Endless practice, Touch Typing Tutor & Error Board",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Modes:
  1: Sprint   - Simple, natural sentences you finish in 1-2 minutes to test your WPM.
  2: Endless  - Endless session with controlled frequency:
                * Numbers appear once every 100 words
                * Special symbols appear once every 200 words
                * Comma and fullstop appear once every ~35 words
                * Clean arbitrary words in between
  3: Tutor    - Interactive Touch Typing Tutor:
                * Full QWERTY keyboard layout
                * Faded hand & finger positions (Left & Right hands)
                * Real-time finger guidance for every key you type
                * Free Key Explorer drill to test any key on your keyboard
  4: Board    - Error & Mistake Board:
                * Tracks every mistyped letter (e.g. typing E instead of D)
                * Confusion matrix showing exactly what you press incorrectly
                * Finger analysis and root cause diagnosis
                * Targeted practice drills for your weakest keys
"""
    )
    parser.add_argument("-1", "--sprint", action="store_true", help="Launch directly in Sprint Mode (1-2 min WPM test)")
    parser.add_argument("-2", "--endless", action="store_true", help="Launch directly in Endless Mode (controlled practice)")
    parser.add_argument("-3", "--tutor", action="store_true", help="Launch directly in Tutor Mode (QWERTY touch typing finger guide)")
    parser.add_argument("-4", "--board", "--errors", action="store_true", help="Launch directly in Error & Mistake Board")
    parser.add_argument("custom", nargs="*", help="Optional custom text or sentence to practice")

    args = parser.parse_args()

    mode = "SPRINT"
    if args.board:
        mode = "BOARD"
    elif args.tutor:
        mode = "TUTOR"
    elif args.endless:
        mode = "ENDLESS"
    elif args.sprint:
        mode = "SPRINT"

    custom_text = " ".join(args.custom) if args.custom else None

    try:
        result = curses.wrapper(run_game, mode, custom_text)
        if result:
            final_stats, final_mode, final_tracker = result
        else:
            final_stats, final_mode, final_tracker = None, mode, None
    except KeyboardInterrupt:
        final_stats, final_mode, final_tracker = None, mode, None

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
    if final_tracker:
        top_errs = final_tracker.get_summary_list(session_only=True)[:4]
        if top_errs:
            print("-" * 50)
            print("  ⚠️  Most Mistyped Keys (This Session):")
            for e in top_errs:
                t_str = repr_ch(e["target"])
                parts = [f"'{repr_ch(w)}' ({c}x)" for w, c in list(e["mistypes"].items())[:3]]
                print(f"     • Target [{t_str}] ➔ typed: {', '.join(parts)}  ({e['diagnosis']})")
    print("=" * 50)
    print("Thanks for playing! Run 'ttyping' anytime to play again.\n")

if __name__ == "__main__":
    main()
