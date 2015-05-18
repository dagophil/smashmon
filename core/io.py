import events
import pygame
import logging


class MenuIOController(object):
    """
    Take Pygame events (mouse, keyboard and quit events) and send requests to control a menu model.
    Since mouse coordinates must be transformed to in-game units, the MenuIOController looks for a
    view that is suited for mouse-input and communicates directly with this view.
    """

    def __init__(self, ev_manager, view):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._view = view

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            for pygame_event in pygame.event.get():
                ev = None
                if pygame_event.type == pygame.QUIT:
                    ev = events.QuitEvent()
                elif pygame_event.type == pygame.KEYDOWN:
                    if pygame_event.key == pygame.K_ESCAPE:
                        ev = events.QuitEvent()
                elif pygame_event.type == pygame.MOUSEMOTION:
                    sx, sy = pygame_event.pos
                    x = self._view.to_game_x(sx)
                    y = self._view.to_game_y(sy)
                    logging.debug("New mouse pos: (%.02f, %.02f)" % (x, y))

                    # TODO: Find the hovered buttons and change their state.

                if ev:
                    self._ev_manager.post(ev)
