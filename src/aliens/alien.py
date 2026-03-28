# alien ships mechanix

import pygame
from pathlib import Path
from pygame.sprite import Sprite

alien_image = Path(__file__).parent.parent.parent/"assets"/"alien_ship.jpg"

class Alien(Sprite):
    """Alien ship blueprints and behavior"""

    def __init__(self, ai_game) -> None:
        """Initialize the alien scum and set starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # Loading the alien ship image
        self.image = pygame.image.load(alien_image).convert_alpha()
        self.rect = self.image.get_rect()

        # Setting starting position
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def edge_check(self) -> bool:
        """Returns True if alien ship is at the edge of screen"""
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0
        

    def update(self) -> None:
        """Moving the alien fleet across the screen to the right or left"""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x


