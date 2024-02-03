import tkinter as tk
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk
import pygame
import os

# Set the default time for work and break intervals
WORK_TIME = 25 * 60  # 25 minutes
SHORT_BREAK_TIME = 5 * 60  # 5 minutes
LONG_BREAK_TIME = 15 * 60  # 15 minutes

class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command=None, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.config(highlightthickness=0)
        self._callback = command

        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.create_text(
            self.width / 2, self.height / 2, text=text, font=("Arial", 12, "bold")
        )

    def _on_press(self, event):
        self.config(relief=tk.SUNKEN)

    def _on_release(self, event):
        self.config(relief=tk.RAISED)
        if self._callback:
            self._callback()

class MovableWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("250x250")
        self.title("Pomodoro Timer")

        # Make the window borderless
        self.overrideredirect(True)

        # Make the window non-closable
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        # Set the opacity to 80%
        # self.attributes("-alpha", 0.7)

        # Keep the window on top
        self.attributes("-topmost", True)

        # Load the background image with Pillow and convert to PhotoImage
        script_dir = os.path.dirname(os.path.realpath(__file__))
        background_image_path = os.path.join(script_dir, "background.jpg")
        background_image = Image.open(background_image_path)
        self.background_image = ImageTk.PhotoImage(background_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.style = ThemedStyle(self)
        self.style.set_theme("clearlooks")

        arabic_font = ("Times New Roman", 16, "bold")
        self.timer_label = tk.Label(
            self, text="ابدأ التايمر يا فاشل", font=arabic_font, bg="lightgray"
        )
        self.timer_label.pack(pady=20)

        self.mode_label = tk.Label(
            self, text="مذاكرة", font=arabic_font, bg="#E2B399"
        )
        self.mode_label.pack(pady=1)

        button_width = 100
        button_height = 40

        self.start_button = RoundButton(
            self,
            text="أبدا",
            command=self.start_timer,
            width=button_width,
            height=button_height,
            bg="lightblue",
        )
        self.start_button.pack(pady=5)

        self.stop_button = RoundButton(
            self,
            text="وقف",
            command=self.stop_timer,
            width=button_width,
            height=button_height,
            bg="lightcoral",
            state=tk.DISABLED,
        )
        self.stop_button.pack(pady=5)

        # Close button in the bottom left
        self.close_button = RoundButton(
            self,
            text="x",
            command=self.close_app,
            width=20,
            height=20,
            bg="#F08080",
            
        )
        self.close_button.place(x=0, rely=1.0, anchor=tk.SW, bordermode=tk.OUTSIDE)

        self.work_time, self.break_time = WORK_TIME, SHORT_BREAK_TIME
        self.is_work_time, self.pomodoros_completed, self.is_running = True, 0, False

        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.dragging)

        pygame.mixer.init()
        self.bind("<FocusOut>", self.on_focus_out)

    def start_timer(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        self.update_timer()

    def stop_timer(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_running = False

    def update_timer(self):
        if self.is_running:
            if self.is_work_time:
                self.work_time -= 1
                if self.work_time == 0:
                    self.is_work_time = False
                    self.pomodoros_completed += 1
                    self.break_time = (
                        LONG_BREAK_TIME
                        if self.pomodoros_completed % 4 == 0
                        else SHORT_BREAK_TIME
                    )
                    self.play_sound("break_time.ogg")
            else:
                self.break_time -= 1
                if self.break_time == 0:
                    self.is_work_time, self.work_time = True, WORK_TIME
                    self.play_sound("break_end.ogg")

            minutes, seconds = divmod(
                self.work_time if self.is_work_time else self.break_time, 60
            )
            self.timer_label.config(text="{:02d}:{:02d}".format(minutes, seconds))

            # Update mode label based on work or break
            mode_text = "عتل و عزق" if self.is_work_time else "فسحة"  # Update this text as needed
            self.mode_label.config(text=mode_text)

            self.after(1000, self.update_timer)

    def start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def dragging(self, event):
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.geometry(f"+{x}+{y}")

    def play_sound(self, sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    def on_focus_out(self, event):
        self.attributes("-topmost", True)

    def close_app(self):
        self.destroy()

if __name__ == "__main__":
    MovableWindow().mainloop()
