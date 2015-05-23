import pygame
import logging
import Box2D
import events
import IPython


class StageModel(object):
    """
    Abstract model for stages.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self._world = Box2D.b2World(gravity=(0, -10), doSleep=True)
        self._static_bodies = {}
        self._dynamic_bodies = {}
        self._fixtures = {}
        self._next_static_body_id = 0
        self._next_dynamic_body_id = 0
        self._next_fixture_id = 0
        self._character_ids = {}  # {controller_id: character_id}
        self._next_character_id = 0

        # TODO: Load the game objects from a file instead of creating them here.
        # TODO: Add background image.

        ground_body = self._create_static_body(
            position=(5, 1.5),  # center point
        )

        ground_body_fixture = self._create_polygon_fixture(
            ground_body,
            box=(4, 0.5)
        )

        dynamic_body = self._create_dynamic_body(
            position=(3, 7)  # center point
        )

        dynamic_body_fixture = self._create_polygon_fixture(
            dynamic_body,
            box=(0.5, 0.6),  # half of width, half of height
            density=1,
            friction=0.3
        )

        # IPython.embed()

    def _create_static_body(self, *args, **kwargs):
        body = self._world.CreateStaticBody(*args, **kwargs)
        body.userData = self._next_static_body_id
        self._static_bodies[self._next_static_body_id] = body
        self._next_static_body_id += 1
        return body

    def _create_dynamic_body(self, *args, **kwargs):
        body = self._world.CreateDynamicBody(*args, **kwargs)
        body.userData = self._next_dynamic_body_id
        self._dynamic_bodies[self._next_dynamic_body_id] = body
        self._next_dynamic_body_id += 1
        return body

    def _create_polygon_fixture(self, body, *args, **kwargs):
        fixture = body.CreatePolygonFixture(*args, **kwargs)
        fixture.userData = self._next_fixture_id
        self._fixtures[self._next_fixture_id] = fixture
        self._next_fixture_id += 1
        return fixture

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            pass
        elif isinstance(event, events.TickEvent):
            elapsed_time = event.elapsed_time
            self._world.Step(elapsed_time, 10, 10)
            # TODO: Maybe replace the number of iterations (here: 10) by a more meaningful value.

            self._ev_manager.post(events.WorldStep(self._world))
        elif isinstance(event, events.NeedCharacterId):
            controller_id = event.controller_id
            if controller_id in self._character_ids:
                character_id = self._character_ids[controller_id]
            else:
                character_id = self._next_character_id
                self._next_character_id += 1
                self._character_ids[controller_id] = character_id
            self._ev_manager.post(events.AssignCharacterId(controller_id, character_id))
