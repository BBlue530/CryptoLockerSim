import os
import sys
import platform

####################################################################################################################

def os_check(script_name_exe, script_name_elf):
    if sys.platform == "win32":
        try:
            import win32com.client
            print("Windows Platform") # Debug Message
            move_to_startup_windows(script_name_exe)
        except ImportError:
            pass
    elif platform.system() == 'Linux':
        print("Linux Platform") # Debug Message
        move_to_startup_linux(script_name_elf)

####################################################################################################################

def move_to_startup_windows(script_name_exe):
    print("Move to startup started Windows") # Debug Message
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    print("Startup folder found") # Debug Message

    exe_name = os.path.splitext(os.path.basename(script_name_exe))[0]
    shortcut_name = f"{exe_name}.lnk"
    shortcut_path = os.path.join(startup_folder, shortcut_name)
    print("Shortcut Preped") # Debug Message

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = script_name_exe
    print("Shortcut Created") # Debug Message

    shortcut.WorkingDirectory = os.path.dirname(script_name_exe)
    shortcut.save()
    print("Shortcut Saved") # Debug Message

####################################################################################################################

def move_to_startup_linux(script_name_elf):
    # It gets moved but still having issues some small issues

    desktop_file_path = os.path.expanduser("~/.config/autostart/myprogram.desktop")
    os.makedirs(os.path.dirname(desktop_file_path), exist_ok=True)
    print("The dir exist") # Debug Message

    # This is the template desktop file
    desktop_file_startup = f"""[Desktop Entry]
    Type=Application
    Exec={script_name_elf}
    X-GNOME-Autostart-enabled=true
    """

    with open(desktop_file_path, "w") as f:
        print("Starting to write in desktop file") # Debug Message
        f.write(desktop_file_startup)
    print("Desktop writing success") # Debug Message

####################################################################################################################