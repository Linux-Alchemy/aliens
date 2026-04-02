# stat tracking for the game

from pathlib import Path

high_score_file = Path(__file__).parent.parent.parent/"assets"/"high_score.txt"


class GameStats():
    """Tracking statistics for the game"""

    def __init__(self, ai_game) -> None:
        """Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.get_high_score() 

    def reset_stats(self) -> None:
        """Stats that can change during the game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def save_high_score(self) -> None:
        """Save high score to file"""
        with open(high_score_file, 'w') as f:
            f.write(str(self.high_score))

    def get_high_score(self) -> None:
        """Fetch the high score to display on the screen"""
        try:
            with open(high_score_file, 'r') as f:
                self.high_score = int(f.read())
        except FileNotFoundError:
            self.high_score = 0
