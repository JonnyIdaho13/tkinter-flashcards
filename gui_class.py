import os
import tkinter as tk

BACKGROUND_COLOR = "#BFDFFF"


class MyGUI:
    """
    Buttons:
      ❌ Don't know -> flip
      ➜ Next -> next random card
      ✅ Mastered -> remove from study pool (Words-to-Learn only)
      ❤ Favorite -> add to favorites; in Favorites view, toggles removal

    Menubar:
      View -> Words to Learn | Known (Learned) | Favorites
    """

    def __init__(
            self,
            initial_word: str,
            on_flip,
            on_next,
            on_mastered,
            on_favorite,
            on_view_to_learn,
            on_view_learned,
            on_view_favorites,
            on_set_timer_value,
            on_direction_s2e,  # NEW
            on_direction_e2s,  # NEW
    ):

        self.main_window = tk.Tk()
        self.main_window.title("Flashcards")
        self.main_window.geometry("900x720")
        self.main_window.configure(padx=50, pady=50, background=BACKGROUND_COLOR)

        # Timer handle for auto-flip
        self.flip_timer_id = None

        # Images
        base_dir = os.path.dirname(__file__)
        self.card_front = tk.PhotoImage(file=os.path.join(base_dir, "images", "card_front.png"))
        self.card_back = tk.PhotoImage(file=os.path.join(base_dir, "images", "card_back.png"))
        self.right_mark = tk.PhotoImage(file=os.path.join(base_dir, "images", "right.png"))
        self.wrong_mark = tk.PhotoImage(file=os.path.join(base_dir, "images", "wrong.png"))
        self.next_img = tk.PhotoImage(file=os.path.join(base_dir, "images", "next.png"))
        self.heart_img = tk.PhotoImage(file=os.path.join(base_dir, "images", "favorite.png"))
        self.congratulations = tk.PhotoImage(file=os.path.join(base_dir, "images", "congratulations.png"))

        # Canvas (span 4 columns for 4 buttons)
        self.canvas = tk.Canvas(self.main_window, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=4)

        # Card + texts
        self.bg_image_id = self.canvas.create_image(400, 263, image=self.card_front, tags="card_front")
        self.language_id = self.canvas.create_text(400, 75, text="Spanish", font=('Arial', 40, 'italic'), tags="language")
        self.word_id = self.canvas.create_text(400, 263, text=initial_word, font=('Arial', 60, 'bold'), tags="spanish_word")

        # Congrats overlay (hidden)
        self.congrats_id = self.canvas.create_image(400, 263, image=self.congratulations, state='hidden', tags='congratulations')

        # Buttons
        self.dont_know_button = tk.Button(
            self.main_window,
            image=self.wrong_mark,
            text="Learning",
            compound="top",  # image above, text below
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_flip
        )
        self.dont_know_button.grid(row=1, column=0, padx=10, pady=10)

        self.next_button = tk.Button(
            self.main_window,
            image=self.next_img,
            text="Next",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_next
        )
        self.next_button.grid(row=1, column=3, padx=10, pady=10)

        self.mastered_button = tk.Button(
            self.main_window,
            image=self.right_mark,
            text="Known",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_mastered
        )
        self.mastered_button.grid(row=1, column=2, padx=10, pady=10)

        self.favorite_button = tk.Button(
            self.main_window,
            image=self.heart_img,
            text="Favorite",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_favorite
        )
        self.favorite_button.grid(row=1, column=1, padx=10, pady=10)

        # Keyboard shortcuts
        self.main_window.bind("<Return>", lambda e: on_flip())   # flip
        self.main_window.bind("n", lambda e: on_next())          # next
        self.main_window.bind("m", lambda e: on_mastered())      # mastered
        self.main_window.bind("f", lambda e: on_favorite())      # favorite
        self.main_window.bind("g", lambda e: self.show_congrats()) # show congrats animation

        # Menu bar
        menubar = tk.Menu(self.main_window)

        # Track ticks for View & Direction menus
        self.view_var = tk.StringVar(value="to_learn")  # matches default in flashcards.py
        self.direction_var = tk.StringVar(value="S2E")  # Spanish→English default

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_radiobutton(label="Words to Learn", variable=self.view_var, value="to_learn", command=on_view_to_learn)
        view_menu.add_radiobutton(label="Known (Learned)", variable=self.view_var, value="learned", command=on_view_learned)
        view_menu.add_radiobutton(label="Favorites", variable=self.view_var, value="favorites", command=on_view_favorites)
        menubar.add_cascade(label="View", menu=view_menu)

        # --- Timer menu with radio buttons ---
        self.timer_var = tk.IntVar(value=3)  # default seconds
        timer_menu = tk.Menu(menubar, tearoff=0)
        for sec in range(3, 11):  # 3 to 10 seconds
            timer_menu.add_radiobutton(
                label=f"{sec} seconds",
                variable=self.timer_var,
                value=sec,
                command=lambda s=sec: on_set_timer_value(s)
            )
        menubar.add_cascade(label="Auto-Flip Timer", menu=timer_menu)

        # --- Direction menu ---
        direction_menu = tk.Menu(menubar, tearoff=0)
        direction_menu.add_radiobutton(label="Spanish → English (Front: Spanish)", variable=self.direction_var, value="S2E", command=on_direction_s2e)
        direction_menu.add_radiobutton(label="English → Spanish (Front: English)", variable=self.direction_var, value="E2S", command=on_direction_e2s)
        menubar.add_cascade(label="Direction", menu=direction_menu)

        self.main_window.config(menu=menubar)


        # ---- Timer helpers ----
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

    def set_view_tick(self, mode: str):
        self.view_var.set(mode)

    def set_direction_tick(self, direction: str):
        self.direction_var.set(direction)

    def show_congrats(self):
        try:
            self.dont_know_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.mastered_button.configure(state="disabled")
            self.favorite_button.configure(state="disabled")
        except Exception:
            pass
        self.canvas.itemconfigure('congratulations', state='normal')

    def run(self):
        self.main_window.mainloop()
