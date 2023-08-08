import pickle
import socket
from threading import Thread


class Client:

    def __init__(self, host, port, game):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.game = game

    def _connect_thread(self):
        while True:
            packet = pickle.loads(self.client_socket.recv(1024))

            packet_type = packet["type"]
            packet_data = packet["data"]

            if packet_type == "hit_ball":
                self.game.ball.velocity = packet_data["velocity"]
                self.game.ball.position = packet_data["position"]
                self.game.ball.clack_sound.play()
            elif packet_type == "update_racket":
                print("hi")

            print(f"[+] Received packet: {packet}")

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        Thread(target=self._connect_thread).start()
