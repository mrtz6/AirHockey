import pickle

import pygame

from client import Client
from config import *
from game import Racket, Ball


class AirHockey:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font("assets/font.ttf", 30)

        self.ball = Ball([WIDTH / 2, HEIGHT / 4])
        self.local_racket = Racket([WIDTH / 2, HEIGHT / 2], self, is_local=True)
        self.other_racket = Racket([-200, -200], self)

        self.client = Client(HOST, PORT, self)

        self.running = False

        try:
            self.client.connect()
        except ConnectionRefusedError:
            print("[-] Connection refused. Is the server running?")
            exit(1)

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.client.client_socket.send(pickle.dumps({"type": "exit", "data": {}}))
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.local_racket.mouse_click(event.button)
            if event.type == pygame.MOUSEBUTTONUP:
                self.local_racket.mouse_release(event.button)

    def update(self):
        delta_time = self.clock.tick(FPS) / 1000

        self.ball.update(delta_time)
        self.local_racket.update(delta_time, self.ball)

    def draw(self):
        self.screen.fill("black")

        self.ball.draw(self.screen)

        self.local_racket.draw(self.screen)
        self.other_racket.draw(self.screen)

        # self.screen.blit(self.font.render(str(int(self.clock.get_fps())), False, (200, 0, 0)), (8, 0))


if __name__ == '__main__':
    AirHockey().run()
