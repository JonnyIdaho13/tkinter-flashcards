import os
import tkinter as tk

BACKGROUND_COLOR = "#BFDFFF"


class MyGUI:
    def __init__(self, initial_word: str, on_flip, on_refresh):
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
        self.congratulations = tk.PhotoImage(file=os.path.join(base_dir, "images", "congratulations.png"))

        # Canvas
        self.canvas = tk.Canvas(self.main_window, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=2)

        # Background image + texts (use consistent tags used by controller)
        self.bg_image_id = self.canvas.create_image(400, 263, image=self.card_front, tags="card_front")
        self.language_id = self.canvas.create_text(400, 75, text="Spanish", font=('Arial', 40, 'italic'), tags="language")
        self.word_id = self.canvas.create_text(400, 263, text=initial_word, font=('Arial', 60, 'bold'), tags="spanish_word")

        # Buttons (delegates actions to controller callbacks)
        self.dont_know_button = tk.Button(self.main_window, image=self.wrong_mark, highlightthickness=0, command=on_flip)
        self.dont_know_button.grid(row=1, column=0)

        self.know_button = tk.Button(self.main_window, image=self.right_mark, highlightthickness=0, command=on_refresh)
        self.know_button.grid(row=1, column=1)

        # Keyboard
        self.main_window.bind("<Return>", lambda e: on_flip())

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

    def run(self):
        self.main_window.mainloop()



