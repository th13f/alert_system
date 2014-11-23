pyinstaller main.py --onefile
XCOPY "maps" "dist/main/maps" /D /E /C /R /I /K /Y
rmdir /s /q "build"