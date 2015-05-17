import framework.menu as menu
import pygame
import IPython


class MainMenu(menu.Menu):
    """The main menu.
    """

    def __init__(self):
        menu_bg = pygame.image.load("resources/menu_bg.jpg").convert()

        btn_normal = pygame.image.load("resources/btn_normal.png").convert()
        btn_hover = pygame.image.load("resources/btn_hover.png").convert()
        btn_pressed = pygame.image.load("resources/btn_pressed.png").convert()
        btn = menu.Button((4, 4), (2, 1), btn_normal, img_hovered=btn_hover, img_pressed=btn_pressed)

        buttons = [btn]
        super(MainMenu, self).__init__(menu_bg, buttons)

    def change_level(self):
        return False

    def next_level(self, get_level_func):
        pass
