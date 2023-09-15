# Creates a folder containing an executable version of the program with all unnecessary files removed
# Run with powershell.exe -noprofile -executionpolicy Bypass -file .\scripts/build.ps1

mkdir SFA_exe
Copy-Item -Path $PWD\*  -Destination "SFA_exe" -Recurse -Exclude @("*SFA_exe", ".git", "__pycache__", ".gitignore", "__init__.py", "Instructions.docx", "README.txt", "scripts")
cd SFA_exe
py -m PyInstaller --onefile Scramble_for_Africa.py --icon=graphics/misc/SFA.ico
Move-Item -Path dist/Scramble_for_Africa.exe
rm Scramble_for_Africa.spec -force
rmdir build -force -Recurse
rm dist -force -Recurse
rm modules -force -Recurse
rm -force Scramble_for_Africa.py
rm -force configuration/dev_config.json