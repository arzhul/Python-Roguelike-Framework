import unittest

import abilities
from abilities.ability import Ability
from abilities.power_abilities import PowerAbilities
from stats.enums import StatsEnum
from stats.stat import StatModifier
from util.leveltree import LevelTree


class LevelTreeTestCase(unittest.TestCase):

    def test_stats_modifiers(self):
        test_tree = LevelTree()
        test_tree.stats_modifiers = {
            1: [StatModifier(StatsEnum.Health, 1, level_progression=1),
                StatModifier(StatsEnum.Charisma, -1, level_progression=2)],
            2: [StatModifier(StatsEnum.Dexterity, 1)]
        }
        modifiers = test_tree.get_stat_modifiers(8)
        self.assertEqual(modifiers[StatsEnum.Health], 7)
        self.assertEqual(modifiers[StatsEnum.Dexterity], 1)
        self.assertEqual(modifiers[StatsEnum.Charisma], 3)

    def test_ability_modifiers(self):
        test_tree = LevelTree()
        test_tree.ability_modifiers = {
            1: [
                abilities.Bite(1),
                Ability(PowerAbilities.Berserk, 1, level_progression=1),
                Ability(PowerAbilities.Regeneration, 1, level_progression=10)
            ]
        }
        modifiers = test_tree.get_ability_modifiers(12)
        self.assertEqual(modifiers[abilities.Bite], 1)
        self.assertEqual(modifiers[PowerAbilities.Berserk], 11)
        self.assertEqual(modifiers[PowerAbilities.Regeneration], 2)
