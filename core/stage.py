import pygame
import logging
import Box2D
import events
import IPython
import math


class StageModel(object):
    """
    Abstract model for stages.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self.world = Box2D.b2World(gravity=(0, -10), doSleep=True)
        self._world_objects = {}
        self._throwable_objects = {}
        self._characters = {}
        self._next_id = 0
        self.colors = {}

        ground_body = self.world.CreateStaticBody(position=(5, 0.5))
        ground_body.CreatePolygonFixture(box=(4, 0.25))
        ground_body.CreatePolygonFixture(vertices=[(-4.5, -0.25), (-4, -0.25), (-4, 5), (-4.5, 5)])
        ground_body.CreatePolygonFixture(vertices=[(4.5, -0.25), (4, -0.25), (4, 5), (4.5, 5)])
        ground_body.CreatePolygonFixture(vertices=[(-0.5, 0.25), (0, 0.75), (0.5, 0.25)])
        ground_id = self._add_world_object(ground_body)
        self.colors[ground_id] = (255, 255, 255, 255)

        char0_body = self.world.CreateDynamicBody(position=(3, 7))
        char0_body.CreatePolygonFixture(
            box=(0.5, 0.5),
            density=1,
            friction=0.3
        )
        char0_id = self._add_character(char0_body)
        self.colors[char0_id] = (127, 200, 127, 255)

        char1_body = self.world.CreateDynamicBody(position=(7, 7))
        char1_body.CreatePolygonFixture(
            box=(0.5, 0.5),
            density=1,
            friction=0.3
        )
        char1_id = self._add_character(char1_body)
        self.colors[char1_id] = (127, 127, 200, 255)

        # TODO: Load the game objects from a file instead of creating them here.
        # TODO: Add background image.
        # TODO: Load all stuff in the init event and not in the constructor.

    def _add_world_object(self, obj):
        obj_id = self._next_id
        self._next_id += 1
        obj.userData = obj_id
        self._world_objects[obj_id] = obj
        return obj_id

    def _add_throwable_object(self, obj):
        obj_id = self._next_id
        self._next_id += 1
        obj.userData = obj_id
        self._throwable_objects[obj_id] = obj
        return obj_id

    def _add_character(self, obj):
        obj_id = self._next_id
        self._next_id += 1
        obj.userData = obj_id
        self._characters[obj_id] = obj
        return obj_id

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            for i, k in enumerate(self._characters):
                self._ev_manager.post(events.AssignCharacterId(i, k))
        elif isinstance(event, events.TickEvent):
            elapsed_time = event.elapsed_time
            self.world.Step(elapsed_time, 10, 10)
            # TODO: Maybe replace the number of iterations (here: 10) by a more meaningful value.
        elif isinstance(event, events.CharacterMoveLeftRequest):
            character_id = event.character_id
            body = self._characters[character_id]
            body.ApplyLinearImpulse((-0.2, 0), body.worldCenter, True)
            MAX_VELO = 2.7
            if abs(body.linearVelocity[0]) > MAX_VELO:
                body.linearVelocity[0] = math.copysign(MAX_VELO, body.linearVelocity[0])
            # TODO: Improve the movement.
        elif isinstance(event, events.CharacterMoveRightRequest):
            character_id = event.character_id
            body = self._characters[character_id]
            body.ApplyLinearImpulse((0.2, 0), body.worldCenter, True)
            MAX_VELO = 2.7
            if abs(body.linearVelocity[0]) > MAX_VELO:
                body.linearVelocity[0] = math.copysign(MAX_VELO, body.linearVelocity[0])
            # TODO: Improve the movement
        elif isinstance(event, events.CharacterJumpRequest):
            character_id = event.character_id
            body = self._characters[character_id]
            body.ApplyLinearImpulse((0, 5), body.worldCenter, True)
            # TODO: Let the character jump, but only when he touches the ground.
