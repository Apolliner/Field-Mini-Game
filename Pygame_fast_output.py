import os
import copy
import random
import string
import keyboard
import time
import math
import pygame
import sys
from pygame.locals import *
from new_generator_map_branch import test_new_map_generator as map_generator
from new_generator_map_branch import old_map_generator

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ ДЛЯ ОТРАБОТКИ ВЫВОДА В PYGAME С ПОДКЛЮЧЕНИЕМ КАК СТАРОГО ТАК И НОВОГО ГЕНЕРАТОРА


    РЕАЛИЗОВАТЬ:

    1)При смене кадра не перессчитывать весь кадр, а убирать или добавлять только крайние линии или столбцы.

    
    ТЕМАТИКА:
    Всё, что мне нравится. Персонажи как в хороший плохой злой, вяленое конское мясо и гремучие змеи!

    
"""
class World:
    """ Содержит в себе описание текущего состояния игрового мира """
    def __init__(self):
        self.npc_path_calculation = False #Считал ли какой-либо NPC глобальный или локальный путь на этом шаге



class Person:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    __slots__ = ('name', 'assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position', 'number_chunk',
                 'check_encounter_position', 'environment_temperature', 'person_temperature', 'person_pass_step', 'enemy_pass_step',
                 'speed', 'test_visible', 'level', 'vertices', 'local_position', 'direction', 'pass_draw_move', 'recalculating_the_display')
    def __init__(self, assemblage_point:list, dynamic:list, chunks_use_map:list, pointer:list, gun:list):
        self.name = 'person'
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chunks_use_map = chunks_use_map
        self.pointer = pointer
        self.gun = gun
        self.global_position = assemblage_point
        self.number_chunk = 1
        self.check_encounter_position = [[self.global_position[0] - 1, self.global_position[1] - 1], [self.global_position[0] - 1, self.global_position[1]],
                                        [self.global_position[0] - 1, self.global_position[1] + 1], [self.global_position[0], self.global_position[1] - 1],
                                        [self.global_position[0], self.global_position[1]], [self.global_position[0], self.global_position[1] + 1],
                                        [self.global_position[0] + 1, self.global_position[1] - 1], [self.global_position[0] + 1, self.global_position[1]],
                                        [self.global_position[0] + 1, self.global_position[1] + 1]]
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


    def check_local_position(self):
        local_position = []
        if self.dynamic[0] > len(self.chunks_use_map)//2:
            local_position.append(self.dynamic[0] - len(self.chunks_use_map)//2)
        else:
            local_position.append(self.dynamic[0])
            
        if self.dynamic[1] > len(self.chunks_use_map)//2:
            local_position.append(self.dynamic[1] - len(self.chunks_use_map)//2)
        else:
            local_position.append(self.dynamic[1])
        self.local_position = local_position
        
    def check_encounter(self):
        """
            Рассчитывает координаты точек проверки. их расположение: 0 1 2
                                                                     3 4 5
                                                                     6 7 8
        """
        self.check_encounter_position = [[self.global_position[0] - 1, self.global_position[1] - 1], [self.global_position[0] - 1, self.global_position[1]],
                                        [self.global_position[0] - 1, self.global_position[1] + 1], [self.global_position[0], self.global_position[1] - 1],
                                        [self.global_position[0], self.global_position[1]], [self.global_position[0], self.global_position[1] + 1],
                                        [self.global_position[0] + 1, self.global_position[1] - 1], [self.global_position[0] + 1, self.global_position[1]],
                                        [self.global_position[0] + 1, self.global_position[1] + 1]]
        
        
    def global_position_calculation(self, chank_size):
        """
            Рассчитывает глобальное положение по положению динамического чанка и положению внутри его
            Выдаёт глобальные координаты и номер чанка, в котором сейчас находится игрок
            Номера чанков выглядят так: 1 2
                                        3 4
        """
        
        if self.dynamic[0] < chank_size > self.dynamic[1]:  
            self.global_position = self.assemblage_point    
            self.number_chunk = 1
        elif self.dynamic[0] >= chank_size > self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1]]
            self.number_chunk = 3
        elif self.dynamic[0] < chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0], self.assemblage_point[1] + 1]
            self.number_chunk = 2
        elif self.dynamic[0] >= chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1] + 1]
            self.number_chunk = 4

class Interfase:
    """ Содержит элементы для последующего вывода на экран """
    __slots__ = ('game_field', 'biom_map', 'minimap_on', 'point_to_draw', 'text1', 'text2', 'text3', 'text4', 'text5', 'text6', 'text7', 'text8', 'text9', 'text10')
    def __init__(self, game_field, biom_map, minimap_on, text1, text2, text3, text4, text5, text6, text7, text8, text9, text10):
        self.game_field = game_field
        self.biom_map = biom_map
        self.minimap_on = minimap_on
        self.point_to_draw = [0,0]
        self.text1 = text1
        self.text2 = text2
        self.text3 = text3
        self.text4 = text4
        self.text5 = text5
        self.text6 = text6
        self.text7 = text7
        self.text8 = text8
        self.text9 = text9
        self.text10 = text10
"""

    ТЕХНИЧЕСКИЕ ФУНКЦИИ И КЛАССЫ

"""

class Location:
    """ Содержит описание локации """
    __slots__ = ('name', 'temperature', 'chunk', 'icon', 'price_move')
    def __init__(self, name:str, temperature:float, chunk:list, icon:str, price_move:int):
        self.name = name
        self.temperature = temperature
        self.chunk = chunk
        self.icon = icon
        self.price_move = price_move

class Tile:
    """ Содержит изображение, описание, особое содержание тайла, стоимость передвижения, тип, высоту и лестницу """
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        
    def getting_attributes(self, icon, number):
        ground_dict =   {
                        'j': ['бархан', 1],
                        's': ['ракушка', 1],
                        '.': ['горячий песок', 1],
                        ',': ['жухлая трава', 1],
                        'o': ['валун', 15],
                        'A': ['холм', 15],
                        '▲': ['скала', 20],
                        'i': ['кактус', 1],
                        ':': ['солончак', 1],
                        ';': ['солончак', 1],
                        '„': ['трава', 1],
                        'u': ['высокая трава', 1],
                        'ü': ['колючая трава', 10],
                        'F': ['чахлое дерево', 1],
                        'P': ['раскидистое дерево', 1],
                        '~': ['вода', 20],
                        '`': ['солёная вода', 50],
                        'C': ['каньон', 20],
                        '??':['ничего', 10],
                        '0': ['пусто', 0],
                        '☺': ['персонаж', 0],
                        }
        return ground_dict[icon][number]

def gluing_location(raw_gluing_map, grid, count_block):
    """
        Склеивает чанки и локации в единое поле из "сырых" карт

        grid - количество кластеров в одной стороне квадратной склеиваемой карты
        count_block - количество сущностей на одной стороне квадратного кластера
    """
    value_region_box = grid * count_block
    gluing_map = []
    for empry_line in range(grid * count_block):
        gluing_map.append([])
    
    count_location = 0
    for number_region_line in range(grid):
        for number_region in range(grid):
            for number_location_line in range(count_block):
                for number_location in range(count_block):
                    gluing_index = (number_region_line + number_location_line) + (count_location//(grid*(count_block**2))*(count_block-1)) #определяет индекс
                    gluing_map[gluing_index].append(raw_gluing_map[number_region_line][number_region][number_location_line][number_location])
                    count_location += 1
    return gluing_map

class Tiles_image_dict:
    """ Загрузка спрайтов """
    def __init__(self):
        self.dune_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_0.png'))
        self.dune_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_1.png'))
        self.sand = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_sand.png'))
        self.dry_grass_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_0.png'))
        self.dry_grass_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_1.png'))
        self.dry_grass_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.png'))
        self.dry_grass_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.png'))
        self.dry_grass_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.png'))
        self.dry_grass_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_5.png'))       
        self.stones_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_0.png'))
        self.stones_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_1.png'))
        self.stones_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.png'))
        self.stones_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.png'))
        self.stones_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.png'))
        self.hills = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills.png'))
        self.cactus_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_0.png'))
        self.cactus_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_1.png'))
        self.cactus_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_2.png'))
        self.cactus_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_3.png'))
        self.saline_1_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_0.png'))
        self.saline_1_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_1.png'))
        self.saline_1_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_2.png'))
        self.saline_1_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_3.png'))
        self.saline_1_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_4.png'))
        self.saline_1_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_5.png'))
        self.saline_1_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_6.png'))
        self.saline_1_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_7.png'))
        self.saline_1_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_8.png'))
        self.saline_1_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_9.png'))
        self.saline_1_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_A.png'))
        self.saline_1_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_B.png'))
        self.saline_1_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_C.png'))
        self.saline_1_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_D.png'))
        self.saline_1_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_E.png'))
        self.saline_1_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_F.png'))
        self.saline_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_2.png'))
        self.grass_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_0.png'))
        self.grass_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_1.png'))
        self.grass_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.png'))
        self.grass_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.png'))
        self.grass_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.png'))
        self.prickly_grass = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_prickly_grass.png'))
        self.live_tree = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_live_tree.png'))
        self.person = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person.png'))
        self.enemy_riffleman = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman.png'))
        self.enemy_horseman = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_horseman.png'))
        self.enemy_coyot = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_coyot.png'))
        self.warning = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_warning.png'))
        self.human_traces = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_human_traces.png'))
        self.horse_traces = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_horse_traces.png'))
        self.animal_traces = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_animal_traces.png'))
        self.bonfire = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bonfire.png'))
        self.rest_stop = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_rest_stop.png'))
        self.gnawed_bones = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_gnawed_bones.png'))
        self.animal_rest_stop = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_animal_rest_stop.png'))
        self.camp = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_camp.png'))
        self.water_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_0.png'))
        self.water_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_1.png'))
        self.water_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_2.png'))
        self.water_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_3.png'))
        self.water_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_4.png'))
        self.water_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_5.png'))
        self.water_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_6.png'))
        self.water_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_7.png'))
        self.water_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_8.png'))
        self.water_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_9.png'))
        self.water_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_A.png'))
        self.water_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_B.png'))
        self.water_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_C.png'))
        self.water_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_D.png'))
        self.water_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_E.png'))
        self.water_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_F.png'))
        self.water_G = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_G.png'))
        self.water_H = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_H.png'))
        self.water_I = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_I.png'))
        self.water_J = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_J.png'))
        self.water_K = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_K.png'))
        self.water_L = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_L.png'))
        self.water_M = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_M.png'))
        self.water_N = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_N.png'))
        self.water_O = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_O.png'))
        self.water_P = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_p.png'))
        self.water_Q = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_Q.png'))
        self.water_R = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_R.png'))
        self.water_S = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_S.png'))
        self.water_T = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_T.png'))
        self.water_U = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_U.png'))

        self.salty_water_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_0.png'))
        self.salty_water_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_1.png'))
        self.salty_water_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_2.png'))
        self.salty_water_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_3.png'))
        self.salty_water_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_4.png'))
        self.salty_water_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_5.png'))
        self.salty_water_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_6.png'))
        self.salty_water_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_7.png'))
        self.salty_water_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_8.png'))
        self.salty_water_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_9.png'))
        self.salty_water_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_A.png'))
        self.salty_water_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_B.png'))
        self.salty_water_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_C.png'))
        self.salty_water_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_D.png'))
        self.salty_water_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_E.png'))
        self.salty_water_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_F.png'))
        self.salty_water_G = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_G.png'))
        self.salty_water_H = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_H.png'))
        self.salty_water_I = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_I.png'))
        self.salty_water_J = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_J.png'))
        self.salty_water_K = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_K.png'))
        self.salty_water_L = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_L.png'))
        self.salty_water_M = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_M.png'))
        self.salty_water_N = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_N.png'))
        self.salty_water_O = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_O.png'))
        self.salty_water_P = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_p.png'))
        self.salty_water_Q = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_Q.png'))
        self.salty_water_R = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_R.png'))
        self.salty_water_S = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_S.png'))
        self.salty_water_T = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_T.png'))
        self.salty_water_U = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_U.png'))

        self.ford_river_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_0.png'))
        self.ford_river_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_1.png'))
        self.ford_river_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_2.png'))
        self.ford_river_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_3.png'))
        self.ford_river_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_4.png'))
        self.ford_river_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_5.png'))
        self.ford_river_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_6.png'))
        self.ford_river_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_7.png'))
        self.ford_river_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_8.png'))
        self.ford_river_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_9.png'))
        self.ford_river_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_A.png'))
        self.ford_river_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_B.png'))
        self.ford_river_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_C.png'))
        self.ford_river_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_D.png'))
        self.ford_river_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_E.png'))
        self.ford_river_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_F.png'))
        self.ford_river_G = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_G.png'))
        self.ford_river_H = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_H.png'))
        self.ford_river_I = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_I.png'))
        self.ford_river_J = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_J.png'))
        self.ford_river_K = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_K.png'))
        self.ford_river_L = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_L.png'))
        self.ford_river_M = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_M.png'))
        self.ford_river_N = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_N.png'))
        self.ford_river_O = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_O.png'))
        self.ford_river_P = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_p.png'))
        self.ford_river_Q = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_Q.png'))
        self.ford_river_R = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_R.png'))
        self.ford_river_S = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_S.png'))
        self.ford_river_T = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_T.png'))
        self.ford_river_U = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_U.png'))

        self.hills_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_0.png'))
        self.hills_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_1.png'))
        self.hills_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_2.png'))
        self.hills_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_3.png'))
        self.hills_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_4.png'))
        self.hills_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_5.png'))
        self.hills_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_6.png'))
        self.hills_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_7.png'))
        self.hills_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_8.png'))
        self.hills_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_9.png'))
        self.hills_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_A.png'))
        self.hills_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_B.png'))
        self.hills_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_C.png'))
        self.hills_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_D.png'))
        self.hills_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_E.png'))
        self.hills_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_F.png'))
        self.hills_G = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_G.png'))
        self.hills_H = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_H.png'))
        self.hills_I = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_I.png'))
        self.hills_J = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_J.png'))
        self.hills_K = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_K.png'))
        self.hills_L = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_L.png'))
        self.hills_M = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_M.png'))
        self.hills_N = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_N.png'))
        self.hills_O = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_O.png'))
        self.hills_P = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_p.png'))
        self.hills_Q = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_Q.png'))
        self.hills_R = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_R.png'))
        self.hills_S = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_S.png'))
        self.hills_T = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_T.png'))
        self.hills_U = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_U.png'))
        self.bump_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_0.png'))
        self.bump_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_1.png'))
        self.dry_tree_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_0.png'))
        self.dry_tree_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_1.png'))
        self.dry_tree_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_2.png'))
        self.dry_tree_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_3.png'))
        self.dry_tree_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_4.png'))
        self.dry_tree_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_5.png'))
        self.dry_tree_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_6.png'))
        self.dry_tree_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_7.png'))
        self.tall_grass_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_0.png'))
        self.tall_grass_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_1.png'))
        self.canyons_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_0.png'))
        self.canyons_1 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_1.png'))
        self.canyons_2 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_2.png'))
        self.canyons_3 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_3.png'))
        self.canyons_4 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_4.png'))
        self.canyons_5 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_5.png'))
        self.canyons_6 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_6.png'))
        self.canyons_7 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_7.png'))
        self.canyons_8 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_8.png'))
        self.canyons_9 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_9.png'))
        self.canyons_A = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_A.png'))
        self.canyons_B = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_B.png'))
        self.canyons_C = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_C.png'))
        self.canyons_D = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_D.png'))
        self.canyons_E = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_E.png'))
        self.canyons_F = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_F.png'))
        self.canyons_G = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_G.png'))
        self.canyons_H = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_H.png'))
        self.canyons_I = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_I.png'))
        self.canyons_J = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_J.png'))
        self.canyons_K = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_K.png'))
        self.canyons_L = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_L.png'))
        self.canyons_M = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_M.png'))
        self.canyons_N = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_N.png'))
        self.canyons_O = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_O.png'))
        self.canyons_P = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_p.png'))
        self.canyons_Q = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_Q.png'))
        self.canyons_R = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_R.png'))
        self.canyons_S = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_S.png'))
        self.canyons_T = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_T.png'))
        self.canyons_U = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_U.png'))
        self.seashell_0 = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_seashell_0.png'))
            
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ИГРОВЫХ СОБЫТИЙ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step, world):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    interaction_processing(global_map, interaction, enemy_list)
    activity_list_check(activity_list, step)
    master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step, world)

def interaction_processing(global_map, interaction, enemy_list):
    """
        Обрабатывает взаимодействие игрока с миром
    """
    if interaction:
        for interact in interaction:
            if interact[0] == 'task_point_all_enemies':
                for enemy in enemy_list:
                    if enemy.type_npc == 'hunter':
                        enemy.target = interact[1]
                        enemy.waypoints = []
                        enemy.local_waypoints = []
                        print(F"{enemy.name_npc} получил задачу {enemy.target}")
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

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА NPC
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

class Action_in_map:
    """ Содержит в себе описание активности и срок её жизни """
    __slots__ = ('name', 'icon', 'description', 'lifetime', 'birth', 'global_position', 'local_position', 'caused',
                 'lifetime_description', 'visible', 'type', 'level')
    def __init__(self, name, birth, position_npc, dynamic_position, chunk_size, caused):
        self.name = name
        self.icon = self.action_dict(0)
        self.lifetime = self.action_dict(2)
        self.birth = birth
        self.global_position = copy.deepcopy(position_npc)
        self.local_position = [dynamic_position[0]%chunk_size, dynamic_position[1]%chunk_size]
        self.caused = caused
        self.lifetime_description = ''
        self.description = f'{self.action_dict(1)} похоже на {self.caused}'
        self.visible = self.action_dict(3)
        self.type = '0'
        self.level = 0

    def all_description(self):
        self.description = f'{self.lifetime_description} {self.action_dict(1)} похоже на {self.caused}'

        
    def action_dict(self, number):
        """ Принимает название активности, возвращает её иконку, описание и срок жизни"""

        action_dict =   {
                        'camp':             ['/', 'следы лагеря',               150,        True],
                        'bonfire':          ['+', 'следы костра',               150,        True],
                        'rest_stop':        ['№', 'следы остановки человека',   150,        True],
                        'horse_tracks':     ['%', 'следы лошади',               150,        True],
                        'human_tracks':     ['8', 'следы человека',             150,        True],
                        'animal_traces':    ['@', 'следы зверя',                150,        True],
                        'gnawed bones':     ['#', 'обглоданные зверем кости',   500,        True],
                        'defecate':         ['&', 'справленная нужда',          150,        True],
                        'animal_rest_stop': ['$', 'следы животной лежанки',     150,        True],
                        'dead_man':         ['D', 'мёртвый человек',           1000,        True],
                        'test_beacon':      ['B', 'маяк для теста',            1000,        True],
                        'unknown':          ['?', 'неизвестно',                 150,        True],
                        'faint_footprints': ['=', 'слабые следы',                50,       False],
                        }
        if self.name in action_dict:
            return action_dict[self.name][number]
        else:
            return action_dict['unknown'][number]

    def lifetime_description_calculation(self, step):
        if step < (self.birth + self.lifetime//3):
            self.lifetime_description = f'свежие [{self.birth + self.lifetime - step}]'
        elif step > (self.birth + (self.lifetime//3)*2):
            self.lifetime_description = f'старые [{self.birth + self.lifetime - step}]'
        else:
            self.lifetime_description = f'[{self.birth + self.lifetime - step}]'
        


class Enemy:
    """ Отвечает за всех NPC """
    def __init__(self, global_position, local_position, action_points):
        self.global_position = global_position
        self.local_position = local_position
        self.action_points = action_points
        self.dynamic_chunk = False
        self.dynamic_chunk_position = [0, 0]  #УСТАРЕЛО
        self.old_position_assemblage_point = [1, 1]
        self.step_exit_from_assemblage_point = 0
        self.waypoints = []
        self.dynamic_waypoints = [] #УСТАРЕЛО
        self.local_waypoints = [] # [[local_y, local_x], vertices, [global_y, global_x]]
        self.alarm = False
        self.pass_step = 0
        self.on_the_screen = False
        self.steps_to_new_step = 1
        self.level = 0
        self.vertices = 0
        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
        self.visible = True
        self.direction = 'center'

    def all_description_calculation(self):
        self.description = f"{self.pass_description} {self.person_description}"

class Horseman(Enemy):
    """ Отвечает за всадников """
    
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, action_points):
        super().__init__(global_position, local_position, action_points)
        self.name = 'horseman'
        self.name_npc = random.choice(['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['▲']
        self.icon = '☻'
        self.activity_map = {
                            'move': [['передвигается', 'horse_tracks', 0, 0]],
                            'hunger': [['перекусывает', 'rest_stop', 40, 5], ['готовит еду', 'bonfire', 80, 10]],
                            'thirst': [['пьёт', 'horse_tracks', 80, 3]],
                            'fatigue': [['отдыхает', 'rest_stop', 30, 10], ['разбил лагерь', 'camp', 80, 20]],
                            'other': [['кормит лошадь', 'horse_tracks', 0, 5], ['чистит оружие', 'rest_stop', 0, 10]],
                            }
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 10
        self.type_npc = 'hunter'
        self.type = 'h'
        self.pass_description = ''
        self.person_description = f"Знаменитый охотник за головами {self.name_npc}"
        self.description = ''
        self.speed = 2

class Riffleman(Enemy):
    """ Отвечает за стрелков """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, action_points):
        super().__init__(global_position, local_position, action_points)
        self.name = 'riffleman'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻'
        self.activity_map = {
                            'move': [['передвигается', 'human_tracks', 0, 0]],
                            'hunger': [['перекусывает', 'rest_stop', 40, 5], ['готовит еду', 'bonfire', 80, 10]],
                            'thirst': [['пьёт', 'human_tracks', 80, 3]],
                            'fatigue': [['отдыхает', 'rest_stop', 30, 10], ['разбил лагерь', 'camp', 80, 20]],
                            'other': [['чистит оружие', 'rest_stop', 0, 10]],
                            }
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type_npc = 'hunter'
        self.type = 'r'
        self.pass_description = ''
        self.person_description = f"Шериф одного мрачного города {self.name_npc}"
        self.description = ''
        self.speed = 1

class Gold_digger(Enemy):
    """ Отвечает за золотоискателей """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, action_points):
        super().__init__(global_position, local_position, action_points)
        self.name = 'gold_digger'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻'
        self.activity_map = {
                            'move': [['передвигается', 'human_tracks', 0, 0]],
                            'hunger': [['перекусывает', 'rest_stop', 40, 5], ['готовит еду', 'bonfire', 80, 10]],
                            'thirst': [['пьёт', 'human_tracks', 80, 3]],
                            'fatigue': [['отдыхает', 'rest_stop', 30, 10], ['разбил лагерь', 'camp', 80, 20]],
                            'other': [['чистит оружие', 'rest_stop', 0, 10]],
                            }
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type_npc = 'chaotic'
        self.type = '-'
        self.pass_description = ''
        self.person_description = f"Отчаяный золотоискатель {self.name_npc}"
        self.description = ''
        self.speed = 1

class Horse(Enemy):
    """ Отвечает за коней """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, action_points):
        super().__init__(global_position, local_position, action_points)
        self.name = 'horse'
        self.name_npc = random.choice(['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['~', ';']
        self.icon = 'h'
        self.activity_map = {
                            'move': [['передвигается', 'horse_tracks', 0, 0]],
                            'hunger': [['ест траву', 'horse_tracks', 80, 5]],
                            'thirst': [['пьёт', 'horse_tracks', 80, 5]],
                            'fatigue': [['отдыхает', 'animal_rest_stop', 80, 20]],
                            'other': [['пугатся и убегает', 'horse_tracks', 0, 0]],
                            }
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 0
        self.type_npc = 'chaotic'
        self.type = '0'
        self.pass_description = ''
        self.person_description = f"{self.name_npc}"
        self.description = ''
        self.speed = 2

class Coyot(Enemy):
    """ Отвечает за койотов """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, action_points):
        super().__init__(global_position, local_position, action_points)
        self.name = 'coyot'
        self.name_npc = random.choice(['плешивый койот', 'молодой койот', 'подраный койот'])
        self.priority_biom = ['.', ',', '„', 'P', 'A']
        self.banned_biom = ['~', ';']
        self.icon = 'c'
        self.activity_map = {
                            'move': [['передвигается', 'animal_traces', 0, 0]],
                            'hunger': [['охотится', 'gnawed bones', 80, 15], ['ест', 'animal_traces', 30, 10]],
                            'thirst': [['пьёт', 'animal_traces', 80, 5]],
                            'fatigue': [['отдыхает', 'animal_rest_stop', 80, 15]],
                            'other': [['чешется', 'animal_traces', 0, 0]],
                            }
        self.hunger = 200
        self.thirst = 200
        self.fatigue = 200
        self.reserves = 0
        self.type_npc = 'chaotic'
        self.type = '0'
        self.pass_description = ''
        self.person_description = f"Голодный и злой {self.name_npc}"
        self.description = ''
        self.speed = 1

def master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step, world):
    """
        Здесь происходят все события, связанные с NPC

        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
        self.local_waypoints = [] # [[local_y, local_x], vertices, [global_y, global_x]]
    """
    for enemy in enemy_list:

        #print(f"{enemy.name_npc} - на начало обработки имеет: \n global_position - {enemy.global_position} {enemy.vertices}, local_position - {enemy.local_position} \n global - {enemy.waypoints} \n local - {enemy.local_waypoints}")
        enemy.direction = 'center'
        enemy.level = global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[0]].level
        enemy.vertices = global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[1]].vertices
        #print(f"global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[1]].vertices - {global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[1]].vertices}")
        #Удаление реализованного глобального вейпоинта
        if enemy.waypoints and [enemy.global_position[0], enemy.global_position[1], enemy.vertices] == enemy.waypoints[0]:
            enemy.waypoints.pop(0)

        #Удаление реализованной цели
        if enemy.target and enemy.target == [enemy.global_position, enemy.vertices, enemy.local_position]:
            enemy.target = []
            #print(F"xxx {enemy.name_npc} удалена реализованнная цель")
            
        if not world.npc_path_calculation: #Если никто не считал вейпоинты на этом шаге
            
            #Если есть цель, но нет динамических вейпоинтов.
            if enemy.target and not(enemy.local_waypoints):
                #print(F"xxx {enemy.name_npc} есть цель, но нет динамических вейпоинтов")
                enemy_move_calculaton(global_map, enemy)
                world.npc_path_calculation = True
                #print(F"\n \n На этом шаге, вейпоинты считает {enemy.name_npc} \n \n ")
            #Если цели нет и нет динамических вейпоинтов
            if not enemy.target and not enemy.local_waypoints:
                #print(F"xxx {enemy.name_npc} цели нет и нет динамических вейпоинтов")
                for vertices in global_map[enemy.global_position[0]][enemy.global_position[1]].vertices:
                    if vertices.number == enemy.vertices:
                        if vertices.connections:
                            #Определяем позицию искомого тайла, путём выбора из точек перехода искомой зоны доступности
                            number_target = random.randrange(len(vertices.connections))
                            target_tiles = [0, 0]
                            for target_vertices in global_map[vertices.connections[number_target].position[0]][vertices.connections[number_target].position[1]].vertices:
                                if target_vertices == vertices.connections[number_target].number:
                                    for connect in target_vertices.connections:
                                        if connect.number == vertices.number:
                                            target_tiles = random.choice(connect.tiles)
                            #Задаётся цель из существующих координат, существующих связей и существующих тайлов
                            enemy.target = [vertices.connections[number_target].position, vertices.connections[number_target].number, target_tiles]
            #Если есть количество глобальных вейпоинтов больше 1 и истекают локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
            if len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 3: 
                enemy_move_calculaton(global_map, enemy)
                world.npc_path_calculation = True
                #print(F"\n \n На этом шаге, заранее считает вейпоинты {enemy.name_npc} \n \n ")
        #Если есть динамические вейпоинты
        if enemy.local_waypoints:
            #print(F"xxx {enemy.name_npc} есть динамические вейпоинты")
            #Добавляются следы
            if random.randrange(21)//18 > 0:
                activity_list.append(Action_in_map(enemy.activity_map['move'][0][1], step, enemy.global_position, enemy.local_position, chunk_size, enemy.name_npc))
            activity_list.append(Action_in_map('faint_footprints', step, enemy.global_position, enemy.local_position, chunk_size, enemy.name_npc))
            #print(f"??? {enemy.name_npc} собирается поменять глобальную позицию enemy.global_position - {enemy.global_position}")
            #print(f"его динамические вейпоинты enemy.local_waypoints - {enemy.local_waypoints}")
            enemy_direction_calculation(enemy)
            enemy.global_position = enemy.local_waypoints[0][3]
            #print(f"??? {enemy.name_npc} поменял глобальную позицию enemy.global_position - {enemy.global_position} меняя локальную позицию - {enemy.local_position}")
            enemy.local_position = [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1]]
            enemy.local_waypoints.pop(0)
            #print(F"??? {enemy.name_npc} поменял локальную позицию - {enemy.local_position}")
            
        #print(f"{enemy.name_npc} - на конец обработки имеет: \n global_position - {enemy.global_position} {enemy.vertices}, local_position - {enemy.local_position} \n global - {enemy.waypoints} \n local - {enemy.local_waypoints} \n ||||||||||||||||||||||||||")


def enemy_direction_calculation(enemy):
    """
        Определяет направление движения NPC
    """
    if enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1]]:
        if enemy.local_position == [enemy.local_waypoints[0][0] - 1, enemy.local_waypoints[0][1]]:
            enemy.direction = 'up'
        elif enemy.local_position == [enemy.local_waypoints[0][0] + 1, enemy.local_waypoints[0][1]]:
            enemy.direction = 'down'
        elif enemy.local_position == [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1] - 1]:
            enemy.direction = 'left'
        elif enemy.local_position == [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1] + 1]:
            enemy.direction = 'right'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0] - 1, enemy.local_waypoints[0][3][1]]:
        enemy.direction = 'up'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0] + 1, enemy.local_waypoints[0][3][1]]:
        enemy.direction = 'down'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1] - 1]:
        enemy.direction = 'left'
    elif enemy.global_position == [enemy.local_waypoints[0][3][0], enemy.local_waypoints[0][3][1] + 1]:
        enemy.direction = 'right'

def enemy_move_calculaton(global_map, enemy):
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
    #Если есть глобальные вейпоинты, но нет локальных - то считаем локальные вейпоинты
    if enemy.waypoints and not enemy.local_waypoints:
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[0][0], enemy.waypoints[0][1]], enemy.waypoints[0][2]], True)

        #print(f"{enemy.name_npc} - посчитал локальные вейпоинты, имея глобальные | {enemy.waypoints} | {enemy.dynamic_waypoints}")
        
    #Если глобальных вейпоинтов больше 1го и есть локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
    elif len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 3:
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[1][0], enemy.waypoints[1][1]], enemy.waypoints[1][2]], True)

    
    #Если нет глобальных вейпоинтов
    else:
        #Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности
        if enemy.target[0] != enemy.global_position or (enemy.target[0] == enemy.global_position and enemy.target[1] != enemy.vertices):
            #Сначала считаем глобальные вейпоинты
            vertices_enemy_a_star_move_global_calculations(global_map, enemy,[enemy.target[0][0], enemy.target[0][1], enemy.target[1]])
            #А затем локальные
            vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[0][0], enemy.waypoints[0][1]], enemy.waypoints[0][2]], True)
            #print(f"{enemy.name_npc} - посчитал глобальные, а затем локальные вейпоинты | {enemy.waypoints} | {enemy.dynamic_waypoints}")
        #Если равны глобальные позиции и зоны доступности
        elif enemy.target[0] == enemy.global_position and enemy.target[1] == enemy.vertices:
            #Считаем только локальные вейпоинты без перехода на другую локацию
            vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.target[2][0], enemy.target[2][1]], enemy.target[1]], False)
            #print(f"{enemy.name_npc} - посчитал локальные вейпоинты без необходимости считать глобальные | {enemy.waypoints} | {enemy.dynamic_waypoints}")
            
        

def vertices_enemy_a_star_move_global_calculations(processed_map, enemy, finish_point):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по глобальной карте
    """
    try:
        start_point = [enemy.global_position[0], enemy.global_position[1], enemy.vertices]
    except TypeError:
        print(f"!!!TypeError enemy.name_npc - {enemy.name_npc}, enemy.global_position - {enemy.global_position}")
    enemy.waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, 'global', enemy)

def vertices_enemy_a_star_move_local_calculations(global_map, enemy, target, moving_between_locations):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по локальной карте

        target:[[local_y, local_x], vertices - номер зоны доступности на следующей или на этой карте в которую нужно прийти]
    """
    
    if enemy.local_waypoints: #Если уже есть локальные вейпоинты, то стартовой точкой объявляется последний вейпоинт
        start_point = [enemy.local_waypoints[-1][0], enemy.local_waypoints[-1][1], enemy.local_waypoints[-1][2]]
        global_axis = [enemy.local_waypoints[-1][3][0], enemy.local_waypoints[-1][3][1]]
    else: #Если локальных вейпоинтов нет, то стартовой точкой объявляется локальная позиция
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
                            #print(F"finish_point - {finish_point} connect.tiles - {connect.tiles}")
    else:
        finish_point = [target[0][0], target[0][1], target[1]]
    
    
    if finish_point:
        raw_local_waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, 'local', enemy)
        #В каждую путевую точку добавляется глобальная позиция этой точки
        for waypoint in raw_local_waypoints:
            if enemy.local_waypoints:
                waypoint.append(enemy.local_waypoints[-1][3])
            else:
                waypoint.append(enemy.global_position)
        #Добавление вейпоинта, соседнего последнему, но на другой карте и с указанием других глобальных координат
        if moving_between_locations and success:
            if target[0] == [global_axis[0] - 1, global_axis[1]]:
                raw_local_waypoints.append([len(global_map[0][0].chunk) - 1, raw_local_waypoints[-1][1], target[1], target[0]])
            elif target[0] == [global_axis[0] + 1, global_axis[1]]:
                raw_local_waypoints.append([0, raw_local_waypoints[-1][1], target[1], target[0]])
            elif target[0] == [global_axis[0], global_axis[1] - 1]:
                raw_local_waypoints.append([raw_local_waypoints[-1][0], len(global_map[0][0].chunk) - 1, target[1], target[0]]) 
            elif target[0] == [global_axis[0], global_axis[1] + 1]:
                raw_local_waypoints.append([raw_local_waypoints[-1][0], 0, target[1], target[0]])

        #Добавление новых вейпоинтов в конец списка
        for local_waypoint in raw_local_waypoints:
            enemy.local_waypoints.append(local_waypoint)
       

def vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, global_or_local, enemy):
    """
        Рассчитывает поиск пути, алгоритмом A* на основании связей полей доступности.

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


        НУЖНО ДЛЯ ИСПРАВЛЕНИЯ ОШИБОК:
        Добавить список уже занятых координат и сравнивать с ним при добавлении новой вершины.

        ЗАПЛАНИРОВАНО:
        1) !!! Если невозможно найти путь локальным поиском, то следующий глобальный вейпоинт объявляется непроходимым и ищется другой путь
        2) При наличии глобальных вейпоинтов, персонажи считают локальные вейпоинты для следующей локации, не доходя несколько локальных
        вейпоинтов по текущей. При этом, они проверяют, не считал ли вейпоинты на этом шаге какой-либо другой персонаж. #РЕАЛИЗОВАНО
        
        
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

    #print(f"{enemy.name_npc} finish_point - {finish_point}, start_point - {start_point}")

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
            sucess = False
            general_loop = False
            #print(f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* не найден. Выбрана ближайшая точка.")
            if global_or_local == 'global': #УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
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
            print(F"!!! {enemy.name_npc} finish_point - {finish_point}")
        step_count += 1
        if step_count == 250:
            min_price = 99999
            node = graph[-1]
            for number_node in range(len(graph)):
                if graph[number_node].ready:
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        number_finish_node = number_node
            #print(f"!!! {enemy.name_npc} {global_or_local} путь по алгоритму А* за отведённые шаги не найден. Выбрана ближайшая точка.")
            if global_or_local == 'global': #УДАЛЕНИЕ ЦЕЛИ ЕСЛИ НЕ НАЙДЕН ПУТЬ ЧТО БЫ НЕ СПАМИЛ
                enemy.target = []
            sucess = False
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
        test_print = ''
        test_reversed_waypoints = []
        for waypoint in reversed_waypoints:
            test_reversed_waypoints.append([waypoint[0], waypoint[1]])
        for number_line in range(len(processed_map)):
            for number_tile in range(len(processed_map[number_line])):
                    
                if [number_line, number_tile] in test_reversed_waypoints:
                    test_print += processed_map[number_line][number_tile].icon + 'v'
                #elif [number_line, number_tile, start_point[2]] in verified_position:
                    #test_print += processed_map[number_line][number_tile].icon + 'x'
                else:
                    test_print += processed_map[number_line][number_tile].icon + ' '
            test_print += '\n'
        #print(test_print)
        
    elif global_or_local == 'local':
        test_print = ''
        for number_line in range(len(processed_map)):
            for number_tile in range(len(processed_map[number_line])):
                    
                if [number_line, number_tile, start_point[2]] in reversed_waypoints:
                    test_print += processed_map[number_line][number_tile].icon + 'v'
                elif [number_line, number_tile, start_point[2]] in verified_position:
                    test_print += processed_map[number_line][number_tile].icon + 'x'
                else:
                    test_print += processed_map[number_line][number_tile].icon + ' '
            test_print += '\n'
        #print(test_print)


    #print(f"{enemy.name_npc} {global_or_local} list(reversed(reversed_waypoints)) - {list(reversed(reversed_waypoints))}")
    return list(reversed(reversed_waypoints)), success


def enemy_on_the_screen(enemy, person, chunk_size):
    """
        Проверяет NPC на видимость игроком
    """
    if (person.dynamic[0] - chunk_size//2 - 1 < enemy.dynamic_chunk_position[0] < person.dynamic[0] + chunk_size//2 + 1) and (
        person.dynamic[1] - chunk_size//2 - 1 < enemy.dynamic_chunk_position[1] < person.dynamic[1] + chunk_size//2 + 1):
        enemy.on_the_screen = True
    else:
        enemy.on_the_screen = False


def enemy_in_dynamic_chunk(global_map, enemy, person, chunk_size, step, activity_list, new_step, max_speed_enemy_visible):
    """
        Обрабатывает поведение NPC на динамическом чанке игрока
    """
    enemy_recalculation_dynamic_chank_position(global_map, enemy, person, chunk_size, step)
    enemy.all_description_calculation()
    enemy_on_the_screen(enemy, person, chunk_size)
    count_speed = enemy.speed
    if new_step:
        enemy.steps_to_new_step = enemy.speed
    #print(f"{enemy.name} имеет динамические вейпоинты - {enemy.dynamic_waypoints}")

    if enemy.on_the_screen or max_speed_enemy_visible:
        if enemy.steps_to_new_step:
            if len(enemy.waypoints) > 0:
                if enemy.global_position == enemy.waypoints[0]:
                    enemy.waypoints.pop(0)
            if len(enemy.waypoints) > 0:
                if len(enemy.dynamic_waypoints) > 0:
                    if enemy.pass_step == 0:
                        enemy.pass_description = ''
                        enemy.dynamic_chunk_position = enemy.dynamic_waypoints[0]
                        enemy.dynamic_waypoints.pop(0)
                        if random.randrange(21)//18 > 0:
                            activity_list.append(Action_in_map(enemy.activity_map['move'][0][1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
                        activity_list.append(Action_in_map('faint_footprints', step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
                        if random.randrange(101)//99 > 0:
                            action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size)
                    else:
                        enemy.pass_step -= 1
                else:
                    enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size, 'moving_between_locations', [chunk_size//2, chunk_size//2])
            else:
                move_biom_enemy(global_map, enemy)
                #print(f'{enemy.name} Посчитались новые вейпоинты {enemy.waypoints}')
            enemy.steps_to_new_step -= 1
        
    else:
        count_speed = enemy.speed
        while count_speed != 0:
            count_speed -= 1
            if len(enemy.waypoints) > 0:
                if enemy.global_position == enemy.waypoints[0]:
                    enemy.waypoints.pop(0)
            if len(enemy.waypoints) > 0:
                if len(enemy.dynamic_waypoints) > 0:
                    if enemy.pass_step == 0:
                        enemy.pass_description = ''
                        enemy.dynamic_chunk_position = enemy.dynamic_waypoints[0]
                        enemy.dynamic_waypoints.pop(0)
                        if random.randrange(21)//18 > 0:
                            activity_list.append(Action_in_map(enemy.activity_map['move'][0][1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
                        activity_list.append(Action_in_map('faint_footprints', step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
                        if random.randrange(101)//99 > 0:
                            action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size)
                    else:
                        enemy.pass_step -= 1
                else:
                    enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size, 'moving_between_locations', [chunk_size//2, chunk_size//2])
            else:
                move_biom_enemy(global_map, enemy)
    enemy_global_position_recalculation(global_map, enemy, person, chunk_size)


def enemy_ideal_move_calculation(start_point, finish_point): #В ДАННЫЙ МОМЕНТ НЕ ИСПОЛЬЗУЕТСЯ
    """
        Рассчитывает идеальную траекторию движения NPC. 
    """
    
    axis_y = finish_point[0] - start_point[0] # длинна стороны и количество шагов
    axis_x = finish_point[1] - start_point[1] # длинна стороны и количество шагов
    if abs(axis_y) > abs(axis_x):
        if axis_x != 0:
            length_step = abs(axis_y)//abs(axis_x) # на один X столько то Y
        else:
            length_step = abs(axis_y)
        long_side = 'y'
    else:
        if axis_y != 0:
            length_step = abs(axis_x)//abs(axis_y) # на один Y столько то X
        else:
            length_step = abs(axis_x)
        long_side = 'x'
        
    waypoints = [start_point]
        
    for step in range((abs(axis_y) + abs(axis_x))):
        if (step + 1)%(length_step + 1) == 0:
            if long_side == 'y':
                if axis_y >= 0 and axis_x >= 0 or axis_y < 0 and axis_x >= 0:
                    waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                else:
                    waypoints.append([waypoints[step][0], waypoints[step][1] - 1])    
            elif long_side == 'x':
                if axis_x >= 0 and axis_y >= 0 or axis_x < 0 and axis_y >= 0:
                    waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                else:
                    waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
        else:
            if long_side == 'y':
                if axis_y >= 0 and axis_x >= 0 or axis_y >= 0 and axis_x < 0:
                    waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                else:
                    waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
            elif long_side == 'x':
                if axis_x >= 0 and axis_y >= 0 or axis_x >= 0 and axis_y < 0:
                    waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                else:
                    waypoints.append([waypoints[step][0], waypoints[step][1] - 1])

    return waypoints

def checking_the_path(calculation_map, waypoints, banned_list):  #В ДАННЫЙ МОМЕНТ НЕ ИСПОЛЬЗУЕТСЯ
        """
            Проверяет путь на отсутствие преград.
        """
        not_ok = False
        for number_waypoint in range(len(waypoints)):
            #print(f'number_waypoint - {number_waypoint}, waypoints - {waypoints}')
            if waypoints[number_waypoint][0] >= len(calculation_map) or waypoints[number_waypoint][1] >= len(calculation_map):
                if calculation_map[waypoints[number_waypoint][0]][waypoints[number_waypoint][1]].icon in banned_list or calculation_map[waypoints[number_waypoint][0]][waypoints[number_waypoint][1]].price_move > 10:
                    not_ok = True
                    if number_waypoint != 0:
                        waypoints = waypoints[0: number_waypoint]
                    else:
                        waypoints = waypoints[0: (number_waypoint + 1)]
                        break
            else:
                not_ok = True
                if number_waypoint != 0:
                    waypoints = waypoints[0: number_waypoint]
                else:
                    waypoints = waypoints[0: (number_waypoint + 1)]
                    break
        return not_ok, waypoints 
    

def action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size):  #В ДАННЫЙ МОМЕНТ НЕ ИСПОЛЬЗУЕТСЯ
    """
        Обрабатывает появление активностей на динамическом чанке
    """
    request_activity = []
    if enemy.hunger < 20:
        request_activity.append('hunger')
    if enemy.thirst < 20:
        request_activity.append('thirst')
    if enemy.fatigue < 20:
        request_activity.append('fatigue')
    if random.randrange(10)//8 >= 1:
        request_activity.append('other')
        
    if request_activity:
        type_activity = random.choice(request_activity)
        activity = random.choice(enemy.activity_map[type_activity])
        if type_activity == 'hunger': 
            activity_list.append(Action_in_map(activity[1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
            enemy.hunger += activity[2]
        elif type_activity == 'thirst':
            activity_list.append(Action_in_map(activity[1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
            enemy.thirst += activity[2]
        elif type_activity == 'fatigue':
            activity_list.append(Action_in_map(activity[1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
            enemy.fatigue += activity[2]
        elif type_activity == 'other':
            activity_list.append(Action_in_map(activity[1], step, enemy.global_position, enemy.dynamic_chunk_position, chunk_size, enemy.name_npc))
            
        enemy.pass_step += activity[3] # Пропуск указанного количества шагов
        enemy.pass_description = activity[0]



def enemy_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size):  #В ДАННЫЙ МОМЕНТ НЕ ИСПОЛЬЗУЕТСЯ
    """
        Обрабатывает жизнь NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """

    enemy.action_points += 1
    enemy.hunger -= 1
    enemy.thirst -= 1
    enemy.fatigue -= 1
    
    if enemy.action_points >= chunk_size//enemy.speed:
        if len(enemy.waypoints) == 0 and len(enemy.dynamic_waypoints) == 0:
            if random.randrange(10)//6 > 0:
                enemy.waypoints.append(enemy.global_position)
                enemy.action_points -= 5
            else:
                move_biom_enemy(global_map, enemy)
                enemy.action_points -= chunk_size//enemy.speed
        else:
            if not enemy.dynamic_chunk:
                move_enemy_waypoints(global_map, enemy)
            
    if enemy.action_points >= 15:
        if enemy.fatigue < 0:
            enemy.fatigue = 50
            enemy.action_points -= 30
            go_to_print.text5 += str(enemy.name_npc)+ ' уснул от усталости \n'
            activity_list.append(Action_in_map(random.choice(enemy.activity_map['fatigue'])[1], step, enemy.global_position, [random.randrange(chunk_size), random.randrange(chunk_size)], chunk_size, enemy.name_npc))
        else:
            request_activity = []
            if enemy.hunger < 20:
                request_activity.append('hunger')
            if enemy.thirst < 20:
                request_activity.append('thirst')
            if enemy.fatigue < 20:
                request_activity.append('fatigue')
            if random.randrange(10)//8 >= 1:
                request_activity.append('other')
        
            if request_activity:
                type_activity = random.choice(request_activity)
                activity = random.choice(enemy.activity_map[type_activity])
                if type_activity == 'hunger': 
                    activity_list.append(Action_in_map(activity[1], step, enemy.global_position, [random.randrange(chunk_size), random.randrange(chunk_size)], chunk_size, enemy.name_npc))
                    enemy.hunger += activity[2]
                elif type_activity == 'thirst':
                    activity_list.append(Action_in_map(activity[1], step, enemy.global_position, [random.randrange(chunk_size), random.randrange(chunk_size)], chunk_size, enemy.name_npc))
                    enemy.thirst += activity[2]
                elif type_activity == 'fatigue':
                    activity_list.append(Action_in_map(activity[1], step, enemy.global_position, [random.randrange(chunk_size), random.randrange(chunk_size)], chunk_size, enemy.name_npc))
                    enemy.fatigue += activity[2]
                elif type_activity == 'other':
                    activity_list.append(Action_in_map(activity[1], step, enemy.global_position, [random.randrange(chunk_size), random.randrange(chunk_size)], chunk_size, enemy.name_npc))
                enemy.action_points -= activity[2]//3



"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ПОЛЬЗОВАТЕЛЬСКИЙ ВВОД И ЕГО ОБРАБОТКА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step, enemy_list):

    person.level = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].level # Определение высоты персонажа
    person.vertices = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].vertices
    pressed_button = ''
    person.check_local_position()
    person.direction = 'center'
    
    mode_action, pressed_button = request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction)
    if pressed_button != 'none':
        if mode_action == 'move':
            activity_list.append(Action_in_map('faint_footprints', step, person.global_position, person.dynamic, chunk_size, person.name))
            if random.randrange(21)//18 > 0: # Оставление персонажем следов
                activity_list.append(Action_in_map('human_tracks', step, person.global_position, person.dynamic, chunk_size, person.name))
            request_move(global_map, person, chunk_size, go_to_print, pressed_button)
    
        elif mode_action == 'test_move':
            test_request_move(global_map, person, chunk_size, go_to_print, pressed_button, interaction, activity_list, step, enemy_list)
        
        elif mode_action == 'pointer':    
            request_pointer(person, chunk_size, go_to_print, pressed_button)
        elif mode_action == 'gun':
            request_gun(global_map, person, chunk_size, go_to_print, pressed_button)
        if pressed_button == 'button_map':
            go_to_print.minimap_on = (go_to_print.minimap_on == False)
        request_processing(pressed_button)
    
    return mode_action

def wait_keyboard():
    pygame.key.set_repeat(1, 2)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    return 'a'
                if event.key == pygame.K_RIGHT:
                    return 'd'
                if event.key == pygame.K_UP:
                    return 'w'
                if event.key == pygame.K_DOWN:
                    return 's'
                if event.key == pygame.K_SPACE:
                    return 'space'
                if event.key == pygame.K_t:
                    return 't'
                if event.key == pygame.K_p:
                    return 'p'
                if event.key == pygame.K_v:
                    return 'v'
                if event.key == pygame.K_c:
                    return 'c'
                if event.key == pygame.K_h:
                    return 'h'
    
def request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction):
    """
        Спрашивает ввод, возвращает тип активности и нажимаемую кнопку

    """
    pygame.event.clear()
    key = wait_keyboard()
   
    #key = keyboard.read_key()
    #key = 'right'
    if key == 'w' or key == 'up' or key == 'ц':
        return (mode_action, 'up')
    elif key == 'a' or key == 'left' or key == 'ф':
        return (mode_action, 'left')
    elif key == 's' or key == 'down' or key == 'ы':
        return (mode_action, 'down')
    elif key == 'd' or key == 'right' or key == 'в':
        return (mode_action, 'right')
    elif key == 'space':
        return (mode_action, 'space')
    elif key == 'k' or key == 'л':
        if mode_action == 'move':
            person.pointer = [chunk_size//2, chunk_size//2]
            return ('pointer', 'button_pointer')
        elif mode_action == 'pointer':
            person.pointer = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer')
        else:
            person.pointer = [chunk_size//2, chunk_size//2]
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer')
    elif key == 'g' or key == 'п':
        if mode_action == 'move':
            person.gun = [chunk_size//2, chunk_size//2]
            return ('gun', 'button_gun')
        elif mode_action == 'gun':
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_gun')
        else:
            person.pointer = [chunk_size//2, chunk_size//2]
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_gun')
    elif key == 'm' or key == 'ь':
        return (mode_action, 'button_map')
    elif key == 't' or key == 'е':
        if mode_action == 'test_move':
            return ('move', 'button_test')
        else:
            return ('test_move', 'button_test')
    elif key == 'p' or key == 'з':
        if mode_action == 'test_move':
            return ('test_move', 'button_purpose_task')
        else:
            return (mode_action, 'none')
    elif key == 'v' or key == 'м':
        if mode_action == 'test_move':
            return ('test_move', 'button_test_visible')
        else:
            return (mode_action, 'none')
    elif key == 'b' or key == 'и':
        if mode_action == 'test_move':
            return ('test_move', 'button_add_beacon')
        else:
            return (mode_action, 'none')
    elif key == 'c' or key == 'с':
        if mode_action == 'test_move':
            return ('test_move', 'add_coyot')
        else:
            return (mode_action, 'none')
    elif key == 'h' or key == 'р':
        if mode_action == 'test_move':
            return ('test_move', 'add_hunter')
        else:
            return (mode_action, 'none')
    else:
        return (mode_action, 'none')

def request_move(global_map:list, person, chunk_size:int, go_to_print, pressed_button):
    """
        Меняет динамическое местоположение персонажа


        Сначала происходит проверка не является ли следующий по пути тайл скалой, затем проверяется не находится ли он на другом уровне
        или лестницей или персонаж сейчас стоит на лестнице.
    """
    if pressed_button == 'up':
        
        if person.chunks_use_map[person.dynamic[0] - 1][person.dynamic[1]].icon != '▲' and (person.level == person.chunks_use_map[
            person.dynamic[0] - 1][person.dynamic[1]].level or person.chunks_use_map[person.dynamic[0] - 1][
                person.dynamic[1]].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[0] >= chunk_size//2 and person.assemblage_point[0] > 0:
                person.dynamic[0] -= 1
                person.direction = 'up'
            
    elif pressed_button == 'left':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] - 1].icon != '▲'and (person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] - 1].level or person.chunks_use_map[person.dynamic[0]][
                person.dynamic[1] - 1].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[1] >= chunk_size//2 and person.assemblage_point[1] > 0:
                person.dynamic[1] -= 1
                person.direction = 'left'

            
    elif pressed_button == 'down':
        
        if person.chunks_use_map[person.dynamic[0] + 1][person.dynamic[1]].icon != '▲'and (person.level == person.chunks_use_map[
            person.dynamic[0] + 1][person.dynamic[1]].level or person.chunks_use_map[person.dynamic[0] + 1][
                person.dynamic[1]].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[0] <= (chunk_size + chunk_size//2) and person.assemblage_point[0] != (len(global_map) - 2):
                person.dynamic[0] += 1
                person.direction = 'down'
            
    elif pressed_button == 'right':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] + 1].icon != '▲' and (person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] + 1].level or person.chunks_use_map[person.dynamic[0]][
                person.dynamic[1] + 1].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[1] <= (chunk_size + chunk_size//2) and person.assemblage_point[1] != (len(global_map) - 2):
                person.dynamic[1] += 1
                person.direction = 'right'
    
    person.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод
    #person.check_encounter() #Рассчитывает порядок и координаты точек проверки

def test_request_move(global_map:list, person, chunk_size:int, go_to_print, pressed_button, interaction, activity_list, step, enemy_list): #тестовый быстрый режим премещения
    """
        Меняет динамическое местоположение персонажа в тестовом режиме, без ограничений. По полчанка за раз.
        При нажатии на 'p' назначает всем NPC точку следования.
    """
    if pressed_button == 'up':
        if person.dynamic[0] >= chunk_size//2 and person.assemblage_point[0] > 0:
            person.dynamic[0] -= chunk_size//2
            person.recalculating_the_display = True
            
    elif pressed_button == 'left':
        if person.dynamic[1] >= chunk_size//2 and person.assemblage_point[1] > 0:
            person.dynamic[1] -= chunk_size//2
            person.recalculating_the_display = True
            
    elif pressed_button == 'down': 
        if person.dynamic[0] <= (chunk_size + chunk_size//2) and person.assemblage_point[0] != (len(global_map) - 2):
            person.dynamic[0] += chunk_size//2
            person.recalculating_the_display = True
            
    elif pressed_button == 'right':
        if person.dynamic[1] <= (chunk_size + chunk_size//2) and person.assemblage_point[1] != (len(global_map) - 2):
            person.dynamic[1] += chunk_size//2
            person.recalculating_the_display = True

    elif pressed_button == 'button_purpose_task':
        local_position = copy.deepcopy(person.dynamic)
        if local_position[0] > chunk_size:
            local_position[0] -= chunk_size
        if local_position[1] > chunk_size:
            local_position[1] -= chunk_size
        interaction.append(['task_point_all_enemies', [person.global_position, person.vertices, local_position]])

    elif pressed_button == 'button_add_beacon':
        activity_list.append(Action_in_map('test_beacon', step, person.global_position, person.dynamic, chunk_size,
                f'\n оставлен вами в локальной точке - {[person.dynamic[0]%chunk_size, person.dynamic[1]%chunk_size]}| динамической - {person.dynamic}| глобальной - {person.global_position}'))
        
    elif pressed_button == 'button_test_visible':
        person.test_visible = not person.test_visible

    elif pressed_button == 'add_hunter':
        enemy_list.append(Riffleman(person.global_position, person.local_position, 2))
    elif pressed_button == 'add_coyot':
        enemy_list.append(Coyot(person.global_position, person.local_position, 0))

         


    person.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод
    person.check_encounter() #Рассчитывает порядок и координаты точек проверки

def request_pointer(person, chunk_size:int, go_to_print, pressed_button):
    """
        Меняет местоположение указателя
    """
    if pressed_button == 'up' and person.pointer[0] > 0:
        person.pointer[0] -= 1
    elif pressed_button == 'left' and person.pointer[1] > 0:
        person.pointer[1] -= 1 
    elif pressed_button == 'down' and person.pointer[0] < chunk_size - 1:
        person.pointer[0] += 1
    elif pressed_button == 'right' and person.pointer[1] < chunk_size - 1:
        person.pointer[1] += 1

def request_gun(global_map:list, person, chunk_size:int, go_to_print, pressed_button):
    """
        Меняет местоположение указателя оружия
    """
    if pressed_button == 'up' and person.gun[0] > chunk_size//2 - 5:
        person.gun[0] -= 1
            
    elif pressed_button == 'left' and person.gun[1] > chunk_size//2 - 5:
        person.gun[1] -= 1
            
    elif pressed_button == 'down' and person.gun[0] < chunk_size//2 + 5:
        person.gun[0] += 1
            
    elif pressed_button == 'right' and person.gun[1] < chunk_size//2 + 5:
        person.gun[1] += 1

def calculation_assemblage_point(global_map:list, person, chunk_size:int):
    """
        Перерассчитывает положение точки сборки, динамические координаты, перерассчитывает динамический чанк.
    """
    
    if person.dynamic[0] > (chunk_size//2 + chunk_size - 1):
        person.assemblage_point[0] += 1
        person.dynamic[0] -= chunk_size        
    elif person.dynamic[0] < chunk_size//2:
        person.assemblage_point[0] -= 1
        person.dynamic[0] += chunk_size
        
    if person.dynamic[1] > (chunk_size//2 + chunk_size - 1):
        person.assemblage_point[1] += 1
        person.dynamic[1] -= chunk_size   
    elif person.dynamic[1] < chunk_size//2:
        person.assemblage_point[1] -= 1
        person.dynamic[1] += chunk_size


    assemblage_chunk = []

    line_slice = global_map[person.assemblage_point[0]:(person.assemblage_point[0] + 2)]
    
    for line in line_slice:
        line = line[person.assemblage_point[1]:(person.assemblage_point[1] + 2)]
        assemblage_chunk.append(line)
    for number_line in range(len(assemblage_chunk)):
        for chunk in range(len(assemblage_chunk)):
            assemblage_chunk[number_line][chunk] = assemblage_chunk[number_line][chunk].chunk
    person.chunks_use_map = gluing_location(assemblage_chunk, 2, chunk_size)

        
def request_processing(pressed_button):
    """
        Обрабатывает пользовательский запрос
    """
    pass




"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ФОРМИРОВАНИЕ БЛОКОВ ДЛЯ ВЫВОДА НА ЭКРАН ЧЕРЕЗ PYGAME

        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
def test_print(layer):
    """
        Печатает слои
    """
    print_map = ''
    for line in layer:
        for tile in line:
            if tile.icon == '0':
                print_map += tile.icon + ' '
            else:
                print_map += tile.icon + 'v'
        print_map += '\n'
    print(print_map)
            



class Island_friends(pygame.sprite.Sprite):
    """ Содержит спрайты миникарты """

    def __init__(self, x, y, size_tile, number):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(number))
        self.image.set_alpha(60)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def color_dict(self, number):
        color_dict =   {
                        -1: (0, 0, 0),
                        0: (255, 255, 0),
                        1: (255, 255, 150),
                        2: (0, 255, 255),
                        3: (150, 255, 255),
                        4: (255, 0, 255),
                        5: (255, 150, 255),
                        6: (0, 0, 255),
                        7: (0, 255, 0),
                        8: (255, 200, 255),
                        9: (0, 255, 0),
                        10: (0, 128, 0),
                        11: (0, 100, 0),
                        12: (128, 128, 0),
                        13: (128, 128, 0),
                        14: (255, 255, 255),
                        15: (235, 255, 255),
                        16: (200, 255, 255),
                        17: (200, 200, 100),
                        18: (100, 200, 100),
                        19: (200, 100, 100),
                        20: (245, 245, 0),
                        21: (245, 245, 140),
                        22: (0, 245, 245),
                        23: (140, 245, 245),
                        24: (245, 0, 245),
                        25: (245, 140, 245),
                        26: (0, 0, 245),
                        27: (0, 245, 0),
                        28: (245, 200, 245),
                        29: (0, 245, 0),
                        30: (0, 148, 0),
                        31: (0, 140, 0),
                        32: (120, 120, 0),
                        33: (120, 120, 0),
                        34: (245, 245, 245),
                        35: (235, 245, 245),
                        36: (200, 245, 245),
                        37: (200, 200, 140),
                        38: (140, 200, 140),
                        39: (200, 140, 140),
                        40: (140, 140, 200),
                        41: (245, 245, 140),
                        42: (0, 235, 235),
                        43: (130, 235, 235),
                        44: (235, 0, 235),
                        45: (235, 130, 235),
                        46: (0, 0, 235),
                        47: (0, 235, 0),
                        48: (235, 200, 235),
                        49: (0, 235, 0),
                        50: (0, 123, 0),
                        51: (0, 130, 0),
                        52: (123, 123, 0),
                        53: (123, 123, 0),
                        54: (235, 235, 235),
                        55: (205, 235, 235),
                        56: (200, 235, 235),
                        57: (210, 210, 100),
                        58: (100, 210, 100),
                        59: (210, 100, 100),
                        60: (100, 100, 210),
                        61: (225, 225, 150),
                        62: (0, 225, 225),
                        63: (150, 225, 225),
                        64: (225, 0, 225),
                        65: (225, 150, 225),
                        66: (0, 0, 225),
                        67: (0, 225, 0),
                        68: (225, 200, 225),
                        69: (0, 225, 0),
                        70: (0, 128, 0),
                        71: (0, 100, 0),
                        72: (128, 128, 0),
                        73: (128, 128, 0),
                        74: (225, 225, 225),
                        75: (235, 225, 225),
                        76: (200, 225, 225),
                        77: (200, 200, 100),
                        78: (100, 200, 100),
                        79: (200, 100, 100),
                        80: (100, 100, 200),
                        255: (255, 0, 0),
                        }

        if number in color_dict:
            return color_dict[number]
        else:
            return (random.randrange(256), random.randrange(256), random.randrange(256))


class Minimap_temperature(pygame.sprite.Sprite):
    """ Содержит спрайты температуры """

    def __init__(self, x, y, size_tile, temperature):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(temperature))
        self.image.set_alpha(95)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def color_dict(self, temperature):
        color_dict =   {
                        0: (0, 0, 0),
                        1: (0, 0, 255),
                        2: (100, 100, 200),
                        3: (100, 200, 100),
                        4: (200, 255, 100),
                        5: (255, 255, 0),
                        6: (255, 225, 0),
                        7: (255, 200, 0),
                        8: (255, 165, 0),
                        9: (255, 130, 0),
                        10:(255, 100, 0),
                        11:(255, 70, 0),
                        12:(255, 40, 0),
                        13:(255, 0, 0),
                        14:(225, 0, 0),
                        15:(200, 0, 0),
                        16:(150, 0, 0),
                        17:(100, 0, 0),
                        18:(0, 0, 0),
                        }
        key = 0
        if temperature <= 0:
            key = 1
        elif 0 < temperature <= 5:
            key = 2
        elif 5 < temperature <= 10:
            key = 3
        elif 10 < temperature <= 15:
            key = 4
        elif 15 < temperature <= 20:
            key = 5
        elif 20 < temperature <= 25:
            key = 6
        elif 25 < temperature <= 30:
            key = 7
        elif 30 < temperature <= 35:
            key = 8
        elif 35 < temperature <= 40:
            key = 9
        elif 40 < temperature <= 45:
            key = 10
        elif 45 < temperature <= 50:
            key = 11
        elif temperature > 50:
            key = 15


        return color_dict[key]





def landscape_layer_calculations(person, chunk_size, go_to_print):
    """
        Формирует изображение ландшафта на печать
    """
    
    half_views = (chunk_size//2)
    start_stop = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views),
                  (person.dynamic[0] + half_views + 1),(person.dynamic[1] + half_views + 1)]
    line_views = person.chunks_use_map[start_stop[0]:start_stop[2]]

    go_to_print.point_to_draw = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views)]
    
    landscape_layer = []
    for line in line_views:
        new_line = []
        line = line[start_stop[1]:start_stop[3]]
        for tile in line:
            new_line.append(tile)
        landscape_layer.append(new_line)
    return landscape_layer

def activity_layer_calculations(person, chunk_size:int, go_to_print, activity_list):
    """
        Отрисовывает слой активностей или слой персонажей
    """
    start_stop = [(person.dynamic[0] - chunk_size//2), (person.dynamic[1] - chunk_size//2),
                  (person.dynamic[0] + chunk_size//2 + 1),(person.dynamic[1] + chunk_size//2 + 1)]
    go_draw_activity = []
    for activity in activity_list:
        if activity.visible or person.test_visible:
            if activity.global_position[0] == person.assemblage_point[0] and activity.global_position[1] == person.assemblage_point[1]:
                go_draw_activity.append([activity.local_position[0], activity.local_position[1], activity])

            elif activity.global_position[0] == person.assemblage_point[0] and activity.global_position[1] == person.assemblage_point[1] + 1:
                go_draw_activity.append([activity.local_position[0], activity.local_position[1] + chunk_size, activity])

            elif activity.global_position[0] == person.assemblage_point[0] + 1 and activity.global_position[1] == person.assemblage_point[1]:
                go_draw_activity.append([activity.local_position[0] + chunk_size, activity.local_position[1], activity])

            elif activity.global_position[0] == person.assemblage_point[0] + 1 and activity.global_position[1] == person.assemblage_point[1] + 1:
                go_draw_activity.append([activity.local_position[0] + chunk_size, activity.local_position[1] + chunk_size, activity])

    activity_layer = []
    for number_line in range(start_stop[0], start_stop[2]):
        new_line = []
        for number_tile in range(start_stop[1], start_stop[3]):
            no_changes = True
            for activity in go_draw_activity:
                if number_line == activity[0] and number_tile == activity[1]:
                    new_line.append(activity[2])
                    no_changes = False
                    break
            if no_changes:
                new_line.append(Tile('0'))
        activity_layer.append(new_line)

    return activity_layer



def entities_layer_calculations(person, chunk_size:int, go_to_print, entities_list):
    """
        Отрисовывает слой активностей или слой персонажей
    """
    start_stop = [(person.dynamic[0] - chunk_size//2), (person.dynamic[1] - chunk_size//2),
                  (person.dynamic[0] + chunk_size//2 + 1),(person.dynamic[1] + chunk_size//2 + 1)]
    go_draw_entities = []
    for entity in entities_list:
        if entity.visible or person.test_visible:
            if entity.global_position[0] == person.assemblage_point[0] and entity.global_position[1] == person.assemblage_point[1]:
                go_draw_entities.append([entity.local_position[0], entity.local_position[1], entity])

            elif entity.global_position[0] == person.assemblage_point[0] and entity.global_position[1] == person.assemblage_point[1] + 1:
                go_draw_entities.append([entity.local_position[0], entity.local_position[1] + chunk_size, entity])

            elif entity.global_position[0] == person.assemblage_point[0] + 1 and entity.global_position[1] == person.assemblage_point[1]:
                go_draw_entities.append([entity.local_position[0] + chunk_size, entity.local_position[1], entity])

            elif entity.global_position[0] == person.assemblage_point[0] + 1 and entity.global_position[1] == person.assemblage_point[1] + 1:
                go_draw_entities.append([entity.local_position[0] + chunk_size, entity.local_position[1] + chunk_size, entity])

    entities_layer = []
    for number_line in range(start_stop[0], start_stop[2]):
        new_line = []
        for number_tile in range(start_stop[1], start_stop[3]):
            no_changes = True
            for entity in go_draw_entities:
                if number_line == entity[0] and number_tile == entity[1]:
                    new_line.append(entity[2])
                    no_changes = False
                    break
            if no_changes:
                new_line.append(Tile('0'))
        entities_layer.append(new_line)

    return entities_layer         


def sky_layer_calculations(chunk_size):
    """
        Отрисовывает сущности на небе. Пока что создаёт карту-пустышку.
    """
    sky_layer = []
    for number_line in range(chunk_size):
        new_line = []
        for number_tile in range(chunk_size):
            new_line.append(Tile('0'))
        sky_layer.append(new_line)
    return sky_layer

class Level_tiles(pygame.sprite.Sprite):
    """ Содержит спрайты миникарты """

    def __init__(self, x, y, size_tile, level):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill((239, 228, 176), special_flags=pygame.BLEND_RGB_ADD)
        self.image.set_alpha(25*level)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
        
class Image_tile(pygame.sprite.Sprite):
    """ Содержит спрайт и его кординаты на экране """
    def __init__(self, x, y, size_tile, tiles_image_dict, icon_tile, type_tile):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.image_dict(icon_tile, type_tile, tiles_image_dict)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def image_dict(self, icon_tile, type_tile, tiles_image_dict):

        image_dict =   {
                        'j': {
                                '0': tiles_image_dict.dune_0,
                                '1': tiles_image_dict.dune_1,
                             },
                        's': {'0': tiles_image_dict.seashell_0},
                        '.': {'0': tiles_image_dict.sand,},
                        ',': {
                                '0': tiles_image_dict.dry_grass_5,
                                '1': tiles_image_dict.dry_grass_0,
                                '2': tiles_image_dict.dry_grass_2,
                                '3': tiles_image_dict.dry_grass_1,
                                '4': tiles_image_dict.dry_grass_2,
                                '5': tiles_image_dict.dry_grass_2,
                                '6': tiles_image_dict.dry_grass_4,
                                '7': tiles_image_dict.dry_grass_3,
                                '8': tiles_image_dict.dry_grass_2,
                                '9': tiles_image_dict.dry_grass_3,
                                'A': tiles_image_dict.dry_grass_4,
                                'B': tiles_image_dict.dry_grass_4,
                                'C': tiles_image_dict.dry_grass_5,
                                'D': tiles_image_dict.dry_grass_2,
                                'E': tiles_image_dict.dry_grass_3,
                                'F': tiles_image_dict.dry_grass_4,
                              },
                        'o': {
                                '0': tiles_image_dict.stones_4,
                                '1': tiles_image_dict.stones_0,
                                '2': tiles_image_dict.stones_2,
                                '3': tiles_image_dict.stones_3,
                                '4': tiles_image_dict.stones_4,
                                '5': tiles_image_dict.stones_2,
                                '6': tiles_image_dict.stones_3,
                                '7': tiles_image_dict.stones_4,
                                '8': tiles_image_dict.stones_2,
                                '9': tiles_image_dict.stones_3,
                                'A': tiles_image_dict.stones_4,
                                'B': tiles_image_dict.stones_2,
                                'C': tiles_image_dict.stones_3,
                                'D': tiles_image_dict.stones_4,
                                'E': tiles_image_dict.stones_2,
                                'F': tiles_image_dict.stones_3,
                              },
                        'A': {
                                '0': tiles_image_dict.bump_0,
                                '1': tiles_image_dict.bump_1,
                             },
                        '▲': {
                                '0': tiles_image_dict.hills_0,
                                '1': tiles_image_dict.hills_1,
                                '2': tiles_image_dict.hills_2,
                                '3': tiles_image_dict.hills_3,
                                '4': tiles_image_dict.hills_4,
                                '5': tiles_image_dict.hills_5,
                                '6': tiles_image_dict.hills_6,
                                '7': tiles_image_dict.hills_7,
                                '8': tiles_image_dict.hills_8,
                                '9': tiles_image_dict.hills_9,
                                'A': tiles_image_dict.hills_A,
                                'B': tiles_image_dict.hills_B,
                                'C': tiles_image_dict.hills_C,
                                'D': tiles_image_dict.hills_D,
                                'E': tiles_image_dict.hills_E,
                                'F': tiles_image_dict.hills_F,
                                'G': tiles_image_dict.hills_G,
                                'H': tiles_image_dict.hills_H,
                                'I': tiles_image_dict.hills_I,
                                'J': tiles_image_dict.hills_J,
                                'K': tiles_image_dict.hills_K,
                                'L': tiles_image_dict.hills_L,
                                'M': tiles_image_dict.hills_M,
                                'N': tiles_image_dict.hills_N,
                                'O': tiles_image_dict.hills_O,
                                'P': tiles_image_dict.hills_P,
                                'Q': tiles_image_dict.hills_Q,
                                'R': tiles_image_dict.hills_R,
                                'S': tiles_image_dict.hills_S,
                                'T': tiles_image_dict.hills_T,
                                'U': tiles_image_dict.hills_U,
                             },
                        'i': {
                                '0': tiles_image_dict.cactus_0,
                                '1': tiles_image_dict.cactus_1,
                                '2': tiles_image_dict.cactus_2,
                                '3': tiles_image_dict.cactus_3,
                              },
                        ':': {
                                '0': tiles_image_dict.saline_1_0,
                                '1': tiles_image_dict.saline_1_1,
                                '2': tiles_image_dict.saline_1_2,
                                '3': tiles_image_dict.saline_1_3,
                                '4': tiles_image_dict.saline_1_4,
                                '5': tiles_image_dict.saline_1_5,
                                '6': tiles_image_dict.saline_1_6,
                                '7': tiles_image_dict.saline_1_7,
                                '8': tiles_image_dict.saline_1_8,
                                '9': tiles_image_dict.saline_1_9,
                                'A': tiles_image_dict.saline_1_A,
                                'B': tiles_image_dict.saline_1_B,
                                'C': tiles_image_dict.saline_1_C,
                                'D': tiles_image_dict.saline_1_D,
                                'E': tiles_image_dict.saline_1_E,
                                'F': tiles_image_dict.saline_1_F,
                             },
                        ';': {'0': tiles_image_dict.saline_2,},
                        '„': {
                                '0': tiles_image_dict.grass_4,
                                '1': tiles_image_dict.grass_0,
                                '2': tiles_image_dict.grass_2,
                                '3': tiles_image_dict.grass_3,
                                '4': tiles_image_dict.grass_4,
                                '5': tiles_image_dict.grass_2,
                                '6': tiles_image_dict.grass_3,
                                '7': tiles_image_dict.grass_4,
                                '8': tiles_image_dict.grass_2,
                                '9': tiles_image_dict.grass_3,
                                'A': tiles_image_dict.grass_4,
                                'B': tiles_image_dict.grass_2,
                                'C': tiles_image_dict.grass_3,
                                'D': tiles_image_dict.grass_4,
                                'E': tiles_image_dict.grass_2,
                                'F': tiles_image_dict.grass_3,
                              },
                        'u': {
                                '0': tiles_image_dict.tall_grass_0,
                                '1': tiles_image_dict.tall_grass_1,
                             },
                        'ü': {'0': tiles_image_dict.prickly_grass,},
                        'F': {
                                '0': tiles_image_dict.dry_tree_0,
                                '1': tiles_image_dict.dry_tree_1,
                                '2': tiles_image_dict.dry_tree_2,
                                '3': tiles_image_dict.dry_tree_3,
                                '4': tiles_image_dict.dry_tree_4,
                                '5': tiles_image_dict.dry_tree_5,
                                '6': tiles_image_dict.dry_tree_6,
                                '7': tiles_image_dict.dry_tree_7,
                             },
                        'P': {'0': tiles_image_dict.live_tree,},
                        '~': {
                                '0': tiles_image_dict.water_0,
                                '1': tiles_image_dict.water_1,
                                '2': tiles_image_dict.water_2,
                                '3': tiles_image_dict.water_3,
                                '4': tiles_image_dict.water_4,
                                '5': tiles_image_dict.water_5,
                                '6': tiles_image_dict.water_6,
                                '7': tiles_image_dict.water_7,
                                '8': tiles_image_dict.water_8,
                                '9': tiles_image_dict.water_9,
                                'A': tiles_image_dict.water_A,
                                'B': tiles_image_dict.water_B,
                                'C': tiles_image_dict.water_C,
                                'D': tiles_image_dict.water_D,
                                'E': tiles_image_dict.water_E,
                                'F': tiles_image_dict.water_F,
                                'G': tiles_image_dict.water_G,
                                'H': tiles_image_dict.water_H,
                                'I': tiles_image_dict.water_I,
                                'J': tiles_image_dict.water_J,
                                'K': tiles_image_dict.water_K,
                                'L': tiles_image_dict.water_L,
                                'M': tiles_image_dict.water_M,
                                'N': tiles_image_dict.water_N,
                                'O': tiles_image_dict.water_O,
                                'P': tiles_image_dict.water_P,
                                'Q': tiles_image_dict.water_Q,
                                'R': tiles_image_dict.water_R,
                                'S': tiles_image_dict.water_S,
                                'T': tiles_image_dict.water_T,
                                'U': tiles_image_dict.water_U,
                             },
                        'f': {
                                '0': tiles_image_dict.ford_river_0,
                                '1': tiles_image_dict.ford_river_1,
                                '2': tiles_image_dict.ford_river_2,
                                '3': tiles_image_dict.ford_river_3,
                                '4': tiles_image_dict.ford_river_4,
                                '5': tiles_image_dict.ford_river_5,
                                '6': tiles_image_dict.ford_river_6,
                                '7': tiles_image_dict.ford_river_7,
                                '8': tiles_image_dict.ford_river_8,
                                '9': tiles_image_dict.ford_river_9,
                                'A': tiles_image_dict.ford_river_A,
                                'B': tiles_image_dict.ford_river_B,
                                'C': tiles_image_dict.ford_river_C,
                                'D': tiles_image_dict.ford_river_D,
                                'E': tiles_image_dict.ford_river_E,
                                'F': tiles_image_dict.ford_river_F,
                                'G': tiles_image_dict.ford_river_G,
                                'H': tiles_image_dict.ford_river_H,
                                'I': tiles_image_dict.ford_river_I,
                                'J': tiles_image_dict.ford_river_J,
                                'K': tiles_image_dict.ford_river_K,
                                'L': tiles_image_dict.ford_river_L,
                                'M': tiles_image_dict.ford_river_M,
                                'N': tiles_image_dict.ford_river_N,
                                'O': tiles_image_dict.ford_river_O,
                                'P': tiles_image_dict.ford_river_P,
                                'Q': tiles_image_dict.ford_river_Q,
                                'R': tiles_image_dict.ford_river_R,
                                'S': tiles_image_dict.ford_river_S,
                                'T': tiles_image_dict.ford_river_T,
                                'U': tiles_image_dict.ford_river_U,
                             },
                        '`': {
                                '0': tiles_image_dict.salty_water_0,
                                '1': tiles_image_dict.salty_water_1,
                                '2': tiles_image_dict.salty_water_2,
                                '3': tiles_image_dict.salty_water_3,
                                '4': tiles_image_dict.salty_water_4,
                                '5': tiles_image_dict.salty_water_5,
                                '6': tiles_image_dict.salty_water_6,
                                '7': tiles_image_dict.salty_water_7,
                                '8': tiles_image_dict.salty_water_8,
                                '9': tiles_image_dict.salty_water_9,
                                'A': tiles_image_dict.salty_water_A,
                                'B': tiles_image_dict.salty_water_B,
                                'C': tiles_image_dict.salty_water_C,
                                'D': tiles_image_dict.salty_water_D,
                                'E': tiles_image_dict.salty_water_E,
                                'F': tiles_image_dict.salty_water_F,
                                'G': tiles_image_dict.salty_water_G,
                                'H': tiles_image_dict.salty_water_H,
                                'I': tiles_image_dict.salty_water_I,
                                'J': tiles_image_dict.salty_water_J,
                                'K': tiles_image_dict.salty_water_K,
                                'L': tiles_image_dict.salty_water_L,
                                'M': tiles_image_dict.salty_water_M,
                                'N': tiles_image_dict.salty_water_N,
                                'O': tiles_image_dict.salty_water_O,
                                'P': tiles_image_dict.salty_water_P,
                                'Q': tiles_image_dict.salty_water_Q,
                                'R': tiles_image_dict.salty_water_R,
                                'S': tiles_image_dict.salty_water_S,
                                'T': tiles_image_dict.salty_water_T,
                                'U': tiles_image_dict.salty_water_U,
                             },
                        'C': {
                                '0': tiles_image_dict.canyons_0,
                                '1': tiles_image_dict.canyons_1,
                                '2': tiles_image_dict.canyons_2,
                                '3': tiles_image_dict.canyons_3,
                                '4': tiles_image_dict.canyons_4,
                                '5': tiles_image_dict.canyons_5,
                                '6': tiles_image_dict.canyons_6,
                                '7': tiles_image_dict.canyons_7,
                                '8': tiles_image_dict.canyons_8,
                                '9': tiles_image_dict.canyons_9,
                                'A': tiles_image_dict.canyons_A,
                                'B': tiles_image_dict.canyons_B,
                                'C': tiles_image_dict.canyons_C,
                                'D': tiles_image_dict.canyons_D,
                                'E': tiles_image_dict.canyons_E,
                                'F': tiles_image_dict.canyons_F,
                                'G': tiles_image_dict.canyons_G,
                                'H': tiles_image_dict.canyons_H,
                                'I': tiles_image_dict.canyons_I,
                                'J': tiles_image_dict.canyons_J,
                                'K': tiles_image_dict.canyons_K,
                                'L': tiles_image_dict.canyons_L,
                                'M': tiles_image_dict.canyons_M,
                                'N': tiles_image_dict.canyons_N,
                                'O': tiles_image_dict.canyons_O,
                                'P': tiles_image_dict.canyons_P,
                                'Q': tiles_image_dict.canyons_Q,
                                'R': tiles_image_dict.canyons_R,
                                'S': tiles_image_dict.canyons_S,
                                'T': tiles_image_dict.canyons_T,
                                'U': tiles_image_dict.canyons_U,
                             },
                        '☺': {'0': tiles_image_dict.person,},
                        '☻': {
                                'r': tiles_image_dict.enemy_riffleman,
                                'h': tiles_image_dict.enemy_horseman,
                             },
                        'c': {'0': tiles_image_dict.enemy_coyot,},
                        '8': {'0': tiles_image_dict.human_traces,},
                        '%': {'0': tiles_image_dict.horse_traces,},
                        '@': {'0': tiles_image_dict.animal_traces,},
                        '/': {'0': tiles_image_dict.camp,},
                        '+': {'0': tiles_image_dict.bonfire,},
                        '№': {'0': tiles_image_dict.rest_stop,},
                        '#': {'0': tiles_image_dict.gnawed_bones,},
                        '$': {'0': tiles_image_dict.animal_rest_stop,},
                        }
        if icon_tile in image_dict and type_tile in image_dict[icon_tile]:
            return image_dict[icon_tile][type_tile]

        else:
            return tiles_image_dict.warning
        
class All_tiles(pygame.sprite.Sprite):
    """ Содержит спрайты миникарты """

    def __init__(self, x, y, size_tile, tiles_image_dict, tile_icon, tile_type):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.img = self.image_dict(tile_icon, tile_type, tiles_image_dict)
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def image_dict(self, icon_tile, type_tile, tiles_image_dict):

        image_dict =   {
                        'j': {
                                '0': tiles_image_dict.dune_0,
                                '1': tiles_image_dict.dune_1,
                             },
                        's': {'0': tiles_image_dict.seashell_0},
                        '.': {'0': tiles_image_dict.sand,},
                        ',': {
                                '0': tiles_image_dict.dry_grass_5,
                                '1': tiles_image_dict.dry_grass_0,
                                '2': tiles_image_dict.dry_grass_2,
                                '3': tiles_image_dict.dry_grass_1,
                                '4': tiles_image_dict.dry_grass_2,
                                '5': tiles_image_dict.dry_grass_2,
                                '6': tiles_image_dict.dry_grass_4,
                                '7': tiles_image_dict.dry_grass_3,
                                '8': tiles_image_dict.dry_grass_2,
                                '9': tiles_image_dict.dry_grass_3,
                                'A': tiles_image_dict.dry_grass_4,
                                'B': tiles_image_dict.dry_grass_4,
                                'C': tiles_image_dict.dry_grass_5,
                                'D': tiles_image_dict.dry_grass_2,
                                'E': tiles_image_dict.dry_grass_3,
                                'F': tiles_image_dict.dry_grass_4,
                              },
                        'S': {
                                '0': tiles_image_dict.stones_4,
                                '1': tiles_image_dict.stones_0,
                                '2': tiles_image_dict.stones_2,
                                '3': tiles_image_dict.stones_3,
                                '4': tiles_image_dict.stones_4,
                                '5': tiles_image_dict.stones_2,
                                '6': tiles_image_dict.stones_3,
                                '7': tiles_image_dict.stones_4,
                                '8': tiles_image_dict.stones_2,
                                '9': tiles_image_dict.stones_3,
                                'A': tiles_image_dict.stones_4,
                                'B': tiles_image_dict.stones_2,
                                'C': tiles_image_dict.stones_3,
                                'D': tiles_image_dict.stones_4,
                                'E': tiles_image_dict.stones_2,
                                'F': tiles_image_dict.stones_3,
                              },
                        'A': {
                                '0': tiles_image_dict.bump_0,
                                '1': tiles_image_dict.bump_1,
                             },
                        '▲': {
                                '0': tiles_image_dict.hills_0,
                                '1': tiles_image_dict.hills_1,
                                '2': tiles_image_dict.hills_2,
                                '3': tiles_image_dict.hills_3,
                                '4': tiles_image_dict.hills_4,
                                '5': tiles_image_dict.hills_5,
                                '6': tiles_image_dict.hills_6,
                                '7': tiles_image_dict.hills_7,
                                '8': tiles_image_dict.hills_8,
                                '9': tiles_image_dict.hills_9,
                                'A': tiles_image_dict.hills_A,
                                'B': tiles_image_dict.hills_B,
                                'C': tiles_image_dict.hills_C,
                                'D': tiles_image_dict.hills_D,
                                'E': tiles_image_dict.hills_E,
                                'F': tiles_image_dict.hills_F,
                                'G': tiles_image_dict.hills_G,
                                'H': tiles_image_dict.hills_H,
                                'I': tiles_image_dict.hills_I,
                                'J': tiles_image_dict.hills_J,
                                'K': tiles_image_dict.hills_K,
                                'L': tiles_image_dict.hills_L,
                                'M': tiles_image_dict.hills_M,
                                'N': tiles_image_dict.hills_N,
                                'O': tiles_image_dict.hills_O,
                                'P': tiles_image_dict.hills_P,
                                'Q': tiles_image_dict.hills_Q,
                                'R': tiles_image_dict.hills_R,
                                'S': tiles_image_dict.hills_S,
                                'T': tiles_image_dict.hills_T,
                                'U': tiles_image_dict.hills_U,
                             },
                        'i': {
                                '0': tiles_image_dict.cactus_0,
                                '1': tiles_image_dict.cactus_1,
                                '2': tiles_image_dict.cactus_2,
                                '3': tiles_image_dict.cactus_3,
                              },
                        ';': {
                                '0': tiles_image_dict.saline_1_0,
                                '1': tiles_image_dict.saline_1_1,
                                '2': tiles_image_dict.saline_1_2,
                                '3': tiles_image_dict.saline_1_3,
                                '4': tiles_image_dict.saline_1_4,
                                '5': tiles_image_dict.saline_1_5,
                                '6': tiles_image_dict.saline_1_6,
                                '7': tiles_image_dict.saline_1_7,
                                '8': tiles_image_dict.saline_1_8,
                                '9': tiles_image_dict.saline_1_9,
                                'A': tiles_image_dict.saline_1_A,
                                'B': tiles_image_dict.saline_1_B,
                                'C': tiles_image_dict.saline_1_C,
                                'D': tiles_image_dict.saline_1_D,
                                'E': tiles_image_dict.saline_1_E,
                                'F': tiles_image_dict.saline_1_F,
                             },
                        ':': {'0': tiles_image_dict.saline_2,},
                        '„': {
                                '0': tiles_image_dict.grass_4,
                                '1': tiles_image_dict.grass_0,
                                '2': tiles_image_dict.grass_2,
                                '3': tiles_image_dict.grass_3,
                                '4': tiles_image_dict.grass_4,
                                '5': tiles_image_dict.grass_2,
                                '6': tiles_image_dict.grass_3,
                                '7': tiles_image_dict.grass_4,
                                '8': tiles_image_dict.grass_2,
                                '9': tiles_image_dict.grass_3,
                                'A': tiles_image_dict.grass_4,
                                'B': tiles_image_dict.grass_2,
                                'C': tiles_image_dict.grass_3,
                                'D': tiles_image_dict.grass_4,
                                'E': tiles_image_dict.grass_2,
                                'F': tiles_image_dict.grass_3,
                              },
                        'u': {
                                '0': tiles_image_dict.tall_grass_0,
                                '1': tiles_image_dict.tall_grass_1,
                             },
                        'ü': {'0': tiles_image_dict.prickly_grass,},
                        'F': {
                                '0': tiles_image_dict.dry_tree_0,
                                '1': tiles_image_dict.dry_tree_1,
                                '2': tiles_image_dict.dry_tree_2,
                                '3': tiles_image_dict.dry_tree_3,
                                '4': tiles_image_dict.dry_tree_4,
                                '5': tiles_image_dict.dry_tree_5,
                                '6': tiles_image_dict.dry_tree_6,
                                '7': tiles_image_dict.dry_tree_7,
                             },
                        'P': {'0': tiles_image_dict.live_tree,},
                        '~': {
                                '0': tiles_image_dict.water_0,
                                '1': tiles_image_dict.water_1,
                                '2': tiles_image_dict.water_2,
                                '3': tiles_image_dict.water_3,
                                '4': tiles_image_dict.water_4,
                                '5': tiles_image_dict.water_5,
                                '6': tiles_image_dict.water_6,
                                '7': tiles_image_dict.water_7,
                                '8': tiles_image_dict.water_8,
                                '9': tiles_image_dict.water_9,
                                'A': tiles_image_dict.water_A,
                                'B': tiles_image_dict.water_B,
                                'C': tiles_image_dict.water_C,
                                'D': tiles_image_dict.water_D,
                                'E': tiles_image_dict.water_E,
                                'F': tiles_image_dict.water_F,
                                'G': tiles_image_dict.water_G,
                                'H': tiles_image_dict.water_H,
                                'I': tiles_image_dict.water_I,
                                'J': tiles_image_dict.water_J,
                                'K': tiles_image_dict.water_K,
                                'L': tiles_image_dict.water_L,
                                'M': tiles_image_dict.water_M,
                                'N': tiles_image_dict.water_N,
                                'O': tiles_image_dict.water_O,
                                'P': tiles_image_dict.water_P,
                                'Q': tiles_image_dict.water_Q,
                                'R': tiles_image_dict.water_R,
                                'S': tiles_image_dict.water_S,
                                'T': tiles_image_dict.water_T,
                                'U': tiles_image_dict.water_U,
                             },
                        'f': {
                                '0': tiles_image_dict.ford_river_0,
                                '1': tiles_image_dict.ford_river_1,
                                '2': tiles_image_dict.ford_river_2,
                                '3': tiles_image_dict.ford_river_3,
                                '4': tiles_image_dict.ford_river_4,
                                '5': tiles_image_dict.ford_river_5,
                                '6': tiles_image_dict.ford_river_6,
                                '7': tiles_image_dict.ford_river_7,
                                '8': tiles_image_dict.ford_river_8,
                                '9': tiles_image_dict.ford_river_9,
                                'A': tiles_image_dict.ford_river_A,
                                'B': tiles_image_dict.ford_river_B,
                                'C': tiles_image_dict.ford_river_C,
                                'D': tiles_image_dict.ford_river_D,
                                'E': tiles_image_dict.ford_river_E,
                                'F': tiles_image_dict.ford_river_F,
                                'G': tiles_image_dict.ford_river_G,
                                'H': tiles_image_dict.ford_river_H,
                                'I': tiles_image_dict.ford_river_I,
                                'J': tiles_image_dict.ford_river_J,
                                'K': tiles_image_dict.ford_river_K,
                                'L': tiles_image_dict.ford_river_L,
                                'M': tiles_image_dict.ford_river_M,
                                'N': tiles_image_dict.ford_river_N,
                                'O': tiles_image_dict.ford_river_O,
                                'P': tiles_image_dict.ford_river_P,
                                'Q': tiles_image_dict.ford_river_Q,
                                'R': tiles_image_dict.ford_river_R,
                                'S': tiles_image_dict.ford_river_S,
                                'T': tiles_image_dict.ford_river_T,
                                'U': tiles_image_dict.ford_river_U,
                             },
                        '`': {
                                '0': tiles_image_dict.salty_water_0,
                                '1': tiles_image_dict.salty_water_1,
                                '2': tiles_image_dict.salty_water_2,
                                '3': tiles_image_dict.salty_water_3,
                                '4': tiles_image_dict.salty_water_4,
                                '5': tiles_image_dict.salty_water_5,
                                '6': tiles_image_dict.salty_water_6,
                                '7': tiles_image_dict.salty_water_7,
                                '8': tiles_image_dict.salty_water_8,
                                '9': tiles_image_dict.salty_water_9,
                                'A': tiles_image_dict.salty_water_A,
                                'B': tiles_image_dict.salty_water_B,
                                'C': tiles_image_dict.salty_water_C,
                                'D': tiles_image_dict.salty_water_D,
                                'E': tiles_image_dict.salty_water_E,
                                'F': tiles_image_dict.salty_water_F,
                                'G': tiles_image_dict.salty_water_G,
                                'H': tiles_image_dict.salty_water_H,
                                'I': tiles_image_dict.salty_water_I,
                                'J': tiles_image_dict.salty_water_J,
                                'K': tiles_image_dict.salty_water_K,
                                'L': tiles_image_dict.salty_water_L,
                                'M': tiles_image_dict.salty_water_M,
                                'N': tiles_image_dict.salty_water_N,
                                'O': tiles_image_dict.salty_water_O,
                                'P': tiles_image_dict.salty_water_P,
                                'Q': tiles_image_dict.salty_water_Q,
                                'R': tiles_image_dict.salty_water_R,
                                'S': tiles_image_dict.salty_water_S,
                                'T': tiles_image_dict.salty_water_T,
                                'U': tiles_image_dict.salty_water_U,
                             },
                        'C': {
                                '0': tiles_image_dict.canyons_0,
                                '1': tiles_image_dict.canyons_1,
                                '2': tiles_image_dict.canyons_2,
                                '3': tiles_image_dict.canyons_3,
                                '4': tiles_image_dict.canyons_4,
                                '5': tiles_image_dict.canyons_5,
                                '6': tiles_image_dict.canyons_6,
                                '7': tiles_image_dict.canyons_7,
                                '8': tiles_image_dict.canyons_8,
                                '9': tiles_image_dict.canyons_9,
                                'A': tiles_image_dict.canyons_A,
                                'B': tiles_image_dict.canyons_B,
                                'C': tiles_image_dict.canyons_C,
                                'D': tiles_image_dict.canyons_D,
                                'E': tiles_image_dict.canyons_E,
                                'F': tiles_image_dict.canyons_F,
                                'G': tiles_image_dict.canyons_G,
                                'H': tiles_image_dict.canyons_H,
                                'I': tiles_image_dict.canyons_I,
                                'J': tiles_image_dict.canyons_J,
                                'K': tiles_image_dict.canyons_K,
                                'L': tiles_image_dict.canyons_L,
                                'M': tiles_image_dict.canyons_M,
                                'N': tiles_image_dict.canyons_N,
                                'O': tiles_image_dict.canyons_O,
                                'P': tiles_image_dict.canyons_P,
                                'Q': tiles_image_dict.canyons_Q,
                                'R': tiles_image_dict.canyons_R,
                                'S': tiles_image_dict.canyons_S,
                                'T': tiles_image_dict.canyons_T,
                                'U': tiles_image_dict.canyons_U,
                             },
                        '☺': {'0': tiles_image_dict.person,},
                        '☻': {
                                'r': tiles_image_dict.enemy_riffleman,
                                'h': tiles_image_dict.enemy_horseman,
                             },
                        'c': {'0': tiles_image_dict.enemy_coyot,},
                        '8': {'0': tiles_image_dict.human_traces,},
                        '%': {'0': tiles_image_dict.horse_traces,},
                        '@': {'0': tiles_image_dict.animal_traces,},
                        '/': {'0': tiles_image_dict.camp,},
                        '+': {'0': tiles_image_dict.bonfire,},
                        '№': {'0': tiles_image_dict.rest_stop,},
                        '#': {'0': tiles_image_dict.gnawed_bones,},
                        '$': {'0': tiles_image_dict.animal_rest_stop,},
                        }
        if icon_tile in image_dict and type_tile in image_dict[icon_tile]:
            return image_dict[icon_tile][type_tile]

        else:
            return tiles_image_dict.warning

    def image_dict2(self, icon, tile_type, tiles_image_dict):
        icon_dict =   {
                        'j': tiles_image_dict.dune_0,
                        's': tiles_image_dict.seashell_0,
                        '.': tiles_image_dict.sand,
                        ',': tiles_image_dict.dry_grass_0,
                        'o': tiles_image_dict.stones_0,
                        'S': tiles_image_dict.stones_2,
                        'A': tiles_image_dict.bump_0,
                        '▲': tiles_image_dict.hills_0,
                        'i': tiles_image_dict.cactus_0,
                        ':': tiles_image_dict.saline_1_0,
                        ';': tiles_image_dict.saline_2,
                        '„': tiles_image_dict.grass_0,
                        'u': tiles_image_dict.tall_grass_0,
                        'ü': tiles_image_dict.prickly_grass,
                        'F': tiles_image_dict.dry_tree_0,
                        'P': tiles_image_dict.live_tree,
                        '~': tiles_image_dict.water_1,
                        '`': tiles_image_dict.salty_water_0,
                        'C': tiles_image_dict.canyons_0,
                        'R': tiles_image_dict.canyons_1,
                        '☺': tiles_image_dict.person,
                        '☻': tiles_image_dict.enemy_riffleman,
                        'c': tiles_image_dict.enemy_coyot,
                        '8': tiles_image_dict.human_traces,
                        '%': tiles_image_dict.horse_traces,
                        '@': tiles_image_dict.animal_traces,
                        '/': tiles_image_dict.camp,
                        '+': tiles_image_dict.bonfire,
                        '№': tiles_image_dict.rest_stop,
                        '#': tiles_image_dict.gnawed_bones,
                        '$': tiles_image_dict.animal_rest_stop,
                        }
        if icon in icon_dict:
            return icon_dict[icon]
        else:
            return tiles_image_dict.warning




def load_tile_table(filename, width, height):
    """
        Режет большой тайлсет на спрайты тайлов
    """
    image = pygame.image.load(filename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, image_width/width):
        line = []
        tile_table.append(line)
        for tile_y in range(0, image_height/height):
            rect = (tile_x*width, tile_y*height, width, height)
            line.append(image.subsurface(rect))
    return tile_table

def print_minimap(global_map, person, go_to_print, enemy_list):
    """
        Печатает упрощенную схему глобальной карты по биомам
    """

    minimap = []
    for number_line in range(len(global_map)):
        print_line = ''
        for biom in range(len(global_map[number_line])):
            enemy_here = '--'
            for enemy in range(len(enemy_list)):
                if number_line == enemy_list[enemy].global_position[0] and biom == enemy_list[enemy].global_position[1]:
                    enemy_here = enemy_list[enemy].icon
            if number_line == person.global_position[0] and biom == person.global_position[1]:
                go_to_print.text2 = global_map[number_line][biom].name
                go_to_print.text3 = [global_map[number_line][biom].temperature, 36.6]
                print_line += '☺'
            elif enemy_here != '--':
                print_line += enemy_here
            else:
                print_line += global_map[number_line][biom].icon + ''
        minimap.append((print_line))
    go_to_print.biom_map = minimap


def master_pygame_draw(person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list, screen, tiles_image_dict,
                                                               minimap, all_sprites, dynamic_sprites, minimap_sprite):
    """
        Работает с классом Interfase, содержащимся в go_to_print

        Формирует 4 слоя итогового изображения:
            1) Ландшафт
            2) Следы активностей
            3) Персонажи
            4) Небо (опционально)

        Отрисовывает в следующем порядке:
            1) Ландшафт
            2) Следы активностей
            3) Персонажи
            4) Персонаж игрока
            5) Небо (опционально)


        ОПРЕДЕЛЕНИЕ ТОРМОЗОВ
        Проскакивают значения:
        2.2022461891174316 - test1
        1.058335542678833 - test1_2
        2.0575599670410156 - end
        1.0473484992980957 - test1_2
        3.0611751079559326 - test_1_end
        4.554834604263306 - test2_1

        РЕАЛИЗОВАТЬ:
        При смене кадра не перессчитывать весь кадр, а убирать или добавлять только крайние линии или столбцы.
    """
    size_tile = 30 # Настройка размера тайлов игрового окна
    size_tile_minimap = 15 # Настройка размера тайлов миникаты

    
    static_sprites = pygame.sprite.Group()
    
    if person.pass_draw_move:
        person.pass_draw_move -= 1
        for sprite in all_sprites:
            if person.direction == 'left':
                sprite.rect.left +=10
            elif person.direction == 'right':
                sprite.rect.left -=10
            elif person.direction == 'up':
                sprite.rect.top +=10
            elif person.direction == 'down':
                sprite.rect.top -=10
        for sprite in dynamic_sprites:
            if person.direction == 'left':
                sprite.rect.left +=10
            elif person.direction == 'right':
                sprite.rect.left -=10
            elif person.direction == 'up':
                sprite.rect.top +=10
            elif person.direction == 'down':
                sprite.rect.top -=10

            if sprite.direction == 'left':
                sprite.rect.left +=10
            elif sprite.direction == 'right':
                sprite.rect.left -=10
            elif sprite.direction == 'up':
                sprite.rect.top +=10
            elif sprite.direction == 'down':
                sprite.rect.top -=10
            
    else:

        dynamic_sprites = pygame.sprite.Group()

        #Определение смещения
        offset_y = 0
        offset_x = 0
        if person.direction == 'left':
            offset_x -= size_tile
        elif person.direction == 'right':
            offset_x += size_tile
        elif person.direction == 'up':
            offset_y -= size_tile
        elif person.direction == 'down':
            offset_y += size_tile
        
        person.pass_draw_move = 3
   
        if person.recalculating_the_display: #Если надо перессчитывать весь экран

            minimap_sprite = pygame.sprite.Group()
            
            landscape_layer = landscape_layer_calculations(person, chunk_size, go_to_print)

            activity_layer = entities_layer_calculations(person, chunk_size, go_to_print, activity_list)

            #sky_layer = sky_layer_calculations(chunk_size)

            all_sprites = pygame.sprite.Group()
            
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    all_sprites.add(Image_tile(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile, tiles_image_dict,
                                               landscape_layer[number_line][number_tile].icon,
                                               landscape_layer[number_line][number_tile].type))
                    if landscape_layer[number_line][number_tile].level > 1:
                        all_sprites.add(Level_tiles(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile,
                                                    landscape_layer[number_line][number_tile].level - 1))
            
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if activity_layer[number_line][number_tile].icon != '0':
                        all_sprites.add(Image_tile(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile, tiles_image_dict,
                                               activity_layer[number_line][number_tile].icon,
                                               activity_layer[number_line][number_tile].type))

            #Отрисовка зон доступности
            if person.test_visible:
                for number_line in range(chunk_size):
                    for number_tile in range(chunk_size):
                        all_sprites.add(Island_friends(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile,
                                               landscape_layer[number_line][number_tile].vertices))


            #for number_line in range(chunk_size):
            #    for number_tile in range(chunk_size):
            #        if sky_layer[number_line][number_tile].icon != '0':
            #            all_sprites.add(Image_tile(number_tile*size_tile, number_line*size_tile, size_tile, tiles_image_dict,
            #                                   sky_layer[number_line][number_tile].icon,
            #                                   sky_layer[number_line][number_tile].type))      



        else: #Если надо перессчитывать только строки и столбцы
        
            landscape_layer = landscape_layer_calculations(person, chunk_size, go_to_print)

            activity_layer = entities_layer_calculations(person, chunk_size, go_to_print, activity_list)
            
            for number_sprite, sprite in enumerate(all_sprites):
                if person.direction == 'left':
                    if sprite.rect.left == size_tile*(chunk_size - 1):
                        sprite.kill()
                elif person.direction == 'right':
                    if sprite.rect.left == 0:
                        sprite.kill()
                elif person.direction == 'up':
                    if sprite.rect.top == size_tile*(chunk_size - 1):
                        sprite.kill()
                elif person.direction == 'down':
                    if sprite.rect.top == 0:
                        sprite.kill()

            for number_len in range(len(landscape_layer)):
                number_line = 0
                number_tile = 0
                if person.direction == 'left':
                    number_line = number_len
                    number_tile = 0
                elif person.direction == 'right':
                    number_line = number_len
                    number_tile = chunk_size - 1
                elif person.direction == 'up':
                    number_line = 0
                    number_tile = number_len
                elif person.direction == 'down':
                    number_line = chunk_size - 1
                    number_tile = number_len
                #Отрисовка рассчитаных линий и столбцов    
                all_sprites.add(Image_tile(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile, tiles_image_dict,
                                               landscape_layer[number_line][number_tile].icon,
                                               landscape_layer[number_line][number_tile].type))
                if landscape_layer[number_line][number_tile].level > 1:
                    all_sprites.add(Level_tiles(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile,
                                                    landscape_layer[number_line][number_tile].level - 1))
                if activity_layer[number_line][number_tile].icon != '0':
                    all_sprites.add(Image_tile(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile, tiles_image_dict,
                                               activity_layer[number_line][number_tile].icon,
                                               activity_layer[number_line][number_tile].type))

        # Печать миникарты
                    
        minimap_sprite.add(All_tiles(person.global_position[1]*size_tile_minimap + (26*size_tile), person.global_position[0]*size_tile_minimap,
                                      size_tile_minimap, tiles_image_dict, '☺', '0'))
        for enemy in enemy_list:
            minimap_sprite.add(All_tiles(enemy.global_position[0]*size_tile_minimap + (26*size_tile), enemy.global_position[0]*size_tile_minimap,
                                          size_tile_minimap, tiles_image_dict, enemy.icon, enemy.type))

        #Отрисовка температуры на миникарте
        if person.test_visible:
            for number_minimap_line, minimap_line in enumerate(minimap):
                for number_minimap_tile, minimap_tile in enumerate(minimap_line):
                    minimap_sprite.add(Minimap_temperature(number_minimap_tile*size_tile_minimap + (26*size_tile), number_minimap_line*size_tile_minimap,
                                                            size_tile_minimap, minimap_tile.temperature))
        #Отрисовка НПЦ
        entities_layer = entities_layer_calculations(person, chunk_size, go_to_print, enemy_list) #Использование функции для отображения активностей
                    
        for number_line in range(chunk_size):
            for number_tile in range(chunk_size):
                if entities_layer[number_line][number_tile].icon != '0':
                    enemy_offset_x = 0
                    enemy_offset_y = 0
                    if entities_layer[number_line][number_tile].direction == 'left':
                        enemy_offset_x = 0 - size_tile

                    elif entities_layer[number_line][number_tile].direction == 'right':
                        enemy_offset_x = size_tile

                    elif entities_layer[number_line][number_tile].direction == 'up':
                        enemy_offset_y = 0 - size_tile

                    elif entities_layer[number_line][number_tile].direction == 'down':
                        enemy_offset_y = size_tile

                    enemy_sprite = Image_tile(number_tile*size_tile + offset_x + enemy_offset_x, number_line*size_tile + offset_y + enemy_offset_y,
                                              size_tile, tiles_image_dict, entities_layer[number_line][number_tile].icon,
                                              entities_layer[number_line][number_tile].type)
                    enemy_sprite.direction = entities_layer[number_line][number_tile].direction

                    dynamic_sprites.add(enemy_sprite)
                    
    
    #Отрисовка персонажа
    static_sprites.add(Image_tile(chunk_size//2*size_tile, chunk_size//2*size_tile, size_tile, tiles_image_dict, '☺', '0'))
    
    #screen.fill((255, 255, 255))
    #minimap.draw(screen)
    
    #all_sprites.draw(screen)

    
    return screen, all_sprites, dynamic_sprites, static_sprites, minimap_sprite

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    РАСЧЁТ ПРОПУСКА ХОДА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

class Interaction:
    """ Содержит описание взаимодействия. НЕ ИСПОЛЬЗУЕТСЯ"""
    
    def __init__(self, perform, whom, type_interaction, description):
        self.perform = perform
        self.whom = whom
        self.type = type_interaction
        self.description = description

def master_pass_step(person):
    """
        Считает пропуски хода для плавного перемещения персонажа
    """
    if person.pass_draw_move:
        person.person_pass_step = True
        person.enemy_pass_step = True
    else:
        person.person_pass_step = False
        person.enemy_pass_step = False

def all_pass_step_calculations(person, enemy_list, mode_action, interaction):
    """
        Рассчитывает пропуск хода персонажа и NPC и кем он осуществляется.
    """
    if mode_action == 'move':
        person.person_pass_step = 0
        person.enemy_pass_step = 0
    if mode_action == 'pointer':
        person.person_pass_step = 0
        person.enemy_pass_step = 1
    if mode_action == 'gun':
        person.person_pass_step = 0
        person.enemy_pass_step = 1

def new_step_calculation(enemy_list, person, step):
    """
        Считает когда начинается новый шаг
    """
    new_step = True
    #person.person_pass_step = False
    #for enemy in enemy_list:
    #    if (enemy.on_the_screen and enemy.steps_to_new_step):
    #        new_step = False
    #        person.person_pass_step = True
    if new_step:
        step += 1
            
    return new_step, step

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    УПРАВЛЯЮЩИЙ БЛОК
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
def main_loop():
    """
        Здесь работает игровое меню
        
    """
    
    global_region_grid = 3
    region_grid = 3
    chunks_grid = 3
    mini_region_grid = 5
    tile_field_grid = 5

    chunk_size = mini_region_grid * tile_field_grid #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    
    pygame.init()
    screen = pygame.display.set_mode((1200, 750), FULLSCREEN | DOUBLEBUF)
    pygame.display.set_caption("My Game")

    
    tiles_image_dict = Tiles_image_dict() #Загружаются тайлы

    while main_loop:

        global_map, raw_minimap = map_generator.master_map_generate(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid)
        
        person = Person([2, 2], [2, 2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
        calculation_assemblage_point(global_map, person, chunk_size)
        enemy_list = [Horseman([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 5), Horseman([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 5),
                      Riffleman([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 2), Coyot([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 0)]
        world = World() #Описание текущего состояния игрового мира

        #Создание миникарты
        minimap = pygame.sprite.Group()
        size_tile = 30
        size_tile_minimap = 15
        for number_minimap_line, raw_minimap_line in enumerate(raw_minimap):
            for number_minimap_tile, minimap_tile in enumerate(raw_minimap_line):
                minimap.add(All_tiles(number_minimap_tile*size_tile_minimap + (26*size_tile), number_minimap_line*size_tile_minimap, size_tile_minimap,
                                        tiles_image_dict, minimap_tile.icon, minimap_tile.type))


        game_loop(global_map, person, chunk_size, enemy_list, world, screen, tiles_image_dict, minimap, raw_minimap)
        

def game_loop(global_map:list, person, chunk_size:int, enemy_list:list, world, screen, tiles_image_dict, minimap, raw_minimap):
    """
        Здесь происходят все игровые события
        
    """
    go_to_print = Interfase([], [], True, '', '', '', '', '', '', '', '', '', '')
    activity_list = []
    step = 0
    print('game_loop запущен')
    global changing_step
    mode_action = 'move'
    clock = pygame.time.Clock()#
    game_fps = 100#
    
    all_sprites = pygame.sprite.Group()
    dynamic_sprites = pygame.sprite.Group()
    minimap_sprite  = pygame.sprite.Group()

    screen.fill((255, 255, 255))

    minimap.draw(screen)

    pygame.display.flip()

    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    
  
    while game_loop:
        clock.tick(game_fps)
        interaction = []
        world.npc_path_calculation = False #Сброс предыдущего состояния поиска пути NPC персонажами
        master_pass_step(person)
        new_step, step = new_step_calculation(enemy_list, person, step)
        if not person.person_pass_step:
            mode_action = master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step, enemy_list)
        start = time.time() #проверка времени выполнения
        calculation_assemblage_point(global_map, person, chunk_size) # Рассчёт динамического чанка
        #all_pass_step_calculations(person, enemy_list, mode_action, interaction)
        if not person.enemy_pass_step:
            master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step, world)
        test1 = time.time() #проверка времени выполнения
        screen, all_sprites, dynamic_sprites, static_sprites, minimap_sprite = master_pygame_draw(person, chunk_size, go_to_print,
                                    global_map, mode_action, enemy_list, activity_list, screen, tiles_image_dict, raw_minimap, all_sprites,
                                    dynamic_sprites, minimap_sprite)
        test2 = time.time() #проверка времени выполнения
        
        #Создание новой группы
        print_sprites = pygame.sprite.Group()
        for sprite in all_sprites:
            print_sprites.add(sprite)
        for sprite in dynamic_sprites:
            print_sprites.add(sprite)
        for sprite in static_sprites:
            print_sprites.add(sprite)
        for sprite in minimap_sprite:
            print_sprites.add(sprite)

        print_sprites.draw(screen)
        
        #print_step = fontObj.render((f"step = {step}, person.person_pass_step - {person.person_pass_step}, person.pass_draw_move - {person.pass_draw_move}"), True, (0, 0, 0), (255, 255, 255))
        #print_step_rect = print_step.get_rect()
        #print_step_rect.center = (30*34, 15*29)
        #screen.blit(print_step, print_step_rect)

        end = time.time() #проверка времени выполнения
        
        print_time = f"{round(test1 - start, 4)} - персонажи \n {round(test2 - test1, 4)} - отрисовка \n {round(end - start, 4)} - общее время \n {len(all_sprites)} - спрайтов"

        textSurfaceObj = fontObj.render(print_time, True, (0, 0, 0), (255, 255, 255))
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (30*34, 15*31)
        screen.blit(textSurfaceObj, textRectObj)            
        pygame.display.flip()


        #person.recalculating_the_display = False
    

def main():
    """
        Запускает игру
        
    """
    chunk_size = 25         #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    value_region_box = 5    #Размер стороны квадрата регионов и количество локаций в регионах.
    grid = 5                #На сколько делится размер чанка. Должно быть кратно размеру игрового экрана.
    frame_size = [35, 40]   #Размер одного кадра [высота, ширина]. УСТАРЕЛО

    print('Подождите, генерируется локация для игры')
    #global_map = old_map_generator.master_generate(value_region_box, chunk_size, grid)

    #                                              global_region_grid | region_grid | chunks_grid | mini_region_grid | tile_field_grid
    global_map, minimap = map_generator.master_map_generate(       3,                  3,          3,              5,                  5)
    
    person = Person([value_region_box//2, value_region_box//2], [chunk_size//2, chunk_size//2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
    calculation_assemblage_point(global_map, person, chunk_size)
    enemy_list = [Horseman([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 5), Horseman([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 5),
                  Riffleman([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 2), Coyot([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 0)]
    world = World() #Описание текущего состояния игрового мира

    pygame.init()
    screen = pygame.display.set_mode((1200, 750))
    pygame.display.set_caption("My Game")

    
    tiles_image_dict = Tiles_image_dict() #Загружаются тайлы

    game_loop(global_map, person, chunk_size, enemy_list, world, screen, tiles_image_dict, minimap)
    
    print('Игра окончена!')

main_loop()
    

