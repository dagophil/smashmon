import sys
import argparse
import logging
from core.gameapp import GameApp


def parse_command_line():
    """Parses the command line arguments.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Smashmon")
    parser.add_argument("--width", type=int, default=600,
                        help="Screen width")
    parser.add_argument("--height", type=int, default=400,
                        help="Screen height")
    parser.add_argument("--fps", type=int, default=60,
                        help="Frames per second")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print verbose output")
    args = parser.parse_args()

    assert args.width > 0
    assert args.height > 0
    assert args.fps > 0

    if args.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    return args


def main():
    """Calls the game loop.
    """
    args = parse_command_line()
    app = GameApp(args)
    app.run()


if __name__ == "__main__":
    main()
    sys.exit(0)