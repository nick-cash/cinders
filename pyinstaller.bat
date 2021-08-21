REM Edit paths before running:
C:\python27\python "E:\Program Files\pyinstaller-2.0\pyinstaller.py" -w -F -i src\graphics\icon.ico src\main.py src\gamescreen.py src\level.py src\menus.py src\screen.py src\sound_manager.py src\sprite.py src\utilities.py src\creditscreen.py
pause
REM If packaged as single file.
xcopy /s /I  src\fonts dist\fonts
xcopy /s /I src\graphics dist\graphics
xcopy /s /I src\levels dist\levels
xcopy /s /I src\music dist\music
xcopy /s /I src\sprites dist\sprites
xcopy /s /I src\sounds dist\sounds
del /Y dist\music\*.wav
REM xcopy /s /I src\fonts dist\main\fonts If packaged as directory
REM xcopy /s /I src\graphics dist\main\graphics
REM xcopy /s /I src\levels dist\main\levels
REM xcopy /s /I src\music dist\main\music
REM xcopy /s /I src\sprites dist\main\sprites
REM xcopy /s /I src\sounds dist\main\sounds
REM del /Y dist\main\music\*.wav
pause
