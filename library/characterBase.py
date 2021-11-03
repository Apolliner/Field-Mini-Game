import os
import copy
import random
import string
import keyboard
import time
import math
from library import gameOutput
import sys
import pickle
import logging
from library.characterPath import Path


garbage = ['░', '▒', '▓', '█', '☺']

"""
    НОВАЯ ОБРАБОТКА ПРОТИВНИКОВ

    ОПИСАНИЕ ТИПОВ КООРДИНАТ:

    Существует 4 типа координат:

    Глобальные координаты (global_position) - координаты локации глобальной карты, на которой в данный момент находится персонаж, NPC или существо.

    Динамические координаты (dynamic_position) - координаты персонажа игрока на динамическом чанке. Первичны для персонажа и используются только им.

    Локальные координаты (local_position) - местоположение персонажа, NPC или существа внутри локации.

    Мировые координаты (world_position) - рассчитываются из локальных и глобальных координат для удобства работы с координатами.

    ТРЕБУЮЩИЕСЯ NPC ПЕРСОНАЖАМ МЕХАНИКИ:
    1)Перемещение в любую доступную точку
    2)Преследование
    3)Убегание
    4)Атака ближняя и дальняя
    5)Случайное перемещение для существ
    6)Полёт
    
"""

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ТЕХНИЧЕСКИЕ КЛАССЫ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

class World:
    """ Содержит в себе описание текущего состояния игрового мира """
    def __init__(self):
        self.npc_path_calculation = False #Считал ли какой-либо NPC глобальный или локальный путь на этом шаге

class Person:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    __slots__ = ('name', 'assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position',
                 'number_chunk', 'environment_temperature', 'person_temperature', 'person_pass_step',
                 'enemy_pass_step', 'speed', 'test_visible', 'level', 'vertices', 'local_position', 'direction',
                 'pass_draw_move', 'recalculating_the_display', 'type', 'icon', 'pointer_step', 'zone_relationships',
                 'activating_spawn', 'world_position')
    def __init__(self, assemblage_point:list, dynamic:list, chunks_use_map:list, pointer:list, gun:list):
        self.name = 'person'
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chunks_use_map = chunks_use_map
        self.pointer = pointer
        self.gun = gun
        self.global_position = assemblage_point
        self.number_chunk = 0
        self.environment_temperature = 36.6
        self.person_temperature = 36.6
        self.person_pass_step = 0
        self.enemy_pass_step = 0
        self.speed = 1
        self.test_visible = False
        self.level = 0
        self.vertices = 0
        self.local_position = dynamic
        self.direction = 'center'
        self.pass_draw_move = 0
        self.recalculating_the_display = True #Перессчёт игрового экрана
        self.type = '0'
        self.icon = '☺'
        self.pointer_step = False
        self.zone_relationships = []
        self.activating_spawn = False
        self.world_position = [0, 0] #общемировое тайловое положение

    def world_position_calculate(self, chunk_size):
        """ Рассчитывает глобальные координаты от центра мира """
        self.world_position = [self.local_position[0] + (self.global_position[0])*(chunk_size),
                               self.local_position[1] + (self.global_position[1])*(chunk_size)]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["assemblage_point"] = self.assemblage_point
        state["dynamic"] = self.dynamic
        state["chunks_use_map"] = self.chunks_use_map
        state["pointer"] = self.pointer
        state["gun"] = self.gun
        state["global_position"] = self.global_position
        state["number_chunk"] = self.number_chunk
        state["environment_temperature"] = self.environment_temperature
        state["person_temperature"] = self.person_temperature
        state["person_pass_step"] = self.person_pass_step
        state["enemy_pass_step"] = self.enemy_pass_step
        state["speed"] = self.speed
        state["test_visible"] = self.test_visible
        state["level"] = self.level
        state["vertices"] = self.vertices
        state["local_position"] = self.local_position
        state["direction"] = self.direction
        state["pass_draw_move"] = self.pass_draw_move
        state["recalculating_the_display"] = self.recalculating_the_display
        state["type"] = self.type
        state["icon"] = self.icon
        state["pointer_step"] = self.pointer_step
        state["zone_relationships"] = self.zone_relationships
        state["activating_spawn"] = self.activating_spawn
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.assemblage_point = state["assemblage_point"]
        self.dynamic = state["dynamic"]
        self.chunks_use_map = state["chunks_use_map"]
        self.pointer = state["pointer"]
        self.gun = state["gun"]
        self.global_position = state["global_position"]
        self.number_chunk = state["number_chunk"]
        self.environment_temperature = state["environment_temperature"]
        self.person_temperature = state["person_temperature"]
        self.person_pass_step = state["person_pass_step"]
        self.enemy_pass_step = state["enemy_pass_step"]
        self.speed = state["speed"]
        self.test_visible = state["test_visible"]
        self.level = state["level"]
        self.vertices = state["vertices"]
        self.local_position = state["local_position"]
        self.direction = state["direction"]
        self.pass_draw_move = state["pass_draw_move"]
        self.recalculating_the_display = state["recalculating_the_display"]
        self.type = state["type"]
        self.icon = state["icon"]
        self.pointer_step = state["pointer_step"]
        self.zone_relationships = state["zone_relationships"]
        self.activating_spawn = state["activating_spawn"]

    def check_local_position(self):
        local_position = []
        if self.dynamic[0] > len(self.chunks_use_map)//2 - 1:
            local_position.append(self.dynamic[0] - len(self.chunks_use_map)//2)
        else:
            local_position.append(self.dynamic[0])
            
        if self.dynamic[1] > len(self.chunks_use_map)//2 - 1:
            local_position.append(self.dynamic[1] - len(self.chunks_use_map)//2)
        else:
            local_position.append(self.dynamic[1])
        self.local_position = local_position
        
    def global_position_calculation(self, chank_size):
        """
            Рассчитывает глобальное положение по положению динамического чанка и положению внутри его
            Выдаёт глобальные координаты и номер чанка, в котором сейчас находится игрок
            Номера чанков выглядят так: 0 1
                                        2 3
        """
        
        if self.dynamic[0] < chank_size > self.dynamic[1]:  
            self.global_position = self.assemblage_point    
            self.number_chunk = 0
        elif self.dynamic[0] < chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0], self.assemblage_point[1] + 1]
            self.number_chunk = 1
        elif self.dynamic[0] >= chank_size > self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1]]
            self.number_chunk = 2
        elif self.dynamic[0] >= chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1] + 1]
            self.number_chunk = 3

class Action_in_map:
    """ Содержит в себе описание активности и срок её жизни """
    __slots__ = ('name', 'icon', 'description', 'lifetime', 'birth', 'global_position', 'local_position', 'caused',
                 'lifetime_description', 'visible', 'type', 'level')

    def __init__(self, name, birth, position_npc, local_position, chunk_size, caused):
        self.name = name
        self.icon = self.action_dict(0)
        self.lifetime = self.action_dict(2)
        self.birth = birth
        self.global_position = copy.deepcopy(position_npc)
        self.local_position = local_position #[dynamic_position[0]%chunk_size, dynamic_position[1]%chunk_size]
        self.caused = caused
        self.lifetime_description = ''
        self.description = f'{self.action_dict(1)} похоже на {self.caused}'
        self.visible = self.action_dict(3)
        self.type = '0'
        self.level = 0

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["icon"] = self.icon
        state["lifetime"] = self.lifetime
        state["birth"] = self.birth
        state["global_position"] = self.global_position
        state["local_position"] = self.local_position
        state["global_position"] = self.global_position
        state["caused"] = self.caused
        state["lifetime_description"] = self.lifetime_description
        state["description"] = self.description
        state["visible"] = self.visible
        state["type"] = self.type
        state["level"] = self.level
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.icon = state["icon"]
        self.lifetime = state["lifetime"]
        self.birth = state["birth"]
        self.global_position = state["global_position"]
        self.local_position = state["local_position"]
        self.global_position = state["global_position"]
        self.caused = state["caused"]
        self.lifetime_description = state["lifetime_description"]
        self.description = state["description"]
        self.visible = state["visible"]
        self.type = state["type"]
        self.level = state["level"]

    def all_description(self):
        self.description = f'{self.lifetime_description} {self.action_dict(1)} похоже на {self.caused}'


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ПРОТИВНИКОВ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
class Target:
    """ Содержит описание задачи, выполняемой персонажем """
    chunk_size = 25
    def __init__(self, type, entity, position, create_step, lifetime, **kwargs):
        self.type = type
        self.entity = entity
        self.position = position
        self.create_step = create_step
        self.lifetime = lifetime
        self.kwargs = kwargs

    def get_position(self):
        """ Возвращает позицию из цели """
        if self.entity is not None and self.entity:
            return self.entity.world_position
        return self.position

    def get_vertices(self, global_map):
        """ Возвращает номер зоны доступности цели """
        if self.entity is not None:
            return self._return_vertices(self.entity.world_position, global_map)
        return self._return_vertices(self.position, global_map)

    def _return_vertices(self, world_position, global_map):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]].vertices

    @staticmethod
    def get_target():
        """ По запросу возвращает цель """  # FIXME Пока заглушка
        target_dict = {
                'move':{'type': 'move', 'entity': None, 'position': None, 'lifetime': 1000}
        }
        return Target(type=None, entity=None, position=None, create_step=None, lifetime=None)

class Character:
    """
        Базовый класс для всех NPC
    """
    chunk_size = 25
    
    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc):
        
        # ИНФОРМАЦИЯ ДЛЯ РАССЧЁТОВ И ПЕРЕМЕЩЕНИЯ:
        self.global_position = global_position      # Положение на глобальной карте         [global_y, global_x]
        self.local_position = local_position        # Положение на локальной карте          [local_y, local_x]
        self.world_position = [0, 0]                # Обобщенное положение от начала мира   [world_y, world_x]
        self.vertices = 0                           # Номер зоны доступности                int
        self.level = 0                              # Высота уровня поверхности             int
        self.global_waypoints = []                  # Список глобальных путевых точек       [[global_y, global_x, vertices], ...]
        self.local_waypoints = []                   # Список локальных путевых точек        [[local_y, local_x, vertices, [global_y, global_x]], ...]
        self.world_waypoints = []                   # Список мировых путевых точек          [[world_y, world_x, vertices], ...]

        # ТЕХНИЧЕСКИЕ ДАННЫЕ
        self.activity = []                          # Текущая активность персонажа          list
        self.target = list()                        # Текущая цель перемещения и действия   [world_y, world_x, vertices, type, description, condition]
        self.past_target = list()                   # Предыдущая цель                       list
        self.follow = []                            # Цель для следования или преследования [follow_character, 'type_follow', расстояние остановки:int]
        self.escape = []                            # Бегство от                            class
        self.investigation = []                     # Поиск следов                          class
        self.pathfinder = 5                         # Умение искать следы                   int
        self.delete = False                         # Удаление персонажа из мира            bool
        self.live = True                            # Живой ли персонаж                     bool
        self.forced_pass = 0                        # Вынужденный пропуск                   int

        # ОТОБРАЖЕНИЕ ПЕРСОНАЖА
        self.name = name                            # Название типа персонажа               str
        self.name_npc = name_npc                    # Имя конкретного персонажа             str
        self.icon = icon                            # Базовое отображение персонажа         char
        self.type = type                            # Тип отображения персонажа             char
        self.visible = True                         # Виден ли персонаж                     bool
        self.direction = 'center'                   # Направление движения персонажа        str
        self.offset = [0, 0]                        # Смещение между промежуточными кадрами [local_y, local_x]
        self.type_npc = type_npc                    # Тип поведения персонажа               str
        self.description = description              # Описание персонажа                    str

    def character_world_position_calculate(self, global_position, local_position):
        """
            Рассчитывает мировые координаты от центра мира
        """
        return [local_position[0] + global_position[0]*self.chunk_size, local_position[1] +
                                                        global_position[1]*self.chunk_size]

    def character_world_position_recalculation(self, world_position):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0]//self.chunk_size, world_position[1]//self.chunk_size]
        local_position = [world_position[0]%self.chunk_size, world_position[1]%self.chunk_size]
        return global_position, local_position

    def character_local_move(self, activity_list, step):
        """
            Передвижение персонажа по локальным вейпоинтам # FIXME УСТАРЕЛО
        """
        if self.local_waypoints:
            #Добавляются следы
            if random.randrange(21)//18 > 0:
                activity_list.append(Action_in_map(self.activity_map['move'][0][1], step,
                                copy.deepcopy(self.global_position), copy.deepcopy(self.local_position),
                                self.chunk_size, self.name_npc))
            activity_list.append(Action_in_map('faint_footprints', step, copy.deepcopy(self.global_position),
                                            copy.deepcopy(self.local_position), self.chunk_size, self.name_npc))
            self.direction_calculation()
            self.global_position = [self.local_waypoints[0][3][0], self.local_waypoints[0][3][1]]
            self.local_position = [self.local_waypoints[0][0], self.local_waypoints[0][1]]
            self.local_waypoints.pop(0)

    def character_check_world_position(self):
        """
            Определение мировой позиции
        """
        self.world_position = [self.local_position[0] + self.global_position[0]*self.chunk_size,
                               self.local_position[1] + self.global_position[1]*self.chunk_size]
        
    def character_check_vertices(self, global_map):
        """
            Определение зоны доступности
        """
        self.vertices = global_map[self.global_position[0]][self.global_position[1]].chunk[
                                    self.local_position[0]][self.local_position[1]].vertices
        
    def character_check_level(self, global_map):
        """
            Определение текущей высоты
        """
        self.level = global_map[self.global_position[0]][self.global_position[1]].chunk[
                                    self.local_position[0]][self.local_position[0]].level
        
    def character_check_all_position(self, global_map):
        """
            Определение всех нужных параметров
        """
        self.character_check_vertices(global_map)
        self.character_check_level(global_map)
        self.character_check_world_position()
        
    def character_reset_at_the_beginning(self):
        """
            Сброс параметров в начале хода
        """
        self.direction = 'center'

class CharacterAction:
    """
        FIXME
    """
    def __init__(self, type, details):
        self.type = type
        self.details = details




