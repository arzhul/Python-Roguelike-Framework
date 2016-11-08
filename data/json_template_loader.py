import logging
import jsonpickle
import os
from components.material import materials
from components.body import get_humanoid_body_sample, get_body_parts_sample

logger_ = logging.getLogger()


class JsonTemplateManager(object):
    TEMPLATE_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    MATERIAL_FULL_PATH = os.path.join(TEMPLATE_FOLDER_PATH, 'materials.json')
    BODIES_FULL_PATH = os.path.join(TEMPLATE_FOLDER_PATH, 'bodies.json')
    BODYPARTS_FULL_PATH = os.path.join(TEMPLATE_FOLDER_PATH, 'bodyparts.json')
    MONSTERS_FULL_PATH = os.path.join(TEMPLATE_FOLDER_PATH, 'monsters.json')

    def __init__(self):
        self.material_templates = []
        self.bodies_templates = []
        self.bodyparts_templates = []
        self.monster_templates = []
        self.load_templates()

    def load_templates(self):
        self.material_templates = self._load_template_file(self.MATERIAL_FULL_PATH, 'Materials')
        self.bodies_templates = self._load_template_file(self.BODIES_FULL_PATH, 'Bodies')
        self.bodyparts_templates = self._load_template_file(self.BODYPARTS_FULL_PATH, 'Bodyparts')
        self.monster_templates = self._load_template_file(self.MONSTERS_FULL_PATH, 'Monsters')

    @staticmethod
    def _load_template_file(full_path, template_name):
        if os.path.isfile(full_path):
            with open(full_path, 'r') as open_json_file:
                return jsonpickle.loads(open_json_file.read())
        else:
            logger_.error(template_name + " template file not found at " + full_path)

    def save_templates(self):
        self._save_templates_file(self.MATERIAL_FULL_PATH, self.material_templates)
        self._save_templates_file(self.BODIES_FULL_PATH, self.bodies_templates)
        self._save_templates_file(self.BODYPARTS_FULL_PATH, self.bodyparts_templates)
        self._save_templates_file(self.MONSTERS_FULL_PATH, self.monster_templates)

    @staticmethod
    def _save_templates_file(full_path, templates):
        with open(full_path, 'w') as new_json_file:
            new_json_file.write(jsonpickle.dumps(templates))


if __name__ == '__main__':
    from characters.character import Character
    from characters.race import Race
    Orc = Character("orc", "Orc", None, None, )
    template_manager = JsonTemplateManager()
    template_manager.material_templates = materials
    template_manager.bodies_templates = [get_humanoid_body_sample()]
    template_manager.bodyparts_templates = get_body_parts_sample()
    template_manager.save_templates()