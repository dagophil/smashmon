import events
import pygame
import Box2D
import IPython


class StagePygameView(object):
    """
    Show a stage model using a Pygame window.
    """

    def __init__(self, ev_manager):
        assert isinstance(ev_manager, events.EventManager)
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self._screen = pygame.display.get_surface()
        self._world = None

    def to_screen_x(self, x):
        return int(x * self._screen.get_width() / 10.0)

    def to_screen_y(self, y):
        return int(y * self._screen.get_height() / 10.0)

    def to_screen_xy(self, x, y):
        return self.to_screen_x(x), self.to_screen_y(y)

    def to_game_x(self, x):
        return x * 10.0 / self._screen.get_width()

    def to_game_y(self, y):
        return y * 10.0 / self._screen.get_height()

    def to_game_xy(self, x, y):
        return self.to_game_x(x), self.to_game_y(y)

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            if self._world is not None:
                colors = {
                    Box2D.b2_staticBody: (255, 255, 255, 255),
                    Box2D.b2_dynamicBody: (127, 127, 127, 255)
                }
                self._screen.fill((0, 0, 0, 0))  # TODO: Use the stage background image instead.
                for body in self._world.bodies:
                    for fixture in body.fixtures:
                        shape = fixture.shape

                        # TODO: This works for polygon shapes only. Change this.
                        vertices = [(body.transform*v) for v in shape.vertices]
                        vertices = [self.to_screen_xy(v[0], v[1]) for v in vertices]
                        vertices = [(v[0], self._screen.get_height() - v[1]) for v in vertices]
                        pygame.draw.polygon(self._screen, colors[body.type], vertices)

                pygame.display.flip()
        elif isinstance(event, events.WorldStep):
            self._world = event.world
