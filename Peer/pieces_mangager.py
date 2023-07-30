import os
from socket import *
from threading import Thread





SERVER_IP = '10.0.0.29'
SERVER_PORT = 9999




class Pieces:
    def __init__(self) -> None:
        self.pieces = []
        self.providers = []
        self.num_of_pieces = 0


        self.sock = socket(AF_INET, SOCK_STREAM)
