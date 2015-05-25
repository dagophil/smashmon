import network
import events


class ServerController(object):
    """
    Send all events that come from the event manager over the network.
    Post all events that come from the network on the event manager.
    """

    def __init__(self, ev_manager, port=32072, max_num_clients=None):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._server = network.NetworkServer(port=port)
        self._max_num_clients = max_num_clients
        self._num_clients = 0
        self._ignore_events = [events.TickEvent, events.InitEvent]
        # TODO: Complete the list of ignore-events. What about events.WorldStep and events.CloseCurrentModel?

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            self._server.accept_clients(max_num_connections=self._max_num_clients)
        elif isinstance(event, events.TickEvent):
            # Get the network events and post them to the event manager.
            if self._num_clients < self._max_num_clients:
                self._server.update_client_list()
            network_events = self._server.get_objects()
            for ev in network_events:
                # Send the event only if its class is not in the ignore list.
                for cl in self._ignore_events:
                    if isinstance(ev, cl):
                        break
                else:
                    self._ev_manager.post(ev)

        # TODO: Send event over network.
