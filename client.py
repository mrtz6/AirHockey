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
            try:
                packet = pickle.loads(self.client_socket.recv(2048))

                packet_type = packet["type"]
                packet_data = packet["data"]

                if packet_type == "update_racket":
                    self.game.other_racket.position = packet_data["position"]
                elif packet_type == "exit":
                    break
                elif packet_type == "update_ball":
                    self.game.ball.position = packet_data["position"]
                    self.game.ball.velocity = packet_data["velocity"]

                print(f"[+] Received packet: {packet}")
            except socket.error:
                pass
        self.client_socket.close()
        print("[-] Disconnected from server")
        self.game.running = False

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        Thread(target=self._connect_thread).start()
