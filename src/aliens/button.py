# bulding the play button

import pygame

class Button():
    """Botton blueprints"""

    def __init__(self, ai_game, msg) -> None:
        """Initialize the button"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Button properties
        self.width: int = 200
        self.height: int = 50
        self.button_color: tuple[int, int, int] = (0, 135, 0)
        self.text_color: tuple[int, int, int] = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # Message
        self._prep_msg(msg)

    def _prep_msg(self, msg) -> None:
        """Render the message as an image and center on the button"""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self) -> None:
        """Create the button and then draw the message"""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)



