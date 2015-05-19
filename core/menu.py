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

    def is_up(self):
        return self.state == self.__UP

    def is_hovered(self):
        return self.state == self.__HOVERED

    def is_pressed(self):
        return self.state == self.__PRESSED

    def set_up(self):
        self.state = self.__UP

    def set_hovered(self):
        self.state = self.__HOVERED

    def set_pressed(self):
        self.state = self.__PRESSED

    def get_image(self):
        if self.is_up():
            return self.img
        elif self.is_hovered():
            return self.img_hovered
        elif self.is_pressed():
            return self.img_pressed
        else:
            raise Exception("Unknown button state: %d" % self.state)

    def action(self):
        if self._action is not None:
            self._action()


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
            self.buttons = []
        else:
            self.buttons = buttons

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
        if isinstance(event, events.InitEvent):
            ev = events.MenuCreatedEvent(self.bg_img, self.buttons)
            self._ev_manager.post(ev)
        elif isinstance(event, events.ButtonHoverRequestedEvent):
            b = event.button
            if b.is_up():
                b.set_hovered()
                self._ev_manager.post(events.ButtonHoverEvent(b))
        elif isinstance(event, events.ButtonUnhoverRequestedEvent):
            b = event.button
            if not b.is_up():
                b.set_up()
                self._ev_manager.post(events.ButtonUnhoverEvent(b))
        elif isinstance(event, events.ButtonPressRequestedEvent):
            b = event.button
            b.set_pressed()
            self._ev_manager.post(events.ButtonPressEvent(b))
        elif isinstance(event, events.ButtonActionRequestedEvent):
            b = event.button
            b.action()
            self._ev_manager.post(events.ButtonActionEvent(b))
            b.set_hovered()
            self._ev_manager.post(events.ButtonHoverEvent(b))
