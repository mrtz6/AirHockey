import pickle
import socket
from threading import Thread


class Server:

    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))

        self.clients = []

    def send_packet(self, packet, client_socket=None, exclude_client=None):
        if client_socket is None:
            for client_socket in self.clients:
                if client_socket == exclude_client:
                    continue
                client_socket.send(pickle.dumps(packet))
        else:
            client_socket.send(pickle.dumps(packet))

    def handle_client(self, client_socket: socket.socket):
        while True:
            try:
                packet = pickle.loads(client_socket.recv(1024))

                packet_type = packet["type"]
                packet_data = packet["data"]

                if packet_type == "hit_ball":
                    self.send_packet(packet, exclude_client=client_socket)
                elif packet_type == "update_racket":
                    self.send_packet(packet, exclude_client=client_socket)

                print(f"[+] Received packet: {packet}")
            except socket.error:
                break

        client_socket.close()
        self.clients.remove(client_socket)

    def run(self):
        self.server_socket.listen()

        print(f"[+] Server listening on {self.server_socket.getsockname()}")

        while True:
            client_socket, address = self.server_socket.accept()

            if len(self.clients) >= 2:
                self.send_packet({"type": "server_full", "data": {}}, client_socket)
                client_socket.close()
                continue

            self.clients.append(client_socket)

            print(f"[+] Client connected from {address}")

            Thread(target=self.handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    server = Server("25.1.245.70", 18769)
    server.run()
