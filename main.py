import tkinter as tk
from gui.recorder import Recorder
from gui.executor import Executor
from utils.adb_check import check_adb_installation, check_device_connection
import os

def create_gui():
    root = tk.Tk()
    root.title("Android Tablet Automation")
    frame = tk.Frame(root)
    frame.pack(pady=20)
    Recorder(frame)
    current_directory = os.getcwd()
    executor = Executor(frame, current_directory)

    def close_window():
        executor.stop_execution()
        root.destroy()
    ## executorのスレッドを終了されるため
    root.protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop()
    

if __name__ == "__main__":

    if not (check_adb_installation() or check_device_connection()):
        create_gui()
