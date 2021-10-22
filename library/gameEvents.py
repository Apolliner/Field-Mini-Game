import logging
import random
import copy
import math
from library.classes import Action_in_map, Global_interact
from library.characterNPC import NPC

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
    global_interaction_processing(global_map, enemy_list, step, chunk_size, activity_list, global_interaction)


def interaction_processing(global_map, interaction, enemy_list, step, chunk_size, activity_list, global_interaction):
    """
        Обрабатывает взаимодействие игрока с миром
    """
    if interaction:
        for interact in interaction:
            if interact[0] == 'task_point_all_enemies':
                for enemy in enemy_list:
                    enemy.target = interact[1]
                    enemy.follow = []
                    enemy.waypoints = []
                    enemy.local_waypoints = []
                    logging.debug(f"{step}: {enemy.name_npc} получил задачу {enemy.target}")

            if interact[0] == 'follow_me_all_enemies':
                for enemy in enemy_list:
                    if hasattr(enemy, 'memory'):  # FIXME Если это новый тип NPC
                        enemy.follow = interact[1][0]
                    else:
                        enemy.target = []
                        enemy.follow = interact[1]
                        enemy.waypoints = []
                        enemy.local_waypoints = []
                        logging.debug(f"{step}: {enemy.name_npc} назначено следование {enemy.follow}")

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
                                              chunk_size, enemy.name_npc))
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


def global_interaction_processing(global_map, enemy_list, step, chunk_size, activity_list, global_interaction):
    """
        Обработка глобальных событий

        Глобальные события могут длиться несколько шагов.
    """
    if global_interaction:
        for number_interact, interact in enumerate(global_interaction):
            if interact.name == 'explosion':
                explosion_calculation(interact, activity_list, step, chunk_size, global_map)
                if interact.step == 5:
                    global_interaction.pop(number_interact)


def explosion_calculation(explosion, activity_list, step, chunk_size, global_map):
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
                    Action_in_map('explosion', step, explosion.global_position, local_position, chunk_size, 'динамит'))
            elif tile == 'd':
                activity_list.append(Action_in_map('dust', step, explosion.global_position, local_position, chunk_size,
                                                   'последствия взрыва'))

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


class Enemy:
    """ Отвечает за всех NPC """
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map, person_description,
                 speed):
        self.global_position = global_position
        self.local_position = local_position
        self.action_points = 10
        self.dynamic_chunk = False  # УСТАРЕЛО
        self.waypoints = []
        self.local_waypoints = []  # [local_y, local_x, vertices, [global_y, global_x]]
        self.alarm = False
        self.pass_step = 0
        self.on_the_screen = False
        self.steps_to_new_step = 1
        self.level = 0
        self.vertices = 0
        self.target = []  # [[global_y, global_x], vertices, [local_y, local_x]]
        self.visible = True
        self.direction = 'center'
        self.offset = [0, 0]
        self.delete = False
        self.follow = []
        self.world_position = [0, 0]

        self.name = name
        self.name_npc = name_npc
        self.icon = icon
        self.type = type
        self.activity_map = activity_map
        self.person_description = person_description
        self.speed = speed
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 10
        self.type_npc = 'hunter'
        self.pass_description = ''
        self.description = ''

    def world_position_calculate(self, chunk_size):
        """ Рассчитывает глобальные координаты от центра мира """
        self.world_position = [self.local_position[0] + self.global_position[0] * chunk_size,
                               self.local_position[1] + self.global_position[1] * chunk_size]

    def all_description_calculation(self):
        self.description = f"{self.person_description} {self.name_npc}"

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["global_position"] = self.global_position
        state["local_position"] = self.local_position
        state["action_points"] = self.action_points
        state["dynamic_chunk"] = self.dynamic_chunk
        state["waypoints"] = self.waypoints
        state["local_waypoints"] = self.local_waypoints
        state["alarm"] = self.alarm
        state["pass_step"] = self.pass_step
        state["on_the_screen"] = self.on_the_screen
        state["steps_to_new_step"] = self.steps_to_new_step
        state["type"] = self.type
        state["level"] = self.level
        state["vertices"] = self.vertices
        state["target"] = self.target
        state["visible"] = self.visible
        state["direction"] = self.direction
        state["offset"] = self.offset
        state["name"] = self.name
        state["name_npc"] = self.name_npc
        state["icon"] = self.icon
        state["activity_map"] = self.activity_map
        state["hunger"] = self.hunger
        state["thirst"] = self.thirst
        state["fatigue"] = self.fatigue
        state["reserves"] = self.reserves
        state["type_npc"] = self.type_npc
        state["type"] = self.type
        state["pass_description"] = self.pass_description
        state["person_description"] = self.person_description
        state["description"] = self.description
        state["speed"] = self.speed
        state["delete"] = self.delete
        state["follow"] = self.follow
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.global_position = state["global_position"]
        self.local_position = state["local_position"]
        self.action_points = state["action_points"]
        self.dynamic_chunk = state["dynamic_chunk"]
        self.waypoints = state["waypoints"]
        self.local_waypoints = state["local_waypoints"]
        self.alarm = state["alarm"]
        self.pass_step = state["pass_step"]
        self.on_the_screen = state["on_the_screen"]
        self.steps_to_new_step = state["steps_to_new_step"]
        self.type = state["type"]
        self.level = state["level"]
        self.vertices = state["vertices"]
        self.target = state["target"]
        self.visible = state["visible"]
        self.direction = state["direction"]
        self.offset = state["offset"]
        self.name = state["name"]
        self.name_npc = state["name_npc"]
        self.icon = state["icon"]
        self.activity_map = state["activity_map"]
        self.hunger = state["hunger"]
        self.thirst = state["thirst"]
        self.fatigue = state["fatigue"]
        self.reserves = state["reserves"]
        self.type_npc = state["type_npc"]
        self.type = state["type"]
        self.pass_description = state["pass_description"]
        self.person_description = state["person_description"]
        self.description = state["description"]
        self.speed = state["speed"]
        self.delete = state["delete"]
        self.follow = state["follow"]


def return_npc(global_position, local_position, key):
    """
        Возвращает NPC указанного типа в указанных координатах
    """
    npc_dict = {
        'horseman': Enemy(global_position, local_position,
                          'horseman',
                          random.choice(
                              ['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок']),
                          '☻',
                          'h',
                          {
                              'move': [['передвигается', 'horse_tracks', 0, 0]],
                              'hunger': [['перекусывает', 'rest_stop', 40, 5], ['готовит еду', 'bonfire', 80, 10]],
                              'thirst': [['пьёт', 'horse_tracks', 80, 3]],
                              'fatigue': [['отдыхает', 'rest_stop', 30, 10], ['разбил лагерь', 'camp', 80, 20]],
                              'other': [['кормит лошадь', 'horse_tracks', 0, 5], ['чистит оружие', 'rest_stop', 0, 10]],
                          },
                          "Знаменитый охотник за головами",
                          2),
        'riffleman': Enemy(global_position, local_position,
                           'riffleman',
                           random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт']),
                           '☻',
                           'd0',
                           {
                               'move': [['передвигается', 'human_tracks', 0, 0]],
                               'hunger': [['перекусывает', 'rest_stop', 40, 5], ['готовит еду', 'bonfire', 80, 10]],
                               'thirst': [['пьёт', 'human_tracks', 80, 3]],
                               'fatigue': [['отдыхает', 'rest_stop', 30, 10], ['разбил лагерь', 'camp', 80, 20]],
                               'other': [['чистит оружие', 'rest_stop', 0, 10]],
                           },
                           "Шериф одного мрачного города",
                           1),
        'coyot': Enemy(global_position, local_position,
                       'coyot',
                       random.choice(['плешивый койот', 'молодой койот', 'подраный койот']),
                       'co',
                       '0',
                       {
                           'move': [['передвигается', 'animal_traces', 0, 0]],
                           'hunger': [['охотится', 'gnawed bones', 80, 15], ['ест', 'animal_traces', 30, 10]],
                           'thirst': [['пьёт', 'animal_traces', 80, 5]],
                           'fatigue': [['отдыхает', 'animal_rest_stop', 80, 15]],
                           'other': [['чешется', 'animal_traces', 0, 0]],
                       },
                       "Голодный и злой",
                       1),
        'horse': Enemy(global_position, local_position,
                       'horse',
                       random.choice(
                           ['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь']),
                       'ho',
                       '0',
                       {
                           'move': [['передвигается', 'horse_tracks', 0, 0]],
                           'hunger': [['ест траву', 'horse_tracks', 80, 5]],
                           'thirst': [['пьёт', 'horse_tracks', 80, 5]],
                           'fatigue': [['отдыхает', 'animal_rest_stop', 80, 20]],
                           'other': [['пугатся и убегает', 'horse_tracks', 0, 0]],
                       },
                       "",
                       2),
        'unknown': Enemy(global_position, local_position,
                         'unknown',
                         'Неизвестный',
                         'un',
                         '0',
                         {
                             'move': [['передвигается', 'human_tracks', 0, 0]],
                             'hunger': [['перекусывает', 'rest_stop', 40, 5]],
                             'thirst': [['пьёт', 'human_tracks', 80, 3]],
                             'fatigue': [['отдыхает', 'rest_stop', 30, 10]],
                             'other': [['говорит об ошибке', 'rest_stop', 0, 10]],
                         },
                         "Демонстрирующий тест или ошибку",
                         3),
    }
    if key in npc_dict:
        return npc_dict[key]
    else:
        return npc_dict['unknown']


def master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction,
                           world, vertices_graph, verices_dict):
    """
        Здесь происходят все события, связанные с NPC

        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
        self.local_waypoints = [] # [[local_y, local_x], vertices, [global_y, global_x]]
    """
    delete_list = []
    for number_enemy, enemy in enumerate(enemy_list):
        enemy.direction = 'center'
        if not isinstance(enemy, NPC):
            enemy.all_description_calculation()
        if not enemy.delete:
            # Если это новый тип противника
            if isinstance(enemy, NPC):
                enemy.npc_master_calculation(step, activity_list, global_map, vertices_graph, verices_dict)
            # Если это противник
            elif isinstance(enemy, Enemy):

                enemy.level = \
                global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][
                    enemy.local_position[0]].level
                enemy.vertices = \
                global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][
                    enemy.local_position[1]].vertices

                # Удаление реализованного глобального вейпоинта
                if enemy.waypoints and [enemy.global_position[0], enemy.global_position[1], enemy.vertices] == \
                        enemy.waypoints[0]:
                    enemy.waypoints.pop(0)

                # Удаление реализованной цели
                if enemy.target and enemy.target == [enemy.global_position, enemy.vertices,
                                                     enemy.local_position] or enemy.target == [enemy.global_position,
                                                                                               enemy.vertices, []]:
                    enemy.target = []
                if enemy.follow:
                    enemy_following(enemy, global_map, chunk_size, activity_list, step)
                else:
                    if not world.npc_path_calculation:  # Если никто не считал вейпоинты на этом шаге

                        # Если есть цель, но нет локальных вейпоинтов.
                        if enemy.target and not (enemy.local_waypoints):
                            enemy_move_calculaton(global_map, enemy, step)
                            world.npc_path_calculation = True
                        # Если цели нет и нет локальных вейпоинтов
                        if not enemy.target and not enemy.local_waypoints:
                            for vertices in global_map[enemy.global_position[0]][enemy.global_position[1]].vertices:
                                if vertices.number == enemy.vertices:
                                    if vertices.connections:
                                        # Определяем позицию искомого тайла, путём выбора из точек перехода искомой зоны доступности
                                        number_target = random.randrange(len(vertices.connections))
                                        target_tiles = []
                                        for target_vertices in \
                                        global_map[vertices.connections[number_target].position[0]][
                                            vertices.connections[number_target].position[1]].vertices:
                                            if target_vertices == vertices.connections[number_target].number:
                                                for connect in target_vertices.connections:
                                                    if connect.number == vertices.number:
                                                        target_tiles = random.choice(connect.tiles)
                                        # Задаётся цель из существующих координат, существующих связей и существующих тайлов
                                        enemy.target = [vertices.connections[number_target].position,
                                                        vertices.connections[number_target].number, target_tiles]
                        # Если есть количество глобальных вейпоинтов больше 1 и истекают локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
                        if len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 5:
                            enemy_move_calculaton(global_map, enemy, step)
                            world.npc_path_calculation = True
                    # Если есть локальные вейпоинты
                    if enemy.local_waypoints:
                        # Добавляются следы
                        if random.randrange(21) // 18 > 0:
                            if not global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[
                                       enemy.local_position[0]][enemy.local_position[1]].icon in ('f', '~'):
                                activity_list.append(Action_in_map(enemy.activity_map['move'][0][1], step,
                                                                   copy.deepcopy(enemy.global_position),
                                                                   copy.deepcopy(enemy.local_position), chunk_size,
                                                                   enemy.name_npc))
                        activity_list.append(
                            Action_in_map('faint_footprints', step, copy.deepcopy(enemy.global_position),
                                          copy.deepcopy(enemy.local_position),
                                          chunk_size, enemy.name_npc))
                        enemy_direction_calculation(enemy)
                        enemy.global_position = enemy.local_waypoints[0][3]
                        enemy.local_position = [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1]]
                        enemy.local_waypoints.pop(0)

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


def enemy_following(character, global_map, chunk_size, activity_list, step):
    """
        Рассчитывает движение существа или NPC к персонажу или другому персонажу или NPC

        sefl.follow содержит словарь с описанием того за кем и как следовать. В частности подходить вплотную или на определённое расстояние.

        self.follow = [[character, 'attack', 5], [атакуемое существо, тип взаимодействия, расстояние для рассчёта]]
    """

    def path_length(start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша
        """
        try:
            return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)
        except TypeError:
            print(f"!!! TypeError start_point - {start_point} | finish_point - {finish_point}")
            return 999

    logging.debug(f"{character.name_npc}: character.waypoints - {character.waypoints}")
    # Если есть глобальные вейпоинты или оба персонажа находятся на одной глобальной позиции
    if character.waypoints or character.global_position == character.follow[
        0].global_position or character.local_waypoints:
        logging.debug(
            f"{character.name_npc}: Если есть глобальные вейпоинты или оба персонажа находятся на одной глобальной позиции")
        # print(f"{character.name_npc}: character.global_position = {character.global_position}, character.follow[0].global_position - {character.follow[0].global_position}")
        if character.local_waypoints:
            # Если персонаж и преследуемый находятся на одной локации
            if character.global_position == character.follow[0].global_position:
                logging.debug(f"{character.name_npc}: Если персонаж и преследуемый находятся на одной локации")
                length = path_length(
                    world_position_calculate(character.local_waypoints[-1][3], [character.local_waypoints[-1][0],
                                                                                character.local_waypoints[-1][1]],
                                             chunk_size), character.follow[0].world_position)
                # Если преследуемый персонаж ушёл от последнего локального вейпоинта дальше чем на 3 тайла
                if length > 3:
                    logging.debug(
                        f"{character.name_npc}: Если преследуемый персонаж ушёл от последнего локального вейпоинта дальше чем на 3 тайла")
                    character.waypoints = []
                    character.local_waypoints = []
                    character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                            finish_world=character.follow[0].world_position)
                # Если преследуемый не уходил от последнего вейпоинта
                else:
                    logging.debug(f"{character.name_npc}: Если преследуемый не уходил от последнего вейпоинта")
                    length_path = path_length(character.world_position, character.follow[0].world_position)
                    if length_path >= character.follow[2]:
                        character_move(character, activity_list, step, chunk_size)
            # Если персонаж и преследуемый находятся на разных локациях
            else:
                logging.debug(f"{character.name_npc}: Если персонаж и преследуемый находятся на разных локациях")
                # Если положение последнего глобального вейпоинта равно положению преследуемого
                if character.waypoints and [character.waypoints[-1][0], character.waypoints[-1][1]] == character.follow[
                    0].global_position:
                    logging.debug(
                        f"{character.name_npc}: Если положение последнего глобального вейпоинта равно положению преследуемого")
                    character_move(character, activity_list, step, chunk_size)
                # Если преследуемый перешёл на другую локацию
                else:
                    logging.debug(f"{character.name_npc}: Если преследуемый перешёл на другую локацию")
                    character.waypoints = []
                    character.local_waypoints = []
                    character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                            finish_world=character.follow[0].world_position)
        # Если нет локальных вейпоинтов
        else:
            logging.debug(f"{character.name_npc}: Если нет локальных вейпоинтов")
            character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                    finish_world=character.follow[0].world_position)

    else:
        logging.debug(f"{character.name_npc}: else")
        character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                finish_world=character.follow[0].world_position)


def character_move(character, activity_list, step, chunk_size):
    """
        Передвижение персонажа по локальным вейпоинтам
    """
    logging.debug(f"{character.name_npc}: запрос на движение")
    if character.local_waypoints:
        logging.debug(f"{character.name_npc}: движение")
        # Добавляются следы
        if random.randrange(21) // 18 > 0:
            activity_list.append(
                Action_in_map(character.activity_map['move'][0][1], step, copy.deepcopy(character.global_position),
                              copy.deepcopy(character.local_position), chunk_size, character.name_npc))
        activity_list.append(Action_in_map('faint_footprints', step, copy.deepcopy(character.global_position),
                                           copy.deepcopy(character.local_position),
                                           chunk_size, character.name_npc))
        enemy_direction_calculation(character)
        character.global_position = [character.local_waypoints[0][3][0], character.local_waypoints[0][3][1]]
        character.local_position = [character.local_waypoints[0][0], character.local_waypoints[0][1]]
        character.local_waypoints.pop(0)


def character_a_star_master(character, global_map, chunk_size, finish_world, start_world=None):
    """
        Все рассчёты передвижения из одной точки в другую.
        Может получить стартовую и конечную/конечные точки в формате world_position
        Стартовая точка не обязательно является текущим положением
    """
    # Если не указана стартовая точка, то за неё принимается местоположение персонажа
    if not start_world:
        start_world = character.world_positon

    # Перессчёт из мировых координат в глобальные, локальные и определение номера вершины графа
    start_global, start_local = world_position_recalculation(start_world, chunk_size)
    start_vertices = global_map[start_global[0]][start_global[1]].chunk[start_local[0]][start_local[1]].vertices

    finish_global, finish_local = world_position_recalculation(finish_world, chunk_size)
    finish_vertices = global_map[finish_global[0]][finish_global[1]].chunk[finish_local[0]][finish_local[1]].vertices
    logging.debug(
        f"{character.name_npc}: character.global_position - {character.global_position}, finish_global - {finish_global}, start_vertices - {start_vertices}, finish_vertices - {finish_vertices}")
    # Если есть вейпоинты
    if character.waypoints:
        logging.debug(f"{character.name_npc}: Если есть вейпоинты")
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                                                       character.local_position, character.vertices, finish_local,
                                                       finish_vertices, start_global, finish_global, True)

    # Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности
    elif character.global_position != finish_global or (
            character.global_position == finish_global and start_vertices != finish_vertices):
        logging.debug(
            f"{character.name_npc}: Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности")
        # Сначала считаем глобальные вейпоинты
        vertices_enemy_a_star_move_global_calculations2(global_map, character, start_global, start_vertices,
                                                        finish_global, finish_vertices)  # Изменить функцию

        # А затем локальные
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                                                       character.local_position, character.vertices, finish_local,
                                                       finish_vertices, start_global, finish_global, True)

    # Если равны глобальные позиции и зоны доступности
    elif character.global_position == finish_global and start_vertices == finish_vertices:
        logging.debug(f"{character.name_npc}: Если равны глобальные позиции и зоны доступности")

        # Считаем только локальные вейпоинты без перехода на другую локацию
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                                                       start_local, start_vertices, finish_local, finish_vertices,
                                                       start_global, finish_global, False)


def vertices_enemy_a_star_move_global_calculations2(processed_map, enemy, start_global, start_vertices, finish_global,
                                                    finish_vertices):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по глобальной карте
    """

    start_point = [start_global[0], start_global[1], start_vertices]
    finish_point = [finish_global[0], finish_global[1], finish_vertices]

    enemy.waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point,
                                                                                finish_point, 'global', enemy)


def vertices_enemy_a_star_move_local_calculations2(global_map, enemy, start_local, start_vertices, finish_local,
                                                   finish_vertices,
                                                   start_global, finish_global, moving_between_locations):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по локальной карте

        target:[[local_y, local_x], vertices - номер зоны доступности на следующей или на этой карте в которую нужно прийти]
    """
    chunk_size = len(global_map[0][0].chunk)

    start_point = [enemy.local_position[0], enemy.local_position[1], enemy.vertices]
    global_axis = enemy.global_position

    processed_map = global_map[global_axis[0]][global_axis[1]].chunk

    finish_point = []
    if moving_between_locations:
        for vertices in global_map[global_axis[0]][global_axis[1]].vertices:
            if vertices.number == start_vertices:
                for connect in vertices.connections:
                    if connect.position == [enemy.waypoints[0][0],
                                            enemy.waypoints[0][1]] and connect.number == start_vertices:
                        finish = random.choice(connect.tiles)
                        finish_point = [finish[0], finish[1], finish_vertices]
    else:
        finish_point = [finish_local[0], finish_local[1], finish_vertices]

    if finish_point:
        raw_local_waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point,
                                                                                        finish_point, 'local', enemy)

        # В каждую путевую точку добавляется глобальная позиция этой точки
        for waypoint in raw_local_waypoints:
            if enemy.local_waypoints:
                waypoint.append(enemy.local_waypoints[-1][3])
            else:
                waypoint.append(enemy.global_position)

        logging.debug(
            f"{enemy.name_npc}: start_point - {start_point}, finish_point - {finish_point}, success - {success}")
        logging.debug(f"{enemy.name_npc}: raw_local_waypoints 0 - {raw_local_waypoints}")
        # Если найден путь до края локации
        if raw_local_waypoints[-1][0] == 0 or raw_local_waypoints[-1][0] == chunk_size - 1 or raw_local_waypoints[-1][
            1] == 0 or raw_local_waypoints[-1][1] == chunk_size - 1:
            # Добавление вейпоинта, соседнего последнему, но на другой карте и с указанием других глобальных координат
            if moving_between_locations and success:
                if [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0] - 1, global_axis[1]]:
                    raw_local_waypoints.append(
                        [len(global_map[0][0].chunk) - 1, raw_local_waypoints[-1][1], finish_vertices,
                         enemy.waypoints[0]])
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0] + 1, global_axis[1]]:
                    raw_local_waypoints.append([0, raw_local_waypoints[-1][1], finish_vertices, enemy.waypoints[0]])
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0], global_axis[1] - 1]:
                    raw_local_waypoints.append(
                        [raw_local_waypoints[-1][0], len(global_map[0][0].chunk) - 1, finish_vertices,
                         enemy.waypoints[0]])
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0], global_axis[1] + 1]:
                    raw_local_waypoints.append([raw_local_waypoints[-1][0], 0, finish_vertices, enemy.waypoints[0]])

        logging.debug(f"{enemy.name_npc}: raw_local_waypoints 1 - {raw_local_waypoints}")
        # Добавление новых вейпоинтов в конец списка
        for local_waypoint in raw_local_waypoints:
            enemy.local_waypoints.append(local_waypoint)


def world_position_recalculation(world_position, chunk_size):
    """
        Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
    """
    global_position = [world_position[0] // chunk_size, world_position[1] // chunk_size]
    local_position = [world_position[0] % chunk_size, world_position[1] % chunk_size]
    return global_position, local_position


def enemy_direction_calculation(enemy):
    """
        Определяет направление движения NPC
    """
    if enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1]]:
        if enemy.local_position == [enemy.local_waypoints[0][0] - 1, enemy.local_waypoints[0][1]]:
            enemy.direction = 'down'
            if enemy.name == 'riffleman':
                enemy.type = 'd3'
        elif enemy.local_position == [enemy.local_waypoints[0][0] + 1, enemy.local_waypoints[0][1]]:
            enemy.direction = 'up'
            if enemy.name == 'riffleman':
                enemy.type = 'u3'
        elif enemy.local_position == [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1] - 1]:
            enemy.direction = 'right'
            if enemy.name == 'riffleman':
                enemy.type = 'r3'
        elif enemy.local_position == [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1] + 1]:
            enemy.direction = 'left'
            if enemy.name == 'riffleman':
                enemy.type = 'l3'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0] - 1, enemy.local_waypoints[0][3][1]]:
        enemy.direction = 'down'
        if enemy.name == 'riffleman':
            enemy.type = 'd3'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0] + 1, enemy.local_waypoints[0][3][1]]:
        enemy.direction = 'up'
        if enemy.name == 'riffleman':
            enemy.type = 'u3'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1] - 1]:
        enemy.direction = 'right'
        if enemy.name == 'riffleman':
            enemy.type = 'r3'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1] + 1]:
        enemy.direction = 'left'
        if enemy.name == 'riffleman':
            enemy.type = 'l3'


def enemy_move_calculaton(global_map, enemy, step):
    """
        Запускается каждый раз при наличии цели и истечении динамических вейпоинтов.

        ОТЛИЧИЯ:
        Обсчитывает весь путь по каждой локальной карте, через которую проходит глобальный путь

        УСЛОВИЯ:
        1) Если глобальные позиции не совпадают, то выполняется поиск по глобальной карте, а за ним по локальной.
        2) Если глобальные позиции совпадают, но не совпадают номера зон доступности, то сначала выполняется глобальный поиск, а за ним локальный
        3) Если совпадают и глобальные позиции и номера зон доступности, то выполняется локальный поиск.
        4) Если глобальных вейпоинтов больше 1го и есть локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
    """
    # Если есть глобальные вейпоинты, но нет локальных - то считаем локальные вейпоинты
    if enemy.waypoints and not enemy.local_waypoints and [enemy.waypoints[0][0],
                                                          enemy.waypoints[0][1]] != enemy.global_position:
        logging.debug(
            f"{step}: {enemy.name_npc} есть глобальные вейпоинты, но нет локальных - считаем локальные вейпоинты. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                                      [[enemy.waypoints[0][0], enemy.waypoints[0][1]],
                                                       enemy.waypoints[0][2]], True)
    # Если глобальных вейпоинтов больше 1го и есть локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
    elif len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 3:
        logging.debug(
            f"{step}: {enemy.name_npc} глобальных вейпоинтов больше 1го и есть локальные вейпоинты, считаются локальные вейпоинты для следующей карты. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                                      [[enemy.waypoints[1][0], enemy.waypoints[1][1]],
                                                       enemy.waypoints[1][2]], True)
    # Если следующий глобальный вейпоинт равен глобальной позиции персонажа, но не равен его зоне доступности, но глобальные вейпоинты сбрасываются для перессчёта
    elif enemy.waypoints and [enemy.waypoints[0][0], enemy.waypoints[0][1]] == enemy.global_position and \
            enemy.waypoints[0][2] != enemy.vertices:
        enemy.waypoints = []
    # Если нет глобальных вейпоинтов
    else:
        logging.debug(
            f"{step}: {enemy.name_npc} нет глобальных вейпоинтов. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        # Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности
        if enemy.target[0] != enemy.global_position or (
                enemy.target[0] == enemy.global_position and enemy.target[1] != enemy.vertices):
            logging.debug(
                f"{step}: {enemy.name_npc} глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
            # Сначала считаем глобальные вейпоинты
            vertices_enemy_a_star_move_global_calculations(global_map, enemy,
                                                           [enemy.target[0][0], enemy.target[0][1], enemy.target[1]])
            # А затем локальные
            vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                                          [[enemy.waypoints[0][0], enemy.waypoints[0][1]],
                                                           enemy.waypoints[0][2]], True)
            # print(f"{enemy.name_npc} - посчитал глобальные, а затем локальные вейпоинты | {enemy.waypoints} | {enemy.dynamic_waypoints}")
        # Если равны глобальные позиции и зоны доступности
        elif enemy.target[0] == enemy.global_position and enemy.target[1] == enemy.vertices:
            logging.debug(
                f"{step}: {enemy.name_npc} глобальные позиции равны и равны зоны доступности. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
            # Считаем только локальные вейпоинты без перехода на другую локацию
            vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                                          [[enemy.target[2][0], enemy.target[2][1]], enemy.target[1]],
                                                          False)
            # print(f"{enemy.name_npc} - посчитал локальные вейпоинты без необходимости считать глобальные | {enemy.waypoints} | {enemy.dynamic_waypoints}")


def vertices_enemy_a_star_move_global_calculations(processed_map, enemy, finish_point):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по глобальной карте
    """
    try:
        start_point = [enemy.global_position[0], enemy.global_position[1], enemy.vertices]
    except TypeError:
        print(f"!!!TypeError enemy.name_npc - {enemy.name_npc}, enemy.global_position - {enemy.global_position}")
    enemy.waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point,
                                                                                finish_point, 'global', enemy)


def vertices_enemy_a_star_move_local_calculations(global_map, enemy, target, moving_between_locations):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по локальной карте

        target:[[local_y, local_x], vertices - номер зоны доступности на следующей или на этой карте в которую нужно прийти]
    """
    chunk_size = len(global_map[0][0].chunk)

    if enemy.local_waypoints:  # Если уже есть локальные вейпоинты, то стартовой точкой объявляется последний вейпоинт
        start_point = [enemy.local_waypoints[-1][0], enemy.local_waypoints[-1][1], enemy.local_waypoints[-1][2]]
        global_axis = [enemy.local_waypoints[-1][3][0], enemy.local_waypoints[-1][3][1]]
    else:  # Если локальных вейпоинтов нет, то стартовой точкой объявляется локальная позиция
        start_point = [enemy.local_position[0], enemy.local_position[1], enemy.vertices]
        global_axis = enemy.global_position

    processed_map = global_map[global_axis[0]][global_axis[1]].chunk

    finish_point = []
    if moving_between_locations:
        if target[0] != enemy.global_position:
            for vertices in global_map[global_axis[0]][global_axis[1]].vertices:
                if vertices.number == enemy.vertices:
                    for connect in vertices.connections:
                        if connect.position == target[0] and connect.number == target[1]:
                            finish = random.choice(connect.tiles)
                            finish_point = [finish[0], finish[1], vertices.number]
                            # print(F"finish_point - {finish_point} connect.tiles - {connect.tiles}")
    else:
        finish_point = [target[0][0], target[0][1], target[1]]

    if finish_point:
        raw_local_waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point,
                                                                                        finish_point, 'local', enemy)
        # В каждую путевую точку добавляется глобальная позиция этой точки
        for waypoint in raw_local_waypoints:
            if enemy.local_waypoints:
                waypoint.append(enemy.local_waypoints[-1][3])
            else:
                waypoint.append(enemy.global_position)

        # Если найден путь до края локации
        if raw_local_waypoints[-1][0] == 0 or raw_local_waypoints[-1][0] == chunk_size - 1 or raw_local_waypoints[-1][
            1] == 0 or raw_local_waypoints[-1][1] == chunk_size - 1:
            # Добавление вейпоинта, соседнего последнему, но на другой карте и с указанием других глобальных координат
            if moving_between_locations and success:
                if target[0] == [global_axis[0] - 1, global_axis[1]]:
                    raw_local_waypoints.append(
                        [len(global_map[0][0].chunk) - 1, raw_local_waypoints[-1][1], target[1], target[0]])
                elif target[0] == [global_axis[0] + 1, global_axis[1]]:
                    raw_local_waypoints.append([0, raw_local_waypoints[-1][1], target[1], target[0]])
                elif target[0] == [global_axis[0], global_axis[1] - 1]:
                    raw_local_waypoints.append(
                        [raw_local_waypoints[-1][0], len(global_map[0][0].chunk) - 1, target[1], target[0]])
                elif target[0] == [global_axis[0], global_axis[1] + 1]:
                    raw_local_waypoints.append([raw_local_waypoints[-1][0], 0, target[1], target[0]])

        # Добавление новых вейпоинтов в конец списка
        for local_waypoint in raw_local_waypoints:
            enemy.local_waypoints.append(local_waypoint)


def vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, global_or_local, enemy):
    """
        Рассчитывает поиск пути, алгоритмом A* на основании связей полей доступности.

        РЕФАКТОРИНГ:
        Объединить обработку случаев истечения количества шагов и не возможности найти дальнейший путь.

        ТРЕБОВАНИЯ:

        Работа как для приблизительной карты локаций, так и для передвижения по игровой карте. #РЕАЛИЗОВАНО
        Учёт разности высот между тайлами, а так же наличие параметра лестницы. #РЕАЛИЗОВАНО
        Возвращает готовый набор вейпоинтов. #РЕАЛИЗОВАНО
        Пара вейпоинтов содержит информацию о том, в какой зоне доступности они находятся. #РЕАЛИЗОВАНО
        Цена передвижения рассчитывается исходя из цены локации, в которой находится зона доступности. #РЕАЛИЗОВАНО
        При отсутствии возможного пути, выбиратся точка, имеющая наименьшую цену.
        При передвижении по игровой карте, расчёт ведется только на тайлах, соответствующих рассчитаной на глобальной карте зоне доступности. #РЕАЛИЗОВАНО
        Вместо отдельной функции выбора финальной точки, заложить выбор случайной точки в определённую сторону за ограниченное количество шагов???

        ОСОБЕННОСТИ:

        Не требуется проверять на проходимость, так как это проверено заранее.
        Область поисков ограничена расчитанной заранее зоной доступности.
        Точки переходов заранее известны.
        Соседние узлы графа уже известны

        Сюда приходит:
        Обрабатываемая карта - processed_map;
        Cтартовые кординаты, содержащие вершину - start_point:[y, x, vertices];
        Финишная точка - finish_point:[y, x, vertices];


        ЗАПЛАНИРОВАНО:
        1) !!! Если невозможно найти путь локальным поиском, то следующий глобальный вейпоинт объявляется непроходимым и ищется другой путь
        2) При наличии глобальных вейпоинтов, персонажи считают локальные вейпоинты для следующей локации, не доходя несколько локальных
        вейпоинтов по текущей. При этом, они проверяют, не считал ли вейпоинты на этом шаге какой-либо другой персонаж. #РЕАЛИЗОВАНО

        СПИСОК ИЗВЕСТНЫХ ОШИБОК:
        1)Неуспешный поиск пути если стартовая и конечная позиция равны #FIXED


    """

    class Node_vertices:
        """Содержит узлы графа для работы с зонами доступности"""
        __slots__ = ('number', 'vertices', 'position', 'price', 'direction', 'ready')

        def __init__(self, number, vertices, position, price, direction):
            self.number = number
            self.vertices = vertices
            self.position = position
            self.price = price
            self.direction = direction  # Хранит номер вершины из которой вышла
            self.ready = True  # Проверена ли точка

    def path_length(start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        try:
            return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)
        except TypeError:
            print(f"!!! TypeError start_point - {start_point} | finish_point - {finish_point}")
            return 999

    def node_connections(processed_map, graph, processed_node, finish_point, verified_position):
        """
            Определяет связи вершины и добавляет их в граф при расчёте по глобальной карте
        """
        processed_node.ready = False
        # Находим указанную зону доступности
        for vertices in processed_map[processed_node.position[0]][processed_node.position[1]].vertices:
            if vertices.number == processed_node.vertices:
                # Проверяем, есть ли у неё связи
                if vertices.connections:
                    for connect in vertices.connections:
                        if not [connect.position, connect.number] in verified_position:
                            verified_position.append([connect.position, connect.number])
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {processed_node.number} и координатами {connect.position}, {connect.number}')
                            graph.append(Node_vertices(len(graph), connect.number, connect.position,
                                                       path_length(connect.position,
                                                                   finish_point), processed_node.number))

    def node_friends_calculation(calculation_map, graph, node, finish_point, verified_position):
        """
            Вычисляет соседние узлы графа при расчёте по локальной карте

            То же самое, что было раньше, только с проверкой на высоту и лестницы
        """
        node.ready = False
        node_tile = calculation_map[node.position[0]][node.position[1]]
        if 0 <= node.position[0] < len(calculation_map):
            if node.position[0] + 1 < len(calculation_map):
                if calculation_map[node.position[0] + 1][node.position[1]].vertices == node_tile.vertices:
                    if calculation_map[node.position[0] + 1][
                        node.position[1]].level == node_tile.level or node_tile.stairs or \
                            calculation_map[node.position[0] + 1][node.position[1]].stairs:
                        if not [[node.position[0] + 1, node.position[1]], node.vertices] in verified_position:
                            verified_position.append([[node.position[0] + 1, node.position[1]], node.vertices])
                            graph.append(
                                Node_vertices(len(graph), node.vertices, [node.position[0] + 1, node.position[1]],
                                              calculation_map[node.position[0] + 1][node.position[1]].price_move +
                                              path_length([node.position[0] + 1, node.position[1]], finish_point),
                                              node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0] + 1, node.position[1]]}, {node.vertices}')

            if node.position[0] - 1 >= 0:
                if calculation_map[node.position[0] - 1][node.position[1]].vertices == node_tile.vertices:
                    if calculation_map[node.position[0] - 1][
                        node.position[1]].level == node_tile.level or node_tile.stairs or \
                            calculation_map[node.position[0] - 1][node.position[1]].stairs:
                        if not [[node.position[0] - 1, node.position[1]], node.vertices] in verified_position:
                            verified_position.append([[node.position[0] - 1, node.position[1]], node.vertices])
                            graph.append(
                                Node_vertices(len(graph), node.vertices, [node.position[0] - 1, node.position[1]],
                                              calculation_map[node.position[0] - 1][node.position[1]].price_move +
                                              path_length([node.position[0] - 1, node.position[1]], finish_point),
                                              node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0] - 1, node.position[1]]}, {node.vertices}')
        if 0 <= node.position[1] < len(calculation_map):
            if node.position[1] + 1 < len(calculation_map):
                if calculation_map[node.position[0]][node.position[1] + 1].vertices == node_tile.vertices:
                    if calculation_map[node.position[0]][
                        node.position[1] + 1].level == node_tile.level or node_tile.stairs or \
                            calculation_map[node.position[0]][node.position[1] + 1].stairs:
                        if not [[node.position[0], node.position[1] + 1], node.vertices] in verified_position:
                            verified_position.append([[node.position[0], node.position[1] + 1], node.vertices])
                            graph.append(
                                Node_vertices(len(graph), node.vertices, [node.position[0], node.position[1] + 1],
                                              calculation_map[node.position[0]][node.position[1] + 1].price_move +
                                              path_length([node.position[0], node.position[1] + 1], finish_point),
                                              node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0], node.position[1] + 1]}, {node.vertices}')
            if node.position[1] - 1 >= 0:
                if calculation_map[node.position[0]][node.position[1] - 1].vertices == node_tile.vertices:
                    if calculation_map[node.position[0]][
                        node.position[1] - 1].level == node_tile.level or node_tile.stairs or \
                            calculation_map[node.position[0]][node.position[1] - 1].stairs:
                        if not [[node.position[0], node.position[1] - 1], node.vertices] in verified_position:
                            verified_position.append([[node.position[0], node.position[1] - 1], node.vertices])
                            graph.append(
                                Node_vertices(len(graph), node.vertices, [node.position[0], node.position[1] - 1],
                                              calculation_map[node.position[0]][node.position[1] - 1].price_move +
                                              path_length([node.position[0], node.position[1] - 1], finish_point),
                                              node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

    # Если конечная и начальная точка равны
    if global_or_local == 'local' and finish_point == start_point:
        return [finish_point], True

    graph = []  # Список, содержащий все вершины
    verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
    graph.append(
        Node_vertices(0, start_point[2], [start_point[0], start_point[1]], path_length(start_point, finish_point), 0))
    verified_position.append([[start_point[0], start_point[1]], start_point[2]])
    if global_or_local == 'global':
        node_connections(processed_map, graph, graph[0], finish_point, verified_position)
    elif global_or_local == 'local':
        node_friends_calculation(processed_map, graph, graph[0], finish_point, verified_position)
    general_loop = True  # Параметр останавливающий цикл
    step_count = 0  # Шаг цикла
    number_finish_node = 0  # Хранит номер финишной точки
    reversed_waypoints = []  # Обращенный список вейпоинтов
    success = True  # Передаёт информацию об успехе и не успехе
    while general_loop:
        min_price = 99999
        node = graph[-1]
        for number_node in range(len(graph)):
            if graph[number_node].ready:
                if graph[number_node].price < min_price:
                    min_price = graph[number_node].price
                    node = graph[number_node]
        if min_price == 99999:
            number_finish_node = len(graph) - 1
            success = False
            general_loop = False
            logging.debug(
                f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* не найден. min_price == 99999 Выбрана ближайшая точка. start_point - {start_point}, finish_point - {finish_point} step_count - {step_count}")
            logging.debug(f"verified_position - {verified_position}")
            if global_or_local == 'global':  # УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
                logging.debug(
                    f"{enemy.name_npc} УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ start_point - {start_point}, finish_point - {finish_point}")
                enemy.target = []
        if global_or_local == 'global':
            node_connections(processed_map, graph, node, finish_point, verified_position)
        elif global_or_local == 'local':
            node_friends_calculation(processed_map, graph, node, finish_point, verified_position)
        try:
            if node.position == [finish_point[0], finish_point[1]] and node.vertices == finish_point[2]:
                number_finish_node = node.number
                general_loop = False
        except IndexError:
            logging.error(F"!!!IndexError!!! {enemy.name_npc} finish_point - {finish_point}")
        step_count += 1
        if step_count == 300:
            last_check_success = False
            for last_check in verified_position:
                if [last_check[0][0], last_check[0][1], last_check[1]] == finish_point:
                    for node in graph:
                        if node.vertices == last_check[1] and node.position == last_check[0]:
                            number_finish_node = node.number
                            last_check_success = True
                            general_loop = False
            if not last_check_success:
                min_price = 99999
                node = graph[-1]
                for number_node in range(len(graph)):
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        number_finish_node = number_node
                logging.debug(
                    f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* за отведённые шаги не найден. Выбрана ближайшая точка. start_point - {start_point}, finish_point - {finish_point} step_count - {step_count}")
                logging.debug(f"verified_position - {verified_position}")
                if global_or_local == 'global':  # УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
                    logging.debug(
                        f"{enemy.name_npc} УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ start_point - {start_point}, finish_point - {finish_point}")
                    enemy.target = []
                success = False
                general_loop = False

    check_node = graph[number_finish_node]
    # reversed_waypoints.append([check_node.position[0], check_node.position[1], check_node.vertices])
    ran_while = True
    while ran_while:
        reversed_waypoints.append([check_node.position[0], check_node.position[1], check_node.vertices])
        if check_node.direction == 0:
            ran_while = False
        # print(f"имея обрабатываемую точку под номером {check_node.number} обрабатываемой точкой становится родительская под номером {check_node.direction}, имеющая координаты {check_node.position}, {check_node.vertices}")
        check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой

    if global_or_local == 'global':
        test_print = '\n'
        test_reversed_waypoints = []
        for waypoint in reversed_waypoints:
            test_reversed_waypoints.append([waypoint[0], waypoint[1]])
        for number_line in range(len(processed_map)):
            for number_tile in range(len(processed_map[number_line])):

                if [number_line, number_tile, start_point[2]] in reversed_waypoints:
                    if processed_map[number_line][number_tile].icon == '▲':
                        test_print += "/" + "v"
                    else:
                        test_print += processed_map[number_line][number_tile].icon + 'v'
                elif [[number_line, number_tile], start_point[2]] in verified_position:
                    if processed_map[number_line][number_tile].icon == '▲':
                        test_print += "/" + "x"
                    else:
                        test_print += processed_map[number_line][number_tile].icon + 'x'
                elif processed_map[number_line][number_tile].icon == '▲':
                    test_print += "/" + " "
                else:
                    test_print += processed_map[number_line][number_tile].icon + ' '
            test_print += '\n'
        # logging.debug(test_print)

    elif global_or_local == 'local':
        test_print = '\n'
        for number_line in range(len(processed_map)):
            for number_tile in range(len(processed_map[number_line])):

                if [number_line, number_tile, start_point[2]] in reversed_waypoints:
                    if processed_map[number_line][number_tile].icon == '▲':
                        test_print += "/" + "v"
                    else:
                        test_print += processed_map[number_line][number_tile].icon + 'v'
                elif [[number_line, number_tile], start_point[2]] in verified_position:
                    if processed_map[number_line][number_tile].icon == '▲':
                        test_print += "/" + "x"
                    else:
                        test_print += processed_map[number_line][number_tile].icon + 'x'
                elif processed_map[number_line][number_tile].icon == '▲':
                    test_print += "/" + " "
                else:
                    test_print += processed_map[number_line][number_tile].icon + ' '
            test_print += '\n'
        # logging.debug(test_print)

    # print(f"{enemy.name_npc} {global_or_local} list(reversed(reversed_waypoints)) - {list(reversed(reversed_waypoints))}")
    return list(reversed(reversed_waypoints)), success

