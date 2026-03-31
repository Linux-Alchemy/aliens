# stat tracking for the game


class GameStats():
    """Tracking statistics for the game"""

    def __init__(self, ai_game) -> None:
        """Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.high_score = 0

    def reset_stats(self) -> None:
        """Stats that can change during the game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1



