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
    assert bullet.y == bullet.rect.y
    



