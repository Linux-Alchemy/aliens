# this is where the hero's ship is built to defeat the evil alien scum!

import pygame

class Ship():
    """blueprints for the hero ship"""

    def __init__(self, ai_game) -> None:
        """initializing the ship and starting position"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        # grab ship image and assign it to self.rect
        self.image = pygame.image.load('assets/ship.bmp')
        self.rect = self.image.get_rect()

        # setting the starting position for the new ship
        self.rect.midbottom = self.screen_rect.midbottom


    def blit_ship(self) -> None:
        """drawing the ship in glorious 4K; just kidding"""
        self.screen.blit(self.image, self.rect)



