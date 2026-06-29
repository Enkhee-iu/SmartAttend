@echo off
setlocal

cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist IssueReportGenerator.spec del /q IssueReportGenerator.spec

python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --manifest windows_as_invoker.manifest ^
  --name IssueReportGenerator ^
  scripts\hcnet_report_launcher.py

echo.
echo Build completed.
echo EXE path: %CD%\dist\IssueReportGenerator.exe
pause
