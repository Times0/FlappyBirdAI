import os
import pickle
from typing import overload

import pygame.sprite
from pygame import Color
from constants import *

from objects import Bird, Pipe, BIRD_X
import neat

pygame.init()
score_font = pygame.font.SysFont("Arial", 50)
stats_font = pygame.font.Font("IBMPlexSans-Regular.ttf", 20)

PIPE_SPACING = 300


class Game:
    instance_number = 0

    def __init__(self):
        self.score = 0
        self.simulation_number = 0
        self.game_is_on = True
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.pipes = []

    def init_bot(self, *, genomes=None, config=None, bird=None, max_score=None):
        self.simulation_number = Game.instance_number
        Game.instance_number += 1
        self.human_playing = False
        self.genomes = genomes
        self.config = config
        self.bird = bird
        self.max_score = max_score
        self.game_is_on = True
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.birds = []
        if not genomes:
            self.birds.append(bird)
            return
        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            g.fitness = 0
            self.birds.append(Bird(net, g))

    def init_human(self):
        self.human_playing = True
        self.birds = [Bird(None, None)]

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            clock.tick(FPS)
            self.events()
            self.check_collision()
            self.update()
            self.draw(self.win)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_is_on = False
                pygame.quit()
                quit()

            elif self.human_playing and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.birds[0].jump()

    def update(self):
        # add pipe
        if len(self.pipes) == 0 or self.pipes[-1].x < WIDTH - PIPE_SPACING:
            self.pipes.append(Pipe())

        for bird in self.birds[:]:
            bird.update()
            if bird.y < 0 or bird.y > HEIGHT:
                bird.die()
                self.birds.remove(bird)

            if not self.human_playing:
                if self.config is not None:
                    bird.genome.fitness += 0.01
                next_pipe = self.pipes[0]
                if next_pipe.x + next_pipe.width + 50 < BIRD_X:
                    next_pipe = self.pipes[1]
                output = bird.net.activate((bird.y, next_pipe.gap_top, next_pipe.gap_top + next_pipe.gap_size))
                if output[0] > 0.5:
                    bird.jump()
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.x < -pipe.width:
                self.pipes.remove(pipe)
                self.score += 1
                if not self.human_playing:
                    if self.config is not None:
                        for bird in self.birds:
                            bird.genome.fitness += 5

        if not self.human_playing and self.max_score is not None and self.score >= self.max_score:
            self.game_is_on = False

    def check_collision(self):
        for pipe in self.pipes:
            for bird in self.birds:
                if pipe.check_collision(bird):
                    bird.die()
                    self.birds.remove(bird)
                    break

        if len(self.birds) == 0:
            self.game_is_on = False

    def draw_stats(self, win):
        if self.config is not None:
            # draw number of birds
            text = stats_font.render(f"Birds: {len(self.birds)}", True, Color("white"))
            win.blit(text, text.get_rect(topleft=(10, 10)))

            # draw simulation number
            text = stats_font.render(f"Generation: {self.simulation_number}", True, Color("white"))
            win.blit(text, text.get_rect(topleft=(10, 40)))

            # draw average fitness
            avg_fitness = sum([bird.genome.fitness for bird in self.birds]) / len(self.birds) if len(
                self.birds) > 0 else 0
            text = stats_font.render(f"Avg. Fitness: {avg_fitness:.2f}", True, Color("white"))
            win.blit(text, text.get_rect(topleft=(10, 70)))

        else:
            # Show trained
            text = stats_font.render(f"Trained", True, Color("white"))
            win.blit(text, text.get_rect(topleft=(10, 10)))

        text = score_font.render(str(self.score), True, Color("Gray"))
        win.blit(text, text.get_rect(center=(WIDTH // 2, 50)))

    def draw(self, win):
        win.fill(Color("black"))
        for bird in self.birds:
            bird.draw(win, self.pipes, show_input=True)
        for pipe in self.pipes:
            pipe.draw(win)

        if not self.human_playing:
            self.draw_stats(win)

        pygame.display.flip()


def main(genomes, config):
    game = Game()
    game.init_bot(genomes=genomes, config=config, max_score=50)
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
        game = Game()
        game.init_bot(bird=bird, max_score=1000)
        game.run()

    else:
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        winner = population.run(main)
        with open("best_genome", 'wb') as file:
            pickle.dump(winner, file)


if __name__ == '__main__':
    game = Game()
    game.init_human()
    game.run()
