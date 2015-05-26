import weakref
import logging
import collections
import json
import IPython
import network


class Event(object):
    """Superclass for any event that is sent to the event manager.
    """

    def __init__(self, name="Generic event"):
        self.name = name


class TickEvent(Event):
    """The tick event is sent once per iteration in the game loop.
    """

    def __init__(self, elapsed_time):
        super(TickEvent, self).__init__(name="Tick")
        self.elapsed_time = elapsed_time


class InitEvent(Event):
    """The init event is sent after all models, views and controllers have been registered at the event manager.
    """

    def __init__(self):
        super(InitEvent, self).__init__(name="Init")


class MenuCreatedEvent(Event):
    """The menu created event is sent after a menu model is created.
    """

    def __init__(self, bg_img, buttons):
        super(MenuCreatedEvent, self).__init__(name="Menu created")
        self.bg_img = bg_img
        self.buttons = buttons


class ButtonHoverRequestedEvent(Event):
    """This event is sent, when a controller detects that a menu button is hovered.
    """

    def __init__(self, button):
        super(ButtonHoverRequestedEvent, self).__init__(name="Button hover requested")
        self.button = button


class ButtonUnhoverRequestedEvent(Event):
    """This event is sent, when a controller detects that a menu button is not hovered.
    """

    def __init__(self, button):
        super(ButtonUnhoverRequestedEvent, self).__init__(name="Button unhover requested")
        self.button = button


class ButtonHoverEvent(Event):
    """This event is sent, when a button is hovered and was not hovered before.
    """

    def __init__(self, button):
        super(ButtonHoverEvent, self).__init__(name="Button hover")
        self.button = button


class ButtonUnhoverEvent(Event):
    """This event is sent, when a button is not hovered but was hovered before.
    """

    def __init__(self, button):
        super(ButtonUnhoverEvent, self).__init__(name="Button unhover")
        self.button = button


class ButtonPressRequestedEvent(Event):
    """This event is sent, when a controller wants a button to be pressed.
    """

    def __init__(self, button):
        super(ButtonPressRequestedEvent, self).__init__(name="Button press requested")
        self.button = button


class ButtonPressEvent(Event):
    """This event is sent, when a button is pressed.
    """

    def __init__(self, button):
        super(ButtonPressEvent, self).__init__(name="Button press")
        self.button = button


class ButtonActionRequestedEvent(Event):
    """This event is sent, when a controller wants to fire a button's action.
    """

    def __init__(self, button):
        super(ButtonActionRequestedEvent, self).__init__(name="Button action requested")
        self.button = button


class ButtonActionEvent(Event):
    """This event is sent, after a button action was fired.
    """

    def __init__(self, button):
        super(ButtonActionEvent, self).__init__(name="Button action")
        self.button = button


class CloseCurrentModel(Event):
    """This event is sent, when the current model is closing.
    """

    def __init__(self, next_model_name):
        super(CloseCurrentModel, self).__init__(name="Close current model")
        self.next_model_name = next_model_name


class WorldStep(Event):
    """This event is sent, when the (Box2D) world made a step.
    """

    def __init__(self, world):
        super(WorldStep, self).__init__(name="World step")
        self.world = world


class AssignCharacterId(Event):
    """This event is sent, when a character got an id.
    """

    def __init__(self, character_index, character_id):
        super(AssignCharacterId, self).__init__(name="Assign character id")
        self.character_index = character_index
        self.character_id = character_id


class CharacterMoveLeftRequest(Event):
    """This event is sent, when a controller wats to move a character to the left.
    """

    def __init__(self, character_id):
        super(CharacterMoveLeftRequest, self).__init__(name="Character move left request")
        self.character_id = character_id

class CharacterMoveRightRequest(Event):
    """This event is sent, when a controller wants to move a character to the right.
    """

    def __init__(self, character_id):
        super(CharacterMoveRightRequest, self).__init__(name="Character move right request")
        self.character_id = character_id


class CharacterJumpRequest(Event):
    """This event is sent, when a controller wants a character to jump.
    """

    def __init__(self, character_id):
        super(CharacterJumpRequest, self).__init__(name="Character jump request")
        self.character_id = character_id


class ModelBroadcastRequest(Event):
    """
    This event is sent, when a controller wants the model to broadcast its current state.
    The ServerController sends this event, when he wants to send the current model state to all clients.
    """

    def __init__(self):
        super(ModelBroadcastRequest, self).__init__(name="Model broadcast request")


class ModelBroadcast(Event):
    """This event contains information to update a model.
    """

    def __init__(self, data):
        super(ModelBroadcast, self).__init__(name="Model broadcast")
        self.data = data


class ModelMetaBroadcastRequest(Event):
    """
    This event is sent, when a component needs meta information (such as level name, number of characters, ...)
    about the current model.
    """

    def __init__(self):
        super(ModelMetaBroadcastRequest, self).__init__(name="Model meta broadcast request")


class ModelMetaBroadcast(Event):
    """
    This event contains meta information (such as level name, number of characters, ...) about the current model.
    """

    def __init__(self, data):
        super(ModelMetaBroadcast, self).__init__(name="Model meta broadcast")
        self.data = data


class EventManager(object):
    """
    Receives events and posts them to all _listeners.
    Is used for communication between Model, View and Controller.
    """

    def __init__(self):
        self._listeners = weakref.WeakKeyDictionary()
        self.next_model_name = None
        self._queue = collections.deque()
        self._next_id = 0

    def register_listener(self, listener):
        id = self._next_id
        self._next_id += 1
        self._listeners[listener] = id
        logging.debug("Register listener: %s, id %d" % (listener.__class__.__name__, id))
        return id

    def unregister_listener(self, listener):
        if listener in self._listeners:
            del self._listeners[listener]
            logging.debug("Unregister listener: %s" % listener.__class__.__name__)

    def post(self, event):
        self._queue.append(event)
        if isinstance(event, CloseCurrentModel):
            self.next_model_name = event.next_model_name
        elif isinstance(event, TickEvent) or isinstance(event, InitEvent):
            while len(self._queue) > 0:
                ev = self._queue.popleft()
                if not isinstance(ev, TickEvent) and not isinstance(ev, WorldStep):
                    logging.debug("Event: %s" % ev.name)

                # Iterate over a copy of the dict, so even from within the loop listeners
                # can delete themselves from the dict.
                listeners = list(self._listeners)
                for l in listeners:
                    l.notify(ev)


class NetworkEventManager(EventManager):
    """
    This event manager can be used between a normal event manager and some controllers.
    All events coming from the controllers are sent over network (and not posted in the normal event manager).
    All events coming from the normal event manager are given to the controllers.
    """

    def __init__(self, ev_manager, host, port=32072):
        assert isinstance(ev_manager, EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        super(NetworkEventManager, self).__init__()
        self._client = network.NetworkClient(host=host, port=port, decode=to_event, encode=to_string)
        self._ignore_events = [TickEvent, InitEvent]
        # TODO: Complete the list of ignore-events. What about WorldStep and CloseCurrentModel?

    def post(self, event):
        if isinstance(event, CloseCurrentModel):
            self._ev_manager.post(event)
        for cls in self._ignore_events:
            if isinstance(event, cls):
                break
        else:
            self._client.send(event)

    def notify(self, event):
        listeners = list(self._listeners)
        for l in listeners:
            l.notify(event)

        if isinstance(event, TickEvent):
            event_list = self._client.get_objects()
            for ev in event_list:
                for cls in self._ignore_events:
                    if isinstance(ev, cls):
                        break
                else:
                    self._ev_manager.post(ev)

    def shutdown(self):
        self._client.close_all()


# Create a dictionary {class_identifier: class} and a dictionary {class: class_identifier}.
# Currently, __class__.__name__ is used as identifier, but this may change later.
_event_classes = [TickEvent, InitEvent, MenuCreatedEvent, ButtonHoverRequestedEvent, ButtonUnhoverRequestedEvent,
                  ButtonHoverEvent, ButtonUnhoverEvent, ButtonPressRequestedEvent, ButtonPressEvent,
                  ButtonActionRequestedEvent, ButtonActionEvent, CloseCurrentModel, WorldStep, AssignCharacterId,
                  CharacterMoveLeftRequest, CharacterMoveRightRequest, CharacterJumpRequest, ModelBroadcastRequest,
                  ModelBroadcast, ModelMetaBroadcast, ModelMetaBroadcastRequest]
_str_to_cls = {}
_cls_to_str = {}
for _cls in _event_classes:
    _s = _cls.__name__
    _str_to_cls[_s] = _cls
    _cls_to_str[_cls] = _s


def to_string(event):
    """Return a string that can be decoded to the given event.
    """
    cls_name = _cls_to_str[event.__class__]
    event_dict = json.dumps(event.__dict__)
    return cls_name + "#" + event_dict


def to_event(s):
    """Return the event that was encoded in the given string.
    """
    i = s.find("#")
    if i == -1:
        raise Exception("Could not find marker # in encoded event string.")
    cls_name, event_dict_string = s[:i], s[i+1:]
    cls = _str_to_cls[cls_name]
    event_dict = json.loads(event_dict_string)
    event = object.__new__(cls)
    event.__dict__.update(event_dict)
    return event
