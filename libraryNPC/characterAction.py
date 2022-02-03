from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
from library.decorators import trace
"""
    Логика действий персонажей
"""

class CharacterAction(Bases):
    @trace
    def action_return_action(self):
        actions_dict = {
            "campfire": {
                "name": "campfire",
                "stages": {
                    "search for a place": self._action_search_for_a_place,
                    "collect firewood": self._action_collect_firewood,
                    "arrange a fire pit": self._action_arrange_a_fire_pit,
                    "kindle campfire": self._action_kindle_campfire
                }
            }
        }
        return actions_dict

    @trace
    def action_add_task_create_campfire(self):
        """ Тестовая функция, добавляющая NPC задачу ставить походный костёр """
        target = self.memory.add_memories("action", "campfire")
        self.action_stack.add_stack_element(name="action", element=self._action_stack_router, target=target)

    @trace
    def _action_stack_router(self, **kwargs):
        """ Маршрутизатор, добавляющий этапы действия, ориентируясь на action_dict """
        action_name = self.target.name
        actions_dict = self.action_return_action()
        print(F"action_name - {action_name}, action_dict - {actions_dict}, in - {action_name in actions_dict}")
        if action_name in actions_dict:
            action = actions_dict[action_name]
            type_action = action["name"]
            stages = action["stages"]
            for stage in stages:
                target = self.memory.add_memories(type_action, stage)
                self.action_stack.add_stack_element(name=stage, element=stages[stage], target=target)
                yield False
        return True

    @trace
    def _action_func(self, **kwargs):
        pass

    @trace
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
                    locations_list.append([self.global_position[0] + number_line - 1,
                                          self.global_position[1] + number_location - 1])
        # Список локаций вокруг персонажа, на которых есть дрова собран.
        if not locations_list:
            return True
        final_tile = None
        for location_position in locations_list:
            vertices_list = global_map[location_position[0]][location_position[1]].vertices
            check_vertices = None
            for vertices in vertices_list:
                # Проверка на возможность достичь точки
                _, success = self._path_world_vertices_a_star_algorithm(kwargs["vertices_dict"], self.vertices,
                                                                        vertices.number)
                if success:
                    check_vertices = vertices.number
                    break
            if check_vertices is not None:
                print(F"check_vertices - {check_vertices}")
                target = self.memory.add_memories("target", "move", positions=[check_vertices], **kwargs)
                self.action_stack.add_stack_element(name="local_move", element=self.path_move, target=target)
                yield False
                circle = self.bases_return_circle()
                null_position = [self.world_position[0] - circle//2, self.world_position[1] - circle//2]
                dry_tiles_list = list()

                for number_line, line in enumerate(circle):
                    past_dry_tile = False
                    for number_tile, tile in enumerate(line):
                        if tile == '.':
                            check_position = (null_position[0] + number_line, null_position[1] + number_tile)
                            check_tile = self.bases_world_tile(global_map, check_position)
                            if check_tile.icon in dry:
                                dry_tiles_list.append(check_position)
                                if past_dry_tile:
                                    # Если есть предыдущий сухой тайл, то поиск окончен
                                    final_tile = check_position
                                    target = self.memory.add_memories("target", "move", positions=[final_tile],
                                                                                                            **kwargs)
                                    self.action_stack.add_stack_element(name="global_move", element=self.path_move,
                                                                                                        target=target)
                                    yield False
                                    return True
                                else:
                                    past_dry_tile = True
                            else:
                                past_dry_tile = False
        if final_tile:
            target = self.memory.add_memories("target", "move", positions=[final_tile], **kwargs)
            self.action_stack.add_stack_element(name="global_move", element=self.path_move, target=target)
            yield False
        return True

    @trace
    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в стартовую точку """
        print(F'test action "_action_collect_firewood"')
        ...

    @trace
    def _action_arrange_a_fire_pit(self, **kwargs):
        """ 3 раза ходит от дров до места установки костра. Каждый раз проводит действие над костром. """
        print(F'test action "_action_arrange_a_fire_pit"')
        ...

    @trace
    def _action_kindle_campfire(self, **kwargs):
        """ Проводит некоторое время производя действие над костром. Время определяется случайно """
        print(F'test action "_action_kindle_campfire"')
        ...