import pygame
import events


class PygameView(object):
    """
    Abstract Pygame view class.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self._screen = pygame.display.get_surface()

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

    def screen_size(self):
        return self._screen.get_size()

    def notify(self, event):
        raise NotImplementedError
