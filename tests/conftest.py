# pytest fixtures for testing

import pytest
import pygame
import os
from src.aliens import main

@pytest.fixture(scope="session")
def pygame_init():
    """Fixture to initialize the pygame screen for testing"""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    # provide screen for testing
    yield 
    # teardown
    pygame.quit()

@pytest.fixture(scope="function")
def pygame_game(pygame_init):
    """Creating an AlienInvasion instance"""
    game = main.AlienInvasion()
    return game


