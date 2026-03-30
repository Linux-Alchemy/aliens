# these *are* the droids you're looking for

class Settings():

    def __init__(self) -> None:
        # screen settings
        self.screen_width: int = 1200
        self.screen_height: int = 800
        self.bg_color: tuple[int, int, int] = (0, 0, 0)

        # ship settings
        self.ship_limit: int = 3

        # bullet settings
        self.bullet_width: int = 3
        self.bullet_height: int = 15
        self.bullet_color: tuple[int, int, int] = (135, 206, 235) # sky blue
        self.bullet_max_count: int = 10

        # alien fleet settings
        self.fleet_rows: int = 5
        self.fleet_drop_speed: int = 10

        # Speeding up the game
        self.speed_scale: float = 1.1
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self) -> None:
        """Managing the settings that will change in the game as you level up"""
        self.ship_speed: float = 2.0
        self.bullet_speed: float = 4.0
        self.alien_speed: float = 1.0
        # Direction: Right = 1; Left = -1
        self.fleet_direction: int = 1

    def increase_speed(self) -> None:
        """Speeding up the game with each new level"""
        self.ship_speed *= self.speed_scale
        self.bullet_speed *= self.speed_scale
        self.alien_speed *= self.speed_scale

