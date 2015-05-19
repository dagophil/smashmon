import pygame
# import Box2D
# import main_menu
# import IPython
# import logging
# from framework.utility import ExitException
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
            ev = events.TickEvent()
            self._ev_manager.post(ev)
            self._clock.tick(self._fps)

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._running = False


# def get_level(level_name, *args, **kwargs):
#     """Create a new level with the given name and given options.
#
#     :param level_name: level name
#     :return:
#     """
#     if level_name == "MainMenu":
#         return main_menu.MainMenu(*args, **kwargs)
#     else:
#         logging.error("Unknown level name: %s" % level_name)
#         raise ExitException()


def run(args):
    """Runs the game loop.

    :param args: Command line arguments.
    """
    ev_manager = events.EventManager()

    ticker = TickerController(ev_manager)
    menu_pygame_view = menu_view.MenuPygameView(ev_manager)
    main_menu = menu.MainMenuModel(ev_manager)
    menu_controller = io.MenuIOController(ev_manager, main_menu, menu_pygame_view)

    init_ev = events.InitEvent()
    ev_manager.post(init_ev)

    ticker.run()

    pygame.quit()

    #
    # pygame.init()
    # screen = pygame.display.set_mode((args.width, args.height))
    # clock = pygame.time.Clock()
    #
    # try:
    #     level = get_level("MainMenu")
    #     while True:
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 raise ExitException()
    #
    #             # TODO: Remove this in the final version.
    #             if hasattr(event, "key"):
    #                 if event.key == pygame.K_ESCAPE:
    #                     raise ExitException()
    #
    #         level.update()
    #         level.display()
    #
    #         pygame.display.flip()
    #
    #         if level.change_level():
    #             level = level.next_level(get_level)
    #
    #         clock.tick(args.fps)
    # except ExitException:
    #     pygame.quit()
