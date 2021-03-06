import pygame
import events
import menu_io
import menu
import menu_view
import logging
import stage
import stage_view
import stage_io
import network
import network_controller


class TickerController(object):
    """
    Regularly sends a tick event to keep the game running (heart beat).
    """

    def __init__(self, ev_manager, fps=60):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._running = False
        self._fps = fps
        self._clock = pygame.time.Clock()

    def run(self):
        self._running = True
        elapsed_time = 0
        while self._running:
            self._ev_manager.post(events.TickEvent(elapsed_time=elapsed_time))
            elapsed_time = self._clock.tick(self._fps) / 1000.0  # elapsed time since last frame in seconds

    def notify(self, event):
        if isinstance(event, events.CloseCurrentModel):
            self._running = False


class GameApp(object):
    """
    This class starts, stops and exchanges the models and the corresponding view and controllers.
    """

    def __init__(self, args):
        """Init the app with the command line arguments.

        :param args: command line arguments
        """
        self._args = args
        self._models = {
            "Main Menu": self._main_menu_model,
            "Stage": self._stage_model
        }
        self._ev_manager = events.EventManager()
        self._ev_manager.next_model_name = self._args.model
        self._ticker = TickerController(self._ev_manager, self._args.fps)

    def _main_menu_model(self):
        logging.debug("GameApp: Loading main menu model")

        # Create MVC.
        menu_pygame_view = menu_view.MenuPygameView(self._ev_manager)
        main_menu = menu.MainMenuModel(self._ev_manager)
        menu_controller = menu_io.MenuIOController(self._ev_manager, main_menu, menu_pygame_view)

        # Init all components and start the ticker.
        self._ev_manager.post(events.InitEvent())
        self._ticker.run()

    def _stage_model(self):
        logging.debug("GameApp: Loading stage model")

        if self._args.server:
            stage_model = stage.StageModel(self._ev_manager, ignore_model_broadcasts=True)
            stage_pygame_view = stage_view.StagePygameView(self._ev_manager, stage_model)
            stage_controller = stage_io.StageIOController(self._ev_manager, character_index=0)
            network_server_controller = network_controller.ServerController(self._ev_manager, max_num_clients=1)
            load_controller = stage.StageStateController(self._ev_manager)
        elif self._args.client:
            # Network-Client.
            stage_model = stage.StageModel(self._ev_manager)
            stage_pygame_view = stage_view.StagePygameView(self._ev_manager, stage_model)

            # TODO: Somehow get the host.
            from socket import gethostname
            network_ev_manager = events.NetworkEventManager(self._ev_manager, gethostname())
            stage_controller = stage_io.StageIOController(network_ev_manager)
            load_controller = stage.StageStateClientController(network_ev_manager)
        else:
            # Single-player.
            stage_model = stage.StageModel(self._ev_manager)
            stage_pygame_view = stage_view.StagePygameView(self._ev_manager, stage_model)
            stage_controller = stage_io.StageIOController(self._ev_manager)
            load_controller = stage.StageStateController(self._ev_manager)

        # Init all components and start the ticker.
        self._ev_manager.post(events.InitEvent())
        self._ticker.run()

        if self._args.server:
            network_server_controller.shutdown()
        elif self._args.client:
            network_ev_manager.shutdown()

    def run(self):
        """Runs the game loop.
        """

        # if self._args.server:
        #
        #     port = 57122
        #     network_server = network.NetworkServer(port, decode=events.to_event, encode=events.to_string)
        #
        #     import time
        #     print "Waiting for clients ..."
        #     network_server.accept_clients(1)
        #     time.sleep(5)
        #     print "Done waiting for clients."
        #     network_server.update_client_list()
        #
        #     print "Waiting for messages ..."
        #     time.sleep(5)
        #     print "Done waiting for messages."
        #
        #     print "Getting objects"
        #     obj_list = network_server.get_objects()
        #     print "Got objects"
        #     to_send = []
        #     for obj in obj_list:
        #         print "Received object:", obj, "dict:", obj.__dict__
        #         # to_send.append(obj + " FROM SERVER!")
        #         obj.elapsed_time = 2
        #         to_send.append(obj)
        #
        #     print "Sending objects"
        #     for obj in to_send:
        #         network_server.broadcast(obj)
        #     print "Done sending"
        #
        #     print "trying to close"
        #     network_server.close_all()
        #     print "closed"
        #
        # else:
        #     import socket
        #     host = socket.gethostname()
        #     port = 57122
        #     network_client = network.NetworkClient(host, port, decode=events.to_event, encode=events.to_string)
        #
        #     print "Sleeping"
        #     import time
        #     time.sleep(5)
        #
        #     # s0 = "this is a string"
        #     # s1 = "hello"
        #     # s2 = "foo"
        #     # print "Trying to send s0:", s0
        #     # network_client.send(s0)
        #     # print "Trying to send s1:", s1
        #     # network_client.send(s1)
        #     # print "Trying to send s2:", s2
        #     # network_client.send(s2)
        #     print "Trying to send tick event"
        #     ev = events.TickEvent(1.5)
        #     network_client.send(ev)
        #
        #     print "Done sending"
        #
        #     print "Waiting for incoming messages"
        #     time.sleep(5)
        #     print "Getting objects"
        #     obj_list = network_client.get_objects()
        #     print "Got objects"
        #     for obj in obj_list:
        #         print "Received object:", obj, "dict:", obj.__dict__
        #
        #     print "trying to close"
        #     network_client.close_all()
        #     print "closed"
        #
        #
        # return

        # Show the window.
        pygame.display.set_mode((self._args.width, self._args.height))

        while self._ev_manager.next_model_name is not None:
            if self._ev_manager.next_model_name in self._models:
                # Load and run the next model.
                model = self._models[self._ev_manager.next_model_name]
                self._ev_manager.next_model_name = None
                model()
            else:
                raise Exception("Unknown model name: %s" % self._ev_manager.next_model_name)

        # Quit when all models finished.
        pygame.quit()
