import os
from socket import *
from threading import Thread
import sqlite3 as sl
import pickle
import time

SERVER_IP = '10.0.0.29'
SERVER_PORT = 9999
CLIENTS_PORT = 9999

class Admin:
    def __init__(self) -> None:
        self.clients = []
        self.peers, self.files = 'peers.db', 'files.db'
        self.open_databases()


        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((SERVER_IP, SERVER_PORT))
        self.sock.listen()
        self.start_admin()

    def start_admin(self):
        while True:
            print(f"Server is running on port {SERVER_PORT}.")
            client, addr = self.sock.accept()
            self.clients.append((client, addr))  # Add the client to the list
            print("got one.")
            Thread(target=self.handle_client, args=(client, addr)).start()


    def handle_client(self, sock: socket, addr: tuple ):
        self.clients.append(addr)

        #the name of the peer
        name = sock.recv(1024)
        if not name:
            return 

        print(f"the address is: {addr}")
        self.update_peers_table(name, addr)
        print("added in table!")

       
        while True:
            #waiting for a request
            data = sock.recv(1024)
            data = pickle.loads(data)
            print(f"data recived from the peer is: {data}")

            if data["type"] == "update_files":
                self.update_files(addr, data)
            if data["type"] == "request_file_creds":
                self.send_file_cred(sock, addr, data)
                
            


        self.delete_peer(name)
        sock.close()
        print(f"Closing {addr}")
        self.clients.remove(addr)  # Remove the client from the list


    def open_databases(self):

        try:

            entry = sl.connect(self.peers)
            cursor = entry.cursor()

            # Open a table named online-users.
            cursor.execute("""CREATE TABLE online_users (
                NAME TEXT,
                IP TEXT,
                port INTEGER
                )""")

            # close all the resources.
            entry.commit()
            cursor.close()
            entry.close()

            entry = sl.connect(self.files)
            cursor = entry.cursor()

            cursor.execute("""CREATE TABLE files (
                FILE_NAME TEXT,
                SIZE INTEGER,
                IP TEXT
                )""")

            # close all the resources.
            entry.commit()
            cursor.close()
            entry.close()
            print("db Table Created!")

        except Exception as e:

            raise e

        finally:
            return


    def update_peers_table(self, name, addr):

        entry = sl.connect(self.peers)
        cursor = entry.cursor()

        ip, port = addr
        inserted_data = (name, ip, port)

        selection_query = """INSERT INTO online_users VALUES(?, ?, ?)"""
        cursor.execute(selection_query, inserted_data)
        entry.commit()

        cursor.close()
        entry.close()
        print("New Peer added! ")

    def delete_peer(self, name):


        entry = sl.connect(self.peers)
        cursor = entry.cursor()

        selection_query = """DELETE from online_users where NAME = ?"""
        cursor.execute(selection_query, (name, ))

        entry.commit()
        cursor.close()
        entry.close()
        print(f"peer with the name {name} deleted! ")

    def update_files(self, addr, peer_files) -> None:
        """
        The input should be like:
        {
            "type": "update_files",
            "text1": file_size,
            "text2": file_size
        }
        """

        entry = sl.connect(self.files)
        cursor = entry.cursor()
        ip, port = addr

        i = 0
        for file, file_size in peer_files.items():
            if i != 0:
                inserted_data = (file, file_size, ip)
                selection_query = """INSERT INTO files VALUES(?, ?, ?)"""
                cursor.execute(selection_query, inserted_data)
            i += 1

        entry.commit()
        cursor.close()
        entry.close()
        print("files updated! ")

    def send_file_cred(self, sock: socket, addr, data):
        """
        The input should be like:
        {
            "type": "request_file",
            "name": "text4"
        } 
        """
        name = data["name"]
        print(f"the peer looking for file name {name}")

        #Open the database.
        entry = sl.connect(self.files)
        cursor = entry.cursor()

        selection_query = """SELECT * FROM files"""
        cursor.execute(selection_query)
        rows = cursor.fetchall()
        file_names = [row[0] for row in rows]        

        print(f"The file names are: {file_names}, and the name is: {name}")
        if name not in file_names:
            doc = {
                "type": "Error"
            }
            sock.sendall(pickle.dumps(doc)) 
            return

        provider = rows[file_names.index(name)][2]
        size_of_file = rows[file_names.index(name)][1]

        doc = {
                "type": "requested_file_creds",
                "name": name,
                "size": size_of_file,
                "provider": provider
            }
        sock.sendall(pickle.dumps(doc))
        print("file creds are sent!")
 






if __name__ == "__main__":
    Admin = Admin()

