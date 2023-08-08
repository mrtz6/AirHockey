import math
import pickle
import random

import pygame

from config import WIDTH, HEIGHT


class Ball:
    def __init__(self, position):
        self.position = position
        self.velocity = [(random.randint(-5, 5) * 100) for _ in range(2)]
        self.radius = 20
        self.clack_sound = pygame.mixer.Sound("assets/clack.mp3")
        self.clack_sound.set_volume(0.125)
        self.image = pygame.image.load("assets/ball.png")

    def update(self, delta_time):
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time

        self.velocity[0] *= 0.9975
        self.velocity[1] *= 0.9975

        if self.position[0] > WIDTH - self.radius:
            self.velocity[0] *= -1
            self.position[0] = WIDTH - self.radius
            self.clack_sound.play()
        elif self.position[0] < self.radius:
            self.velocity[0] *= -1
            self.position[0] = self.radius
            self.clack_sound.play()

        if self.position[1] > HEIGHT - self.radius:
            self.velocity[1] *= -1
            self.position[1] = HEIGHT - self.radius
            self.clack_sound.play()
        elif self.position[1] < self.radius:
            self.velocity[1] *= -1
            self.position[1] = self.radius
            self.clack_sound.play()

    def draw(self, screen):
        screen.blit(self.image, self.image.get_rect(center=self.position))


class Racket:
    def __init__(self, position, game):
        self.game = game
        self.position = position
        self.last_position = position
        self.radius = 32
        self.last_collision = False
        self.image = pygame.image.load("assets/racket.png")

    def update(self, delta_time, ball):
        mx, my = pygame.mouse.get_pos()
        self.position[0] = mx
        self.position[1] = my

        self.game.client.client_socket.send(pickle.dumps({
            "type": "update_racket",
            "data": {
                "position": self.position
            }
        }))

        distance = math.sqrt(math.pow(ball.position[0] - self.position[0], 2) + math.pow(ball.position[1] - self.position[1], 2))

        if distance < self.radius + ball.radius:
            if not self.last_collision:

                racket_power = math.sqrt(math.pow(self.position[0] - self.last_position[0], 2) + math.pow(self.position[1] - self.last_position[1], 2))

                racket_power = min(racket_power, 10)

                ball_speed = math.sqrt(math.pow(ball.velocity[0], 2) + math.pow(ball.velocity[1], 2))

                ball_angle = math.atan2(ball.position[1] - self.position[1], ball.position[0] - self.position[0])

                if racket_power == 0 or racket_power * 200 < ball_speed:
                    factor = ball_speed
                else:
                    factor = racket_power * 1000

                ball.velocity[0] = math.cos(ball_angle) * factor
                ball.velocity[1] = math.sin(ball_angle) * factor

                ball.clack_sound.play()

                self.game.client.client_socket.send(pickle.dumps({
                    "type": "hit_ball",
                    "data": {
                        "velocity": ball.velocity,
                        "position": ball.position
                    }
                }))

                self.last_collision = True
        else:
            self.last_collision = False

        self.last_position = [mx, my]

    def draw(self, screen):
        screen.blit(self.image, self.image.get_rect(center=self.position))
