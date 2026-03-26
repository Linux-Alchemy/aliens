# unittests for the ship

import pytest
from src.aliens import ship

def test_ship_starts_midbottom(pygame_game) -> None:
    """Verify ship startng position
    
    Ship should start game at the bottom middle of the screen

    Args:
        game: Instance of AlienInvasion from game fixture"""
    screen = pygame_game.screen.get_rect()
    assert pygame_game.ship.rect.midbottom == screen.midbottom
    assert pygame_game.ship.x == float(pygame_game.ship.x)

def test_ship_screen_boundaries(pygame_game) -> None:
    """Verify ship cannot move past screen boundaries
    Testing update()

    Args:
        game: Instance of AlienInvasion"""
    screen_rect = pygame_game.screen.get_rect()
    pygame_game.ship.x = (screen_rect.right - pygame_game.ship.rect.width)
    pygame_game.ship.rect.x = int(pygame_game.ship.x)
    pygame_game.ship.moving_right = True
    pygame_game.ship.update()
    assert pygame_game.ship.rect.right <= screen_rect.right
    
    pygame_game.ship.moving_right = False
    pygame_game.ship.x = 0.0
    pygame_game.ship.rect.x = int(pygame_game.ship.x)
    pygame_game.ship.moving_left = True
    pygame_game.ship.update()
    assert pygame_game.ship.rect.left >= screen_rect.left



