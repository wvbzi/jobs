#!/usr/bin/env bash
# Sets up a virtualenv on first run, then starts BOOM in the background.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install --quiet -r requirements.txt
nohup .venv/bin/python boom.py > boom.log 2>&1 &
echo "BOOM running (pid $!). Stop it with: pkill -f boom.py"
