import events
import logging
import pygame


class StageIOController(object):
    """
    Take Pygame events (mouse, keyboard and quit events) and send requests to control a stage model.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            for pygame_event in pygame.event.get():
                if pygame_event.type == pygame.QUIT:
                    self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                elif pygame_event.type == pygame.KEYDOWN:
                    if pygame_event.key == pygame.K_ESCAPE:
                        self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                    # logging.debug("Keydown: %s" % pygame.key.name(pygame_event.key))
