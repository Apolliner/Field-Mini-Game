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
        vertices_dict = kwargs["vertices_dict"]
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
        if not locations_list:
            return True
        for location_position in locations_list:
            vertices_list = global_map[location_position[0], location_position[1]].vertices
            check_vertices = None
            for vertices in vertices_list:
                # Проверка на возможность достичь точки
                _, success = self._path_world_vertices_a_star_algorithm(kwargs["vertices_dict"], self.vertices,
                                                                        vertices.number)
                if success:
                    check_vertices = vertices.number
                    break
            if check_vertices is not None:
                target = self.memory.add_memories("target", "move", positions=[check_vertices], **kwargs)
                self.action_stack.add_stack_element(name="local_move", element=self.path_move, target=target)
                yield False
                self_tile = self.bases_world_tile(global_map, self.world_position)
                if self_tile.icon in dry:
                    return True
        return True

                


    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в стартовую точку """
        ...

    def _action_arrange_a_fire_pit(self, **kwargs):
        """ 3 раза ходит от дров до места установки костра. Каждый раз проводит действие над костром. """
        ...

    def _action_kindle_campfire(self, **kwargs):
        """ Проводит некоторое время производя действие над костром. Время определяется случайно """
        ...