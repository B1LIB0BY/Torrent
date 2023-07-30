import re
import os
import os.path
import subprocess
from socket import *
from threading import Thread
import pickle


IP_REG = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
NAME = 'Yuval'
SERVER_ADDRESS = '10.0.0.29'
SERVER_PORT = 9999


class Peer:

    def __init__(self, name) -> None:

        self.name = name

        self.files = []

        self.server_ip = SERVER_ADDRESS

        temp_socket = socket(AF_INET, SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))  # Connect to Google's public DNS server

        # Get the local IP address from the temporary socket
        self.local_ip = temp_socket.getsockname()[0]
        temp_socket.close()

        self.server_sock = socket(AF_INET, SOCK_STREAM)

        self.client_sock = socket(AF_INET, SOCK_STREAM)
        self.client_sock.connect((SERVER_ADDRESS, SERVER_PORT))
        print("Connected!")
        #send my creds to the admin.

        self.send_cred_to_server()

        #send my files to the admin.
        self.send_files_to_server()

        # BIND.
        self.server_sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.server_sock.listen(5)

        print("starting peer...")
        self.listen()

    def send_cred_to_server(self):
        #self.client_sock.connect((SERVER_ADDRESS, SERVER_PORT))
        self.client_sock.sendall('yuval'.encode())


    def send_files_to_server(self):

        if not (os.path.isdir("./Shared_Files")):
            print("Pls move your files you want to share into Shared_Files directory.")
            self.client_sock.sendall('None'.encode())
            return
        list_dir = os.listdir("./Shared_Files")
        print(pickle.dumps(list_dir))
        self.client_sock.sendall(pickle.dumps(list_dir))
        print("files sent")


    def listen(self):

            while True:
                # establish a connection.
                other_sock, addr = self.server_sock.accept()
                Thread(target=self.handle_peer, daemon=True, args=(other_sock, addr)).start()
    def handle_peer(self, other_sock, addr):

        while True:
            ip, port = addr
            data = self.other_sock.recv(1024)
            if not data:
                print("No data!")
                break

            print(f"The data is: {data}")
            if("get_file:".encode() in data):
                file_to_forward = str(data).split(":")[1]
                print(f"the file to forward is: {file_to_forward}")
                self.forward_file(other_sock, file_to_forward, ip)


    def forward_file(other_sock, file_to_forward, ip):
        f = open(f"./Shared_Files/{file_to_forward}", "r")
        file_data = f.read()
        file_doc = {
                'type': 'send_file',
                'file_name': file_to_forward,
                'size': len(file_data),
                'data': file_data
                }

        #send the pickled file doc including the data.
        self.other_sock.sendall(pickle.dumps(file_doc))
        print(f"The file: {file_to_forward}, just sent to {ip}.")





if __name__ == "__main__":
    My_Peer = Peer(NAME)
    print(My_Peer)
