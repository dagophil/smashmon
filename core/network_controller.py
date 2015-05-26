import network
import events
import logging


class ServerController(object):
    """
    Send all events that come from the event manager over the network.
    Post all events that come from the network on the event manager.
    """

    def __init__(self, ev_manager, port=32072, max_num_clients=None):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._server = network.NetworkServer(port=port, decode=events.to_event, encode=events.to_string)
        self._max_num_clients = max_num_clients
        self._num_clients = 0
        self._post_ignore_events = [events.TickEvent, events.InitEvent, events.CloseCurrentModel]
        self._send_ignore_events = [events.TickEvent, events.InitEvent, events.ModelMetaBroadcastRequest,
                                    events.ModelBroadcastRequest]
        # TODO: Complete the list of ignore-events. What about events.WorldStep and events.CloseCurrentModel?

        self._last_model_broadcast = 0  # elapsed time since the model was sent to all clients
        self._model_broadcast_interval = 1.0  # the network clients are updated in this interval

    def notify(self, event):
        if isinstance(event, events.InitEvent):
            self._server.accept_clients(max_num_connections=self._max_num_clients)
        elif isinstance(event, events.TickEvent):
            # Get the network events from the clients and post them to the event manager.
            if self._num_clients < self._max_num_clients:
                self._server.update_client_list()
            network_events = self._server.get_objects()
            for ev in network_events:
                # Send the event only if its class is not in the ignore list.
                for cl in self._post_ignore_events:
                    if isinstance(ev, cl):
                        break
                else:
                    self._ev_manager.post(ev)

            self._last_model_broadcast += event.elapsed_time
            if self._last_model_broadcast >= self._model_broadcast_interval:
                self._last_model_broadcast = 0
                self._ev_manager.post(events.ModelBroadcastRequest())

        for cl in self._send_ignore_events:
            if isinstance(event, cl):
                break
        else:
            self._server.broadcast(event)

    def shutdown(self):
        self._server.close_all()
