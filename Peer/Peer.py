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
SERVER_PORT = 9998


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
        #send my creds to the admin.
        self.send_cred_to_server()
        #send my files to the admin.
        self.send_files_to_server()

        # BIND
        #self.server_sock.bind((SERVER_ADDRESS, SERVER_PORT))
        #self.server_sock.listen(5)

        #print("starting peer...")
        #self.listen()

    def send_cred_to_server(self):
        #self.client_sock.connect((SERVER_ADDRESS, SERVER_PORT))
        self.client_sock.sendall('my creds...'.encode())
        data = self.client_sock.recv(1024).decode()
        #self.client_sock.close()
        print(data)

    def send_files_to_server(self):

        #self.client_sock.connect((SERVER_ADDRESS, SERVER_PORT))
        if not (os.path.isdir("./Shared_Files")):
            print("Pls move your files you want to share into Shared_Files directory.")
            self.client_sock.sendall('None'.encode())
            return
        list_dir = os.listdir("./Shared_Files")
        self.client_sock.sendall(pickle.dumps(list_dir))
        #self.client_sock.close()



    def listen(self):

            while True:
                # establish a connection.
                other_sock, addr = self.server_sock.accept()
                Thread(target=self.handle_peer, daemon=True, args=(other_sock,)).start()



if __name__ == "__main__":
    My_Peer = Peer(NAME)
    print(My_Peer)
