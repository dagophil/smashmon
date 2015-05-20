import pygame
import events
import logging
import resource_manager


class MenuPygameView(object):
    """
    Show a menu model using a Pygame window.
    """

    def __init__(self, ev_manager):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._screen = pygame.display.get_surface()
        self._bg_img = None
        self._buttons = None

    def show_bg(self):
        im = resource_manager.ResourceManager.instance().get_image(self._bg_img, size=self._screen.get_size())
        self._screen.blit(im, (0, 0))

    def show_buttons(self):
        for b in self._buttons:
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))

    def to_screen_x(self, x):
        return int(x * self._screen.get_width() / 10.0)

    def to_screen_y(self, y):
        return int(y * self._screen.get_height() / 10.0)

    def to_screen_xy(self, x, y):
        return self.to_screen_x(x), self.to_screen_y(y)

    def to_game_x(self, x):
        return x * 10.0 / self._screen.get_width()

    def to_game_y(self, y):
        return y * 10.0 / self._screen.get_height()

    def to_game_xy(self, x, y):
        return self.to_game_x(x), self.to_game_y(y)

    def _get_button_image(self, button):
        w, h = self.to_screen_xy(button.width, button.height)
        im = resource_manager.ResourceManager.instance().get_image(button.get_image(), size=(w, h))
        x, y = self.to_screen_xy(button.x, button.y)
        return im, (x, y)

    def notify(self, event):
        if isinstance(event, events.MenuCreatedEvent):
            self._bg_img = event.bg_img
            self._buttons = event.buttons
            self.show_bg()
            self.show_buttons()
        elif isinstance(event, events.TickEvent):
            pygame.display.flip()
        elif isinstance(event, events.ButtonHoverEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))
        elif isinstance(event, events.ButtonUnhoverEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))
        elif isinstance(event, events.ButtonPressEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))

    def screen_size(self):
        return self._screen.get_size()