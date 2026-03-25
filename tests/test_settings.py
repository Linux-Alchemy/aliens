# testing the default settings 

import pytest
from src.aliens import settings


@pytest.fixture()
def defaults():
    d = settings.Settings()
    return d

def test_default_screen_settings(defaults) -> None:
    """Testing that the default settings match the initialized screen
    Tests screen width/height and background color

    Args:
    settings: A Settings instance"""
    s = defaults
    assert s.screen_width == 1200
    assert s.screen_height == 800
    assert s.bg_color == (0, 0, 0)

def test_default_bullet_settings(defaults) -> None:
    """Testing that bullet defaults are correct
    Tests bullet speed, dimensions, color and max background

    Args:
        settings: A Settings instance"""
    b = defaults
    assert b.bullet_speed == 3
    assert b.bullet_width == 3
    assert b.bullet_height == 15
    assert b.bullet_color == (60, 60, 60)
    assert b.bullet_max_count == 10
