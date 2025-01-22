import socket
import time
import logging
import os
import json

logging.basicConfig(filename='error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 1145

base_directory = os.path.dirname(os.path.abspath(__file__))
jpg_path = os.path.join(base_directory, 'capture.jpg')

def recv():
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    saddr = ('', PORT)
    sockfd.bind(saddr)
    # logging.info(f"Listening on port {PORT}...")
    print(f"Listening on port {PORT}...")
    while True:
        recvline, presaddr = sockfd.recvfrom(1024)
        message = recvline.decode()
        if message == "":
            time.sleep(0.1)
        else:
            print(f"recvfrom {presaddr[0]} {message}")
            # logging.info(f"recvfrom {presaddr[0]} {message}")
            msg = message.split(":", 1)
            hostname, appname = msg
            return hostname, appname

def recvPic():
    CHUNK_SIZE = 1024
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    saddr = ('', PORT)
    sockfd.bind(saddr)
    # print(f"Listening on port {PORT}...")
    logging.info(f"Listening on port {PORT}...")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    recvImg_path = os.path.join(parent_directory, 'src', 'recvImg.jpg')
    with open(recvImg_path, "wb") as f:
        while True:
            recvline, presaddr = sockfd.recvfrom(CHUNK_SIZE)
            if recvline == b'END':
                break
            f.write(recvline)
    # print("recvImg.jpg saved")
    logging.info("recvImg.jpg saved")

def send2ui(hostname, appname):
    data = {
        "host_name": hostname,
        "app_name": appname
    }
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    json_path = os.path.join(parent_directory, 'src', 'message.json')
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    recvHostname,recvAppname = recv()
    recvPic()
    send2ui(recvHostname,recvAppname)