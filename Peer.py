import re
import os
import subprocess
from socket import *
from threading import Thread


FILTER_REG = r'[^\w\n|.]'
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

        # BIND
        self.server_sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.server_sock.listen(5)

        print(f"""
    Starting peer...
    SERVER SOCKET: {self.server_sock.getsockname()}
    CLIENT SOCKET: {self.client_sock.getsockname()}, PEER: {self.client_sock.getpeername()}
        """)
        self.listen()


    def listen(self):

            while True:
                # establish a connection.
                other_sock, addr = self.server_sock.accept()
                Thread(target=self.handle_peer, daemon=True, args=(other_sock,)).start()



if __name__ == "__main__":
    My_Peer = Peer(NAME)
    print(My_Peer)

