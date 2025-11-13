![Minimal Launcher logo](logo.png)
# Minimal_Launcher
Minimal Launcher is a Minecraft Launcher that gives you the power of managing all your versions, as
well as the power of adding and deleting files locally like Mods, Texture Packs and Shaders.
# Compile it
You can use pyinstaller util (pip install pyinstaller) to make it an EXE or ELF executable.
For example with the command: "pyinstaller --onefile --icon=icon.ico --windowed --noconsole main.py --add-data "logo.png:." -n minimal_launcher --hidden-import flet
"
# Acknowledgements
Credit to [@JakobDev](https://github.com/JakobDev) for making [minecraft_launcher_lib](https://github.com/JakobDev/minecraft-launcher-lib)
