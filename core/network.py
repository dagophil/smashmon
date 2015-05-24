import events
import socket
import logging
import sys
import json
import Queue
import threading


def accept_clients(port, qu, stop_event, timeout=1.0):
    """
    Listen for socket connections on the given port on the local machine. Accept all connections and put the tuple
    (connection, address) in the given queue. Exit when the stop event is set.

    :param port: port
    :param qu: queue to put the clients in
    :param stop_event: stop event
    :param timeout: socket timeout
    """
    assert timeout > 0

    # Create the socket and bind it to localhost:port.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    host = socket.gethostname()
    sock.bind((host, port))

    logging.debug("Network: Listening for connections on port %d" % port)

    # Listen for incoming connections.
    while True:
        if stop_event.isSet():
            break
        sock.listen(5)
        try:
            c, addr = sock.accept()
        except socket.timeout:
            continue
        logging.debug("Network: Accepted client with address %s" % str(addr))
        qu.put((c, addr))
    sock.close()


def listen_on_connection(conn, qu, stop_event, timeout=1.0):
    """
    Listen on the given connection and put the received items in the given queue. Exit when the stop event is set.

    :param conn: socket connection
    :param qu: queue to put the items in
    :param stop_event: stop event
    :param timeout: socket timeout
    """

    conn.settimeout(timeout)
    data_string = ""  # data string that is filled by the socket's recv method.
    data_len = None  # size of the current item
    connection_lost = False
    while True:
        if stop_event.isSet() or connection_lost:
            break
        print "current data string:", data_string
        # Get the data that will be appended to the data string.
        to_append = ""
        try:
            to_append = conn.recv(4096)
        except socket.timeout:
            continue
        if to_append == "":
            connection_lost = True
        data_string += to_append

        if data_len is None:
            # Read the item size from the data string.
            r_index = data_string.find("#")
            if r_index == -1:
                continue
            data_len = int(data_string[:r_index])
            data_string = data_string[r_index+1:]

        if len(data_string) >= data_len:
            # Create the received object.
            obj_string = data_string[:data_len]
            data_string = data_string[data_len:]
            obj = json.loads(obj_string)
            qu.put(obj, block=True)
            data_len = None

    logging.debug("Network: Closed client connection.")
    conn.close()


class NetworkServer(object):
    """
    The NetworkServer class accepts connections from clients and can be used to send and receive arbitrary objects.
    Before the server listens to an accepted connection, the update_client_list() method must be called.

    Internally, the following protocol is used to send data:
    def send(obj):
        data_string = json.dumps(obj)
        send_string = str(len(data_string)) + "#" + data_string
        socket.send(send_string)
    """

    def __init__(self, port):
        self._port = port
        self._clients = []
        self._client_queue = Queue.Queue()
        self._client_listeners = []
        self._item_queue = Queue.Queue()
        self._stop = threading.Event()
        self._client_acceptor = threading.Thread(target=accept_clients, args=(port, self._client_queue, self._stop))
        self._client_acceptor.start()

    def update_client_list(self):
        new_clients = []
        while not self._client_queue.empty():
            new_clients.append(self._client_queue.get())
            self._client_queue.task_done()
        for c, addr in new_clients:
            t = threading.Thread(target=listen_on_connection, args=(c, self._item_queue, self._stop))
            t.start()
            self._clients.append((c, addr, t))

    def get_objects(self):
        items = []
        while not self._item_queue.empty():
            items.append(self._item_queue.get())
            self._item_queue.task_done()
        return items

    def close_all(self):
        """Close all connections and exit all threads.
        """
        self._stop.set()
        self._client_acceptor.join()
        for c, addr, t in self._clients:
            t.join()


class NetworkClient(object):
    """
    The NetworkClient class connects to a server and can send and receive arbitrary objects.

    Protocol:
    data_string = json.dumps(obj)
    sent_string = str(len(data_string)) + "#" + data_string
    """

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._queue = Queue.Queue()
        self._stop = threading.Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        logging.debug("Network: Established connection to %s:%d" % (host, port))
        self._network_listener = threading.Thread(target=self._listen)
        self._network_listener.start()

    def send(self, obj):
        data = json.dumps(obj)
        data_string = str(len(data)) + "#" + data
        try:
            self._socket.sendall(data_string)
        except socket.error, msg:
            logging.error("Failed to send via socket. Error code: %d. Error message: %s" % (msg[0], str(msg[1])))

    def get_objects(self):
        """Take all items from the queue, put them in a list. Clear the queue and return the list.
        """
        items = []
        while not self._queue.empty():
            items.append(self._queue.get())
            self._queue.task_done()
        return items

    def _listen(self):
        """Receive data from the socket, construct the object that was sent and put it in the queue.
        """
        data_string = ""
        data_len = None
        self._socket.settimeout(1)
        while True:
            if self._stop.isSet():
                break
            try:
                data_string += self._socket.recv(4096)
            except socket.timeout:
                continue
            if data_len is None:
                r_index = data_string.find("#")
                if r_index == -1:
                    continue
                data_len = int(data_string[:r_index])
                data_string = data_string[r_index+1:]

            if len(data_string) >= data_len:
                full_data_string = data_string[:data_len]
                data_string = data_string[data_len:]
                obj = json.loads(full_data_string)
                self._queue.put(obj, block=True)

    def close_all(self):
        print "trying to close"
        self._stop.set()
        print "waiting for listener to join"
        self._network_listener.join()
        print "trying to close socket"
        self._socket.close()
        print "closed"


# class NetworkEventManager(events.EventManager):
#     """
#     Receives events and sends them over network.
#     """
#
#     def __init__(self, ev_manager):
#         assert isinstance(ev_manager, events.EventManager)
#         self._ev_manager = ev_manager
#         self._ev_manager.register_listener(self)
#         super(NetworkEventManager, self).__init__()
#
#     def post(self, event):
#         # TODO: Send event over network.
#         pass
#
#     def notify(self, event):
#         listeners = list(self._listeners)
#         for l in listeners:
#             l.notify(event)