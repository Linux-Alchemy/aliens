# these *are* the droids you're looking for

class Settings():

    def __init__(self) -> None:
        # screen settings
        self.screen_width: int = 1200
        self.screen_height: int = 800
        self.bg_color: tuple[int, int, int] = (0, 0, 0)

        # ship settings
        self.ship_speed: float = 2.0

        # bullet settings
        self.bullet_speed: int = 3
        self.bullet_width: int = 3
        self.bullet_height: int = 15
        self.bullet_color: tuple[int, int, int] = (60, 60, 60)
        self.bullet_max_count: int = 10

        # alien fleet settings
        self.fleet_rows: int = 5
