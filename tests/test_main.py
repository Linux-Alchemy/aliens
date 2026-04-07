# unittests for main game loop
from src.aliens.settings import Settings
from src.aliens.ship import Ship
import pygame

def test_game_initialization(pygame_game) -> None:
    """Verify that AlienInvasion.__init__ creates all game components

    The game needs screen surface, Settings, Ship, Bullets

    Args:
        game: Instance of AlienInvasion from the fixture"""
    assert isinstance(pygame_game.settings, Settings)
    assert isinstance(pygame_game.screen, pygame.Surface)
    assert isinstance(pygame_game.ship, Ship)
    assert isinstance(pygame_game.bullets, pygame.sprite.Group)
    # check if initial Group is empty
    assert len(pygame_game.bullets) == 0

def test_bullet_max_count(pygame_game) -> None:
    """Verify that _fire_bullet() stops making bullets when the max is reached

    Args:
        game: Instance of AlienInvasion from fixture"""
    max_bullets = pygame_game.settings.bullet_max_count
    for _ in range(max_bullets):
        pygame_game._fire_bullet()
    # verify max count is respected
    assert len(pygame_game.bullets) == max_bullets
    # try to fire more bullets
    pygame_game._fire_bullet()
    assert len(pygame_game.bullets) == max_bullets

def test_game_starts_inactive(pygame_game) -> None:
    """Verify that the game starts in inactive state"""
    assert not pygame_game.game_active

def test_alien_fleet_not_empty(pygame_game) -> None:
    """Verify that the fleet is created and not empty"""
    assert len(pygame_game.aliens) > 0


