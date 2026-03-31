# scoreboard config


import pygame

class Scoreboard():
    """Blueprints for the scoreboard mechanism"""

    def __init__(self, ai_game) -> None:
        """Initialize the scoreboard"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.text_color: tuple[int, int, int] = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)
        # Initial score
        self.prep_score()
        self.prep_high_score()

    def prep_high_score(self) -> None:
        """Render the high score as an image then center it"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = (f"{high_score:,}")
        self.high_score_image = self.font.render(high_score_str, True, self.text_color, self.settings.bg_color)

        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.screen_rect.top

    def prep_score(self) -> None:
        """Render the score as an image to be displayed"""
        score_str = str(self.stats.score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)

        # Score position on the screen
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = self.screen_rect.top + 20

    def show_score(self) -> None:
        """Drawing the score on the screen"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)

    def check_high_score(self) -> None:
        """Look to see if there's a new high score"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()






