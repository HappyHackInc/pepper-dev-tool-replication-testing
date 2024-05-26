import subprocess
import sys
from datetime import datetime
import os

def run_adb_logcat(output_filepath):
    with open(output_filepath, 'w') as outfile:
        try:
            # adb logcat を実行
            process = subprocess.Popen(['adb', 'logcat'], stdout=outfile, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)

        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping adb logcat.")
            process.terminate()

def execute_logcat(output_folder):
    try:
        # logcat の出力を取得して保存
        logcat_filename = "logcat.txt"
        logcat_filepath = os.path.join(output_folder , logcat_filename)
        run_adb_logcat(logcat_filepath)  # キーボード入力で停止

        print(f"Logcat output saved to: {logcat_filepath}")

    except KeyboardInterrupt:
        print("Process interrupted by user.")
