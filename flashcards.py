from gui_class import MyGUI
from tkinter import messagebox, simpledialog
import random
import pandas as pd
import os

flip_delay_ms = 3000
BACKGROUND_COLOR = "#BFDFFF"

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
def random_index():
    pool = _active_pool()
    return random.randint(0, len(pool) - 1) if pool else 0

if not _active_pool():
    messagebox.showinfo("Done", "No words available to study.")
    raise SystemExit

idx = random_index()
def _rebind_from_idx():
    global wd, eng_wd
    pool = _active_pool()
    wd = pool[idx]["word"]
    eng_wd = pool[idx]["English Word Translation"]

_rebind_from_idx()

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
    global active_mode, idx
    active_mode = mode
    pool = _active_pool()
    if not pool:
        messagebox.showinfo("Empty", "No words in this view.")
        gui.cancel_flip()
        return
    idx = random_index()
    _rebind_from_idx()
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
    global idx
    pool = _active_pool()
    if not pool:
        messagebox.showinfo("Done", "No words in this view.")
        gui.cancel_flip()
        return
    idx = _pick_new_index(exclude_idx=idx)
    _rebind_from_idx()
    _show_front(gui)

def mastered_word(gui: MyGUI):
    """Only in Words-to-Learn view: move word to learned + remove from to-learn."""
    global idx
    if active_mode != MODE_TO_LEARN:
        messagebox.showinfo("Not available", "‘Mastered’ only works in the Words to Learn view.")
        return
    if not TO_LEARN:
        messagebox.showinfo("Done", "No words to learn.")
        gui.cancel_flip()
        return

    mastered = TO_LEARN.pop(idx)
    _save_to_learn()
    _save_learned_append([mastered])
    LEARNED.append(mastered)

    if not TO_LEARN:
        messagebox.showinfo("Congratulations!", "You've mastered all words!")
        gui.show_congrats()
        gui.cancel_flip()
        return

    idx = idx % len(TO_LEARN)
    _rebind_from_idx()
    _show_front(gui)

def favorite_toggle(gui: MyGUI):
    """
    Add to favorites from any view.
    If currently in Favorites view, pressing favorite toggles removal.
    """
    global idx
    pool = _active_pool()
    if not pool:
        messagebox.showinfo("Empty", "No words in this view.")
        return

    current = pool[idx]
    key = current["word"]

    def _in_favorites(w):
        return any(row.get("word") == w for row in FAVORITES)

    if active_mode == MODE_FAVORITES:
        # Toggle removal only while viewing Favorites
        if _in_favorites(key):
            FAVORITES[:] = [row for row in FAVORITES if row.get("word") != key]
            _save_favorites()
            if not FAVORITES:
                messagebox.showinfo("Favorites", "No favorites left.")
                return
            idx = idx % len(FAVORITES)
            _rebind_from_idx()
            _show_front(gui)
        else:
            FAVORITES.append(current)
            _save_favorites()
            _show_front(gui)
    else:
        if not _in_favorites(key):
            FAVORITES.append(current)
            _save_favorites()
            messagebox.showinfo("Favorites", f"Added ‘{key}’ to favorites.")
        else:
            messagebox.showinfo("Favorites", f"‘{key}’ is already in favorites.")

def set_direction_s2e(gui: MyGUI):
    global active_direction
    active_direction = DIRECTION_SPANISH_TO_ENGLISH
    _show_front(gui)

def set_direction_e2s(gui: MyGUI):
    global active_direction
    active_direction = DIRECTION_ENGLISH_TO_SPANISH
    _show_front(gui)


# ---------- APP ----------
app = MyGUI(
    initial_word=_active_pool()[idx]["word"],
    on_flip=lambda: flip_card(app),
    on_next=lambda: next_word(app),
    on_mastered=lambda: mastered_word(app),
    on_favorite=lambda: favorite_toggle(app),
    on_view_to_learn=lambda: view_to_learn(app),
    on_view_learned=lambda: view_learned(app),
    on_view_favorites=lambda: view_favorites(app),
    on_set_timer_value=lambda sec: set_flip_delay_value(app, sec),
    on_direction_s2e=lambda: set_direction_s2e(app),   # <-- add
    on_direction_e2s=lambda: set_direction_e2s(app)    # <-- add
)

app.schedule_flip(flip_delay_ms, lambda: flip_card(app))
app.run()
