from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
from library.decorators import trace
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
                    yield False
            return True
        if self.target.generator is None:
            self.target.generator = _generator_action_stack_router()
        return next(self.target.generator, True)

    @trace
    def _action_func(self, **kwargs):
        pass

    @trace
    def _action_search_for_a_place(self, **kwargs):
        """ Ищет подходящее место для костра. Оно должно быть сухим и неподалёку должны быть дрова. """
        def _generator_action_search_for_a_place():
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
                    target = self.memory.add_memories("target", "move", positions=[check_vertices], **kwargs)
                    self.action_stack.add_stack_element(name="local_move", element=self.path_move, target=target)
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
        if self.target.generator is None:
            self.target.generator = _generator_action_search_for_a_place()
        x = self.target.generator
        print(F"x - {x}")
        y = next(x, True)
        print(F"y - {y}")
        return y

    @trace
    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в стартовую точку """
        def _generator_action_collect_firewood():
            start_positions = copy.deepcopy(self.world_position)
            firewoods_tiles, firewoods_length = self.bases_search_tile_in_circle(start_positions, firewood, **kwargs)
            if not firewoods_tiles:
                return self.nan
            collected_firewood_positions = list()

            payload = {"animations": [{"name": "look around", "steps": 3}]}
            target = self.memory.add_memories("target", "move", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router, target=target)
            yield self.inf
            kwargs['activity_list'].append(Action_in_map('firewood', kwargs['step'], self.global_position,
                                                                        self.local_position, self.chunk_size, '', self))
            for i in range(3):
                firewood_tile = random.choice(firewoods_tiles)
                target = self.memory.add_memories("target", "action_move", positions=[firewood_tile], **kwargs)
                self.action_stack.add_stack_element(name="action_move", element=self.path_move, target=target)
                yield self.inf
                payload = {"animations": [{"name": "stand create", "steps": 5}]}
                target = self.memory.add_memories("target", "move", payload=payload, **kwargs)
                self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router, target=target)
                yield self.inf
                target = self.memory.add_memories("target", "action_move", positions=[start_positions], **kwargs)
                self.action_stack.add_stack_element(name="action_move", element=self.path_move, target=target)
                yield self.inf
                payload = {"animations": [{"name": "squat create", "steps": 2}]}
                target = self.memory.add_memories("target", "move", payload=payload, **kwargs)
                self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                    target=target)
                yield self.inf
                success = self.action_base_activity_update(self.world_position, new_type=str(i + 1), lifetime=150, **kwargs)
                if not success:
                    kwargs['activity_list'].append(Action_in_map('firewood', kwargs['step'], self.global_position,
                                                                 self.local_position, self.chunk_size, '', self))
                    success = self.action_base_activity_update(self.world_position, new_type=str(i + 1), lifetime=150,
                                                               **kwargs)


            # FIXME Последующее должно быть в другом месте
            campfire_position = [start_positions[0], start_positions[1] + 1]
            target = self.memory.add_memories("target", "action_move", positions=[campfire_position], **kwargs)
            self.action_stack.add_stack_element(name="action_move", element=self.path_move, target=target)
            yield self.inf
            payload = {"animations": [{"name": "squat create", "steps": 5}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            success = self.action_base_activity_update(start_positions, new_type=str(2), lifetime=150, **kwargs)
            kwargs['activity_list'].append(Action_in_map('bonfire', kwargs['step'], self.global_position,
                                                         self.local_position, self.chunk_size, '', self))
            yield self.inf
            new_position = [self.world_position[0] - 1, self.world_position[1]]
            target = self.memory.add_memories("target", "action_move", positions=[new_position], **kwargs)
            self.action_stack.add_stack_element(name="action_move", element=self.path_move, target=target)

            yield self.inf
            payload = {"animations": [{"name": "squat create", "steps": 5}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            success = self.action_base_activity_update(start_positions, new_type=str(1), lifetime=150, **kwargs)
            success = self.action_base_activity_update(campfire_position, new_type=str(1), lifetime=150, **kwargs)
            payload = {"animations": [{"name": "squat create", "steps": 5}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            success = self.action_base_activity_update(start_positions, new_type=str(0), lifetime=150, **kwargs)
            success = self.action_base_activity_update(campfire_position, new_type=str(2), lifetime=150, **kwargs)
            payload = {"animations": [{"name": "squat", "steps": 20}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            success = self.action_base_activity_update(campfire_position, new_type=str(1), lifetime=150, **kwargs)
            payload = {"animations": [{"name": "squat", "steps": 10}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            payload = {"animations": [{"name": "squat create", "steps": 5}]}
            target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
            self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                                target=target)
            yield self.inf
            success = self.action_base_activity_update(campfire_position, new_type=str(3), lifetime=150, **kwargs)
            return True
        if self.target.generator is None:
            self.target.generator = _generator_action_collect_firewood()
        return self._action_use_generator()


    def _action_use_generator(self):
        x = self.target.generator
        print(F"x - {x}")
        y = next(x, True)
        print(F"y - {y}")
        return y

    @trace
    def _action_arrange_a_fire_pit(self, **kwargs):
        """ 3 раза ходит от дров до места установки костра. Каждый раз проводит действие над костром. """
        print(F'test action "_action_arrange_a_fire_pit"')
        return True

    @trace
    def _action_kindle_campfire(self, **kwargs):
        """ Проводит некоторое время производя действие над костром. Время определяется случайно """
        print(F'test action "_action_kindle_campfire"')
        return True