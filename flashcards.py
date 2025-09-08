from gui_class import MyGUI
from tkinter import messagebox
import random
import pandas as pd
import os

BACKGROUND_COLOR = "#BFDFFF"

# --------- CREATE THE DICTIONARY AND LOAD DATA --------------- #
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, 'spanish_popular_words-to_english.csv')
df = pd.read_csv(csv_path)
sp_dict = df.to_dict(orient='records')

# ---------------- LEARNED WORDS -------------------------- #
learned_path = os.path.join(base_dir, 'words_learned.csv')

# --------- LOOKING FOR THE FILE WITH UNKNOWN WORDS ------------- #
try:
    df = pd.read_csv(os.path.join(base_dir, 'words_to_learn.csv'))
    pool = df.to_dict(orient='records')
except FileNotFoundError:
    pool = sp_dict.copy()

def random_index():
    return random.randint(0, len(pool) - 1) if pool else 0

# Pick an initial card
if not pool:
    # Nothing to study
    messagebox.showinfo("Done", "No words available to study.")
    raise SystemExit

idx = random_index()
wd = pool[idx]["word"]
eng_wd = pool[idx]["English Word Translation"]


def _show_spanish(gui: MyGUI):
    """Show front (Spanish) and arm auto flip."""
    gui.canvas.itemconfig("card_front", image=gui.card_front)
    gui.canvas.itemconfig('language', fill='black', text="Spanish")
    gui.canvas.itemconfig('spanish_word', fill='black', text=wd)
    gui.is_english = False
    gui.cancel_flip()
    gui.schedule_flip(3000, lambda: flip_card(gui))


def _show_english(gui: MyGUI):
    """Show back (English). No auto flip back."""
    gui.canvas.itemconfig("card_front", image=gui.card_back)
    gui.canvas.itemconfig("language", fill="white", text="English")
    gui.canvas.itemconfig("spanish_word", fill="white", text=eng_wd)
    gui.is_english = True


def save_words_to_learn(pool, base_dir):
    """Safely save the current pool of unknown words to words_to_learn.csv."""
    tmp = os.path.join(base_dir, 'words_to_learn.tmp.csv')
    final = os.path.join(base_dir, 'words_to_learn.csv')
    pd.DataFrame(pool).to_csv(tmp, index=False)
    os.replace(tmp, final)


def _pick_new_index(exclude_idx=None):
    """Pick a random index different from exclude_idx when possible."""
    if not pool:
        return 0
    if len(pool) == 1:
        return 0
    new_idx = random_index()
    while exclude_idx is not None and len(pool) > 1 and new_idx == exclude_idx:
        new_idx = random_index()
    return new_idx


def flip_card(gui: MyGUI):
    # initialize state once
    if not hasattr(gui, 'is_english'):
        gui.is_english = False

    gui.cancel_flip()

    if gui.is_english:
        _show_spanish(gui)
    else:
        _show_english(gui)


def next_word(gui: MyGUI):
    """Get a new word WITHOUT removing the current one (keeps in study pool)."""
    global idx, wd, eng_wd

    if not pool:
        messagebox.showinfo("Done", "No words available to study.")
        gui.show_congrats()
        gui.cancel_flip()
        return

    new_idx = _pick_new_index(exclude_idx=idx)
    idx = new_idx
    wd = pool[idx]["word"]
    eng_wd = pool[idx]["English Word Translation"]

    _show_spanish(gui)


def mastered_word(gui: MyGUI):
    """
    Mark current word as mastered:
      - remove from pool
      - append to words_learned.csv
      - save updated pool to words_to_learn.csv
      - show next word (if any)
    """
    global idx, wd, eng_wd

    if not pool:
        messagebox.showinfo("Done", "No words available to study.")
        gui.show_congrats()
        gui.cancel_flip()
        return

    # Remove current word from pool and persist
    mastered = pool.pop(idx)

    # Save pool and learned word
    save_words_to_learn(pool, base_dir)
    pd.DataFrame([mastered]).to_csv(
        learned_path,
        mode="a",
        header=not os.path.exists(learned_path),
        index=False
    )

    if not pool:
        # No more words left
        messagebox.showinfo("Congratulations!", "You've mastered all words!")
        gui.show_congrats()
        gui.cancel_flip()
        return

    # Pick next index (avoid same index when possible)
    new_idx = _pick_new_index(exclude_idx=None if idx >= len(pool) else idx)
    idx = new_idx
    wd = pool[idx]["word"]
    eng_wd = pool[idx]["English Word Translation"]

    _show_spanish(gui)


# Build app with Option B callbacks
app = MyGUI(
    wd,
    on_flip=lambda: flip_card(app),
    on_next=lambda: next_word(app),
    on_mastered=lambda: mastered_word(app),
)

# Arm the initial auto flip
app.schedule_flip(3000, lambda: flip_card(app))

app.run()
