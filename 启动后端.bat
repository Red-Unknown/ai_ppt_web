@echo off
conda activate ai_ppt_web
D:
cd D:\FanYa\ai_ppt_web\backend
set PYTHONPATH=D:\FanYa\ai_ppt_web;%PYTHONPATH%
python main.py
pause