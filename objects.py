import pygame
from pygame import Color
from constants import *
import random

BIRD_X = 100
GAP_SIZE = 200
X_SPEED = 0.2

pygame.font.init()
font = pygame.font.SysFont("Arial", 15)


class Bird:
    def __init__(self, net, genome):
        self.net = net
        self.genome = genome

        self.y = HEIGHT // 2

        self.velocity = 0
        self.gravity = 0.1
        self.lift = -1

        self.radius = 20
        self.color = random.choice([Color("red"), Color("blue"), Color("green"), Color("yellow"), Color("white"),
                                    Color("orange"), Color("purple"), Color("pink"), Color("brown"), Color("grey")])

    def update(self, dt):
        """Update bird's position using dt."""
        self.velocity += self.gravity
        self.velocity *= 0.9
        self.y += self.velocity * dt

    def die(self):
        if self.genome is not None:
            self.genome.fitness -= 10

    def jump(self):
        self.velocity = 0
        self.velocity += self.lift

    def draw(self, win):
        pygame.draw.circle(win, self.color, (BIRD_X, self.y), self.radius)
        # draw velocity
        velocity = pygame.math.Vector2(0, self.velocity)
        velocity.x = X_SPEED
        velocity *= 10
        pygame.draw.line(win, Color("red"),
                         (BIRD_X, self.y),
                         (BIRD_X + velocity.x * 10, self.y + velocity.y * 10), 2)
        # draw fitness
        if self.genome is not None:
            text = font.render(f"{self.genome.fitness:.1f}", True, Color("white"))
            win.blit(text, text.get_rect(center=(BIRD_X, self.y - self.radius - 10)))


class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = WIDTH
        self.gap_top = random.randint(50, HEIGHT - 50 - GAP_SIZE)
        self.gap_size = GAP_SIZE

        self.width = 50
        self.color = Color("green")

    def update(self, dt):
        self.x -= X_SPEED * dt

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, 0, self.width, self.gap_top))
        pygame.draw.rect(win, self.color, (
            self.x, self.gap_top + self.gap_size, self.width, HEIGHT - self.gap_top - self.gap_size))

        # draw the outline of the pipes
        pygame.draw.rect(win, Color("red"), (self.x, 0, self.width, self.gap_top), 2)
        pygame.draw.rect(win, Color("red"), (
            self.x, self.gap_top + self.gap_size, self.width, HEIGHT - self.gap_top - self.gap_size), 2)

    def check_collision(self, bird):
        if BIRD_X + bird.radius > self.x and BIRD_X - bird.radius < self.x + self.width:
            if bird.y - bird.radius < self.gap_top or bird.y + bird.radius > self.gap_top + self.gap_size:
                return True
        return False
