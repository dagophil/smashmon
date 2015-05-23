import events
import pygame
import Box2D
import IPython
import pygame_view


class StagePygameView(pygame_view.PygameView):
    """
    Show a stage model using a Pygame window.
    """

    def __init__(self, ev_manager):
        super(StagePygameView, self).__init__(ev_manager)
        self._world = None

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
