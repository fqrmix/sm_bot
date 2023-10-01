#/bin/bash
set -m
python ./sm_bot/src/api.py &
python ./sm_bot/src/main.py
fg %1