@echo off
echo [1/5] Erstelle virtuelle Umgebung...
python -m venv env && echo Virtuelle Umgebung erstellt.

echo [2/5] Aktiviere virtuelle Umgebung...
call env\Scripts\activate.bat && echo Virtuelle Umgebung aktiviert.

echo [3/5] Installiere Abhängigkeiten...
pip install --upgrade pip && echo Pip aktualisiert.
pip install -r requirements.txt && echo Abhängigkeiten installiert.

echo [4/5] Erstelle ausführbare Datei...
pyinstaller main.spec && echo EXE-Datei erstellt.

echo [5/5] Erstelle Verknüpfung auf dem Desktop...
powershell -command "$s=(New-Object -COM WScript.Shell).CreateShortcut(\"$env:USERPROFILE\Desktop\Keye.lnk\"); $s.TargetPath=\"%CD%\dist\Keye.exe\"; $s.IconLocation=\"%CD%\icon.ico\"; $s.Save()"

echo Verknüpfung wurde erstellt!
echo Installation abgeschlossen! Die EXE befindet sich im dist-Ordner.
pause
