import re
import os
import os.path
import subprocess
from socket import *
from threading import Thread
import pickle
import time


IP_REG = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
NAME = 'Yuval'
SERVER_ADDRESS = '10.0.0.29'
SERVER_PORT = 9999
my_address = '10.0.0.27'
my_port = 9999
PEER_PORT = 9999


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
        print(f"Connected to admin {(SERVER_ADDRESS, SERVER_PORT)}")

        self.send_cred_to_server()

        time.sleep(2.5)
        self.send_files_to_server()

        time.sleep(5)
        self.req_file_creds()

        time.sleep(5)
        self.download_file()

        # BIND.
        self.server_sock.bind((my_address, my_port))
        self.server_sock.listen(5)

        print("starting peer...")
        self.listen()

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


    def send_cred_to_server(self):
        #self.client_sock.connect((SERVER_ADDRESS, SERVER_PORT))
        self.client_sock.sendall('yuval'.encode())
        print("creds sent!")

    

    def send_files_to_server(self):
        """
        send_file in this struct 
        {
            "type": "update_files",
            "text1": file_size,
            "text2": file_size
        }
        """
        
        if not (os.path.isdir("./Shared_Files")):
            print("Pls move your files you want to share into Shared_Files directory.")
            self.client_sock.sendall('None'.encode())
            return
        doc = {
            "type": "update_files"
        }
        list_dir = os.listdir("./Shared_Files")
        for file in list_dir:
            doc[file] = os.path.getsize(f"./Shared_Files/{file}")
        
        print(f"doc is: {doc}") 

        self.client_sock.sendall(pickle.dumps(doc))
        print("files sent!")



    def forward_file(self, other_sock, file_to_forward, ip):
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

    def req_file_creds(self):
        """
        ::input:: giving the server the name of the file we want.
        {
            "type": "request_file_creds"
            "name": "text4"
        }
        

        ::return:: the creds of the file are given us.
        {
            "type": "requested_file_creds",
            "name": name,
            "size": size_of_file,
            "provider": provider 
        }

        """
        doc = {
            "type": "request_file_creds",
            "name": "text3.txt"
        }
        self.client_sock.sendall(pickle.dumps(doc))
        data_back = pickle.loads(self.client_sock.recv(1024))
        print(f"the data that came back from the server is: {data_back}")
        if data_back["type"] == "Error":
            print("file not found!")
            return
        
        print("nice!")
        return

    def download_file(self, addr, name):
        """
        ::input:: giving the peer my file request 
        {
            "type": "request_file",
            "name": name
        }

        ::output:: getting the file we requested.
        {
            "type": "send_file",
            "name": name,
            "data": data
        }
        """
        peer_sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect((addr, PEER_PORT))

        doc = {
            "type": "request_file",
            "name": name
        }

        peer_sock.sendall(pickle.dumps(doc))

        data = pickle.loads(peer_sock.recv(1024))
        print(f"data recived: {data}")

        if(data["type"] == "Error"):
            print("file not available")
            return
        
        file_data = data["data"]
        file = open(f"{name}", "w")
        file.write(file_data)
        file.close()
        peer_sock.close()







if __name__ == "__main__":
    My_Peer = Peer(NAME)
    print(My_Peer)