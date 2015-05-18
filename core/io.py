import events
import pygame


class MenuIOController(object):
    """
    Take Pygame events (mouse, keyboard and quit events) and send requests to control a menu model.
    Since mouse coordinates must be transformed to in-game units, the MenuIOController looks for a
    view that is suited for mouse-input and communicates directly with this view.
    """

    # TODO: Connect with a view. Do this either by giving one in the constructor or by using events to search for one.

    def __init__(self, ev_manager):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            for pygame_event in pygame.event.get():
                ev = None
                if pygame_event.type == pygame.QUIT:
                    ev = events.QuitEvent()
                elif pygame_event.type == pygame.KEYDOWN:
                    if pygame_event.key == pygame.K_ESCAPE:
                        ev = events.QuitEvent()

                if ev:
                    self._ev_manager.post(ev)
