import logging
import random
import copy
import math
from library.classes import Action_in_map, Global_interact
from library.characterNPC import NPC
from library.characterBase import Target
from libraryNPC.characterMain import NewNPC

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ИГРОВЫХ СОБЫТИЙ

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


def master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, world,
                       global_interaction, vertices_graph, verices_dict):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    interaction_processing(global_map, interaction, enemy_list, step, chunk_size, activity_list, global_interaction)
    activity_list_check(activity_list, step)
    master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction,
                           world, vertices_graph, verices_dict)
    global_interaction_processing(global_map, enemy_list, step, chunk_size, activity_list, global_interaction, person)


def interaction_processing(global_map, interaction, enemy_list, step, chunk_size, activity_list, global_interaction):
    """
        Обрабатывает взаимодействие игрока с миром
    """
    if interaction:
        for interact in interaction:
            if interact[0] == 'task_point_all_enemies':

                for enemy in enemy_list:
                    if hasattr(enemy, 'memory'):  # FIXME Если это новый тип NPC
                        enemy.target = Target(type='move', entity=None, position=interact[2],
                                                                create_step=step, lifetime=1000)
                    else:
                        enemy.target = interact[1]
                        enemy.follow = []
                        enemy.waypoints = []
                        enemy.local_waypoints = []
                        logging.debug(f"{step}: {enemy.name_npc} получил задачу {enemy.target}")

            if interact[0] == 'follow_me_all_enemies':
                for enemy in enemy_list:
                    if hasattr(enemy, 'memory') and enemy is not interact[1][0]:  # FIXME Если это новый тип NPC и цель не на самого себя
                        enemy.follow = interact[1][0]
                    #else:
                    #    enemy.target = []
                    #    enemy.follow = interact[1]
                    #    enemy.waypoints = []
                    #    enemy.local_waypoints = []
                    #    logging.debug(f"{step}: {enemy.name_npc} назначено следование {enemy.follow}")

            if interact[0] == 'escape_me_all_enemies':
                for enemy in enemy_list:
                    if hasattr(enemy, 'memory'):  # FIXME Если это новый тип NPC
                        enemy.escape = interact[1][0]
                        #print("Назначен побег")


            if interact[0] == 'view_waypoints':
                for enemy in enemy_list:
                    if enemy.local_waypoints:
                        for waypoint in enemy.local_waypoints:  # [local_y, local_x, vertices, [global_y, global_x]]
                            activity_list.append(
                                Action_in_map('waypoint', step, waypoint[3], [waypoint[0], waypoint[1]],
                                              chunk_size, enemy.name_npc, enemy))
            if interact[0] == 'add_global_interaction':
                if interact[1] == 'explosion':
                    global_interaction.append(Global_interact('explosion', 'взрыв', interact[2], interact[3]))
    interaction = []


def activity_list_check(activity_list, step):
    """
        Проверяет активности на истечение времени
    """
    for activity in activity_list:
        activity.lifetime_description_calculation(step)
        activity.all_description()
        if step - activity.lifetime > activity.birth:
            activity_list.remove(activity)


def global_interaction_processing(global_map, enemy_list, step, chunk_size, activity_list, global_interaction, person):
    """
        Обработка глобальных событий

        Глобальные события могут длиться несколько шагов.
    """
    if global_interaction:
        for number_interact, interact in enumerate(global_interaction):
            if interact.name == 'explosion':
                explosion_calculation(interact, activity_list, step, chunk_size, global_map, person)
                if interact.step == 5:
                    global_interaction.pop(number_interact)


def explosion_calculation(explosion, activity_list, step, chunk_size, global_map, person):
    """
        Обработка взрыва
    """
    if explosion.step == 0:
        explosion_draw = [
            '0e0',
            'eee',
            '0e0',
        ]

    elif explosion.step == 1:
        explosion_draw = [
            '00e00',
            '0eee0',
            'eeeee',
            '0eee0',
            '00e00',
        ]
    elif explosion.step == 2:
        explosion_draw = [
            '000e000',
            '00eee00',
            '0eeeee0',
            'eeedeee',
            '0eeeee0',
            '00eee00',
            '000e000',
        ]
    elif explosion.step == 3:
        explosion_draw = [
            '000e000',
            '00eee00',
            '0eedee0',
            'eed0dee',
            '0eedee0',
            '00eee00',
            '000e000',
        ]
        destruction_draw = [
            '.D.',
            'CUA',
            '.B.',
        ]
        destruction_map = global_map[explosion.global_position[0]][explosion.global_position[1]].chunk
        for number_line, line in enumerate(destruction_draw):
            for number_tile, tile in enumerate(line):
                local_position = [explosion.local_position[0] - len(destruction_draw) // 2 + number_line,
                                  explosion.local_position[1] - len(destruction_draw) // 2 + number_tile]
                if tile != '.' and local_position[0] < chunk_size - 1 and local_position[1] < chunk_size - 1:
                    destruction_map[local_position[0]][local_position[1]].icon = 'C'
                    destruction_map[local_position[0]][local_position[1]].type = tile
                    destruction_map[local_position[0]][local_position[1]].level -= 1
    elif explosion.step == 4:
        explosion_draw = [
            '000e000',
            '00ede00',
            '0ed0de0',
            'ed000de',
            '0ed0de0',
            '00ede00',
            '000e000',
        ]
    elif explosion.step == 5:
        explosion_draw = [
            '000d000',
            '00d0d00',
            '0d000d0',
            'd00000d',
            '0d000d0',
            '00d0d00',
            '000d000',
        ]
    else:
        explosion_draw = [
            '0',
        ]

    for number_line, line in enumerate(explosion_draw):
        for number_tile, tile in enumerate(line):
            local_position = [explosion.local_position[0] - len(explosion_draw) // 2 + number_line,
                              explosion.local_position[1] - len(explosion_draw) // 2 + number_tile]
            if tile == 'e':
                activity_list.append(
                    Action_in_map('explosion', step, explosion.global_position, local_position, chunk_size, 'динамит',
                                  person))

            elif tile == 'd':
                activity_list.append(Action_in_map('dust', step, explosion.global_position, local_position, chunk_size,
                                                   'последствия взрыва', person))

    explosion.step += 1


def destruction_calculation(interact):
    """
        Обработка обрушений и разрушений
    """
    pass


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА NPC

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


class Creature:
    """
    Мелкие, необсчитываемые за кадром существа и противники

    РЕАЛИЗОВАТЬ:
    1) Изменение режима передвижения с полёта, на хождение по земле.
    2) Изменение высоты полёта птиц, их иконки и тени под ними
    """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map, person_description,
                 speed, deactivation_tiles, fly):
        self.global_position = global_position
        self.local_position = local_position
        self.waypoints = []  # На будущее
        self.local_waypoints = []  # На будущее
        self.name = name
        self.name_npc = name_npc
        self.icon = icon
        self.type = type
        self.activity_map = activity_map
        self.person_description = person_description
        self.description = ''
        self.alarm = False
        self.delete = False
        self.direction = 'center'
        self.visible = True
        self.fly = fly
        self.steps_to_despawn = 30
        self.deactivation_tiles = deactivation_tiles
        self.follow = []
        self.world_position = [0, 0]

    def world_position_calculate(self, chunk_size):
        """ Рассчитывает глобальные координаты от центра мира """
        self.world_position = [self.local_position[0] + self.global_position[0] * chunk_size,
                               self.local_position[1] + self.global_position[1] * chunk_size]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["global_position"] = self.global_position
        state["local_position"] = self.local_position
        state["waypoints"] = self.waypoints
        state["local_waypoints"] = self.local_waypoints
        state["name"] = self.name
        state["name_npc"] = self.name_npc
        state["icon"] = self.icon
        state["type"] = self.type
        state["activity_map"] = self.activity_map
        state["description"] = self.description
        state["person_description"] = self.person_description
        state["alarm"] = self.alarm
        state["delete"] = self.delete
        state["direction"] = self.direction
        state["visible"] = self.visible
        state["fly"] = self.fly
        state["steps_to_despawn"] = self.steps_to_despawn
        state["deactivation_tiles"] = self.deactivation_tiles
        state["follow"] = self.follow
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.global_position = state["global_position"]
        self.local_position = state["local_position"]
        self.waypoints = state["waypoints"]
        self.local_waypoints = state["local_waypoints"]
        self.name = state["name"]
        self.name_npc = state["name_npc"]
        self.icon = state["icon"]
        self.type = state["type"]
        self.activity_map = state["activity_map"]
        self.description = state["description"]
        self.person_description = state["person_description"]
        self.alarm = state["alarm"]
        self.delete = state["delete"]
        self.direction = state["direction"]
        self.visible = state["visible"]
        self.fly = state["fly"]
        self.steps_to_despawn = state["steps_to_despawn"]
        self.deactivation_tiles = state["deactivation_tiles"]
        self.follow = state["follow"]

    def all_description_calculation(self):
        self.description = f"{self.person_description} {self.name_npc}"

    def if_deactivation_tiles(self, global_map):
        """
            Проверяет находится ли существо на тайле деактивации и выбрасывает шанс на диактивацию
        """
        if global_map[self.global_position[0]][self.global_position[1]].chunk[self.local_position[0]][
            self.local_position[1]].icon in self.deactivation_tiles:
            if random.randrange(20) // 18 > 0:
                self.delete = True

    def in_dynamic_chunk(self, person):
        """
            Рассчитывает находится ли существо на динамическом чанке
        """
        if self.global_position in (
        person.assemblage_point, [person.assemblage_point[0] + 1, person.assemblage_point[1]],
        [person.assemblage_point[0], person.assemblage_point[1] + 1],
        [person.assemblage_point[0] + 1, person.assemblage_point[1] + 1]):
            self.steps_to_despawn = 30
        else:
            self.steps_to_despawn -= 1
        if self.steps_to_despawn <= 0:
            self.delete = True
        logging.debug(
            f"self.name_npc - {self.name_npc}, self.steps_to_despawn - {self.steps_to_despawn}, self.delete - {self.delete}")

    def simple_move(self, chunk_size, global_map):
        """
            Хаотичное рандомное движение с учётом препятствий
        """
        global_position_y = self.global_position[0]
        global_position_x = self.global_position[1]
        tile = global_map[global_position_y][global_position_x].chunk[self.local_position[0]][self.local_position[1]]
        if random.randrange(2) == 0:
            axis_y = random.randrange(-1, 2)
            axis_x = 0
        else:
            axis_y = 0
            axis_x = random.randrange(-1, 2)
        local_position_y = self.local_position[0] + axis_y
        if local_position_y > chunk_size - 1:
            global_position_y += 1
            local_position_y = 0
        elif local_position_y < 0:
            global_position_y -= 1
            local_position_y = chunk_size - 1

        local_position_x = self.local_position[1] + axis_x
        if local_position_x > chunk_size - 1:
            global_position_x += 1
            local_position_x = 0
        elif local_position_x < 0:
            global_position_x -= 1
            local_position_x = chunk_size - 1

        if 0 > global_position_y < chunk_size - 1:
            global_position_y = 0
            self.delete = True
        if 0 > global_position_x < chunk_size - 1:
            global_position_x = 0
            self.delete = True

        go_tile = global_map[global_position_y][global_position_x].chunk[local_position_y][local_position_x]

        if (tile.level == go_tile.level or tile.stairs or go_tile.stairs) and not go_tile.icon in ('~', '▲'):
            if axis_y == -1:
                self.direction = 'up'
            elif axis_y == 1:
                self.direction = 'down'
            elif axis_x == -1:
                self.direction = 'left'
            elif axis_x == 1:
                self.direction = 'right'
            self.global_position = [global_position_y, global_position_x]
            self.local_position = [local_position_y, local_position_x]

    def fly_simple_move(self, chunk_size):
        """
            Хаотичное рандомное движение без учёта препятствий
        """
        global_position_y = self.global_position[0]
        global_position_x = self.global_position[1]
        if random.randrange(2) == 0:
            axis_y = random.randrange(-1, 2)
            axis_x = 0
        else:
            axis_y = 0
            axis_x = random.randrange(-1, 2)
        local_position_y = self.local_position[0] + axis_y
        if local_position_y > chunk_size - 1:
            global_position_y += 1
            local_position_y = 0
        elif local_position_y < 0:
            global_position_y -= 1
            local_position_y = chunk_size - 1

        local_position_x = self.local_position[1] + axis_x
        if local_position_x > chunk_size - 1:
            global_position_x += 1
            local_position_x = 0
        elif local_position_x < 0:
            global_position_x -= 1
            local_position_x = chunk_size - 1

        if 0 > global_position_y < chunk_size - 1:
            global_position_y = 0
            self.delete = True
        if 0 > global_position_x < chunk_size - 1:
            global_position_x = 0
            self.delete = True

        if axis_y == -1:
            self.direction = 'up'
        elif axis_y == 1:
            self.direction = 'down'
        elif axis_x == -1:
            self.direction = 'left'
        elif axis_x == 1:
            self.direction = 'right'

        self.global_position = [global_position_y, global_position_x]
        self.local_position = [local_position_y, local_position_x]


def return_creature(global_position, local_position, key):
    """
        Возвращает NPC указанного типа в указанных координатах
    """
    npc_dict = {
        'snake': Creature(global_position, local_position,
                          'Snake',
                          random.choice(['гадюка', 'уж']),
                          'Sn',
                          '0',
                          {
                              'move': [['передвигается', 'animal_rest_stop', 0, 0]],
                              'hunger': [['ест', 'animal_rest_stop', 40, 5]],
                              'thirst': [['пьёт', 'animal_rest_stop', 80, 3]],
                              'fatigue': [['отдыхает', 'animal_rest_stop', 30, 10]],
                              'other': [['осматривается', 'animal_rest_stop', 0, 5]],
                          },
                          "Змея, похоже что",
                          1,
                          ('o',),
                          False),  # fly
        'rattlesnake': Creature(global_position, local_position,
                                'Rattlesnake',
                                random.choice(['гремучая змея']),
                                'Rs',
                                '0',
                                {
                                    'move': [['передвигается', 'animal_rest_stop', 0, 0]],
                                    'hunger': [['ест', 'animal_rest_stop', 40, 5]],
                                    'thirst': [['пьёт', 'animal_rest_stop', 80, 3]],
                                    'fatigue': [['отдыхает', 'animal_rest_stop', 30, 10]],
                                    'other': [['осматривается', 'animal_rest_stop', 0, 5]],
                                },
                                "Осторожно! ",
                                1,
                                ('o',),
                                False),  # fly
        'bird': Creature(global_position, local_position,
                         'Bird',
                         random.choice(['Птица']),
                         'Bi',
                         '0',
                         {
                             'move': [['передвигается', 'animal_rest_stop', 0, 0]],
                             'hunger': [['ест', 'animal_rest_stop', 40, 5]],
                             'thirst': [['пьёт', 'animal_rest_stop', 80, 3]],
                             'fatigue': [['отдыхает', 'animal_rest_stop', 30, 10]],
                             'other': [['осматривается', 'animal_rest_stop', 0, 5]],
                         },
                         "Гляди ка, летит ",
                         1,
                         ('F', 'P',),
                         True),  # fly
        'snake_unknown': Creature(global_position, local_position,
                                  'unknown',
                                  'Snake Неизвестный',
                                  'un',
                                  '0',
                                  {
                                      'move': [['передвигается', 'human_tracks', 0, 0]],
                                      'hunger': [['перекусывает', 'rest_stop', 40, 5]],
                                      'thirst': [['пьёт', 'human_tracks', 80, 3]],
                                      'fatigue': [['отдыхает', 'rest_stop', 30, 10]],
                                      'other': [['говорит об ошибке', 'rest_stop', 0, 10]],
                                  },
                                  "Выползающий для теста",
                                  1,
                                  ('o',),
                                  True),  # fly
    }
    if key in npc_dict:
        return npc_dict[key]
    else:
        return npc_dict['snake_unknown']


def master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction,
                           world, vertices_graph, vertices_dict):
    """
        Здесь происходят все события, связанные с NPC

        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
        self.local_waypoints = [] # [[local_y, local_x], vertices, [global_y, global_x]]
    """
    ids_list = list()  # FIXME Пока зашлушка
    step_activity_dict = dict()
    for activity in activity_list:
        world_position = world_position_calculate(activity.global_position, activity.local_position,
                        chunk_size)
        step_activity_dict[tuple(world_position)] = activity

    delete_list = []
    for number_enemy, enemy in enumerate(enemy_list):
        enemy.direction = 'center'
        #if not isinstance(enemy, NPC):
        #    enemy.all_description_calculation()
        if not enemy.delete:  # FIXME Самый новый вид NPC
            if isinstance(enemy, NewNPC):
                enemy.npc_master_calculation(step=step, activity_list=activity_list, global_map=global_map,
                                             vertices_graph=vertices_graph, vertices_dict=vertices_dict,
                                             enemy_list=enemy_list, step_activity_dict=step_activity_dict,
                                             ids_list=ids_list, chunk_size=chunk_size)
            # Если это существо
            if isinstance(enemy, Creature):
                if enemy.fly:
                    # Если может летать
                    enemy.fly_simple_move(chunk_size)
                else:
                    # Если ходит по земле
                    enemy.simple_move(chunk_size, global_map)
                enemy.in_dynamic_chunk(person)
                enemy.if_deactivation_tiles(global_map)
                if enemy.delete:
                    delete_list.append(number_enemy)
    enemy.world_position_calculate(chunk_size)
    if person.activating_spawn:
        person.activating_spawn = False
        activating_spawn_creatures(global_map, enemy_list, person)
    for number in reversed(sorted(delete_list)):
        enemy_list.pop(number)


def activating_spawn_creatures(global_map, enemy_list, person):
    """
        Активирует окружающие персонажа спавны существ
    """

    def path_length(start_point, finish_point):
        """
            Вычисляет расстояния до персонажа
        """
        return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)

    candidats_list = []
    price_list = []
    for number_line, line in enumerate(global_map[person.global_position[0]][person.global_position[1]].chunk):
        for number_tile, tile in enumerate(line):
            if tile.list_of_features:
                price = path_length([number_line, number_tile], person.local_position)
                candidats_list.append([[number_line, number_tile], price, tile.list_of_features])
                price_list.append(price)
    if candidats_list:
        final_price = min(price_list)
        for candidat in candidats_list:
            if candidat[1] == final_price:
                enemy_list.append(return_creature(person.global_position, candidat[0], random.choice(candidat[2])))


def world_position_calculate(global_position, local_position, chunk_size):
    """ Рассчитывает глобальные координаты от начала мира в координатах [0, 0] """
    return [local_position[0] + global_position[0] * chunk_size, local_position[1] + global_position[1] * chunk_size]


