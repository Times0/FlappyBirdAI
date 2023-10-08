import os
import pickle

import pygame.sprite
from pygame import Color
from constants import *

from objects import Bird, Pipe, BIRD_X
import neat

pygame.init()
font = pygame.font.SysFont("Arial", 50)


class Game:
    def __init__(self, genomes=None, config=None, bird=None):
        self.genomes = genomes
        self.config = config
        self.bird = bird
        if bird is not None:
            self.birds = [bird]
            self.pipes = [Pipe()]
            self.score = 0
            self.time_since_last_pipe = 0
            self.game_is_on = True
            self.win = pygame.display.set_mode((WIDTH, HEIGHT))
            return

        self.game_is_on = True
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))

        self.birds = []
        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            g.fitness = 0
            self.birds.append(Bird(net, g))

        self.pipes: list[Pipe] = []

        self.time_since_last_pipe = float("inf")
        self.score = 0

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS)
            self.win.fill(Color("black"))
            self.events()
            self.update(dt)
            self.check_collision()
            self.draw(self.win)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_is_on = False
                pygame.quit()
                quit()
            # elif event.type == pygame.KEYDOWN:
            #      if event.key == pygame.K_SPACE:
            #          self.bird.jump()

    def update(self, dt):
        self.time_since_last_pipe += dt
        if self.time_since_last_pipe > 1000:
            self.time_since_last_pipe = 0
            self.pipes.append(Pipe())

        for bird in self.birds:
            bird.update(dt)
            if bird.y < 0 or bird.y > HEIGHT:
                bird.die()
                self.birds.remove(bird)
                break

            if self.config is not None:
                bird.genome.fitness += 0.01
            next_pipe = self.pipes[0]
            if next_pipe.x + next_pipe.width < BIRD_X:
                next_pipe = self.pipes[1]

            output = bird.net.activate((bird.y, next_pipe.gap_top, next_pipe.gap_top + next_pipe.gap_size))

            if output[0] > 0.5:
                bird.jump()
        for pipe in self.pipes:
            pipe.update(dt)
            if pipe.x < -pipe.width:
                self.pipes.remove(pipe)
                self.score += 1
                if self.config is not None:
                    for bird in self.birds:
                        bird.genome.fitness += 5

    def check_collision(self):
        for pipe in self.pipes:
            for bird in self.birds:
                if pipe.check_collision(bird):
                    bird.die()
                    self.birds.remove(bird)
                    break

        if len(self.birds) == 0:
            self.game_is_on = False

    def draw(self, win):
        for bird in self.birds:
            bird.draw(win)
        for pipe in self.pipes:
            pipe.draw(win)

        text = font.render(str(self.score), True, Color("white"))
        win.blit(text, text.get_rect(center=(WIDTH // 2, 50)))
        pygame.display.update()


def main(genomes, config):
    game = Game(genomes, config)
    game.run()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    if os.path.exists("best_genome"):
        with open("best_genome", 'rb') as file:
            winner = pickle.load(file)
        net = neat.nn.FeedForwardNetwork.create(winner, config)
        bird = Bird(net, None)
        game = Game(bird=bird)
        game.run()


    else:
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        winner = population.run(main, 5)
        with open("best_genome", 'wb') as file:
            pickle.dump(winner, file)
