# Spanish Flashcards (Tkinter)

A clean, portfolio-ready flashcards app built with Tkinter. It auto-flips from Spanish to English, supports keyboard shortcuts, and persists your progress. Designed with a simple MVC-ish split between the GUI (`MyGUI`) and controller logic.

## Demo
'images/front_of_card_example.png'
'images/back_of_card_example.png'


## Features
- Auto-flip from front (Spanish) to back (English) after a delay
- Keyboard shortcuts:
  - **Enter**: flip
  - **N**: next word
  - **M**: mark mastered
- Persistent progress:
  - `words_to_learn.csv` (remaining study words)
  - `words_learned.csv` (append-only log of mastered words)
- Clean separation of concerns (`gui_class.py` vs `flashcards.py`)

## Getting Started
```bash
# (Optional) create a venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Run
python flashcards.py
