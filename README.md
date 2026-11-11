# BOOM

A tiny desktop app that reacts to copy and paste anywhere on your computer:

- **Ctrl+C**: plays a boom and flashes a cat over the whole screen, then fades it out.
- **Ctrl+V**: plays a boom and opens a job application site (McHire or Indeed, picked at random).

Copy and paste keep working as normal. The app only listens to the keys and never blocks them.

Runs on **Windows** and **Linux (X11)**.

---

## Windows

### Install

1. Install [Python 3](https://www.python.org/downloads/). In the installer, tick **Add python.exe to PATH**. tkinter comes with it.
2. Clone the repo:
   ```bash
   git clone https://github.com/wvbzi/jobs.git
   cd jobs
   ```

### Run

Double-click `start.bat`. It installs the dependencies and starts the app in the background with no window.

To run it with a console so you can see errors instead:

```bash
pip install -r requirements.txt
python boom.py
```

### Stop

- Started with `start.bat`: open Task Manager and end **pythonw.exe**.
- Started with `python boom.py`: close the console window or press Ctrl+Break.

---

## Linux

> **X11 only.** Wayland doesn't let apps see global key presses, so on Wayland the app will only notice Ctrl+C / Ctrl+V inside some apps. On GNOME or KDE, pick **"Xorg"** / **"X11"** on the login screen (gear icon at the bottom right) before signing in. Check your session with `echo $XDG_SESSION_TYPE`.

### Install

1. Install Python, tkinter, venv and a sound player.

   Debian / Ubuntu / Mint:
   ```bash
   sudo apt install python3 python3-tk python3-venv pulseaudio-utils git
   ```
   Fedora:
   ```bash
   sudo dnf install python3 python3-tkinter pulseaudio-utils git
   ```
   Arch:
   ```bash
   sudo pacman -S python tk libpulse git
   ```
   The app plays sound with the first of `paplay`, `pw-play`, `aplay` or `ffplay` it finds. It works silently if none are installed.

2. Clone the repo:
   ```bash
   git clone https://github.com/wvbzi/jobs.git
   cd jobs
   chmod +x start.sh
   ```

### Run

```bash
./start.sh
```

The first run creates a `.venv` folder and installs the dependencies into it. The app then runs in the background and writes any errors to `boom.log`.

To run it in the foreground so you can see errors instead:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python boom.py
```

### Stop

```bash
pkill -f boom.py
```

Or press Ctrl+C in its terminal if it's running in the foreground (that also triggers the cat once on the way out).

---

## Test without pressing keys

```bash
python boom.py --test
```

On Linux, use `.venv/bin/python boom.py --test`. It plays the boom, shows the cat once, then exits.

## Customize

- **Image:** replace `images/cat.webp`. To use a different filename, change `CTRL_C_IMAGE` in `boom.py`.
- **Sound:** replace `sounds/boom.wav` with any `.wav`. If the file is missing, the app generates the boom again.
- **Links:** edit the `CTRL_V_URLS` list in `boom.py`.
- **Timing:** `SHOW_MS` sets how long the image stays up and `FADE_MS` sets how long it takes to fade out, both in milliseconds.

After changing anything, stop the app and start it again.

## Notes

- On Linux the fade needs a compositor (most desktops have one). Without one, the cat just disappears instead of fading.
- On Linux, clicks during the 1 second the cat is on screen land on the cat rather than the window behind it. On Windows they pass through.
