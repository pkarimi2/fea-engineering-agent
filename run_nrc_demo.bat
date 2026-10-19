@echo off
setlocal

if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python examples\nrc_piping\run_demo.py

if errorlevel 1 (
    echo.
    echo Demo failed. Review the message above. If MAPDL was not found, set:
    echo set ANSYS_MAPDL_EXECUTABLE=C:\Program Files\ANSYS Inc\v251\ansys\bin\winx64\ANSYS251.exe
    exit /b 1
)

echo.
echo Demo complete.
echo Open examples\nrc_piping\outputs\demo_report.md
endlocal
