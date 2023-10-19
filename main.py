import os

import pygame

from constants import *
from game import run

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Flappy Bird")
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
