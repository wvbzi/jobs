"""Ctrl+C -> BOOM + fullscreen cat. Ctrl+V -> BOOM + a random job application site.

Copy/paste still work normally; the keystrokes are only observed, never blocked.
Runs on Windows and Linux (X11). See README.md for how to start and stop it.
"""
import math
import os
import queue
import random
import shutil
import struct
import subprocess
import sys
import tkinter as tk
import wave
import webbrowser

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import ctypes
    import winsound

from PIL import Image, ImageTk
from pynput import keyboard

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(HERE, "images")
SOUND_FILE = os.path.join(HERE, "sounds", "boom.wav")
SHOW_MS = 500          # how long the picture stays fully visible
FADE_MS = 600          # then how long it takes to fade out

CTRL_C_IMAGE = os.path.join(IMAGE_DIR, "cat.webp")
CTRL_V_URLS = [  # Ctrl+V opens one of these at random
    "https://jobs.mchire.com/",
    "https://www.indeed.com/?from=gnav-acme--acme-webapp",
]

VK_C, VK_V = 0x43, 0x56  # Windows virtual-key codes
CTRL_KEYS = (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)


def letter(key):
    """Return 'c' / 'v' for those keys, else None. Windows reports vk codes; X11 reports the char."""
    vk = getattr(key, "vk", None)
    if vk == VK_C:
        return "c"
    if vk == VK_V:
        return "v"
    char = (getattr(key, "char", None) or "").lower()
    return char if char in ("c", "v") else None


def play_sound(path):
    if IS_WINDOWS:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        return
    for cmd in (["paplay", path], ["pw-play", path], ["aplay", "-q", path],
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]):
        if shutil.which(cmd[0]):
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return


def make_boom(path):
    """Synthesize a boom: falling low sine + noise burst with exponential decay."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rate, dur = 44100, 1.2
    rng = random.Random(1)
    frames = bytearray()
    phase, noise = 0.0, 0.0
    for i in range(int(rate * dur)):
        t = i / rate
        freq = 30 + 90 * math.exp(-t * 8)
        phase += 2 * math.pi * freq / rate
        noise = 0.85 * noise + 0.15 * rng.uniform(-1, 1)  # low-passed noise = rumble
        s = 0.8 * math.sin(phase) * math.exp(-t * 3.5) + 1.6 * noise * math.exp(-t * 6)
        s = math.tanh(s * 2.2)  # soft clip for punch
        frames += struct.pack("<h", int(s * 32000))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


class App:
    def __init__(self):
        self.events = queue.Queue()
        self.ctrl_down = False
        self.held = set()
        self.fade_job = None

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.label = tk.Label(self.root, bd=0, bg="black")
        self.label.pack()
        self._no_focus_steal()

        keyboard.Listener(on_press=self.on_press, on_release=self.on_release, daemon=True).start()
        self.root.after(15, self.poll)

    def _no_focus_steal(self):
        self.root.attributes("-alpha", 1.0)
        if not IS_WINDOWS:
            return  # overrideredirect windows don't take focus on X11 anyway
        # WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_LAYERED | WS_EX_TRANSPARENT: never takes focus
        # from the app you paste into, and clicks pass straight through the fullscreen overlay.
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        GWL_EXSTYLE = -20
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | 0x08000000 | 0x80 | 0x80000 | 0x20)

    # --- listener thread ---
    def on_press(self, key):
        if key in CTRL_KEYS:
            self.ctrl_down = True
            return
        name = letter(key)
        if self.ctrl_down and name and name not in self.held:
            self.held.add(name)  # ignore auto-repeat while held
            self.events.put(name)

    def on_release(self, key):
        if key in CTRL_KEYS:
            self.ctrl_down = False
        self.held.discard(letter(key))

    # --- tk thread ---
    def poll(self):
        try:
            while True:
                self.boom(self.events.get_nowait())
        except queue.Empty:
            pass
        self.root.after(15, self.poll)

    def boom(self, name):
        play_sound(SOUND_FILE)
        if name == "v":
            webbrowser.open(random.choice(CTRL_V_URLS))
        elif os.path.exists(CTRL_C_IMAGE):
            self.show_image(CTRL_C_IMAGE)

    def show_image(self, path):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        img = Image.open(path).convert("RGB").resize((sw, sh))  # stretch to fill the whole screen
        self.photo = ImageTk.PhotoImage(img)
        self.label.configure(image=self.photo)
        self.root.geometry(f"{sw}x{sh}+0+0")
        if self.fade_job:
            self.root.after_cancel(self.fade_job)
        self.root.attributes("-alpha", 1.0)
        self.root.deiconify()
        self.root.lift()
        self.fade_job = self.root.after(SHOW_MS, self.fade, 1.0)

    def fade(self, alpha):
        step_ms = 30
        alpha -= step_ms / FADE_MS
        if alpha <= 0:
            self.root.withdraw()
            self.fade_job = None
            return
        self.root.attributes("-alpha", alpha)
        self.fade_job = self.root.after(step_ms, self.fade, alpha)

    def run(self):
        print("BOOM armed. Ctrl+C / Ctrl+V anywhere. Close this window to quit.")
        self.root.mainloop()


if __name__ == "__main__":
    os.makedirs(IMAGE_DIR, exist_ok=True)
    if not os.path.exists(SOUND_FILE):
        make_boom(SOUND_FILE)
    if "--test" in sys.argv:
        app = App()
        app.root.after(300, app.boom, "c")
        app.root.after(SHOW_MS + FADE_MS + 800, app.root.destroy)
        app.root.mainloop()
    else:
        App().run()
