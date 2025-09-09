from gui_class import MyGUI
from tkinter import messagebox, simpledialog
import random
import pandas as pd
import os

flip_delay_ms = 3000
BACKGROUND_COLOR = "#BFDFFF"

# ---------- STUDY SESSION STATE ----------
STUDY_RANGE = None            # None or (start_1based, end_1based)
TRAVERSE_MODE = "random"      # "random" | "linear"
ACTIVE_LIST = []              # derived from current view + range
cursor = 0                    # index into ACTIVE_LIST


# ---------- PATHS ----------
base_dir = os.path.dirname(__file__)
src_csv_path   = os.path.join(base_dir, 'spanish_popular_words-to_english.csv')
to_learn_path  = os.path.join(base_dir, 'words_to_learn.csv')
learned_path   = os.path.join(base_dir, 'words_learned.csv')
favorites_path = os.path.join(base_dir, 'favorites.csv')

# ---------- LOAD ----------
src_df = pd.read_csv(src_csv_path)
ALL_WORDS = src_df.to_dict(orient='records')

def _load_csv_or_empty(path):
    try:
        return pd.read_csv(path).to_dict(orient='records')
    except FileNotFoundError:
        return []

try:
    to_learn_df = pd.read_csv(to_learn_path)
    TO_LEARN = to_learn_df.to_dict(orient='records')
except FileNotFoundError:
    TO_LEARN = ALL_WORDS.copy()

LEARNED   = _load_csv_or_empty(learned_path)
FAVORITES = _load_csv_or_empty(favorites_path)

# ---------- MODES ----------
MODE_TO_LEARN  = "to_learn"
MODE_LEARNED   = "learned"
MODE_FAVORITES = "favorites"
active_mode = MODE_TO_LEARN
# ----STUDY DIRECTION --------
# ---------- DIRECTION (study direction) ----------
DIRECTION_SPANISH_TO_ENGLISH = "S2E"   # Front: Spanish, Back: English (current default)
DIRECTION_ENGLISH_TO_SPANISH = "E2S"   # Front: English, Back: Spanish
active_direction = DIRECTION_SPANISH_TO_ENGLISH

def set_flip_delay_value(gui: MyGUI, seconds: int):
    global flip_delay_ms
    flip_delay_ms = seconds * 1000

    # Re-schedule if currently showing Spanish
    if hasattr(gui, "is_english") and not gui.is_english:
        gui.schedule_flip(flip_delay_ms, lambda: flip_card(gui))


def _active_pool():
    if active_mode == MODE_TO_LEARN:
        return TO_LEARN
    if active_mode == MODE_LEARNED:
        return LEARNED
    return FAVORITES

# ---------- SAVE HELPERS ----------
def _save_to_learn():
    tmp = os.path.join(base_dir, 'words_to_learn.tmp.csv')
    pd.DataFrame(TO_LEARN).to_csv(tmp, index=False)
    os.replace(tmp, to_learn_path)

def _save_learned_append(rows):
    pd.DataFrame(rows).to_csv(
        learned_path,
        mode="a",
        header=not os.path.exists(learned_path),
        index=False
    )

def _save_favorites():
    tmp = os.path.join(base_dir, 'favorites.tmp.csv')
    pd.DataFrame(FAVORITES).to_csv(tmp, index=False)
    os.replace(tmp, favorites_path)

# ---------- INDEX/WORD STATE ----------

if not _active_pool():
    messagebox.showinfo("Done", "No words available to study.")
    raise SystemExit

def _rebind_from_cursor():
    global wd, eng_wd
    current = ACTIVE_LIST[cursor]
    wd = current["word"]
    eng_wd = current["English Word Translation"]


# ---------- RENDER ----------
def _show_front(gui: MyGUI):
    """
    Show the 'front' of the card depending on direction:
      - S2E: Spanish on front
      - E2S: English on front
    """
    gui.canvas.itemconfig("card_front", image=gui.card_front)
    if active_direction == DIRECTION_SPANISH_TO_ENGLISH:
        gui.canvas.itemconfig('language', fill='black', text="Spanish")
        gui.canvas.itemconfig('spanish_word', fill='black', text=wd)
    else:  # DIRECTION_ENGLISH_TO_SPANISH
        gui.canvas.itemconfig('language', fill='black', text="English")
        gui.canvas.itemconfig('spanish_word', fill='black', text=eng_wd)

    gui.is_english = False  # "False" means we're on the front side
    gui.cancel_flip()
    gui.schedule_flip(flip_delay_ms, lambda: flip_card(gui))


def _show_back(gui: MyGUI):
    """
    Show the 'back' of the card depending on direction:
      - S2E: English on back
      - E2S: Spanish on back
    """
    gui.canvas.itemconfig("card_front", image=gui.card_back)
    if active_direction == DIRECTION_SPANISH_TO_ENGLISH:
        gui.canvas.itemconfig("language", fill="white", text="English")
        gui.canvas.itemconfig("spanish_word", fill="white", text=eng_wd)
    else:  # DIRECTION_ENGLISH_TO_SPANISH
        gui.canvas.itemconfig("language", fill="white", text="Spanish")
        gui.canvas.itemconfig("spanish_word", fill="white", text=wd)

    gui.is_english = True  # "True" means we're on the back side


# ---------- VIEW SWITCH ----------
def _switch_view(gui: MyGUI, mode: str):
    global active_mode, cursor
    active_mode = mode
    gui.set_view_tick(active_mode)

    _rebuild_active_list(gui)
    if not ACTIVE_LIST:
        return

    cursor = 0  # start at first in derived list
    _rebind_from_cursor()
    _show_front(gui)


def view_to_learn(gui: MyGUI):   _switch_view(gui, MODE_TO_LEARN)
def view_learned(gui: MyGUI):    _switch_view(gui, MODE_LEARNED)
def view_favorites(gui: MyGUI):  _switch_view(gui, MODE_FAVORITES)

# ---------- ACTIONS ----------
def flip_card(gui: MyGUI):
    if not hasattr(gui, 'is_english'):
        gui.is_english = False  # start on front
    gui.cancel_flip()
    _show_front(gui) if gui.is_english else _show_back(gui)


def _pick_new_index(exclude_idx=None):
    pool = _active_pool()
    if not pool: return 0
    if len(pool) == 1: return 0
    new_idx = random_index()
    while exclude_idx is not None and len(pool) > 1 and new_idx == exclude_idx:
        new_idx = random_index()
    return new_idx

def next_word(gui: MyGUI):
    global cursor
    if not ACTIVE_LIST:
        messagebox.showinfo("Done", "No words in this view.")
        gui.cancel_flip()
        return

    if TRAVERSE_MODE == "linear":
        cursor = (cursor + 1) % len(ACTIVE_LIST)
    else:  # random
        if len(ACTIVE_LIST) == 1:
            pass
        else:
            new_idx = random.randrange(len(ACTIVE_LIST))
            while new_idx == cursor:
                new_idx = random.randrange(len(ACTIVE_LIST))
            cursor = new_idx

    _rebind_from_cursor()
    _show_front(gui)

def mastered_word(gui: MyGUI):
    global cursor
    if active_mode != MODE_TO_LEARN:
        messagebox.showinfo("Not available", "‘Mastered’ only works in the Words to Learn view.")
        return
    if not ACTIVE_LIST:
        messagebox.showinfo("Done", "No words to learn.")
        gui.cancel_flip()
        return

    current = ACTIVE_LIST[cursor]
    key = current["word"]

    # remove from TO_LEARN by word
    removed = [row for row in TO_LEARN if row.get("word") == key]
    if not removed:
        # nothing to do; rebuild and continue
        _rebuild_active_list(gui);
        if not ACTIVE_LIST: return
        _rebind_from_cursor(); _show_front(gui);
        return

    TO_LEARN[:] = [row for row in TO_LEARN if row.get("word") != key]
    _save_to_learn()
    _save_learned_append(removed)
    LEARNED.extend(removed)

    # rebuild derived list and move on
    _rebuild_active_list(gui)
    if not ACTIVE_LIST:
        messagebox.showinfo("Congratulations!", "You've mastered all words!")
        gui.show_congrats()
        gui.cancel_flip()
        return

    if TRAVERSE_MODE == "linear" and cursor >= len(ACTIVE_LIST):
        cursor = 0
    _rebind_from_cursor()
    _show_front(gui)

def favorite_toggle(gui: MyGUI):
    global cursor
    if not ACTIVE_LIST:
        messagebox.showinfo("Empty", "No words in this view.")
        return

    current = ACTIVE_LIST[cursor]
    key = current["word"]

    def _in_favorites(w): return any(row.get("word") == w for row in FAVORITES)

    if active_mode == MODE_FAVORITES:
        if _in_favorites(key):
            FAVORITES[:] = [row for row in FAVORITES if row.get("word") != key]
            _save_favorites()
            _rebuild_active_list(gui)
            if not ACTIVE_LIST:
                messagebox.showinfo("Favorites", "No favorites left.")
                return
            cursor = cursor % len(ACTIVE_LIST)
            _rebind_from_cursor(); _show_front(gui)
        else:
            FAVORITES.append(current); _save_favorites(); _show_front(gui)
    else:
        if not _in_favorites(key):
            FAVORITES.append(current); _save_favorites()
            messagebox.showinfo("Favorites", f"Added ‘{key}’ to favorites.")
        else:
            messagebox.showinfo("Favorites", f"‘{key}’ is already in favorites.")

def set_direction_s2e(gui: MyGUI):
    global active_direction
    active_direction = DIRECTION_SPANISH_TO_ENGLISH
    gui.set_direction_tick(active_direction)
    _show_front(gui)

def set_direction_e2s(gui: MyGUI):
    global active_direction
    active_direction = DIRECTION_ENGLISH_TO_SPANISH
    gui.set_direction_tick(active_direction)
    _show_front(gui)


def _rebuild_active_list(gui: MyGUI | None = None):
    """Recompute ACTIVE_LIST from current view and STUDY_RANGE."""
    global ACTIVE_LIST, cursor
    base = _active_pool()

    if STUDY_RANGE is None:
        ACTIVE_LIST = list(base)  # keep order
    else:
        start, end = STUDY_RANGE
        # clamp to master length
        end = min(end, len(ALL_WORDS))
        start = max(1, min(start, end))
        allowed = {row["word"] for row in ALL_WORDS[start-1:end]}
        ACTIVE_LIST = [row for row in base if row.get("word") in allowed]

    if not ACTIVE_LIST:
        if gui:
            gui.cancel_flip()
        messagebox.showinfo("Empty", "No words in this range for this view.")
        return

    # keep cursor in-bounds
    cursor = cursor % len(ACTIVE_LIST)

# Build initial ACTIVE_LIST from default view + no range

_rebuild_active_list(None)
if not ACTIVE_LIST:
    messagebox.showinfo("Done", "No words available to study.")
    raise SystemExit
_rebind_from_cursor()

def set_traverse_random(gui: MyGUI):
    global TRAVERSE_MODE
    TRAVERSE_MODE = "random"
    gui.set_traverse_tick(TRAVERSE_MODE)

def set_traverse_linear(gui: MyGUI):
    global TRAVERSE_MODE
    TRAVERSE_MODE = "linear"
    gui.set_traverse_tick(TRAVERSE_MODE)

def set_study_range(gui: MyGUI):
    global STUDY_RANGE, cursor
    s = simpledialog.askstring("Study Range", "Enter range like 1-100:")
    if not s: return
    try:
        parts = s.replace(" ", "").split("-")
        if len(parts) != 2: raise ValueError
        start = int(parts[0]); end = int(parts[1])
        if start < 1 or end < start: raise ValueError
    except ValueError:
        messagebox.showerror("Invalid", "Please enter a valid range like 1-100.")
        return
    STUDY_RANGE = (start, end)
    _rebuild_active_list(gui)
    if ACTIVE_LIST:
        cursor = 0
        _rebind_from_cursor(); _show_front(gui)

def clear_study_range(gui: MyGUI):
    global STUDY_RANGE, cursor
    STUDY_RANGE = None
    _rebuild_active_list(gui)
    if ACTIVE_LIST:
        cursor = 0
        _rebind_from_cursor(); _show_front(gui)

def reset_study_list(gui: MyGUI):
    global TO_LEARN, LEARNED, cursor
    if messagebox.askyesno("Reset Study List", "Reload working list from Master and clear Known?\n(Favorites are NOT changed.)"):
        TO_LEARN = ALL_WORDS.copy()
        _save_to_learn()
        # clear learned file on disk
        open(learned_path, "w").close()
        LEARNED.clear()
        _rebuild_active_list(gui)
        if ACTIVE_LIST:
            cursor = 0
            _rebind_from_cursor(); _show_front(gui)


# ---------- APP ----------
app = MyGUI(
    initial_word=ALL_WORDS[0]["word"],  # any text; we'll immediately rebind from ACTIVE_LIST
    on_flip=lambda: flip_card(app),
    on_next=lambda: next_word(app),
    on_mastered=lambda: mastered_word(app),
    on_favorite=lambda: favorite_toggle(app),
    on_view_to_learn=lambda: view_to_learn(app),
    on_view_learned=lambda: view_learned(app),
    on_view_favorites=lambda: view_favorites(app),
    on_set_timer_value=lambda sec: set_flip_delay_value(app, sec),
    on_direction_s2e=lambda: set_direction_s2e(app),
    on_direction_e2s=lambda: set_direction_e2s(app),
    # NEW:
    on_traverse_random=lambda: set_traverse_random(app),
    on_traverse_linear=lambda: set_traverse_linear(app),
    on_set_range=lambda: set_study_range(app),
    on_clear_range=lambda: clear_study_range(app),
    on_reset_study=lambda: reset_study_list(app),
)

# Initialize menu ticks to match defaults
app.set_view_tick(active_mode)
app.set_direction_tick(active_direction)
app.set_traverse_tick(TRAVERSE_MODE)

# First render from ACTIVE_LIST
_rebind_from_cursor()
app.schedule_flip(flip_delay_ms, lambda: flip_card(app))
app.run()
