import os
import copy
import random
from libraryNPC.bases import Bases


class Character(Bases):
    """
        Базовый класс для всех NPC
    """
    chunk_size = 25
    
    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc, **kwargs):
        
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
        self.target = list()                        # Текущая цель перемещения и действия   [world_y, world_x, vertices, type, description, condition]
        self.past_target = list()                   # Предыдущая цель                       list
        self.pathfinder = 5                         # Умение искать следы                   int
        self.delete = False                         # Удаление персонажа из мира            bool
        self.live = True                            # Живой ли персонаж                     bool
        self.forced_pass = 0                        # Вынужденный пропуск                   int
        self.id = self.bases_gen_random_id(
                        kwargs["ids_list"])         # Идентификатор персонажа               int

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




