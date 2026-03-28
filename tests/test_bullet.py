# bullets unittest

import pytest
from src.aliens.bullet import Bullet

def test_bullet_spawns_correct_position(pygame_game) -> None:
    """Checking bullet draws on screen at the nose of the ship

    Args:
        game: Instance of AlienInvasion"""
    expected_position = pygame_game.ship.rect.midtop
    bullet = Bullet(pygame_game)
    assert bullet.rect.midtop == expected_position
    assert bullet.y == float(bullet.rect.y)

def test_bullet_movement(pygame_game) -> None:
    """Checking that update() moves bullet upwards by bullet_speed

    bullet y value should decrease as bullet moves up the screen

    Args:
        game: Instance of AlienInvasion"""
    bullet = Bullet(pygame_game)
    start_y = bullet.rect.y
    speed = pygame_game.settings.bullet_speed
    bullet.update()
    assert bullet.rect.y == (start_y - speed)
    assert bullet.y == float(bullet.rect.y)



    



