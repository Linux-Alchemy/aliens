# bullet mechanix

import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """Management of the bullet behavior"""

    def __init__(self, ai_game) -> None:
        """Create the bullet object"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Start the bullet at correct position relative to the ship
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        self.y = float(self.rect.y)

    def update(self) -> None:
        """Bullet movement mechanic"""
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y

    def draw_bullet(self) -> None:
        """Draw the bullet on the game screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)

