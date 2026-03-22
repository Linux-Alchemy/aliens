# invasion file

import sys
import pygame
from .settings import Settings
from .ship import Ship

class AlienInvasion():
    """Management for game assets and behavior."""
    

    def __init__(self) -> None:
        """Initialize game"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # pulling gameboard settings from settings.py
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("AlienInvasion")
        # create ship instance as attribute for AlienInvasion
        self.ship = Ship(self)

    def run_game(self) -> None:
        """Start the main game loop"""
        while True:
            self._check_events()
            
            self.screen.fill(self.settings.bg_color)
            # call blitme() to actually draw the ship on the gameboard
            self.ship.blitme()
            pygame.display.flip()
            # set frame rate
            self.clock.tick(60)

    def _check_events(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()


