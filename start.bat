@echo off
cd /d "%~dp0"
python -m pip install --quiet pynput pillow
start "" pythonw boom.py
