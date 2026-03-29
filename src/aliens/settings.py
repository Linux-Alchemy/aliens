# these *are* the droids you're looking for

class Settings():

    def __init__(self) -> None:
        # screen settings
        self.screen_width: int = 1200
        self.screen_height: int = 800
        self.bg_color: tuple[int, int, int] = (0, 0, 0)

        # ship settings
        self.ship_speed: float = 3.0  # change back to 2.0
        self.ship_limit: int = 3

        # bullet settings
        self.bullet_speed: int = 4
        self.bullet_width: int = 3
        self.bullet_height: int = 15
        self.bullet_color: tuple[int, int, int] = (60, 60, 60)
        self.bullet_max_count: int = 20 # change back to 10

        # alien fleet settings
        self.fleet_rows: int = 5
        self.alien_speed: float = 1.0
        self.fleet_drop_speed: int = 10
        # Direction: Right = 1; Left = -1
        self.fleet_direction: int = 1
