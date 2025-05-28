![](logo.png)
# Minimal_Launcher
Minimal Launcher is a Minecraft Launcher that gives you the power of managing all your versions, as
well as adding and deleting files like Mods, Texture Packs and Shaders.
# Compile it
You can use pyinstaller util (pip install pyinstaller) to make it an EXE or ELF executable.
For example with the command: "pyinstaller --onefile --icon=icon.ico --hide-console hide-early main.py --add-data "logo.png:." -n minimal_launcher --hidden-import flet"
# Acknowledgements
Credit to [@JakobDev](https://github.com/JakobDev) for making [minecraft_launcher_lib](https://github.com/JakobDev/minecraft-launcher-lib)
