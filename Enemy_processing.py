import os
import copy
import random
import string
import keyboard
import time
import math
import pygame
import sys
import pickle
import logging
from pygame.locals import *
from map_generator import map_generator


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
    __slots__ = ('name', 'assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position', 'number_chunk',
                 'environment_temperature', 'person_temperature', 'person_pass_step', 'enemy_pass_step',
                 'speed', 'test_visible', 'level', 'vertices', 'local_position', 'direction', 'pass_draw_move', 'recalculating_the_display', 'type',
                 'icon', 'pointer_step', 'zone_relationships', 'activating_spawn', 'world_position')
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

class Interfase:
    """ Содержит элементы для последующего вывода на экран """
    def __init__(self, game_field, biom_map, minimap_on):
        self.game_field = game_field
        self.biom_map = biom_map
        self.minimap_on = minimap_on
        self.point_to_draw = [0,0]

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ПРОТИВНИКОВ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
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
        self.target = []                            # Текущая цель перемещения и действия   [world_y, world_x, vertices, type, description, condition]
        self.follow = []                            # Цель для следования или преследования [follow_character, 'type_follow', расстояние остановки:int]
        self.escape = []                            # Бегство от                            list
        self.delete = False                         # Удаление персонажа из мира            bool
        self.live = True                            # Живой ли персонаж                     bool

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
        return [local_position[0] + global_position[0]*self.chunk_size, local_position[1] + global_position[1]*self.chunk_size]

    def character_world_position_recalculation(self, world_position):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0]//self.chunk_size, world_position[1]//self.chunk_size]
        local_position = [world_position[0]%self.chunk_size, world_position[1]%self.chunk_size]
        return global_position, local_position

    def character_waypoints_move(self, activity_list, step):
    """
        Передвижение персонажа по локальным вейпоинтам
    """
    if self.local_waypoints:
        #Добавляются следы
        if random.randrange(21)//18 > 0:
            activity_list.append(Action_in_map(self.activity_map['move'][0][1], step, copy.deepcopy(self.global_position),
                                               copy.deepcopy(self.local_position), self.chunk_size, self.name_npc))
        activity_list.append(Action_in_map('faint_footprints', step, copy.deepcopy(self.global_position), copy.deepcopy(self.local_position),
                                           self.chunk_size, self.name_npc))
        self.direction_calculation()
        self.global_position = [self.local_waypoints[0][3][0], self.local_waypoints[0][3][1]]
        self.local_position = [self.local_waypoints[0][0], self.local_waypoints[0][1]]
        self.local_waypoints.pop(0)

    def character_direction_calculation(self):
    """
        Определяет направление движения персонажа
    """
    if self.global_position == [self.local_waypoints[0][3][0], self.local_waypoints[0][3][1]]:
        if self.local_position == [self.local_waypoints[0][0] - 1, self.local_waypoints[0][1]]:
            self.direction = 'down'
            self.type = 'd3'
        elif self.local_position == [self.local_waypoints[0][0] + 1, self.local_waypoints[0][1]]:
            self.direction = 'up'
            self.type = 'u3'
        elif self.local_position == [self.local_waypoints[0][0], self.local_waypoints[0][1] - 1]:
            self.direction = 'right'
            self.type = 'r3'
        elif self.local_position == [self.local_waypoints[0][0], self.local_waypoints[0][1] + 1]:
            self.direction = 'left'
            self.type = 'l3'
    elif self.global_position == [self.local_waypoints[0][3][0] - 1, self.local_waypoints[0][3][1]]:
        self.direction = 'down'
        self.type = 'd3'
    elif self.global_position == [self.local_waypoints[0][3][0] + 1, self.local_waypoints[0][3][1]]:
        self.direction = 'up'
        self.type = 'u3'
    elif self.global_position == [self.local_waypoints[0][3][0], self.local_waypoints[0][3][1] - 1]:
        self.direction = 'right'
        self.type = 'r3'
    elif self.global_position == [self.local_waypoints[0][3][0], self.local_waypoints[0][3][1] + 1]:
        self.direction = 'left'
        self.type = 'l3'

    def character_check_global_position(self):
        """
            Определение глобальной позиции
        """
        pass
    def character_check_local_position(self):
        """
            Определение локальной позиции
        """
        pass
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
        self.vertices = global_map[self.global_position[0]][self.global_position[1]].chunk[self.local_position[0]][self.local_position[1]].vertices
        
    def character_check_level(self, global_map):
        """
            Определение текущей высоты
        """
        self.level = global_map[self.global_position[0]][self.global_position[1]].chunk[self.local_position[0]][self.local_position[0]].level
        
    def character_check_all_position(self, global_map):
        """
            Определение всех нужных параметров
        """
        self.check_vertices(global_map)
        self.check_level(global_map)
        self.check_world_position()
        
    def character_reset_at_the_beginning(self):
        """
            Сброс параметров в начале хода
        """
        enemy.direction = 'center'

    class CharacterAction:
        def __init__(self, type, details):
            sefl.type = type
            self.details = details


class NPC(Character):
    """
        Умные противники, обрабатываемые в каждый момент времени
    """
    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc):
        super().__init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc)
        
        # ЖИЗНЕННЫЕ ПОКАЗАТЕЛИ:
        self.health = 100                           # Здоровье                              int
        self.hunger = 100                           # Голод                                 int
        self.thirst = 100                           # Жажда                                 int
        self.fatigue = 100                          # Усталость                             int

        # ЭКИПИРОВКА:
        self.inventory = []                         # Инвентарь                             list
        self.equipment = []                         # Экипировка                            list

        # ПОВЕДЕНИЕ:
        self.alarm = False                          # Атака, ожидание атаки.                bool
        self.stealth = False                        # Скрытность                            bool
        self.alertness = False                      # Настороженность                       bool
        self.determination = 100                    # Решительность (качество персонажа)    int

        # ОБРАБОТКА
        self.status = []                            # Список текущего состояния             list



    def npc_master_calculation(self, step, activity_list):
        """
            Обработка действий персонажа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position() #Родительский метод
        self.character_reset_at_the_beginning() #Родительский метод
        self.npc_new_step_check_status()

        # Рассчёт действий
        action = self.npc_checking_the_situation()

        # Совершение действий
        if action.type == 'move':
            self.npc_move_calculations(action)
            
        elif action.type == 'activity':
            self.npc_activity_calculations(action)
            
        elif action.type == 'attack':
            self.npc_attack_calculations(action) 

        elif action.type == 'getting_damaged':
            self.npc_getting_damaged_calculations(action)

        elif action.type == 'extra':
            self.npc_extra_action_calculations(action)

        else:
            pass

        # Рассчёт последствий
        self.npc_consequences_calculation()

    def npc_new_step_check_status(self):
        """
            Проверяет состояние персонажа на начало хода.
        """
        self.status = []
        if self.health < 50:
            self.status.append('injury')
        elif self.hunger < 50:
            self.status.append('hunger')
        elif self.thirst < 50:
            self.status.append('thirst')
        elif self.fatigue < 50:
            self.status.append('fatigue')

    def npc_checking_the_situation(self):
        """
            Проверяет обстановку для решения дальнейших действий

            Проверяет наличие опасности, наличие путевых точек, наличие неудовлетворённых потребностей.
            Возвращат тип действия, совершаемого на данном шаге.
        """

        if self.alarm:
            if 'injury' in self.status: and 100//self.determination > 0:
                # тут указание преследователя для убегания от него
                return CharacterAction('move', 'escape')
            else:
                return CharacterAction('attack', 'target')

        elif 'injury' in self.status or 'hunger' in self.status or 'thirst' in self.status or 'fatigue' in self.status:
            if self.alertness:
                return CharacterAction('activity', 'slow')
            else:
                return CharacterAction('activity', 'fast')
        else:
            return CharacterAction('move', 'details')
        
    def npc_move_calculations(self, action, activity_list, step):
        """
            Передвижение персонажа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        if self.escape:
            self.npc_escape_move()
        if self.follow:
            self.npc_follow_move()
        elif self.activity:
            self.npc_activity_move()
        elif:
            self.npc_move()
        else:
            self.npc_random_move()
        self.character_waypoints_move(activity_list, step)

    def npc_move(self):
        """ Рассчёт перемещения в конкретную точку """
        pass

    def npc_escape_move(self):
        """ Рассчёт бегства """
    
    def npc_follow_move(self):
        """ Рассчёт преследования некоторого персонажа """
        pass
    
    def npc_random_move(self):
        """ Случайное перемещение или пропуск хода """
        pass
    
    def npc_activity_move(self):
        """ Перемещение всвязи с выполнением активности """
        pass
    
    def npc_activity_calculations(self, action):
        """ Выполнение и оставление активностей на карте, связанных с удовлетворением потребностей или праздным времяпрепровожденим. """
        pass

    def npc_attack_calculations(self, action):
        """ Действия при атаке """
        pass
    
    def npc_getting_damaged_calculations(self, action):
        """ Получение повреждений """
        pass
    
    def npc_extra_action_calculations(self, action):
        """ Особенные действия NPC """
        pass
    
    def npc_consequences_calculation(self):
        """ Рассчёт последствий действий персонажа """
        pass
    

class Creature(Character):
    """
    Мелкие, необсчитываемые за кадром существа и противники

    РЕАЛИЗОВАТЬ:
    1) Изменение режима передвижения с полёта, на хождение по земле.
    2) Изменение высоты полёта птиц, их иконки и тени под ними
    """
    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map, person_description, speed, deactivation_tiles, fly):
        super().__init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc)
        
        self.fly = fly                              # Полёт                                 bool
        self.steps_to_despawn = 30                  # Шагов до удаления                     int
        self.deactivation_tiles = deactivation_tiles# Тайлы удаления                        tuple

    def master_character_calculation(self):
        """
            Обработка действий существа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position() #Родительский метод
        self.character_reset_at_the_beginning() #Родительский метод

        # Рассчёт действий
        action = self.npc_checking_the_situation()

        # Совершение действий
        if action.type == 'move':
            self.creature_move_calculations(action)
            
        elif action.type == 'activity':
            self.creature_activity_calculations(action)
            
        elif action.type == 'attack':
            self.creature_attack_calculations(action) 

        elif action.type == 'getting_damaged':
            self.creature_getting_damaged_calculations(action)

        elif action.type == 'extra':
            self.creature_extra_action_calculations(action)

        else:
            pass

        # Рассчёт последствий
        self.creature_consequences_calculation()

    def creature_move_calculations(self, action, activity_list, step):
        """
            Передвижение существа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        pass
    
    def creature_activity_calculations(self, action):
        """ Выполнение и оставление активностей на карте, связанных с удовлетворением потребностей или праздным времяпрепровожденим. """
        pass

    def creature_attack_calculations(self, action):
        """ Действия существа при атаке """
        pass
    
    def creature_getting_damaged_calculations(self, action):
        """ Получение повреждений существом """
        pass
    
    def creature_extra_action_calculations(self, action):
        """ Особенные действия существа """
        pass
    
    def creature_consequences_calculation(self):
        """ Рассчёт последствий действий существа """
        pass

    def if_deactivation_tiles(self, global_map):
        """
            Проверяет находится ли существо на тайле деактивации и выбрасывает шанс на диактивацию
        """
        if global_map[self.global_position[0]][self.global_position[1]].chunk[self.local_position[0]][self.local_position[1]].icon in self.deactivation_tiles:
            if random.randrange(20)//18 > 0:
                self.delete = True

    def in_dynamic_chunk(self, person):
        """
            Рассчитывает находится ли существо на динамическом чанке
        """
        if self.global_position in (person.assemblage_point, [person.assemblage_point[0] + 1, person.assemblage_point[1]],
                               [person.assemblage_point[0], person.assemblage_point[1] + 1],
                               [person.assemblage_point[0] + 1, person.assemblage_point[1] + 1]):
            self.steps_to_despawn = 30
        else:
            self.steps_to_despawn -= 1
        if self.steps_to_despawn <= 0:
            self.delete = True
        logging.debug(f"self.name_npc - {self.name_npc}, self.steps_to_despawn - {self.steps_to_despawn}, self.delete - {self.delete}")

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




def a_star_algorithm_move_calculation(processed_map, start_point, finish_point, global_or_local, enemy):
    """
        Рассчитывает поиск пути, алгоритмом A* на основании связей полей доступности.

        ЗАПЛАНИРОВАНО:
        Найти возможность рассчитывать весь путь без мороки с глобальными и локальными вейпоинтами, а с применением только мировых кординат.
        Возможно, сначала рассчитывая глобальный путь по вершинам, а потом обращаясь к тайлам только тех локаций, которые попали в глобальные вейпоинты.

        ТРЕБОВАНИЯ:
        При отсутствии возможного пути, выбиратся точка, имеющая наименьшую цену.
        Вместо отдельной функции выбора финальной точки, заложить выбор случайной точки в определённую сторону за ограниченное количество шагов???

        Сюда приходит:
        Обрабатываемая карта - processed_map;
        Cтартовые кординаты, содержащие вершину - start_point:[y, x, vertices];
        Финишная точка - finish_point:[y, x, vertices];
        
        
    """
    class Node_vertices:
        """Содержит узлы графа для работы с зонами доступности"""
        __slots__ = ('number', 'vertices', 'position', 'price', 'direction', 'ready')
        def __init__(self, number, vertices, position, price, direction):
            self.number = number
            self.vertices = vertices
            self.position = position
            self.price = price
            self.direction = direction #Хранит номер вершины из которой вышла
            self.ready = True #Проверена ли точка

    def path_length(start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        try:
            return math.sqrt((start_point[0] - finish_point[0])**2 + (start_point[1] - finish_point[1])**2)
        except TypeError:
            print(f"!!! TypeError start_point - {start_point} | finish_point - {finish_point}")
            return 999

    def node_connections(processed_map, graph, processed_node, finish_point, verified_position):
        """
            Определяет связи вершины и добавляет их в граф при расчёте по глобальной карте
        """
        processed_node.ready = False
        #Находим указанную зону доступности
        for vertices in processed_map[processed_node.position[0]][processed_node.position[1]].vertices:
            if vertices.number == processed_node.vertices:
                #Проверяем, есть ли у неё связи
                if vertices.connections:
                    for connect in vertices.connections:
                        if not [connect.position, connect.number] in verified_position:
                            verified_position.append([connect.position, connect.number])
                            #print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {processed_node.number} и координатами {connect.position}, {connect.number}')
                            graph.append(Node_vertices(len(graph), connect.number, connect.position, path_length(connect.position,
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
                    if calculation_map[node.position[0] + 1][node.position[1]].level == node_tile.level or node_tile.stairs or calculation_map[node.position[0] + 1][node.position[1]].stairs:
                        if not [[node.position[0] + 1, node.position[1]], node.vertices] in verified_position:
                            verified_position.append([[node.position[0] + 1, node.position[1]], node.vertices])
                            graph.append(Node_vertices(len(graph), node.vertices, [node.position[0] + 1, node.position[1]],
                                                   calculation_map[node.position[0] + 1][node.position[1]].price_move +
                                                   path_length([node.position[0] + 1, node.position[1]], finish_point), node.number))
                            #print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0] + 1, node.position[1]]}, {node.vertices}')
                                                                                           
            if node.position[0] - 1 >= 0:
                if calculation_map[node.position[0] - 1][node.position[1]].vertices == node_tile.vertices:
                    if calculation_map[node.position[0] - 1][node.position[1]].level == node_tile.level or node_tile.stairs or calculation_map[node.position[0] - 1][node.position[1]].stairs:
                        if not [[node.position[0] - 1, node.position[1]], node.vertices] in verified_position:
                            verified_position.append([[node.position[0] - 1, node.position[1]], node.vertices])
                            graph.append(Node_vertices(len(graph), node.vertices, [node.position[0] - 1, node.position[1]],
                                                   calculation_map[node.position[0] - 1][node.position[1]].price_move +
                                                   path_length([node.position[0] - 1, node.position[1]], finish_point), node.number))
                            #print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0] - 1, node.position[1]]}, {node.vertices}')
        if 0 <= node.position[1] < len(calculation_map):
            if node.position[1] + 1 < len(calculation_map):
                if calculation_map[node.position[0]][node.position[1] + 1].vertices == node_tile.vertices:
                    if calculation_map[node.position[0]][node.position[1] + 1].level == node_tile.level or node_tile.stairs or calculation_map[node.position[0]][node.position[1] + 1].stairs:
                        if not [[node.position[0], node.position[1] + 1], node.vertices] in verified_position:
                            verified_position.append([[node.position[0], node.position[1] + 1], node.vertices])
                            graph.append(Node_vertices(len(graph), node.vertices, [node.position[0], node.position[1] + 1],
                                                   calculation_map[node.position[0]][node.position[1] + 1].price_move +
                                                   path_length([node.position[0], node.position[1] + 1], finish_point), node.number))
                            #print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0], node.position[1] + 1]}, {node.vertices}')
            if node.position[1] - 1 >= 0:
                if calculation_map[node.position[0]][node.position[1] - 1].vertices == node_tile.vertices:
                    if calculation_map[node.position[0]][node.position[1] - 1].level == node_tile.level or node_tile.stairs or calculation_map[node.position[0]][node.position[1] - 1].stairs:
                        if not [[node.position[0], node.position[1] - 1], node.vertices] in verified_position:
                            verified_position.append([[node.position[0], node.position[1] - 1], node.vertices])
                            graph.append(Node_vertices(len(graph), node.vertices, [node.position[0], node.position[1] - 1],
                                                   calculation_map[node.position[0]][node.position[1] - 1].price_move +
                                                   path_length([node.position[0], node.position[1] - 1], finish_point), node.number))
                            #print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number} и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

    #Если конечная и начальная точка равны
    if global_or_local == 'local' and finish_point == start_point:
        return [finish_point], True
    
    graph = [] #Список, содержащий все вершины
    verified_position = [] #Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
    graph.append(Node_vertices(0, start_point[2], [start_point[0], start_point[1]], path_length(start_point, finish_point), 0))
    verified_position.append([[start_point[0], start_point[1]], start_point[2]])
    if global_or_local == 'global':
        node_connections(processed_map, graph, graph[0], finish_point, verified_position)
    elif global_or_local == 'local':
        node_friends_calculation(processed_map, graph, graph[0], finish_point, verified_position)
    general_loop = True #Параметр останавливающий цикл
    step_count = 0 #Шаг цикла
    number_finish_node = 0 #Хранит номер финишной точки
    reversed_waypoints = [] #Обращенный список вейпоинтов
    success = True #Передаёт информацию об успехе и не успехе
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
            logging.debug(f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* не найден. min_price == 99999 Выбрана ближайшая точка. start_point - {start_point}, finish_point - {finish_point} step_count - {step_count}")
            logging.debug(f"verified_position - {verified_position}")
            if global_or_local == 'global': #УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
                logging.debug(f"{enemy.name_npc} УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ start_point - {start_point}, finish_point - {finish_point}")
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
                logging.debug(f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* за отведённые шаги не найден. Выбрана ближайшая точка. start_point - {start_point}, finish_point - {finish_point} step_count - {step_count}")
                logging.debug(f"verified_position - {verified_position}")
                if global_or_local == 'global': #УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
                    logging.debug(f"{enemy.name_npc} УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ start_point - {start_point}, finish_point - {finish_point}")
                    enemy.target = []
                success = False
                general_loop = False
            
    check_node = graph[number_finish_node]
    #reversed_waypoints.append([check_node.position[0], check_node.position[1], check_node.vertices])
    ran_while = True
    while ran_while:
        reversed_waypoints.append([check_node.position[0], check_node.position[1], check_node.vertices])
        if check_node.direction == 0:
            ran_while = False
        #print(f"имея обрабатываемую точку под номером {check_node.number} обрабатываемой точкой становится родительская под номером {check_node.direction}, имеющая координаты {check_node.position}, {check_node.vertices}")
        check_node = graph[check_node.direction] #Предыдущая вершина объявляется проверяемой

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
        #logging.debug(test_print)
        
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
        #logging.debug(test_print)


    #print(f"{enemy.name_npc} {global_or_local} list(reversed(reversed_waypoints)) - {list(reversed(reversed_waypoints))}")
    return list(reversed(reversed_waypoints)), success

        
