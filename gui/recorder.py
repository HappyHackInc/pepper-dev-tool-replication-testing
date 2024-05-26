import subprocess
import time
import csv
import threading
import tkinter as tk
from tkinter import filedialog
from utils.button_state import button_state

EV_ABS = "0003"
ABS_MT_POSITION_X = "0035"
ABS_MT_POSITION_Y = "0036"

class Recorder:
    def __init__(self, frame):
        self.x_value = None
        self.y_value = None
        self.prev_timestamp = None
        self.recording_active = False
        self.recording_thread = None

        label = tk.Label(frame, text="Recorder", font=("MSゴシック", "10", "bold"))
        label.grid(row=0, column=0, padx=10, sticky=tk.W)
        self.record_button = tk.Button(frame, text="Record Taps", command=self.start_recording)
        self.record_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.stop_record_button = tk.Button(frame, text="Stop Recording", command=self.stop_recording, state=button_state(self.recording_active))
        self.stop_record_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
    def execute_adb_command(self, command, output_file):
        try:
            with open(output_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['X', 'Y', 'DELAY', 'MEMO'])
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                while self.recording_active:
                    output = process.stdout.readline()
                    if output == b'' and process.poll() is not None:
                        break
                    if output:
                        self.parse_output(output.strip().decode(), writer)
                process.terminate()
        except Exception as e:
            print(f"An error occurred: {e}")

    def parse_output(self, line, writer):
        if not line:
            return
        parts = line.split()
        if len(parts) < 4:
            return
        event_type = parts[1]
        event_code = parts[2]
        event_value = parts[3]
        if event_type == EV_ABS and event_code == ABS_MT_POSITION_X:
            self.x_value = event_value
        elif event_type == EV_ABS and event_code == ABS_MT_POSITION_Y:
            self.y_value = event_value
        if self.x_value is not None and self.y_value is not None:
            x = int(self.x_value, 16)
            y = int(self.y_value, 16)
            curr_timestamp = time.time()
            if self.prev_timestamp is None:
                self.prev_timestamp = curr_timestamp
            time_diff = curr_timestamp - self.prev_timestamp
            print(x, y, f"{time_diff:.3f}")
            writer.writerow([x, y, f"{time_diff:.3f}", " "])
            self.prev_timestamp = curr_timestamp
            self.x_value = None
            self.y_value = None

    def start_recording(self):
        output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_file:
            self.recording_active = True
            self.stop_record_button["state"] = button_state(self.recording_active)
            self.record_button["state"] = button_state(not self.recording_active)
            self.prev_timestamp = time.time()
            command = "adb shell getevent"
            self.recording_thread = threading.Thread(target=self.execute_adb_command, args=(command, output_file))
            self.recording_thread.start()
            print("Recording taps... Press 'Stop' to stop.")

    def stop_recording(self):
        self.recording_active = False
        self.stop_record_button["state"] = button_state(self.recording_active)
        self.record_button["state"] = button_state(not self.recording_active)
        if self.recording_thread:
            self.recording_thread.join()
            print("Recording stopped.")
