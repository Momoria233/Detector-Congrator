import socket
import time
import logging
import os
import json
import traceback
import sys

logging.basicConfig(
    filename='rl_error.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
PORT = 1145

base_dir = os.path.dirname(sys.executable)
jpg_path = os.path.join(base_dir, 'capture.jpg')

def recv():
    try:
        sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        saddr = ('', PORT)
        sockfd.bind(saddr)
        print(f"Listening on port {PORT}...")
        while True:
            try:
                recvline, presaddr = sockfd.recvfrom(1024)
                try:
                    message = recvline.decode('utf-8')
                except UnicodeDecodeError:
                    logging.warning(f"Received non-UTF-8 data from {presaddr[0]}")
                    continue
                if message == "":
                    time.sleep(0.1)
                else:
                    print(f"recvfrom {presaddr[0]} {message}")
                    msg = message.split(":", 1)
                    hostname, appname = msg
                    return hostname, appname
            except UnicodeDecodeError as e:
                logging.error(f"Decode error: {e}\n{traceback.format_exc()}")
                raise
    except socket.error as e:
        logging.error(f"Socket error: {e}\n{traceback.format_exc()}")
        raise

def recvPic():
    CHUNK_SIZE = 1024
    try:
        sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        saddr = ('', PORT)
        sockfd.bind(saddr)
        logging.info(f"Listening on port {PORT}...")

        recvImg_path = os.path.join(base_dir, 'recvImg.jpg')

        try:
            with open(recvImg_path, "wb") as f:
                while True:
                    try:
                        recvline, presaddr = sockfd.recvfrom(CHUNK_SIZE)
                        if recvline == b'END':
                            break
                        f.write(recvline)
                    except socket.error as e:
                        logging.error(f"Receive error: {e}\n{traceback.format_exc()}")
                        raise
        except IOError as e:
            logging.error(f"File write error: {e}\n{traceback.format_exc()}")
            raise

        logging.info("recvImg.jpg saved")
        logging.info(f"Image saved to {recvImg_path}")
    except Exception as e:
        logging.error(f"Unexpected error in recvPic: {e}\n{traceback.format_exc()}")
        raise

def send2ui(hostname, appname):
    try:
        data = {
            "host_name": hostname,
            "app_name": appname
        }

        json_path = os.path.join(base_dir, 'message.json')

        try:
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        except (IOError, json.JSONEncodeError) as e:
            logging.error(f"JSON write error: {e}\n{traceback.format_exc()}")
            raise
    except Exception as e:
        logging.error(f"Unexpected error in send2ui: {e}\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        recvHostname, recvAppname = recv()
        recvPic()
        send2ui(recvHostname, recvAppname)
        time.sleep(10)
    except Exception as e:
        logging.critical(f"Main execution failed: {e}\n{traceback.format_exc()}")