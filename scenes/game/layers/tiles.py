from itertools import chain

import cocos
import pyglet
import tdl

import settings
from settings import DUNGEON_COLORS as COLORS
from stats.enums import StatsEnum
from components.cocos import CocosLabelComponent


class TilesLayer(cocos.tiles.RectMapLayer):
    is_event_handler = True

    def __init__(self, game_context, scrolling_manager):
        current_level = game_context.player.location.level
        super().__init__(current_level.name, 1, 1, cells=current_level.tiles)
        self.game_context = game_context
        # TODO Eventually we want to map more than just movement keys
        self.movement_keys = settings.KEY_MAPPINGS
        self.scrolling_manager = scrolling_manager
        for game_object in chain(current_level.spawned_monsters, (game_context.player,)):
            r, g, b = game_object.display.foreground_color
            x, y = game_object.location.get_local_coords()
            cocos_node = CocosLabelComponent(
                game_object.display.ascii_character, x=x * 10, y=y * 10,
                font_name='terminal', font_size=10,
                align='center', anchor_x='center', anchor_y='center',
                color=(r, g, b, 255)
            )
            game_object.register_component(cocos_node)
            self.add(game_object.cocos)
            self.pressed = False
            self.scrolling_manager.force_focus(x * 10, y * 10)


    def render(self, active):
        """
        Render the areas, characters, items, etc..
        """
        super().render(active)
        player = self.game_context.player
        current_level = player.location.level
        self.render_gui(player)
        self.set_tiles_background_color(current_level)




        # NB: Order in which things are render is important
        self.render_map(current_level, player.fov)
        self.render_items(player, current_level)
        self.render_characters(player, current_level)
        self.render_player(player)
        if player.is_dead():
            self.consoles[GameConsoles.Status].drawStr(0, 4, 'You have died!')

    def render_gui(self, player):
        status_console = self.consoles[GameConsoles.Status]
        status_console.drawStr(0, 2, "Health: {}\n\n".format(int(player.stats.get_current_value(StatsEnum.Health))))
        status_console.drawStr(0, 5, "Attack Power: {}\n\n".format(player.get_attack_modifier()))
        status_console.drawStr(0, 8, "Defense: {}\n\n".format(player.get_armor_class()))
        status_console.drawStr(0, 11, "Speed: {}\n\n".format(player.get_speed_modifier()))

        self.game_context.console_manager.render_console(self.consoles[GameConsoles.ActionLog], 0, 45)
        self.game_context.console_manager.render_console(status_console, 80, 45)

    def render_map(self, current_level, viewer_fov):
        for x, y in viewer_fov:
            if not x >= len(current_level.tiles) and not y >= len(current_level.tiles[x]):
                self.main_console.drawChar(x, y, **current_level.tiles[x][y].display.get_draw_info())
                current_level.tiles[x][y].is_explored = True

    def render_items(self, player, level):
        for item in level.spawned_items:
            x, y = item.location.get_local_coords()
            if (x, y) in player.fov:
                self.main_console.drawChar(x, y, **item.display.get_draw_info())

    def render_characters(self, player, level):
        # draw monsters
        for monster in level.spawned_monsters:
            x, y = monster.location.get_local_coords()
            if (x, y) in player.fov:
                self.main_console.drawChar(x, y, **monster.display.get_draw_info())

    def render_player(self, player):
        self.main_console.drawChar(
            player.location.local_x,
            player.location.local_y,
            **player.display.get_draw_info()
        )


    def set_tiles_background_color(self, current_level):
        # TODO Instead of using a different color, we should darken whatever color it is.
        # TODO Allowing us to use many colors as walls and tiles to create levels with different looks.
        for y in range(current_level.height):
            for x in range(current_level.width):
                tile = current_level.tiles[x][y]
                wall = tile.block_sight
                ground = tile.is_ground

                if tile.is_explored:
                    if wall:
                        self.main_console.drawChar(x, y, '#', fgcolor=COLORS['dark_gray_wall'])
                    elif ground:
                        self.main_console.drawChar(x, y, '.', fgcolor=COLORS['dark_ground'])

    @staticmethod
    def is_transparent(current_level, x, y):
        """
        Used by map.quickFOV to determine which tile fall within the players "field of view"
        """
        try:
            # Pass on IndexErrors raised for when a player gets near the edge of the screen
            # and tile within the field of view fall out side the bounds of the.tiles.
            tile = current_level.tiles[x][y].tile
            if tile.block_sight and tile.is_blocked:
                return False
            else:
                return True
        except IndexError:
            return False

    def _update_sprite_set(self):
        # update the sprites set
        keep = set()
        for cell in self.get_visible_cells():
            cx, cy = key = cell.origin[:2]
            keep.add(key)
            if cell.tile is None:
                continue
            if key in self._sprites:
                s = self._sprites[key]
            else:
                image = cell.tile.image
                if isinstance(image, str):
                    r, g, b = cell.tile.display.foreground_color
                    s = pyglet.text.Label(image, x=cx, y=cy, batch=self.batch, font_size=10, align='center', anchor_x='center', anchor_y='center', color=(r, g, b, 255))
                else:
                    s = pyglet.sprite.Sprite(cell.tile.image,
                                             x=cx, y=cy, batch=self.batch)
                if 'color4' in cell.properties:
                    r, g, b, a = cell.properties['color4']
                    s.color = (r, g, b)
                    s.opacity = a
                self._sprites[key] = s

            if self.debug:
                if getattr(s, '_label', None):
                    continue
                label = [
                    'cell=%d,%d' % (cell.i, cell.j),
                    'origin=%d,%d px' % (cx, cy),
                ]
                for p in cell.properties:
                    label.append('%s=%r' % (p, cell.properties[p]))
                if cell.tile is not None:
                    for p in cell.tile.properties:
                        label.append('%s=%r' % (p, cell.tile.properties[p]))
                lx, ly = cell.topleft
                s._label = pyglet.text.Label(
                    '\n'.join(label), multiline=True, x=lx, y=ly,
                    bold=True, font_size=8, width=cell.width,
                    batch=self.batch)
            else:
                s._label = None
        for k in list(self._sprites):
            if k not in keep and k in self._sprites:
                self._sprites[k]._label = None
                del self._sprites[k]

    def on_key_press(self, key, modifiers):
        player = self.game_context.player
        current_level = player.location.level
        moved = False
        if self.pressed:
            return

        x, y = player.location.get_local_coords()

        def is_transparent_callback(x, y):
            if x <= 0 or y <= 0:
                return False
            return self.is_transparent(current_level, x, y)
        player.fov = tdl.map.quickFOV(x, y, is_transparent_callback, 'basic')

        # We mix special keys with normal characters so we use keychar.
        if not player.is_dead():
            if key in (pyglet.window.key.NUM_5, pyglet.window.key.PERIOD):
                moved = True

            if key in self.movement_keys:
                key_x, key_y = self.movement_keys[key]
                # TODO MANAGERS SHOULD BE IN THE GAME CONTEXT AND ACCESSED FROM IT, NOT GAME SCENE
                self.game_context.action_manager.move_or_attack(player, key_x, key_y)
                moved = True

            if moved:
                player.update()
                for monster in current_level.spawned_monsters:
                    monster.update()
                    self.game_context.action_manager.monster_take_turn(monster, player)
                moved = False

                self.scrolling_manager.force_focus(x * 10, y * 10)
        self.pressed = True

    def on_key_release(self, symbol, modifiers):
        self.pressed = False

