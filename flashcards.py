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
    return random.randint(0, len(pool) - 1)

# Pick an initial card
idx = random_index()
wd = pool[idx]["word"]
eng_wd = pool[idx]["English Word Translation"]

def _show_spanish(gui: MyGUI):
    """Show front (Spanish) and arm auto flip."""
    gui.canvas.itemconfig("card_front", image=gui.card_front)
    gui.canvas.itemconfig('language', fill='black', text="Spanish")
    gui.canvas.itemconfig('spanish_word', fill='black', text=wd)
    gui.is_english = False
    # cancel existing flip timer first
    gui.cancel_flip()
    # schedule auto flip -> English after 3s
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


def flip_card(gui: MyGUI):
    # initialize state once
    if not hasattr(gui, 'is_english'):
        gui.is_english = False

    # any manual/auto flip should cancel pending timer first
    gui.cancel_flip()

    # Toggle
    if gui.is_english:
        # English -> Spanish (re-arm auto flip)
        _show_spanish(gui)
    else:
        # Spanish -> English
        _show_english(gui)

def refresh_word(gui: MyGUI):
    global idx, wd, eng_wd
    if len(pool) < 2:
        messagebox.showerror("Not enough words", "You need more words in your database.")
        gui.cancel_flip()
        gui.canvas.itemconfig("congratulations", image=gui.congratulations)
        pool.clear()
        gui.main_window.destroy()
        return

    known = pool.pop(idx)
    save_words_to_learn(pool, base_dir)
    # for future use:
    pd.DataFrame([known]).to_csv(learned_path, mode="a", header=not os.path.exists(learned_path),index=False)

    new_idx = random_index()
    while new_idx == idx:
        new_idx = random_index()
    idx = new_idx
    wd = pool[idx]["word"]
    eng_wd = pool[idx]["English Word Translation"]

    # Show front and (re)start auto flip
    _show_spanish(gui)

app = MyGUI(wd, on_flip=lambda: flip_card(app), on_refresh=lambda: refresh_word(app))

# Arm the initial auto flip
#Note: app has schedule_flip via gui_class.py
app.schedule_flip(3000, lambda: flip_card(app))

app.run()