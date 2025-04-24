import os
import win32com.client
import platform

####################################################################################################################

def os_check(script_name_exe):
    if platform.system() == 'Windows':
        print("Windows Platform") # Debug Message
        move_to_startup_windows(script_name_exe)
    elif platform.system() == 'Linux':
        print("Linux Platform") # Debug Message
        pass

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