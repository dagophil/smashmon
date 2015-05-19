import pygame
import events
import io
import menu
import menu_view


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
        if isinstance(event, events.QuitEvent):
            self._running = False


def run(args):
    """Runs the game loop.

    :param args: Command line arguments.
    """
    # Create event manager.
    ev_manager = events.EventManager()

    # Create MVC.
    ticker = TickerController(ev_manager)
    menu_pygame_view = menu_view.MenuPygameView(ev_manager)
    main_menu = menu.MainMenuModel(ev_manager)
    menu_controller = io.MenuIOController(ev_manager, main_menu, menu_pygame_view)

    # The MVC is set up, so all components can be initialized.
    ev_manager.post(events.InitEvent())

    # Start the heart beat.
    ticker.run()

    # Quit when the heart stops beating.
    pygame.quit()
