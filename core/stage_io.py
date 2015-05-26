import events
import logging
import pygame


class StageIOController(object):
    """
    Take Pygame events (mouse, keyboard and quit events) and send requests to control a stage model.
    """

    def __init__(self, ev_manager, character_index=None):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self._character_index = character_index
        self._character_id = None

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            pass
        elif isinstance(event, events.AssignCharacter):
            self._character_id = event.character_id
            logging.debug("Controller %d (%s) got character with id %d" %
                          (self._id, self.__class__.__name__, self._character_id))
        elif isinstance(event, events.TickEvent):
            # Handle key down events.
            for pygame_event in pygame.event.get():
                if pygame_event.type == pygame.QUIT:
                    self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                elif pygame_event.type == pygame.KEYDOWN:
                    if pygame_event.key == pygame.K_ESCAPE:
                        self._ev_manager.post(events.CloseCurrentModel(next_model_name=None))
                    elif pygame_event.key == pygame.K_SPACE:
                        if self._character_id is not None:
                            self._ev_manager.post(events.CharacterJumpRequest(self._character_id))

            # Handle key pressed events.
            if self._character_id is not None:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_a]:
                    self._ev_manager.post(events.CharacterMoveLeftRequest(self._character_id))
                if pressed[pygame.K_d]:
                    self._ev_manager.post(events.CharacterMoveRightRequest(self._character_id))
