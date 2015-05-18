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
        super(TickEvent, self).__init__(name="Tick event")


class QuitEvent(Event):
    """The quit event is sent when the whole app shall shut down.
    """

    def __init__(self):
        super(QuitEvent, self).__init__(name="Quit event")


class InitEvent(Event):
    """The init event is sent after all models, views and controllers have been registered at the event manager.
    """

    def __init__(self):
        super(InitEvent, self).__init__(name="Init event")


class MenuCreatedEvent(Event):
    """The menu created event is sent after a menu model is created.
    """

    def __init__(self, bg_img, buttons):
        super(MenuCreatedEvent, self).__init__(name="Menu created event")
        self.bg_img = bg_img
        self.buttons = buttons


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
