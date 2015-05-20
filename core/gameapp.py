import pygame
import events
import io
import menu
import menu_view
import logging


class TickerController(object):
    """
    Regularly sends a tick event to keep the game running (heart beat).
    """

    def __init__(self, ev_manager, fps=60):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._running = True
        self._fps = fps
        self._clock = pygame.time.Clock()

    def run(self):
        while self._running:
            self._ev_manager.post(events.TickEvent())
            self._clock.tick(self._fps)

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
        self._ev_manager = events.EventManager()
        # self._ev_manager.register_listener(self)
        self._quit_app_requested = False
        self._models = {
            "Main Menu": self.main_menu_model
        }
        self._next_model_name = "Main Menu"

    def main_menu_model(self):
        # Create MVC.
        ticker = TickerController(self._ev_manager, self._args.fps)
        menu_pygame_view = menu_view.MenuPygameView(self._ev_manager)
        main_menu = menu.MainMenuModel(self._ev_manager)
        menu_controller = io.MenuIOController(self._ev_manager, main_menu, menu_pygame_view)

        # The MVC is set up, so all components can be initialized.
        self._ev_manager.post(events.InitEvent())

        # Start the heart beat.
        ticker.run()

        # Get the next model.
        self._next_model_name = self._ev_manager.next_model_name

    def run(self):
        """Runs the game loop.
        """
        # Show the window.
        pygame.display.set_mode((self._args.width, self._args.height))

        while self._next_model_name is not None:
            # Initialize and run the next model.
            if self._next_model_name in self._models:
                self._models[self._next_model_name]()
            else:
                raise Exception("Unknown model name: %s" % self._next_model_name)

            if self._quit_app_requested:
                break
            elif self._next_model_name is None:
                logging.warning("GameApp: The current model finished and did not set a new model, "
                                "but there was no quit event.")
            else:
                logging.warning("TODO: Clean the listeners before loading the next model.")

        # Quit when all models finished.
        pygame.quit()
