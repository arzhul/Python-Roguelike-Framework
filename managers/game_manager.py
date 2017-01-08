import tdl
from areas.level import Level
from data.json_template_loader import JsonTemplateManager
from factories.body_factory import BodyFactory
from factories.character_factory import CharacterFactory
from factories.factory_service import FactoryService
from generators.dungeon_generator import DungeonGenerator
from managers.console_manager import ConsoleManager
from managers.scene_manager import SceneManager


class GameManager(object):
    """
    Game Manager: Handles setup and progression of the game
    Admittedly this is a bit of a mess and will need to be cleaned up.
    """
    def __init__(self):
        # Pre-load levels into database
        self.loaded_levels = []
        self.items = []
        self.monsters = []
        self.factory_service = None
        self.player = None
        self.load_game_data()
        self.console_manager = ConsoleManager()
        self.scene_manager = SceneManager(self.console_manager, start_game_callback=self.new_game)
        self.dungeon_generator = DungeonGenerator(self.factory_service)

    def start(self):
        self.scene_manager.current_scene.render()
        tdl.setTitle("Roguelike Framework")
        while True:  # Continue in an infinite game loop.
            self.console_manager.main_console.clear()  # Blank the console
            self.scene_manager.render(player=self.player)
            self.scene_manager.handle_input(player=self.player)
            tdl.flush()
            # TODO When dead it should switch to a new scene for character dump.

    def new_game(self):
        # TODO This should prepare the first level
        level = Level()
        level.name = "DEFAULT"
        level.min_room_size = 1
        level.max_room_size = 10
        level.max_rooms = 10
        level.width = 80
        level.height = 45
        self.init_dungeon(level)

    def init_dungeon(self, level):
        # TODO The player must be built and retrieved here.
        self.player = self.monsters.pop(-1)
        self.player.is_player = True
        level.monster_spawn_list = self.monsters
        self.dungeon_generator.generate(level, self.player)

    def load_game_data(self):
        """
        This is where the game templates / data is loaded.
        """
        json_template_loader = JsonTemplateManager()
        self.factory_service = FactoryService(
            template_loader=json_template_loader,
            body_factory=BodyFactory(json_template_loader.bodies_templates),
        )
        character_factory = CharacterFactory(
            character_templates=json_template_loader.monster_templates,
            factory_service=self.factory_service,
            race_templates=json_template_loader.race_templates,
            class_templates=json_template_loader.class_templates
        )
        self.factory_service.character_factory = character_factory
        # TODO Currently it builds the monsters one time, it does validate if the template is correct BUT
        # TODO Do we really want to hold an instance of each in memory?
        self.monsters = [character_factory.build(uid) for uid, monster in
                         json_template_loader.monster_templates.items()]
        self.items = []
