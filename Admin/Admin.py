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

            if ("update_files".encode()) in data:
                peer_files = pickle.loads(data)
                print(f"data recived from the peer is: {peer_files}")
                self.update_files(addr, peer_files)
    

            


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
        print("in update_files")

        entry = sl.connect(self.files)
        cursor = entry.cursor()
        ip, port = addr

        print(f"peer files are: \n{peer_files}")

        i = 0
        for file, file_size in peer_files.items():
            if i != 0:
                inserted_data = (file, file_size, ip)
                print(f"inserted data: {inserted_data}")
                selection_query = """INSERT INTO files VALUES(?, ?, ?)"""
                cursor.execute(selection_query, inserted_data)
            i += 1

        entry.commit()
        cursor.close()
        entry.close()
        print("New file added! ")




if __name__ == "__main__":
    Admin = Admin()

