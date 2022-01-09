import os
import copy
import random


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
        self.global_waypoints = list()              # Список глобальных путевых точек       [[global_y, global_x, vertices], ...]
        self.local_waypoints = list()               # Список локальных путевых точек        [[local_y, local_x, vertices, [global_y, global_x]], ...]
        self.world_waypoints = list()               # Список мировых путевых точек          [[world_y, world_x, vertices], ...]

        # ТЕХНИЧЕСКИЕ ДАННЫЕ
        self.activity = list()                      # Текущая активность персонажа          list
        self.target = list()                        # Текущая цель перемещения и действия   [world_y, world_x, vertices, type, description, condition]
        self.past_target = list()                   # Предыдущая цель                       list
        self.follow = list()                        # Цель для следования или преследования [follow_character, 'type_follow', расстояние остановки:int]
        self.escape = list()                        # Бегство от                            class
        self.attack = list()                        # Атака этого персонажа                 class
        self.investigation = list()                 # Поиск следов                          class
        self.pathfinder = 5                         # Умение искать следы                   int
        self.delete = False                         # Удаление персонажа из мира            bool
        self.live = True                            # Живой ли персонаж                     bool
        self.forced_pass = 0                        # Вынужденный пропуск                   int

        # ОТОБРАЖЕНИЕ ПЕРСОНАЖА
        self.name = name                            # Название типа персонажа               str
        self.name_npc = name_npc                    # Имя конкретного персонажа             str
        self.icon = icon                            # Базовое отображение персонажа         string
        self.type = type                            # Тип отображения персонажа             string
        self.animation = ''                         # Префикс анимации                      string
        self.visible = True                         # Виден ли персонаж                     bool
        self.direction = 'center'                   # Направление движения персонажа        str
        self.old_direction = 'down'                 # Старое направление движения персонажа str
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




