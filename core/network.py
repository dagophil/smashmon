import socket
import logging
import json
import Queue
import threading


def accept_clients(port, qu, stop_event, max_num_connections=None, timeout=1.0):
    """
    Listen for socket connections on the given port on the local machine. Accept all connections and put the tuple
    (connection, address) in the given queue. Exit when the stop event is set.

    :param port: port
    :param qu: queue to put the clients in
    :param stop_event: stop event
    :param max_num_connections: maximum number of connections
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
    count = 0
    while True:
        if stop_event.isSet():
            break
        if max_num_connections is not None:
            if count >= max_num_connections:
                break

        sock.listen(5)
        try:
            c, addr = sock.accept()
        except socket.timeout:
            continue
        qu.put((c, addr))
        count += 1
        logging.debug("Network: Accepted client with address %s" % str(addr))
    sock.close()


def listen_on_connection(conn, qu, stop_event, timeout=1.0):
    """
    Listen on the given connection and put the received items in the given queue. Exit when the stop event is set or
    when the maximum number of connections is reached.

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

        # Get the data that will be appended to the data string.
        to_append = ""
        try:
            to_append = conn.recv(4096)
        except socket.timeout:
            continue
        if to_append == "":
            connection_lost = True
        data_string += to_append

        # Read the item size from the data string.
        if data_len is None:
            r_index = data_string.find("#")
            if r_index == -1:
                continue
            data_len = int(data_string[:r_index])
            data_string = data_string[r_index+1:]

        # Decode the received string to an object.
        if len(data_string) >= data_len:
            obj_string = data_string[:data_len]
            data_string = data_string[data_len:]
            qu.put(obj_string, block=True)
            data_len = None

    logging.debug("Network: Closed client connection.")
    conn.close()


class NetworkServer(object):
    """
    The NetworkServer class accepts connections from clients and can be used to send and receive arbitrary objects.
    Before the server listens to an accepted connection, the update_client_list() method must be called.
    The constructor takes methods to encode an object to a string and decode a string to an object. If those methods are
    not given, json.dumps() and json.loads() is used.

    Internally, the following protocol is used to send data:
    def send(obj):
        data_string = encode(obj)
        send_string = str(len(data_string)) + "#" + data_string
        socket.send(send_string)
    """

    def __init__(self, port, decode=None, encode=None):
        self._port = port
        if decode is None:
            self._decode = json.loads
        else:
            self._decode = decode
        if encode is None:
            self._encode = json.dumps
        else:
            self._encode = encode
        self._clients = []
        self._client_queue = Queue.Queue()
        self._client_listeners = []
        self._item_queue = Queue.Queue()
        self._stop = threading.Event()
        self._client_acceptor = None

    def num_clients(self):
        return len(self._clients)

    def accept_clients(self, max_num_connections=None):
        """
        Start a thread that accepts the given number of connections. If max_num_connections is None, all connections
        are accepted until the server closes.

        :param max_num_connections: maximum number of connections
        """
        if self._client_acceptor is not None:
            raise Exception("The client acceptor is already running.")
        self._client_acceptor = threading.Thread(target=accept_clients,
                                                 args=(self._port, self._client_queue, self._stop, max_num_connections))
        self._client_acceptor.start()

    def update_client_list(self):
        """Get all clients from the queue that is filled by the accept_clients thread and move them in a list.
        """
        new_clients = []
        while not self._client_queue.empty():
            new_clients.append(self._client_queue.get())
            self._client_queue.task_done()
        for c, addr in new_clients:
            t = threading.Thread(target=listen_on_connection, args=(c, self._item_queue, self._stop))
            t.start()
            self._clients.append((c, addr, t))
        if self._client_acceptor is not None:
            if not self._client_acceptor.isAlive():
                logging.debug("Network: Accepted the desired number of connections.")
                self._client_acceptor = None

    def get_objects(self):
        """Return a list with all objects that came in from the listener threads.
        """
        items = []
        while not self._item_queue.empty():
            item_string = self._item_queue.get()
            item = self._decode(item_string)
            items.append(item)
            self._item_queue.task_done()
        return items

    def close_all(self):
        """Close all connections and exit all threads.
        """
        self._stop.set()
        if self._client_acceptor is not None:
            self._client_acceptor.join()
        for c, addr, t in self._clients:
            t.join()

    def broadcast(self, obj):
        """Send the object to all clients.
        """
        data = self._encode(obj)
        data_string = str(len(data)) + "#" + data
        for c, addr, t in self._clients:
            c.sendall(data_string)


class NetworkClient(object):
    """
    The NetworkClient class connects to a server and can send and receive arbitrary objects.
    The constructor takes methods to encode an object to a string and decode a string to an object. If those methods are
    not given, json.dumps() and json.loads() is used.

    Internally, the following protocol is used to send data:
    def send(obj):
        data_string = encode(obj)
        send_string = str(len(data_string)) + "#" + data_string
        socket.send(send_string)
    """

    def __init__(self, host, port, decode=None, encode=None):
        if decode is None:
            self._decode = json.loads
        else:
            self._decode = decode
        if encode is None:
            self._encode = json.dumps
        else:
            self._encode = encode
        self._queue = Queue.Queue()
        self._stop = threading.Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        logging.debug("Network: Established connection to %s:%d" % (host, port))
        self._network_listener = threading.Thread(target=listen_on_connection, args=(self._socket, self._queue, self._stop))
        self._network_listener.start()

    def send(self, obj):
        """Send the object to the server.
        """
        data = self._encode(obj)
        data_string = str(len(data)) + "#" + data
        self._socket.sendall(data_string)

    def get_objects(self):
        """Take all items from the item queue, put them in a list. Clear the queue and return the list.
        """
        items = []
        while not self._queue.empty():
            item_string = self._queue.get()
            item = self._decode(item_string)
            items.append(item)
            self._queue.task_done()
        return items

    def close_all(self):
        self._stop.set()
        self._network_listener.join()
