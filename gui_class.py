import os
import tkinter as tk
import tkinter.font as tkfont

BACKGROUND_COLOR = "#BFDFFF"
MENU_FONT = ("Arial", 14, "bold")   # unified font for top bar and dropdowns

def _mk_menu_label(parent, text, menu, font):
    lbl = tk.Label(
        parent, text=text, font=font,
        bg=BACKGROUND_COLOR, fg="black",
        bd=0, highlightthickness=0,  # kill borders
        padx=0, pady=0,              # no internal padding
        cursor="hand2"
    )
    def _open_menu(e, m=menu):
        m.tk_popup(e.x_root, e.y_root + 2)  # tiny drop below the text
        try: m.grab_release()
        except Exception: pass
    lbl.bind("<Button-1>", _open_menu)
    return lbl


class MyGUI:
    """
    Buttons:
      ❌ Don't know -> flip
      ➜ Next -> next random card
      ✅ Mastered -> remove from study pool (Words-to-Learn only)
      ❤ Favorite -> add to favorites; in Favorites view, toggles removal

    Top bar (custom, large font):
      View | Auto-Flip Timer | Direction | Study
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
            on_direction_s2e,
            on_direction_e2s,
            # --- Study controls ---
            on_traverse_random,
            on_traverse_linear,
            on_set_range,
            on_clear_range,
            on_reset_study,
    ):
        self.main_window = tk.Tk()
        self.main_window.title("Flashcards")
        self.main_window.geometry("900x720")
        self.main_window.configure(padx=50, pady=20, background=BACKGROUND_COLOR)

        # Keep dropdown items consistent too (affects Menu widgets, not needed for Menubutton labels)
        self.main_window.option_add("*Menu.font", MENU_FONT)

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

        # --- Custom large “menubar” row (row 0) ---
        topbar = tk.Frame(self.main_window, bg=BACKGROUND_COLOR)
        topbar.grid(row=0, column=0, columnspan=4, sticky="w", padx=0, pady=(0, 10))  # no vertical padding
        # Force the top row to be only as tall as the text
        f = tkfont.Font(self.main_window, font=MENU_FONT)
        line_h = f.metrics("linespace")
        topbar.configure(height=line_h)
        topbar.grid_propagate(False)  # don't let children stretch the frame taller

        # Menus (dropdowns) – keep exactly as you already have
        view_menu = tk.Menu(topbar, tearoff=0, font=MENU_FONT)
        timer_menu = tk.Menu(topbar, tearoff=0, font=MENU_FONT)
        direction_menu = tk.Menu(topbar, tearoff=0, font=MENU_FONT)
        study_menu = tk.Menu(topbar, tearoff=0, font=MENU_FONT)

        # --- Labels that pop those menus (thinner than Menubuttons) ---
        lbl_view = _mk_menu_label(topbar, "View", view_menu, MENU_FONT)
        lbl_timer = _mk_menu_label(topbar, "Auto-Flip-Timer", timer_menu, MENU_FONT)
        lbl_direction = _mk_menu_label(topbar, "Direction", direction_menu, MENU_FONT)
        lbl_study = _mk_menu_label(topbar, "Study", study_menu, MENU_FONT)

        # Pack with no vertical padding; small horizontal spacing
        for w in (lbl_view, lbl_timer, lbl_direction, lbl_study):
            w.pack(side="left", padx=(0, 12), pady=0)

        # Ticks / state vars
        self.view_var = tk.StringVar(value="to_learn")
        self.direction_var = tk.StringVar(value="S2E")
        self.traverse_var = tk.StringVar(value="random")
        self.timer_var = tk.IntVar(value=3)

        # --- View menu items ---
        view_menu.add_radiobutton(label="Words to Learn", variable=self.view_var, value="to_learn",
                                  command=on_view_to_learn, font=MENU_FONT)
        view_menu.add_radiobutton(label="Known (Learned)", variable=self.view_var, value="learned",
                                  command=on_view_learned, font=MENU_FONT)
        view_menu.add_radiobutton(label="Favorites", variable=self.view_var, value="favorites",
                                  command=on_view_favorites, font=MENU_FONT)

        # --- Timer menu items ---
        for sec in range(3, 11):  # 3 to 10 seconds
            timer_menu.add_radiobutton(label=f"{sec} seconds", variable=self.timer_var, value=sec,
                                       command=lambda s=sec: on_set_timer_value(s), font=MENU_FONT)

        # --- Direction menu items ---
        direction_menu.add_radiobutton(label="Spanish → English (Front: Spanish)", variable=self.direction_var, value="S2E",
                                       command=on_direction_s2e, font=MENU_FONT)
        direction_menu.add_radiobutton(label="English → Spanish (Front: English)", variable=self.direction_var, value="E2S",
                                       command=on_direction_e2s, font=MENU_FONT)

        # --- Study menu items ---
        traverse_menu = tk.Menu(study_menu, tearoff=0, font=MENU_FONT)
        traverse_menu.add_radiobutton(label="Random order", variable=self.traverse_var, value="random",
                                      command=on_traverse_random, font=MENU_FONT)
        traverse_menu.add_radiobutton(label="In order (linear)", variable=self.traverse_var, value="linear",
                                      command=on_traverse_linear, font=MENU_FONT)
        study_menu.add_cascade(label="Traversal", menu=traverse_menu)
        study_menu.add_command(label="Set Range…", command=on_set_range, font=MENU_FONT)
        study_menu.add_command(label="Clear Range", command=on_clear_range, font=MENU_FONT)
        study_menu.add_separator()
        study_menu.add_command(label="Reset Study List…", command=on_reset_study, font=MENU_FONT)


        # --- Canvas (moved to row 1) ---
        self.canvas = tk.Canvas(self.main_window, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        self.canvas.grid_configure(pady=0, ipady=0)

        # Card + texts
        self.bg_image_id = self.canvas.create_image(400, 263, image=self.card_front, tags="card_front")
        self.language_id = self.canvas.create_text(400, 75, text="Spanish", font=('Arial', 40, 'italic'), tags="language")
        self.word_id = self.canvas.create_text(400, 263, text=initial_word, font=('Arial', 60, 'bold'), tags="spanish_word")

        # Congrats overlay (hidden)
        self.congrats_id = self.canvas.create_image(400, 263, image=self.congratulations, state='hidden', tags='congratulations')

        # --- Bottom buttons (moved to row 2) ---
        self.dont_know_button = tk.Button(
            self.main_window,
            image=self.wrong_mark,
            text="Learning",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_flip
        )
        self.dont_know_button.grid(row=2, column=0, padx=10, pady=10)

        self.favorite_button = tk.Button(
            self.main_window,
            image=self.heart_img,
            text="Favorite",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_favorite
        )
        self.favorite_button.grid(row=2, column=1, padx=10, pady=10)

        self.mastered_button = tk.Button(
            self.main_window,
            image=self.right_mark,
            text="Known",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_mastered
        )
        self.mastered_button.grid(row=2, column=2, padx=10, pady=10)

        self.next_button = tk.Button(
            self.main_window,
            image=self.next_img,
            text="Next",
            compound="top",
            font=("Arial", 10, "bold"),
            highlightthickness=0,
            command=on_next
        )
        self.next_button.grid(row=2, column=3, padx=10, pady=10)

        # Keyboard shortcuts
        self.main_window.bind("<Return>", lambda e: on_flip())   # flip
        self.main_window.bind("n", lambda e: on_next())          # next
        self.main_window.bind("m", lambda e: on_mastered())      # mastered
        self.main_window.bind("f", lambda e: on_favorite())      # favorite
        self.main_window.bind("g", lambda e: self.show_congrats())  # show congrats overlay

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

    def set_traverse_tick(self, mode: str):
        self.traverse_var.set(mode)

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

