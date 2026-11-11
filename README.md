# BOOM

A tiny Windows app that reacts to copy and paste anywhere on your computer:

- **Ctrl+C**: plays a boom and flashes a cat over the whole screen, then fades it out.
- **Ctrl+V**: plays a boom and opens a job application site (McHire or Indeed, picked at random).

Copy and paste keep working as normal. The app only listens to the keys and never blocks them.

## Requirements

- Windows
- [Python 3](https://www.python.org/downloads/) with tkinter (included in the standard Windows installer)

## Run it

1. Clone the repo:
   ```bash
   git clone https://github.com/wvbzi/jobs.git
   cd jobs
   ```
2. Double-click `start.bat`.

   It installs the two dependencies (`pynput`, `pillow`) and starts the app in the background with no window.

To run it with a console instead, so you can see errors:

```bash
pip install pynput pillow
python boom.py
```

To check that it works without pressing any keys, run `python boom.py --test`. It plays the boom, shows the cat once, then exits.

## Stop it

- Started with `start.bat`: open Task Manager and end **pythonw.exe**.
- Started with `python boom.py`: close the console window or press Ctrl+Break.

## Customize

- **Image:** replace `images/cat.webp`. To use a different filename, change `CTRL_C_IMAGE` in `boom.py`.
- **Sound:** replace `sounds/boom.wav` with any `.wav`. If the file is missing, the app generates the boom again.
- **Links:** edit the `CTRL_V_URLS` list in `boom.py`.
- **Timing:** `SHOW_MS` sets how long the image stays up and `FADE_MS` sets how long it takes to fade out, both in milliseconds.

After changing anything, stop the app and start it again.
