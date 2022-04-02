from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
from library.decorators import trace, action_base_generator
from libraryNPC.characterActionBase import CharacterActionBase
import random
import copy
from library.classes import Action_in_map

"""
    Логика действий персонажей
"""

class CharacterAction(CharacterActionBase):
    @trace
    def action_return_action(self):
        actions_dict = {
            "campfire": {
                "name": "campfire",
                "stages": {
                    "search for a place": self._action_search_for_a_place,
                    "collect firewood": self._action_collect_firewood,
                },
            "test action": {
                "name": "test acion",
                "stages": {
                    "test stage": self._test_action,
                },
            },
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
        def _generator_action_stack_router():
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
                    yield self.inf
            return True
        if self.target.generator is None:
            self.target.generator = _generator_action_stack_router()
        return next(self.target.generator, True)

    @trace
    def _action_func(self, **kwargs):
        pass

    @trace
    @action_base_generator
    def _action_search_for_a_place(self, **kwargs):
        """ Ищет подходящее место для костра. Оно должно быть сухим и неподалёку должны быть дрова. """
        locations_list = list()
        firewood_set = set(firewood)
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
                self.action_base_go_position(check_vertices)
                yield self.inf
                circle = self.bases_return_circle()
                len_circle = len(circle)
                null_position = [self.world_position[0] - len_circle//2, self.world_position[1] - len_circle//2]
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
                                    yield self.inf
                                    return True
                                else:
                                    past_dry_tile = True
                            else:
                                past_dry_tile = False
        if final_tile:
            target = self.memory.add_memories("target", "move", positions=[final_tile], **kwargs)
            self.action_stack.add_stack_element(name="search_move", element=self.path_move, target=target)
            return True
        return self.nan

    @trace
    @action_base_generator
    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в стартовую точку """
        start_positions = copy.deepcopy(self.world_position)
        firewoods_tiles, firewoods_length = self.bases_search_tile_in_circle(start_positions, firewood, **kwargs)
        if not firewoods_tiles:
            return self.nan
        self.action_base_set_animation("look around", 3)
        yield self.inf
        kwargs['activity_list'].append(Action_in_map('firewood', kwargs['step'], self.global_position,
                                                                    self.local_position, self.chunk_size, '', self))
        for i in range(3):
            firewood_tile = random.choice(firewoods_tiles)
            self.action_base_go_position(firewood_tile)
            yield self.inf

            self.action_base_set_animation("stand create", 5)
            yield self.inf

            self.action_base_go_position(start_positions)
            yield self.inf

            self.action_base_set_animation("squat create", 2)
            yield self.inf
            success = self.action_base_activity_update(self.world_position, new_type=str(i + 1), lifetime=150, **kwargs)
            if not success:
                kwargs['activity_list'].append(Action_in_map('firewood', kwargs['step'], self.global_position,
                                                             self.local_position, self.chunk_size, '', self))
                _ = self.action_base_activity_update(self.world_position, new_type=str(i + 1), lifetime=150,
                                                           **kwargs)
            yield self.inf

        campfire_position = [start_positions[0], start_positions[1] + 1]
        self.action_base_go_position(campfire_position)
        yield self.inf

        self.action_base_set_animation("squat create", 5)
        yield self.inf
        _ = self.action_base_activity_update(start_positions, new_type=str(2), lifetime=150, **kwargs)
        kwargs['activity_list'].append(Action_in_map('bonfire', kwargs['step'], self.global_position,
                                                     self.local_position, self.chunk_size, '', self))
        yield self.inf

        new_position = [self.world_position[0] - 1, self.world_position[1]]
        self.action_base_go_position(new_position)
        yield self.inf

        self.action_base_set_animation("squat create", 5)
        yield self.inf

        _ = self.action_base_activity_update(start_positions, new_type=str(1), lifetime=150, **kwargs)
        _ = self.action_base_activity_update(campfire_position, new_type=str(1), lifetime=150, **kwargs)
        self.action_base_set_animation("squat create", 5)
        yield self.inf

        _ = self.action_base_activity_update(start_positions, new_type=str(0), lifetime=150, **kwargs)
        _ = self.action_base_activity_update(campfire_position, new_type=str(2), lifetime=150, **kwargs)
        self.action_base_set_animation("squat", 20)
        yield self.inf

        _ = self.action_base_activity_update(campfire_position, new_type=str(1), lifetime=150, **kwargs)
        self.action_base_set_animation("squat", 10)
        yield self.inf

        self.action_base_set_animation("squat create", 5)
        yield self.inf

        _ = self.action_base_activity_update(campfire_position, new_type=str(3), lifetime=150, **kwargs)
        return True

    @trace
    @action_base_generator
    def _test_action(self, **kwargs):
        """ Активность для помщения  места, где неоходимая активность ещё не реализвана """
        self.action_base_set_animation("look around", 3)
        yield self.inf

        self.action_base_set_animation("squat", 2)
        yield self.inf

        self.action_base_set_animation("squat create", 5)
        yield self.inf

        self.action_base_set_animation("squat", 2)
        yield self.inf
        