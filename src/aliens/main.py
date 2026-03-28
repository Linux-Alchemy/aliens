# main game file

import sys
import pygame
from .settings import Settings
from .ship import Ship
from .bullet import Bullet

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
        
        # create ship & bullet instance as attribute for AlienInvasion
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()


    def run_game(self) -> None:
        """Start the main game loop"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_screen()
            # set frame rate
            self.clock.tick(60)


    def _check_key_down(self, event) -> None:
        """Listen for key press"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        # option to quit game with 'q'
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_key_up(self,event) -> None:
        """Listen for key release"""
        if event.key == pygame.K_RIGHT:
           self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
           self.ship.moving_left = False

    def _fire_bullet(self) -> None:
        """Fire a bullet at the evil doers"""
        if len(self.bullets) < self.settings.bullet_max_count:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self) -> None:
        self.bullets.update()
        # remove bullets that reach the edge of the screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

    def _check_events(self) -> None:
        """Listening for game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_key_down(event)
            elif event.type == pygame.KEYUP:
                self._check_key_up(event)

    def _update_screen(self) -> None:
        """Update the screen and draw images"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # call blit_ship() to actually draw the ship on the gameboard
        self.ship.blit_ship()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()


