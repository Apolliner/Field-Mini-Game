from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
"""
    Логика действий персонажей
"""

class CharacterAction(Bases):
    def action_return_action(self):
        actions_dict = {
            "campfire": {
                "name": "campfire",
                "description": "",
                "stages": {
                    "search for a place": self._action_search_for_a_place,
                    "collect firewood": self._action_collect_firewood,
                    "arrange a fire pit": self._action_arrange_a_fire_pit,
                    "kindle campfire": self._action_kindle_campfire
                }
            }
        }

    def _action_func(self, **kwargs):
        pass

    def _action_search_for_a_place(self, **kwargs):
        """ Ищет подходящее место для костра. Оно должно быть сухим и неподалёку должны быть дрова. """
        locations_list = list()
        firewood_set = set(dry)
        global_map = kwargs["global_map"]
        lines = global_map[self.global_position[0] - 1:self.global_position[0] + 1]
        for number_line, line in enumerate(lines):
            locations = line[self.global_position[1] - 1:self.global_position[1] + 1]
            for number_location, location in enumerate(locations):
                icons_set = set(location.tiles_count.keys())
                intersections = firewood_set.intersection(icons_set)
                if intersections:
                    locations_list.append([self.global_position[0] + number_line - 1],
                                          [self.global_position[1] + number_location - 1])
        # Список локаций вокруг персонажа, на которых есть дрова собран.


    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в одну точку """
        ...

    def _action_arrange_a_fire_pit(self, **kwargs):
        """ 3 раза ходит от дров до места установки костра. Каждый раз проводит действие над костром. """
        ...

    def _action_kindle_campfire(self, **kwargs):
        """ Проводит некоторое время производя действие над костром. Время определяется случайно """
        ...