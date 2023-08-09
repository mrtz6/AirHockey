import pickle
import socket
from time import sleep
from threading import Thread

from config import HOST, PORT, FPS, HEIGHT, WIDTH


class Server:

    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))

        self.clients = []

        self.ball = {
            "position": [WIDTH / 2, HEIGHT / 5],
            "velocity": [0, 0]
        }

    def send_packet(self, packet, client_socket=None, exclude_client=None):
        if client_socket is None:
            for client_socket in self.clients:
                if client_socket == exclude_client:
                    continue
                client_socket.send(pickle.dumps(packet))
        else:
            client_socket.send(pickle.dumps(packet))

    def handle_client(self, client_socket: socket.socket):
        self.send_packet({"type": "update_ball", "data": self.ball}, client_socket)

        while True:
            try:
                data = client_socket.recv(2048)

                if not data:
                    break

                packet = pickle.loads(data)

                packet_type = packet["type"]
                packet_data = packet["data"]

                if packet_type == "hit_ball":
                    self.ball["velocity"] = packet_data["velocity"]
                elif packet_type == "exit":
                    self.send_packet({"type": "exit", "data": {}}, client_socket)
                else:
                    self.send_packet(packet, exclude_client=client_socket)
            except socket.error:
                break

        client_socket.close()
        self.clients.remove(client_socket)

    def _run_thread(self):
        while True:
            client_socket, address = self.server_socket.accept()

            if len(self.clients) >= 2:
                self.send_packet({"type": "server_full", "data": {}}, client_socket)
                client_socket.close()
                continue

            self.clients.append(client_socket)

            print(f"[+] Client connected from {address}")

            Thread(target=self.handle_client, args=(client_socket,)).start()

    def run(self):
        self.server_socket.listen()

        print(f"[+] Server listening on {self.server_socket.getsockname()}")

        Thread(target=self._run_thread).start()

        time = 0
        while True:

            if time % 1 == 0:
                self.send_packet({"type": "update_ball", "data": self.ball})

            self.ball["position"][0] += self.ball["velocity"][0] * 1 / FPS
            self.ball["position"][1] += self.ball["velocity"][1] * 1 / FPS

            if self.ball["position"][0] < 10:
                self.ball["position"][0] = 10
                self.ball["velocity"][0] *= -1
            elif self.ball["position"][0] > WIDTH - 10:
                self.ball["position"][0] = WIDTH - 10
                self.ball["velocity"][0] *= -1

            if self.ball["position"][1] < 10:
                self.ball["position"][1] = 10
                self.ball["velocity"][1] *= -1
            elif self.ball["position"][1] > HEIGHT - 10:
                self.ball["position"][1] = HEIGHT - 10
                self.ball["velocity"][1] *= -1

            time += 1

            sleep(1 / FPS)


if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.run()
