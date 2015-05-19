import weakref
import logging


class Event(object):
    """Superclass for any event that is sent to the event manager.
    """

    def __init__(self, name="Generic event"):
        self.name = name


class TickEvent(Event):
    """The tick event is sent once per iteration in the game loop.
    """

    def __init__(self):
        super(TickEvent, self).__init__(name="Tick")


class QuitEvent(Event):
    """The quit event is sent when the whole app shall shut down.
    """

    def __init__(self):
        super(QuitEvent, self).__init__(name="Quit")


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


class EventManager(object):
    """
    Receives events and posts them to all _listeners.
    Is used for communication between Model, View and Controller.
    """

    def __init__(self):
        self._listeners = weakref.WeakKeyDictionary()

    def register_listener(self, listener):
        self._listeners[listener] = 1

    def unregister_listener(self, listener):
        if listener in self._listeners:
            del self._listeners[listener]

    def post(self, event):
        if not isinstance(event, TickEvent):
            logging.debug("Event: %s" % event.name)
        for listener in self._listeners:
            listener.notify(event)
