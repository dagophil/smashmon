import events
import pygame
import logging


class MenuIOController(object):
    """
    Take Pygame events (mouse, keyboard and quit events) and send requests to control a menu model.
    Since mouse coordinates must be transformed to in-game units, the MenuIOController looks for a
    view that is suited for mouse-input and communicates directly with this view.
    """

    def __init__(self, ev_manager, menu, view):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._menu = menu
        self._view = view

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            for pygame_event in pygame.event.get():
                if pygame_event.type == pygame.QUIT:
                    self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                elif pygame_event.type == pygame.KEYDOWN:
                    if pygame_event.key == pygame.K_ESCAPE:
                        self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                elif pygame_event.type == pygame.MOUSEMOTION:
                    sx, sy = pygame_event.pos
                    x, y = self._view.to_game_xy(sx, sy)
                    for b in self._menu.buttons:
                        if b.x <= x <= b.x + b.width and b.y <= y <= b.y + b.height:
                            if b.is_up():
                                self._ev_manager.post(events.ButtonHoverRequestedEvent(b))
                        else:
                            if not b.is_up():
                                self._ev_manager.post(events.ButtonUnhoverRequestedEvent(b))
                elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                    sx, sy = pygame_event.pos
                    x, y = self._view.to_game_xy(sx, sy)
                    for b in self._menu.buttons:
                        if b.x <= x <= b.x + b.width and b.y <= y <= b.y + b.height:
                            self._ev_manager.post(events.ButtonPressRequestedEvent(b))
                elif pygame_event.type == pygame.MOUSEBUTTONUP:
                    sx, sy = pygame_event.pos
                    x, y = self._view.to_game_xy(sx, sy)
                    for b in self._menu.buttons:
                        if b.x <= x <= b.x + b.width and b.y <= y <= b.y + b.height:
                            if b.is_pressed():
                                self._ev_manager.post(events.ButtonActionRequestedEvent(b))
