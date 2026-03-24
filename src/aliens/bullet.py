# bullet mechanix

import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """Management of the bullet behavior"""

    def __init__(self, ai_game) -> None:
        """create a bullet object"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color


