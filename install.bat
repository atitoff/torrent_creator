del /S /Q web\work\*
.venv\Scripts\pyinstaller.exe --add-data="web;web" --windowed --icon=ico.ico torrent_creator.py
xcopy "add" "dist\torrent_creator\_internal\_add" /h /i /c /k /e /r /y
