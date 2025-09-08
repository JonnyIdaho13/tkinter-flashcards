import os
import tkinter as tk

BACKGROUND_COLOR = "#BFDFFF"


class MyGUI:
    """
    Option B UI:
      - ❌ Don't know: flips the card (keeps word in pool)
      - 🔄 Next: new random word (keeps word in pool)
      - ✅ Mastered: remove from pool + save to learned
    """
    def __init__(self, initial_word: str, on_flip, on_next, on_mastered):
        self.main_window = tk.Tk()
        self.main_window.title("Flashcards")
        self.main_window.geometry("900x700")
        self.main_window.configure(padx=50, pady=50, background=BACKGROUND_COLOR)

        # Timer handle for auto-flip
        self.flip_timer_id = None

        # Images
        base_dir = os.path.dirname(__file__)
        self.card_front = tk.PhotoImage(file=os.path.join(base_dir, "images", "card_front.png"))
        self.card_back = tk.PhotoImage(file=os.path.join(base_dir, "images", "card_back.png"))
        self.right_mark = tk.PhotoImage(file=os.path.join(base_dir, "images", "right.png"))
        self.wrong_mark = tk.PhotoImage(file=os.path.join(base_dir, "images", "wrong.png"))
        self.next = tk.PhotoImage(file=os.path.join(base_dir, "images", "next.png"))
        self.congratulations = tk.PhotoImage(file=os.path.join(base_dir, "images", "congratulations.png"))

        # Canvas
        self.canvas = tk.Canvas(self.main_window, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        # Span 3 columns (we now have 3 buttons)
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Background image + texts (use consistent tags used by controller)
        self.bg_image_id = self.canvas.create_image(400, 263, image=self.card_front, tags="card_front")
        self.language_id = self.canvas.create_text(400, 75, text="Spanish", font=('Arial', 40, 'italic'), tags="language")
        self.word_id = self.canvas.create_text(400, 263, text=initial_word, font=('Arial', 60, 'bold'), tags="spanish_word")

        # Hidden congratulations overlay (we'll show it when done)
        self.congrats_id = self.canvas.create_image(400, 263, image=self.congratulations,
                                                    state='hidden', tags='congratulations')

        # Buttons (delegates actions to controller callbacks)
        # ❌ Don't know -> flip
        self.dont_know_button = tk.Button(self.main_window, image=self.wrong_mark, highlightthickness=0, command=on_flip)
        self.dont_know_button.grid(row=1, column=0, padx=10, pady=10)

        # 🔄 Next -> new random word (text button; we don't have a 'next' icon asset)
        self.next_button = tk.Button(self.main_window, image=self.next, font=("Arial", 14, "bold"),
                                     relief="ridge", padx=18, pady=8, command=on_next)
        self.next_button.grid(row=1, column=1, padx=10, pady=10)

        # ✅ Mastered -> remove + save
        self.mastered_button = tk.Button(self.main_window, image=self.right_mark, highlightthickness=0, command=on_mastered)
        self.mastered_button.grid(row=1, column=2, padx=10, pady=10)

        # Keyboard shortcuts
        #   Enter: flip
        #   n: next
        #   m: mastered
        self.main_window.bind("<Return>", lambda e: on_flip())
        self.main_window.bind("n", lambda e: on_next())
        self.main_window.bind("m", lambda e: on_mastered())

        # ------------- Timer Functionality --------------- #
        def _safe_cancel():
            if self.flip_timer_id is not None:
                try:
                    self.main_window.after_cancel(self.flip_timer_id)
                except Exception:
                    pass
                finally:
                    self.flip_timer_id = None

        self.cancel_flip = _safe_cancel

        def _schedule(ms, fn):
            _safe_cancel()
            self.flip_timer_id = self.main_window.after(ms, fn)

        self.schedule_flip = _schedule

    def show_congrats(self):
        # Disable buttons and show overlay
        try:
            self.dont_know_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.mastered_button.configure(state="disabled")
        except Exception:
            pass
        self.canvas.itemconfigure('congratulations', state='normal')

    def run(self):
        self.main_window.mainloop()

