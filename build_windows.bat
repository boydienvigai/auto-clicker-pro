@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo       AUTO CLICKER PRO - BUILD EXE
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Khong tim thay Python. Dung GitHub Actions theo README.md de build EXE ma khong can cai Python tren may.
  pause
  exit /b 1
)
py -m pip install --upgrade pip
py -m pip install -r requirements-build.txt
py -m PyInstaller --noconfirm --clean --onefile --windowed --name AutoClickerPro --collect-all pynput --collect-all pyautogui --hidden-import=win32timezone autoclicker_pro.py
if errorlevel 1 (
  echo Build that bai. Hay kiem tra ket qua loi ben tren.
  pause
  exit /b 1
)
echo.
echo Da tao: dist\AutoClickerPro.exe
pause
