@echo off
REM Archipel Node Startup Script for Windows

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Archipel Node...
python main.py --port 0 --keys ./keys

pause
