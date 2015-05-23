import pygame
import logging
import Box2D
import events


class StageModel(object):
    """
    Abstract model for stages.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._world = Box2D.b2World(gravity=(0, -10), doSleep=True)

        # TODO: Load the game objects from a file instead of creating them here.
        # TODO: Add background image.

        ground_body = self._world.CreateStaticBody(
            position=(5, 1.5),  # this is the center point
            shapes=Box2D.b2PolygonShape(box=(4, 0.5))  # this is half width and half height
        )

        dynamic_body = self._world.CreateDynamicBody(
            position=(3, 7)
        )

        box = dynamic_body.CreatePolygonFixture(
            box=(0.5, 0.6),
            density=1,
            friction=0.3
        )

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            pass
        elif isinstance(event, events.TickEvent):
            elapsed_time = event.elapsed_time
            self._world.Step(elapsed_time, 10, 10)
            # TODO: Maybe replace the number of iterations (here: 10) by a more meaningful value.

            self._ev_manager.post(events.WorldStep(self._world))
