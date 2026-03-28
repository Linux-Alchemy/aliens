# main game file

import sys
import pygame
from .settings import Settings
from .ship import Ship
from .bullet import Bullet
from .alien import Alien

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
        
        # create ship & bullet & aline instance as attribute for AlienInvasion
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()


    # Main game loop 
    def run_game(self) -> None:
        """Start the main game loop"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_screen()
            self._update_aliens()
            # set frame rate
            self.clock.tick(60)


    # Management for the alien scum
    def _create_alien(self, x_position, y_position) -> None:
        """Creating an single alien and adding to the row"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _create_fleet(self) -> None:
        """Create the fleet of alien evil doers"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        row_count = 0
        while current_y < (self.settings.screen_height - 3 * alien_height) and row_count < self.settings.fleet_rows:
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Reset x value and increment y for a new row of alien ship
            current_x = alien_width
            current_y += 2 * alien_height
            row_count += 1

    def _check_fleet_edges(self) -> None:
        """Run check to act if fleet reaches screen edge"""
        for alien in self.aliens.sprites():
            if alien.edge_check():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self) -> None:
        """Drop down a line and change direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self) -> None:
        """Check edges then update positon"""
        self._check_fleet_edges()
        self.aliens.update()


    # Management for the bullet mechanix
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


    # Events Listening
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

    def _check_events(self) -> None:
        """Listening for game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_key_down(event)
            elif event.type == pygame.KEYUP:
                self._check_key_up(event)


    # Screen updates and drawing
    def _update_screen(self) -> None:
        """Update the screen and draw images"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # call blit_ship() to actually draw the ship on the gameboard
        self.ship.blit_ship()
        self.aliens.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()


