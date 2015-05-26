import pygame
import logging
import Box2D
import events
import IPython
import math


class StageModel(object):
    """
    The stage model.
    """

    def __init__(self, ev_manager, ignore_model_broadcasts=False):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self.world = Box2D.b2World(gravity=(0, -10), doSleep=True)
        self._world_bodies = {}
        self._throwable_bodies = {}
        self._character_bodies = {}
        self._character_names = {}
        self.colors = {}
        self._ignore_model_broadcasts = ignore_model_broadcasts
        self._meta = None
        self._created_level = False

    def _clear_level(self):
        for i in self._world_bodies:
            self.world.DestroyBody(self._world_bodies[i])
        self._world_bodies.clear()

    def _load_level(self, level_name):
        if level_name == "Level 1":
            body = self.world.CreateStaticBody(position=(5, 0.5))
            body.CreatePolygonFixture(box=(4, 0.25))
            body.CreatePolygonFixture(vertices=[(-4.5, -0.25), (-4, -0.25), (-4, 5), (-4.5, 5)])
            body.CreatePolygonFixture(vertices=[(4.5, -0.25), (4, -0.25), (4, 5), (4.5, 5)])
            body.CreatePolygonFixture(vertices=[(-0.5, 0.25), (0, 0.75), (0.5, 0.25)])
            body.userData = ("world", 0)
            self._world_bodies[0] = body
            self.colors[body.userData] = (255, 255, 255, 255)
        else:
            raise Exception("Unknown level name: %s" % level_name)
        self._created_level = True

    def _delete_characters(self):
        for i in self._character_bodies:
            self.world.DestroyBody(self._character_bodies[i])
        self._character_bodies.clear()
        self._character_names.clear()

    def _create_character(self, character_id, character_name):
        if character_name == "char0":
            body = self.world.CreateDynamicBody(position=(3, 7))
            body.CreatePolygonFixture(
                box=(0.5, 0.5),
                density=1,
                friction=0.3
            )
            body.userData = ("character", character_id)
            self.colors[body.userData] = (127, 200, 127, 255)
        elif character_name == "char1":
            body = self.world.CreateDynamicBody(position=(7, 7))
            body.CreatePolygonFixture(
                box=(0.5, 0.5),
                density=1,
                friction=0.3
            )
            body.userData = ("character", character_id)
            self.colors[body.userData] = (127, 127, 200, 255)
        else:
            raise Exception("Unknown character name: %s" % character_name)

        self._character_bodies[character_id] = body
        self._character_names[character_id] = character_name

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            self._ev_manager.post(events.ModelMetaBroadcastRequest())
            # TODO: Load the game objects from a file.
            # TODO: Add background image.
            # for i, k in enumerate(self._character_bodies):
            #     self._ev_manager.post(events.AssignCharacterId(i, k))
        elif isinstance(event, events.ModelMetaBroadcast):
            self._meta = event.data
            if not self._created_level:
                self._load_level(self._meta["level_name"])
            if len(self._character_bodies) < len(self._meta["character_names"]):
                names = self._meta["character_names"]
                for i, name in enumerate(names):
                    self._create_character(i, name)
                self._ev_manager.post(events.ModelBroadcastRequest())
        elif isinstance(event, events.TickEvent):
            elapsed_time = event.elapsed_time
            self.world.Step(elapsed_time, 10, 10)
            # TODO: Maybe replace the number of iterations (here: 10) by a more meaningful value.
        elif isinstance(event, events.CharacterMoveLeftRequest):
            character_id = event.character_id
            # body = self._character_bodies[character_id]
            # body.ApplyLinearImpulse((-0.2, 0), body.worldCenter, True)
            # MAX_VELO = 2.7
            # if abs(body.linearVelocity[0]) > MAX_VELO:
            #     body.linearVelocity[0] = math.copysign(MAX_VELO, body.linearVelocity[0])
            # # TODO: Improve the movement.
        elif isinstance(event, events.CharacterMoveRightRequest):
            character_id = event.character_id
            # body = self._character_bodies[character_id]
            # body.ApplyLinearImpulse((0.2, 0), body.worldCenter, True)
            # MAX_VELO = 2.7
            # if abs(body.linearVelocity[0]) > MAX_VELO:
            #     body.linearVelocity[0] = math.copysign(MAX_VELO, body.linearVelocity[0])
            # # TODO: Improve the movement
        elif isinstance(event, events.CharacterJumpRequest):
            character_id = event.character_id
            # body = self._character_bodies[character_id]
            # body.ApplyLinearImpulse((0, 5), body.worldCenter, True)
            # # TODO: Let the character jump, but only when he touches the ground.
        elif isinstance(event, events.ModelBroadcastRequest):
            data = {}
            self._ev_manager.post(events.ModelBroadcast(data))
            # TODO: Create an event that can be sent to update the model.
            pass
        elif isinstance(event, events.ModelBroadcast) and not self._ignore_model_broadcasts:
            # TODO: Update the model.
            pass


class StageStateController(object):
    """
    This controller sends meta information about the current stage.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)
        self._current_level = None
        self._character_names = None

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            # TODO: Somehow get the current level.
            self._current_level = "Level 1"
            self._character_names = ["char0", "char1"]
        elif isinstance(event, events.ModelMetaBroadcastRequest):
            if self._current_level is None:
                raise Exception("A ModelMetaBroadcastRequest came before the InitEvent.")
            data = {"level_name": self._current_level,
                    "character_names": self._character_names}
            self._ev_manager.post(events.ModelMetaBroadcast(data))


class StageStateClientController(object):
    """
    This controller takes meta information requests and sends them over the network.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.NetworkEventManager)
        self._ev_manager = ev_manager
        self._id = self._ev_manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, events.ModelMetaBroadcastRequest):
            self._ev_manager.post(event)
