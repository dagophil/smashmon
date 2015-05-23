import pygame
import events
import logging
import resource_manager
import pygame_view


class MenuPygameView(pygame_view.PygameView):
    """
    Show a menu model using a Pygame window.
    """

    def __init__(self, ev_manager):
        super(MenuPygameView, self).__init__(ev_manager)

    def _get_button_image(self, button):
        w, h = self.to_screen_xy(button.width, button.height)
        im = resource_manager.ResourceManager.instance().get_image(button.get_image(), size=(w, h))
        x, y = self.to_screen_xy(button.x, button.y)
        return im, (x, y)

    def notify(self, event):
        if isinstance(event, events.MenuCreatedEvent):
            im = resource_manager.ResourceManager.instance().get_image(event.bg_img, size=self._screen.get_size())
            self._screen.blit(im, (0, 0))
            for b in event.buttons:
                im, (x, y) = self._get_button_image(b)
                self._screen.blit(im, (x, y))
        elif isinstance(event, events.TickEvent):
            pygame.display.flip()
        elif isinstance(event, events.ButtonHoverEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))
        elif isinstance(event, events.ButtonUnhoverEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))
        elif isinstance(event, events.ButtonPressEvent):
            b = event.button
            im, (x, y) = self._get_button_image(b)
            self._screen.blit(im, (x, y))
        elif isinstance(event, events.CloseCurrentModel):
            next_model_name = event.next_model_name
            if next_model_name != "Main Menu":
                self._ev_manager.unregister_listener(self)
