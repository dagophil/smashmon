import weakref
import logging
import collections
import IPython


# TODO: Group the events according to the model they belong to.


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


class NeedCharacterId(Event):
    """This event is sent, when a controller needs an id for the controlled character.
    """

    def __init__(self, controller_id):
        super(NeedCharacterId, self).__init__(name="Need character id")
        self.controller_id = controller_id


class AssignCharacterId(Event):
    """This event is sent, when someone assigned a character id to a controller.
    """

    def __init__(self, controller_id, character_id):
        super(AssignCharacterId, self).__init__(name="Assign character id")
        self.controller_id = controller_id
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
