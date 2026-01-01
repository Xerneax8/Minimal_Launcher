![Minimal Launcher logo](logo.png)
# Minimal_Launcher
Minimal Launcher is a Minecraft Launcher that gives you the power of managing all your versions, as
well as the power of adding and deleting files locally like Mods, Texture Packs and Shaders.
# Compile it
You can use pyinstaller util (pip install pyinstaller) to make it an EXE or ELF executable.
For example with the command: "pyinstaller --onefile --icon=icon.ico --windowed --noconsole main.py --add-data "logo.png:." -n minimal_launcher --hidden-import flet
"
# Known Errors
In Linux, if you recieve error while loading shared libraries with flet: libmpv.so.1: cannot open shared object file: No such file or directory it means the library is not installed.

To install libmpv run the following commands:

sudo apt update
sudo apt install libmpv-dev libmpv2
sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1
# Acknowledgements
Credit to [@JakobDev](https://github.com/JakobDev) for making [minecraft_launcher_lib](https://github.com/JakobDev/minecraft-launcher-lib)
