import subprocess
from tkinter import messagebox

def check_adb_installation():
    error = False
    try:
        adb_version_output = subprocess.run(["adb", "version"], capture_output=True, text=True)
        if "Android Debug Bridge version" in adb_version_output.stdout:
            # print("ADB is installed.")
            error = False
        else:
            print("ADB is not installed")
            messagebox.showerror("ADB Not Found", "ADB is not installed.")
            error = True
    except FileNotFoundError:
        print("ADB is not installed")
        messagebox.showerror("ADB Not Found", "ADB is not installed.")
        error = True
    return error

def check_device_connection():
    error = False
    # try:
    #     devices_output = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    #     if "device" in devices_output.stdout:
    #         # print("A device is connected via ADB.")
    #         error = False
    #     else:
    #         print("A device is not connected via ADB.")
    #         messagebox.showerror("No Device Connected", "No device is connected via ADB.")
    #         error = True
    # except FileNotFoundError:
    #     print("ADB Not Found", "ADB is not installed.")
    #     messagebox.showerror("ADB Not Found", "ADB is not installed.")
    #     error = True
    return error
