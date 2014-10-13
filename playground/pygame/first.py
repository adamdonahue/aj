#!/usr/local/bin/python-32

import pygame

from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
surface = pygame.display.set_mode((640, 480))

RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
WHITE = pygame.Color(255, 255, 255)

pygame.image.load('/Users/adamdonahue/Downloads/HIPHOP 101 Drum Kit.png')

sound = pygame.mixer.Sound('/Users/adamdonahue/pygame1.wav')

while True:
    surface.fill(RED)

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            sound.play()
            sound.fadeout(1000)
        # event.type

    pygame.display.update()
    clock.tick(30)
