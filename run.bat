@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
venv\Scripts\python.exe -m src.main >> logs\run.log 2>&1