import events
import pygame
import Box2D
import IPython
import pygame_view
import stage


class StagePygameView(pygame_view.PygameView):
    """
    Show a stage model using a Pygame window.
    """

    def __init__(self, ev_manager, stage_model):
        super(StagePygameView, self).__init__(ev_manager)
        assert isinstance(stage_model, stage.StageModel)
        self._stage_model = stage_model

    def to_game_y(self, y):
        return self.to_game_x(y)

    def to_screen_y(self, y):
        return self.to_screen_x(y)

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            world = self._stage_model.world
            colors = self._stage_model.colors
            self._screen.fill((0, 0, 0, 0))  # TODO: Use the stage background image instead.
            for body in world.bodies:
                for fixture in body.fixtures:
                    shape = fixture.shape

                    # TODO: This works for polygon shapes only. Change this.
                    vertices = [(body.transform*v) for v in shape.vertices]
                    vertices = [self.to_screen_xy(v[0], v[1]) for v in vertices]
                    vertices = [(v[0], self._screen.get_height() - v[1]) for v in vertices]
                    pygame.draw.polygon(self._screen, colors[body.userData], vertices)

            pygame.display.flip()
