#/bin/bash
set -m
python ./sm_bot/src/main.py &
python ./sm_bot/src/api.py
fg %1