import pygame
from pygame import Color
from constants import *
import random

BIRD_X = 100
GAP_SIZE = 200
X_SPEED = 2

pygame.font.init()
font = pygame.font.SysFont("Arial", 15)


class Bird:
    def __init__(self, net, genome):
        self.net = net
        self.genome = genome

        self.y = HEIGHT // 2

        self.velocity = 0
        self.gravity = 0.3
        self.lift = -5

        self.radius = 20
        self.color = random.choice([Color("red"), Color("blue"), Color("green"), Color("yellow"), Color("white"),
                                    Color("orange"), Color("purple"), Color("pink"), Color("brown"), Color("grey")])

        self.time_since_last_jump = 0

    def update(self):
        """Update bird's position using dt."""
        self.time_since_last_jump += 1
        self.velocity += self.gravity
        self.velocity *= 0.9
        self.y += self.velocity * 5

    def die(self):
        if self.genome is not None:
            self.genome.fitness -= 5

    def jump(self):
        if self.time_since_last_jump > 10:
            self.time_since_last_jump = 0
        else:
            return
        self.velocity = 0
        self.velocity += self.lift

    def draw(self, win, pipes, show_input=False):
        pygame.draw.circle(win, self.color, (BIRD_X, self.y), self.radius)
        if show_input:
            # Next pipe gap top
            next_pipe = pipes[0]
            if next_pipe.x + next_pipe.width < BIRD_X:
                next_pipe = pipes[1]
            pygame.draw.line(win, Color("pink"), (BIRD_X, self.y),
                             (next_pipe.x + next_pipe.width, next_pipe.gap_top), 2)
            # Next pipe gap bottom
            pygame.draw.line(win, Color("pink"), (BIRD_X, self.y),
                             (next_pipe.x + next_pipe.width, next_pipe.gap_top + next_pipe.gap_size), 2)


class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = WIDTH
        self.gap_top = random.randint(50, HEIGHT - 50 - GAP_SIZE)
        self.gap_size = GAP_SIZE

        self.width = 50
        self.color = Color("green")

    def update(self):
        self.x -= X_SPEED

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, 0, self.width, self.gap_top))
        pygame.draw.rect(win, self.color, (self.x, self.gap_top + GAP_SIZE, self.width, HEIGHT))

        # draw pipes outlines in red
        pygame.draw.rect(win, Color("red"), (self.x, 0, self.width, self.gap_top), 2)
        pygame.draw.rect(win, Color("red"), (self.x, self.gap_top + GAP_SIZE, self.width, HEIGHT), 2)

    def check_collision(self, bird):
        if BIRD_X + bird.radius > self.x and BIRD_X - bird.radius < self.x + self.width:
            if bird.y - bird.radius < self.gap_top or bird.y + bird.radius > self.gap_top + GAP_SIZE:
                return True
        return False
