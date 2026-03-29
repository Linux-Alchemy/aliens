# stat tracking for the game

class GameStats():
    """Tracking statistics for the game"""

    def __init__(self) -> None:
        """Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()

    def reset_stats(self) -> None:
        """Stats that can change during the game"""
        self.ships_left = self.settings.ship_limit
        
