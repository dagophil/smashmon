import pygame
import events


class Button(object):
    """
    Button with three states (normal, hovered, pressed).
    """

    # The button states.
    __UP = 0
    __HOVERED = 1
    __PRESSED = 2

    def __init__(self, (x, y), (width, height), img, img_hovered=None, img_pressed=None, action=None):
        """
        Initialize the button with the given parameters.

        :param (x, y): button position
        :param (width, height): button size
        :param img: default image
        :param img_hovered: image when hovered
        :param img_pressed: image when pressed
        :param action: function that is called when the button is pressed (must not have parameters)
        """
        self.state = self.__UP
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img
        if img_hovered is None:
            self.img_hovered = img
        else:
            self.img_hovered = img_hovered
        if img_pressed is None:
            self.img_pressed = img
        else:
            self.img_pressed = img_pressed
        self._action = action

    def get_image(self):
        if self.state == self.__UP:
            return self.img
        elif self.state == self.__HOVERED:
            return self.img_hovered
        elif self.state == self.__PRESSED:
            return self.img_pressed
        else:
            raise Exception("Unknown button state: %d" % self.state)


class MenuModel(object):
    """
    Abstract model for menus (a background with buttons).
    A menu has coordinates from (0, 0) to (10, 10).
    """

    def __init__(self, ev_manager, bg_img, buttons=None):
        self._ev_manager = ev_manager
        self._ev_manager.register_listener(self)
        self.bg_img = bg_img
        if buttons is None:
            self._buttons = []
        else:
            self._buttons = buttons

    def notify(self, event):
        raise NotImplementedError


class MainMenuModel(MenuModel):
    """
    The main menu model.
    """

    def __init__(self, ev_manager):
        menu_bg = "resources/menu_bg.jpg"
        btn_normal = "resources/btn_normal.png"
        btn_hover = "resources/btn_hover.png"
        btn_pressed = "resources/btn_pressed.png"
        btn = Button((4, 4), (2, 1), btn_normal, img_hovered=btn_hover, img_pressed=btn_pressed)

        buttons = [btn]
        super(MainMenuModel, self).__init__(ev_manager, menu_bg, buttons=buttons)

    def notify(self, event):
        # TODO: Capture ChangeButtonState events.

        if isinstance(event, events.InitEvent):
            ev = events.MenuCreatedEvent(self.bg_img, self._buttons)
            self._ev_manager.post(ev)
