import sys
import argparse
import core.gameapp as app


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
    args = parser.parse_args()

    assert args.width > 0
    assert args.height > 0
    assert args.fps > 0

    return args


def main():
    """Calls the game loop.
    """
    args = parse_command_line()
    app.gameloop(args)


if __name__ == "__main__":
    main()
    sys.exit(0)