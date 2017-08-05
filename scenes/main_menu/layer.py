import cocos
from scenes.main_menu.menu import MainMenu


class MainMenuUILayer(cocos.layer.Layer):
    def __init__(self):
        super().__init__()
        self.menu = MainMenu(title=self.get_description())
        self.add(self.menu)

    def get_description(self):
        # TODO We should get this from a config file.
        return "\nWelcome to Python Roguelike Framework!\n " \
               "This '@' is you. Your goal is to explore the dungeon.\n " \
               "Use caution though as there are monsters lurking around every corner \n " \
               "waiting to jump out and attack you!\n "

