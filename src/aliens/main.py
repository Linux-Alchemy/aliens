# main game file

import sys
from time import sleep
import pygame
from .settings import Settings
from .game_stats import GameStats
from .ship import Ship
from .bullet import Bullet
from .alien import Alien
from .button import Button
from .scoreboard import Scoreboard

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
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        # create ship & bullet & alien instance as attribute for AlienInvasion
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Setting game status to inactive in order to use the button to start
        self.game_active = False
        self.play_button = Button(self, "Play")


    # MAIN GAME LOOP
    def run_game(self) -> None:
        """Start the main game loop"""
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            # set frame rate
            self.clock.tick(60)


    # SHIP MANAGEMENT
    def _ship_hit(self) -> None:
        """Decrement ship count when ship is destroyed and clear game board"""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.bullets.empty()
            self.aliens.empty()
            # Create a new fleet and ship from starting positon
            self._create_fleet()
            self.ship.center_ship()
            # Pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    # MANAGEMENT FOR THE ALIEN SCUM
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

        # check for collision between alien and ship
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Treat aliens reaching the bottom same as destroyed ship
        self._check_aliens_bottom()

    def _check_aliens_bottom(self) -> None:
        """Check to see if alien fleet reached the bottom of the screen"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    # BULLET MANAGEMENT
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

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self) -> None:
        """Remove bullets and aliens when a collsion occurs

        Adjust score for each alien destroyed
        Repopulate fleet when all destroyed"""
        collisions = pygame.sprite.groupcollide(
        self.bullets, self.aliens, True, True)

        # Adjusting score for each blasted alien scum destroyed | catches multiple hits
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        # repopulate alien fleet when one is destoyed
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # increase the level
            self.stats.level += 1
            self.sb.prep_level()


    # EVENTS
    def _check_key_down(self, event) -> None:
        """Listen for ship movement and bullet firing buttons"""
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
        """Listen for key release -- """
        if event.key == pygame.K_RIGHT:
           self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
           self.ship.moving_left = False

    def _check_events(self) -> None:
        """Listening for game events -- quitting or starting the game"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_key_down(event)
            elif event.type == pygame.KEYUP:
                self._check_key_up(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                self._check_play_button(mouse_position)

    def _check_play_button(self, mouse_position) -> None:
        """Start the game when the button is pressed"""
        button_clicked = self.play_button.rect.collidepoint(mouse_position)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            # Reset the stats for a new game
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.game_active = True
            pygame.mouse.set_visible(False)

            # Clear out remaining bullets/aliens and create a new board with a new ship and alien fleet
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()


    # SCREEN UPDATES AND DRAWING ELEMENTS
    def _update_screen(self) -> None:
        """Update the screen and draw images"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # call blit_ship() to actually draw the ship on the gameboard
        self.ship.blit_ship()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()


