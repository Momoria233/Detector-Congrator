import socket
import sys
import time
import logging
import cv2
import os
import psutil
import json
import tkinter as tk
from tkinter import messagebox

logging.basicConfig(filename='error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PORT = 9999
PORT = 1145

def load_targets(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data["target_processes"]

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, 'list.json')
target_processes = load_targets(json_file_path)

base_directory = os.path.dirname(os.path.abspath(__file__))
jpg_path = os.path.join(base_directory, 'capture.jpg')

def capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        logging.error("Error capturing image: No image captured")
        cap.release()
        return False

    logging.info("captured")
    cv2.imwrite(jpg_path, frame)
    cap.release()
    return True

def sendPic():
    CHUNK_SIZE = 1024
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    hostIP = socket.gethostbyname(socket.gethostname())
    des_addr = (hostIP, PORT)

    with open(jpg_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            try:
                sockfd.sendto(chunk, des_addr)
            except socket.error as e:
                logging.error(f"Error sending image chunk: {e}")
                sys.exit(-1)
    sockfd.sendto(b'END', des_addr)
    logging.info("Image sent successfully")

with open('list.json', 'r') as f:
    data = json.load(f)
    translations = data["translations"]

def send(process_name):
    translated_name = translations.get(process_name, process_name)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    hostIP = socket.gethostbyname(socket.gethostname())
    des_addr = (hostIP, PORT)
    sendline = socket.gethostname() + ":" + translated_name
    try:
        r = sockfd.sendto(sendline.encode(), des_addr)
        if r <= 0:
            logging.error("Error sending message: No data sent")
            sys.exit(-1)
    except socket.error as e:
        logging.error(f"Error sending message: {e}")
        print(e)
        sys.exit(-1)
    logging.info("finish")

def check_process(target_process):
    running_processes = [p for p in psutil.process_iter(['name'])]
    for p in running_processes:
        if p.info['name'] and p.info['name'].lower() == target_process.lower():
            return p
    return None

root = tk.Tk()
root.withdraw()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f'{width}x{height}+{x}+{y}')

def show_custom_messagebox(title, message, process_to_kill):
    top = tk.Toplevel(root)
    top.title(title)
    top.attributes('-topmost', True)

    top.overrideredirect(True)
    width = 600
    height = 300
    center_window(top, width, height)

    label = tk.Label(top, text=message, padx=20, pady=20)
    label.pack()

    def close_and_kill_process():
        if process_to_kill:
            try:
                process_to_kill.terminate()
                process_to_kill.wait(timeout=5)
                logging.info(f"Process {process_to_kill.name()} (PID: {process_to_kill.pid}) terminated successfully")
            except psutil.NoSuchProcess:
                logging.info(f"Process {process_to_kill.name()} (PID: {process_to_kill.pid}) already terminated")
            except psutil.TimeoutExpired:
                logging.error(f"TimeoutExpired: Process {process_to_kill.name()} (PID: {process_to_kill.pid}) could not be terminated")
        top.destroy()

    close_button = tk.Button(top, text="关闭", command=close_and_kill_process)
    close_button.pack(pady=10)

    root.wait_window(top)

if __name__ == '__main__':
    print("detecting...")
    logging.info("Starting detectionMain.py")
    launchCount = 0
    while True:
        for process in target_processes:
            process_info = check_process(process)
            if process_info and launchCount == 3:
                send(process)
                capture()
                time.sleep(1)
                sendPic()
                sys.exit(0)
            elif process_info and launchCount == 0:
                launchCount += 1
                print("launchCount: ", launchCount)
                logging.info(f"launchCount: {launchCount}")
                show_custom_messagebox("警告", f"检测到您第1次运行违规软件 {process}，请在10秒内关闭，否则将再次计入警告次数。", process_info)
                time.sleep(10)
            elif process_info and launchCount == 1:
                launchCount += 1
                print("launchCount: ", launchCount)
                logging.info(f"launchCount: {launchCount}")
                show_custom_messagebox("警告", f"检测到您第2次运行违规软件 {process}，请在10秒内关闭，累计3次将通报全班。", process_info)
                time.sleep(10)
            elif process_info and launchCount == 2:
                launchCount += 1
                print("launchCount: ", launchCount)
                logging.info(f"launchCount: {launchCount}")
                show_custom_messagebox("警告", f"这是您第3次运行违规软件 {process}，请不要再这么做，否则将通报全班！", process_info)
                time.sleep(10)
            else:
                time.sleep(0.5)