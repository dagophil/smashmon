import pygame
import Box2D
import main_menu
import IPython
import logging
from framework.utility import ExitException


def get_level(level_name, *args, **kwargs):
    """Create a new level with the given name and given options.

    :param level_name: level name
    :return:
    """
    if level_name == "MainMenu":
        return main_menu.MainMenu(*args, **kwargs)
    else:
        logging.error("Unknown level name: %s" % level_name)
        raise ExitException()


def gameloop(args):
    """Runs the game loop.

    :param args: Command line arguments.
    """
    pygame.init()
    screen = pygame.display.set_mode((args.width, args.height))
    clock = pygame.time.Clock()

    level = get_level("MainMenu")
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise ExitException()

                # TODO: Remove this in the final version.
                if hasattr(event, "key"):
                    if event.key == pygame.K_ESCAPE:
                        raise ExitException()

            level.update()
            level.display()

            pygame.display.flip()

            if level.change_level():
                level = level.next_level(get_level)

            clock.tick(args.fps)
    except ExitException:
        pygame.quit()
