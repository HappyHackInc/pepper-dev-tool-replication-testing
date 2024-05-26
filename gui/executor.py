import subprocess
import time
import csv
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from utils.button_state import button_state
import os
from datetime import datetime, timedelta
from utils.adb_check import check_adb_installation, check_device_connection


class Executor:
    def __init__(self, frame, current_directory):
        self.execution_active = False
        self.execution_threads = [None, None, None]
        self.stop_event = threading.Event()
        label = tk.Label(frame, text="Executor", font=("MSゴシック", "10", "bold"))
        label.grid(row=2, column=0, padx=10, pady=(30, 0), sticky=tk.W)
        number_of_loops_entry = self._display_number_of_loop(frame)
        self._display_log_select(frame)
        self._display_executor(frame, number_of_loops_entry)
        self.current_directory = current_directory

    def _display_number_of_loop(self,frame):
        number_of_loops_label = tk.Label(frame, text="Number of Loops:")
        number_of_loops_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)        
        number_of_loops_entry = tk.Entry(frame, width=5, justify="right")
        number_of_loops_entry.insert(0, "10")
        number_of_loops_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        return number_of_loops_entry

    def _display_log_select(self,frame):
        log_label = tk.Label(frame, text="Log Select:")
        log_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.dumps_var = tk.BooleanVar()
        self.logcat_var = tk.BooleanVar()
        self.logcat_cb = tk.Checkbutton(frame, text='Logcat', variable=self.logcat_var)
        self.logcat_cb.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        self.dumps_cb = tk.Checkbutton(frame, text='Dumpsys meminfo', variable=self.dumps_var)
        self.dumps_cb.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)
        dumps_parameters_label =  tk.Label(frame, text="Parameters:")
        dumps_parameters_label.grid(row=5, column=2, padx=10, pady=10, sticky=tk.W) 
        dumps_parameters_interval_label =  tk.Label(frame, text="Interval[s]:")
        dumps_parameters_interval_label.grid(row=5, column=3, padx=10, pady=10, sticky=tk.W) 
        self.dumps_parameters_interval_entry = tk.Entry(frame, width=5, justify="right")
        self.dumps_parameters_interval_entry.insert(0, "1")
        self.dumps_parameters_interval_entry.grid(row=5, column=4, padx=10, pady=10, sticky=tk.W)

        dumps_parameters_package_name_label =  tk.Label(frame, text="Package Name:")
        dumps_parameters_package_name_label.grid(row=5, column=5, padx=10, pady=10, sticky=tk.W) 
        self.dumps_parameters_package_name_entry = tk.Entry(frame, width=30, justify="right")
        self.dumps_parameters_package_name_entry.insert(0, "com.softbankrobotics.apps.party")
        self.dumps_parameters_package_name_entry.grid(row=5, column=6, padx=10, pady=10, sticky=tk.W)

    def _display_executor(self, frame, number_of_loops_entry):
        self.execute_button = tk.Button(frame, text="Execute Taps", command=lambda: self.execute_taps(number_of_loops_entry))
        self.execute_button.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
        self.stop_execute_button = tk.Button(frame, text="Stop Execution", command=self.stop_execution, state=button_state(self.execution_active))
        self.stop_execute_button.grid(row=6, column=1, padx=10, pady=10, sticky=tk.W)

    def on_checkbox_change(self):
        print(f"Dumps selected: {self.dumps_var.get()}")
        print(f"Logcat selected: {self.logcat_var.get()}")

    def tap_from_csv(self, csv_file_path,save_folder):
        try:
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:

                    if  check_device_connection():
                        self.stop_execution()

                    if self.stop_event.is_set():
                        break
                    if row == []:
                        break
                    x, y, delay, memo = row
                    current_time = datetime.now()
                    tap_time = current_time + timedelta(seconds=float(delay))
                    tap_entry = f" {tap_time.strftime('%m-%d %H:%M:%S')} Tap at ({x}, {y})"
                    with open(os.path.join(save_folder , "tap_log.csv"), 'w') as file:
                        file.write(tap_entry)
                        file.write("\n")
                    print(tap_entry)
                    time.sleep(float(delay))
                    if self.stop_event.is_set():
                        break
                    subprocess.run(["adb", "shell", "input", "tap", x, y])
        except FileNotFoundError:
            print(f"Error: File '{csv_file_path}' not found.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def start_execution(self, save_folder, number_of_loops):
        self.execution_active = True
        self.stop_execute_button["state"] = button_state(self.execution_active)
        self.execute_button["state"] = button_state(not self.execution_active)
 
        try:
            for i in range(number_of_loops):
                if self.stop_event.is_set():
                    break
                print(f"{i+1}回目")
                self.tap_from_csv(os.path.join(save_folder , "record.csv"), save_folder)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the loops.")
        finally:
            self.execution_active = False
            if self.execution_threads[0] is None:
                self.stop_execute_button["state"] = button_state(self.execution_active)
                self.execute_button["state"] = button_state(not self.execution_active)
                self.execution_threads[0] = None

    def stop_execution(self):
        self.execution_active = False
        self.stop_execute_button["state"] = button_state(self.execution_active)
        self.execute_button["state"] = button_state(not self.execution_active)
        self.stop_event.set()
        for i in range(len(self.execution_threads)):
            if self.execution_threads[i] is not None:
                self.execution_threads[i].join()
        print("Execution stopped.")

    def execute_taps(self, number_of_loops_entry):
        self.stop_event.clear()
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

        file_name = os.path.splitext(file_path)[0].split("/")[-1]
        save_folder = self.generate_save_folder(file_name)
        
        csv_data = self.read_csv(file_path)
        self.write_csv(os.path.join(save_folder , "record.csv"), csv_data)


        if file_path:
            try:
                number_of_loops = int(number_of_loops_entry.get())
                print(f"Executing taps from file: {file_path}")
            
                self.execution_threads[0] = threading.Thread(target=self.start_execution, args=(save_folder , number_of_loops))


                # dumpsysログ取得スレッド
                if self.dumps_var.get():
                    self.execution_threads[1] = threading.Thread(target=self.execute_dumpsys, args=(save_folder, self.dumps_parameters_interval_entry.get(), self.dumps_parameters_package_name_entry.get()))

                # logcatログ取得スレッド
                if self.logcat_var.get():
                    self.execution_threads[2] = threading.Thread(target=self.execute_logcat, args=(save_folder,))

                for i in range(len(self.execution_threads)):
                    if self.execution_threads[i] is not None:
                        self.execution_threads[i].start()

                        

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for the loops.")


    def generate_save_folder(self, record_file_name):
        def get_unique_foldername(base_foldername):
            counter = 1
            unique_foldername = base_foldername
            while os.path.exists(unique_foldername):
                unique_foldername = f"{base_foldername}_{counter}"
                counter += 1
            return unique_foldername
        
        log_base_folder = os.path.join(self.current_directory, "Log")
        os.makedirs(log_base_folder , exist_ok=True)
        unique_Log_folder_directory = get_unique_foldername(os.path.join(log_base_folder , record_file_name))
        os.makedirs(unique_Log_folder_directory, exist_ok=True)
        return unique_Log_folder_directory
    
    def read_csv(self, filepath):
        data = []
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        return data

    def write_csv(self, filepath, data):
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)



    def run_adb_command(self, command):
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(e)
            return None

    def save_output_to_file(self, output, filepath):
        try:
            current_time = datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            with open(filepath, 'a') as file:
                separator = "-" * 80
                file.write(f"{separator}\n{current_time}\n{separator}\n")
                file.write(output)
                file.write("\n")
        except Exception as e:
            print(f"Error saving output to file: {filepath}")
            print(e)

    def execute_dumpsys(self, output_folder, interval, package_name):
        output_file = os.path.join(output_folder, "dumpsys.txt")
        interval = float(interval)
        print(interval)
        while not self.stop_event.is_set():
            try:
                dumpsys_output = self.run_adb_command("adb shell dumpsys meminfo {}".format(package_name))
                if dumpsys_output:
                    self.save_output_to_file(dumpsys_output, output_file)
            except KeyboardInterrupt:
                print("Process interrupted by user.")
                break
            time.sleep(interval)
        print("adb shell dumpsys meminfo {} stopped.".format(package_name))

    def run_adb_logcat(self, output_filepath):
        with open(output_filepath, 'w') as outfile:
            try:
                # adb logcat を実行
                process = subprocess.Popen(['adb', 'logcat'], stdout=outfile, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)

                while not self.stop_event.is_set():
                    # 0.1秒ごとにチェック
                    if process.poll() is not None:
                        break
                    self.stop_event.wait(0.1)

                # プロセスがまだ動いている場合は終了
                if process.poll() is None:
                    process.terminate()
                    process.wait()
                print("adb logcat stopped.")

            except KeyboardInterrupt:
                print("KeyboardInterrupt: Stopping adb logcat.")
                process.terminate()

    def execute_logcat(self, output_folder):
        try:
            # logcat の出力を取得して保存
            logcat_filename = "logcat.txt"
            logcat_filepath = os.path.join(output_folder , logcat_filename)
            self.run_adb_logcat(logcat_filepath) 

            print(f"Logcat output saved to: {logcat_filepath}")

        except KeyboardInterrupt:
            print("Process interrupted by user.")
