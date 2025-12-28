@echo off
pushd %~dp0
cd ..
if not exist "debug" mkdir debug
echo Building RAM-CLI...
pyinstaller --clean --onefile --name "RAM-CLI" --distpath "debug" --workpath "debug/build" --specpath "debug" "command.py"
popd
echo Build complete. Check debug/RAM-CLI.exe
pause
