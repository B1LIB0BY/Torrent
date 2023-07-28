import os
from socket import *
from threading import Thread

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

class Admin:
    def __init__(self) -> None:
        self.clients = []
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((SERVER_IP, SERVER_PORT))
        self.sock.listen(5)

        self.start_admin()

    def start_admin(self):
        while True:
            client, addr = self.sock.accept()
            self.clients.append(client)  # Add the client to the list
            Thread(target=self.handle_client, args=(client, addr)).start()

    def handle_client(self, client, addr):
        while True:
            data = client.recv(1024)
            if not data:
                break
            print(f"Received data from {addr}: {data.decode('utf-8')}")

        client.close()
        self.clients.remove(client)  # Remove the client from the list

if __name__ == "__main__":
    Admin = Admin()

