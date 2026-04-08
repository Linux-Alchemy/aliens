# unittest for game_stats.py


def test_game_stats_defaults(pygame_game) -> None:
    """Verify that game correctly starts wit with default stats."""
    assert pygame_game.stats.score == 0
    assert pygame_game.stats.level == 1
    assert pygame_game.stats.ships_left == 3

def test_reset_stats(pygame_game) -> None:
    """Verify that reset_stats correctly resets the stats."""
    pygame_game.stats.score = 500
    pygame_game.stats.level = 5
    pygame_game.stats.reset_stats()
    assert pygame_game.stats.score == 0
    assert pygame_game.stats.level == 1


