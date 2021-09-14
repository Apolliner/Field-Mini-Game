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

    РЕАЛИЗОВАТЬ:

    1)Взрывчатка и разрушения. Добавить тайлам параметры веса и устойчивости. При воздействии, рассчитывать разрушение и/или сползание.
    2)Так как под тайлами фактически не идет просчёт уровней ниже, добавить им описание коренной породы, которая обнажится при разрушении.
    3)Вся работа с координатами через координаты в формате world_position, то есть, в формате мировых координат.
    4)Переписать всё управление персонажами в отдельный модуль, заранее проработав все необходимые им механики.

    СПИСОК ИЗВЕСТНЫХ БАГОВ:
    При оставлении персонажем активности в 0х координатах, активность получает странные координаты и не остаётся под персонажем
    (в частности, лёгкие шаги). #ИСПРАВЛЕНО

    ТЕМАТИКА:
    Всё, что мне нравится. Персонажи как в хороший плохой злой, вяленое конское мясо и гремучие змеи!

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

    ЗАГРУЗКА ИГРОВЫХ РЕСУРСОВ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
class Fast_image_tile(pygame.sprite.Sprite):
    """ Содержит заранее созданную поверхность спрайта """
    def __init__(self, image_tile):
        pygame.sprite.Sprite.__init__(self)
        self.image = image_tile
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.left = 0
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)

def loading_all_sprites():
    """
        Создаёт поверхности всех спрайтов до начала игры, для ускорения вывода очередного кадра на экран.
    """
    sprites_dict =   {
                    'j': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_1.jpg'))),
                         },
                    's': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_seashell_0.jpg')))},
                    '.': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_sand.jpg')))},
                    ',': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_5.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_0.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_1.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_5.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                          },
                    'o': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_0.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                          },
                    'A': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_1.jpg'))),
                         },
                    '▲': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_F.jpg'))),
                            'G': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_G.jpg'))),
                            'H': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_H.jpg'))),
                            'I': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_I.jpg'))),
                            'J': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_J.jpg'))),
                            'K': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_K.jpg'))),
                            'L': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_L.jpg'))),
                            'M': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_M.jpg'))),
                            'N': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_N.jpg'))),
                            'O': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_O.jpg'))),
                            'P': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_P.jpg'))),
                            'Q': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_Q.jpg'))),
                            'R': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_R.jpg'))),
                            'S': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_S.jpg'))),
                            'T': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_T.jpg'))),
                            'U': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_U.jpg'))),
                         },
                    'i': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_3.jpg'))),
                          },
                    ':': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_F.jpg'))),
                         },
                    ';': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_2.jpg')))},
                    '„': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_0.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                          },
                    'u': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_1.jpg'))),
                         },
                    'ü': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_prickly_grass.jpg')))},
                    'F': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_7.jpg'))),
                         },
                    'P': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_live_tree.jpg')))},
                    '~': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_F.jpg'))),
                            'G': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_G.jpg'))),
                            'H': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_H.jpg'))),
                            'I': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_I.jpg'))),
                            'J': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_J.jpg'))),
                            'K': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_K.jpg'))),
                            'L': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_L.jpg'))),
                            'M': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_M.jpg'))),
                            'N': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_N.jpg'))),
                            'O': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_O.jpg'))),
                            'P': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_P.jpg'))),
                            'Q': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_Q.jpg'))),
                            'R': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_R.jpg'))),
                            'S': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_S.jpg'))),
                            'T': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_T.jpg'))),
                            'U': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_U.jpg'))),
                         },
                    'f': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_F.jpg'))),
                            'G': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_G.jpg'))),
                            'H': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_H.jpg'))),
                            'I': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_I.jpg'))),
                            'J': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_J.jpg'))),
                            'K': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_K.jpg'))),
                            'L': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_L.jpg'))),
                            'M': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_M.jpg'))),
                            'N': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_N.jpg'))),
                            'O': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_O.jpg'))),
                            'P': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_P.jpg'))),
                            'Q': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_Q.jpg'))),
                            'R': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_R.jpg'))),
                            'S': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_S.jpg'))),
                            'T': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_T.jpg'))),
                            'U': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_U.jpg'))),
                         },
                    '`': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_F.jpg'))),
                            'G': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_G.jpg'))),
                            'H': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_H.jpg'))),
                            'I': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_I.jpg'))),
                            'J': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_J.jpg'))),
                            'K': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_K.jpg'))),
                            'L': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_L.jpg'))),
                            'M': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_M.jpg'))),
                            'N': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_N.jpg'))),
                            'O': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_O.jpg'))),
                            'P': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_P.jpg'))),
                            'Q': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_Q.jpg'))),
                            'R': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_R.jpg'))),
                            'S': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_S.jpg'))),
                            'T': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_T.jpg'))),
                            'U': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_U.jpg'))),
                         },
                    'C': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_0.jpg'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_1.jpg'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_2.jpg'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_3.jpg'))),
                            '4': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_4.jpg'))),
                            '5': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_5.jpg'))),
                            '6': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_6.jpg'))),
                            '7': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_7.jpg'))),
                            '8': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_8.jpg'))),
                            '9': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_9.jpg'))),
                            'A': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_A.jpg'))),
                            'B': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_B.jpg'))),
                            'C': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_C.jpg'))),
                            'D': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_D.jpg'))),
                            'E': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_E.jpg'))),
                            'F': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_F.jpg'))),
                            'G': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_G.jpg'))),
                            'H': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_H.jpg'))),
                            'I': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_I.jpg'))),
                            'J': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_J.jpg'))),
                            'K': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_K.jpg'))),
                            'L': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_L.jpg'))),
                            'M': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_M.jpg'))),
                            'N': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_N.jpg'))),
                            'O': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_O.jpg'))),
                            'P': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_P.jpg'))),
                            'Q': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_Q.jpg'))),
                            'R': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_R.jpg'))),
                            'S': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_S.jpg'))),
                            'T': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_T.jpg'))),
                            'U': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_U.jpg'))),
                         },
                    '☺': {
                            '0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_0.png'))),
                            '1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_0.png'))),
                            '2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_0.png'))),
                            '3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_0.png'))),
                            'l0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_0.png'))),
                            'l1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_1.png'))),
                            'l2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_2.png'))),
                            'l3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_3.png'))),
                            'r0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_0.png'))),
                            'r1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_1.png'))),
                            'r2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_2.png'))),
                            'r3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_3.png'))),
                            'd0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_0.png'))),
                            'd1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_1.png'))),
                            'd2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_2.png'))),
                            'd3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_3.png'))),
                            'u0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_0.png'))),
                            'u1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_1.png'))),
                            'u2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_2.png'))),
                            'u3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_3.png'))),

                          },
                    '☻': {
                            
                            'l0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_0.png'))),
                            'l1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_1.png'))),
                            'l2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_2.png'))),
                            'l3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_3.png'))),
                            'r0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_0.png'))),
                            'r1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_1.png'))),
                            'r2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_2.png'))),
                            'r3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_3.png'))),
                            'd0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_0.png'))),
                            'd1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_1.png'))),
                            'd2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_2.png'))),
                            'd3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_3.png'))),
                            'u0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_0.png'))),
                            'u1': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_1.png'))),
                            'u2': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_2.png'))),
                            'u3': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_3.png'))),
                            
                            'h': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_horseman.png'))),
                            
                         },
                    'co': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_coyot.png')))},
                    'un': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_warning.jpg')))},
                    '8': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_human_traces.png')))},
                    '%': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_horse_traces.png')))},
                    '@': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_animal_traces.png')))},
                    '/': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_camp.png')))},
                    '+': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bonfire.png')))},
                    '№': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_rest_stop.png')))},
                    '#': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_gnawed_bones.png')))},
                    '$': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_animal_rest_stop.png')))},
                    'W': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_warning.jpg')))},
                    '=': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_faint_traces.png')))},
                    'П': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'pointer_0.png')))},
                    'w': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_waypoint.png')))},
                    'e': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_explosion.png')))},
                    'd': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dust.png')))},
                    'stairs': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stairs.png')))},
                    'Sn': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_snake.png')))},
                    'Rs': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_rattlesnake.png')))},
                    'Bi': {'0': Fast_image_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bird.png')))},
                    }
    return sprites_dict
class Fast_minimap_tile(pygame.sprite.Sprite):
    """ Содержит заранее созданную поверхность спрайта """
    def __init__(self, image_tile):
        pygame.sprite.Sprite.__init__(self)
        self.img = image_tile
        self.image = pygame.transform.scale(self.img, (15, 15))
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.left = 0
        self.speed = 0
    def draw(self, surface):
        surface.blit(self.image, self.rect)

def minimap_dict_create():

        minimap_dict =  {
                        'j': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dune_1.jpg'))),
                             },
                        '.': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_sand.jpg')))},
                        ',': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_5.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_0.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_1.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_5.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_2.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_3.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_grass_4.jpg'))),
                             },
                        'S': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_0.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_4.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_2.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_3.jpg'))),
                             },
                        'A': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bump_1.jpg'))),

                             },
                        '▲': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_7.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_8.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_9.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_A.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_B.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_C.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_D.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_E.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_F.jpg'))),
                                'G': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_G.jpg'))),
                                'H': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_H.jpg'))),
                                'I': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_I.jpg'))),
                                'J': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_J.jpg'))),
                                'K': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_K.jpg'))),
                                'L': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_L.jpg'))),
                                'M': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_M.jpg'))),
                                'N': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_N.jpg'))),
                                'O': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_O.jpg'))),
                                'P': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_P.jpg'))),
                                'Q': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_Q.jpg'))),
                                'R': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_R.jpg'))),
                                'S': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_S.jpg'))),
                                'T': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_T.jpg'))),
                                'U': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_hills_U.jpg'))),
                             },
                        'i': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_cactus_3.jpg'))),
                             },
                        ';': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_7.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_8.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_9.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_A.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_B.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_C.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_D.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_E.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_1_F.jpg'))),
                             },
                        ':': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_saline_2.jpg')))},
                        '„': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_0.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_4.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_2.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_3.jpg'))),
                             },
                        'u': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_tall_grass_1.jpg'))),
                             },
                        'ü': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_prickly_grass.jpg')))},
                        'F': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_dry_tree_7.jpg'))),
                             },
                        'P': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_live_tree.jpg')))},
                        '~': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_7.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_8.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_9.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_A.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_B.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_C.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_D.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_E.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_F.jpg'))),
                                'G': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_G.jpg'))),
                                'H': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_H.jpg'))),
                                'I': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_I.jpg'))),
                                'J': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_J.jpg'))),
                                'K': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_K.jpg'))),
                                'L': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_L.jpg'))),
                                'M': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_M.jpg'))),
                                'N': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_N.jpg'))),
                                'O': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_O.jpg'))),
                                'P': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_P.jpg'))),
                                'Q': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_Q.jpg'))),
                                'R': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_R.jpg'))),
                                'S': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_S.jpg'))),
                                'T': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_T.jpg'))),
                                'U': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_water_U.jpg'))),
                             },
                        'f': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_7.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_8.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_9.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_A.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_B.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_C.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_D.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_E.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_F.jpg'))),
                                'G': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_G.jpg'))),
                                'H': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_H.jpg'))),
                                'I': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_I.jpg'))),
                                'J': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_J.jpg'))),
                                'K': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_K.jpg'))),
                                'L': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_L.jpg'))),
                                'M': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_M.jpg'))),
                                'N': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_N.jpg'))),
                                'O': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_O.jpg'))),
                                'P': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_P.jpg'))),
                                'Q': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_Q.jpg'))),
                                'R': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_R.jpg'))),
                                'S': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_S.jpg'))),
                                'T': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_T.jpg'))),
                                'U': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_ford_river_U.jpg'))),
                             },
                        'C': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_0.jpg'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_1.jpg'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_2.jpg'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_3.jpg'))),
                                '4': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_4.jpg'))),
                                '5': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_5.jpg'))),
                                '6': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_6.jpg'))),
                                '7': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_7.jpg'))),
                                '8': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_8.jpg'))),
                                '9': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_9.jpg'))),
                                'A': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_A.jpg'))),
                                'B': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_B.jpg'))),
                                'C': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_C.jpg'))),
                                'D': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_D.jpg'))),
                                'E': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_E.jpg'))),
                                'F': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_F.jpg'))),
                                'G': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_G.jpg'))),
                                'H': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_H.jpg'))),
                                'I': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_I.jpg'))),
                                'J': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_J.jpg'))),
                                'K': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_K.jpg'))),
                                'L': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_L.jpg'))),
                                'M': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_M.jpg'))),
                                'N': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_N.jpg'))),
                                'O': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_O.jpg'))),
                                'P': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_P.jpg'))),
                                'Q': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_Q.jpg'))),
                                'R': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_R.jpg'))),
                                'S': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_S.jpg'))),
                                'T': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_T.jpg'))),
                                'U': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_canyons_U.jpg'))),
                             },
                        '☺': {
                                '0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_0.png'))),
                                '1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_0.png'))),
                                '2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_0.png'))),
                                '3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_0.png'))),
                                'l0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_0.png'))),
                                'l1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_1.png'))),
                                'l2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_2.png'))),
                                'l3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_left_3.png'))),
                                'r0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_0.png'))),
                                'r1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_1.png'))),
                                'r2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_2.png'))),
                                'r3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_right_3.png'))),
                                'd0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_0.png'))),
                                'd1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_1.png'))),
                                'd2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_2.png'))),
                                'd3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_down_3.png'))),
                                'u0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_0.png'))),
                                'u1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_1.png'))),
                                'u2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_2.png'))),
                                'u3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_person_up_3.png'))),

                             },
                        '☻': {
                                
                                'l0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_0.png'))),
                                'l1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_1.png'))),
                                'l2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_2.png'))),
                                'l3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_left_3.png'))),
                                'r0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_0.png'))),
                                'r1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_1.png'))),
                                'r2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_2.png'))),
                                'r3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_right_3.png'))),
                                'd0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_0.png'))),
                                'd1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_1.png'))),
                                'd2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_2.png'))),
                                'd3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_3.png'))),
                                'u0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_0.png'))),
                                'u1': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_1.png'))),
                                'u2': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_2.png'))),
                                'u3': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_up_3.png'))),
                                
                                'h': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_horseman.png'))),
                                
                             },
                        'co': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_coyot.png')))},
                        'un': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_warning.jpg')))},
                        'Sn': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_snake.png')))},
                        'Rs': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_rattlesnake.png')))},
                        'Bi': {'0': Fast_minimap_tile(pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bird.png')))},
                        }
        return minimap_dict

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
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices', 'world_vertices')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1
        self.world_vertices = -2
        
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
                        '`': ['солёная вода', 20],
                        'f': ['брод', 7],
                        'C': ['каньон', 7],
                        '??': ['ничего', 10],
                        }
        return ground_dict[icon][number]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["icon"] = self.icon
        state["description"] = self.description
        state["list_of_features"] = self.list_of_features
        state["price_move"] = self.price_move
        state["type"] = self.type
        state["level"] = self.level
        state["stairs"] = self.stairs
        state["vertices"] = self.vertices
        state["world_vertices"] = self.world_vertices
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.icon = state["icon"] 
        self.description = state["description"]
        self.list_of_features = state["list_of_features"]
        self.price_move = state["price_move"]
        self.type = state["type"]
        self.level = state["level"]
        self.stairs = state["stairs"]
        self.vertices = state["vertices"]
        self.world_vertices = state["world_vertices"]
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
            
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ИГРОВЫХ СОБЫТИЙ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, world, global_interaction):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    interaction_processing(global_map, interaction, enemy_list, step, chunk_size, activity_list, global_interaction)
    activity_list_check(activity_list, step)
    master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, world)
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
                    enemy.target = []
                    enemy.follow = interact[1]
                    enemy.waypoints = []
                    enemy.local_waypoints = []
                    logging.debug(f"{step}: {enemy.name_npc} назначено следование {enemy.follow}")

                    
            if interact[0] == 'view_waypoints':
                for enemy in enemy_list:
                    if enemy.local_waypoints:
                        for waypoint in enemy.local_waypoints: #[local_y, local_x, vertices, [global_y, global_x]]
                            activity_list.append(Action_in_map('waypoint', step, waypoint[3], [waypoint[0], waypoint[1]],
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

class Global_interact:
    """ Описание глобального события """
    def __init__(self, name, description, global_position, local_position):
        self.name = name
        self.description = description
        self.global_position = global_position
        self.local_position = local_position
        self.step = 0

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
                local_position = [explosion.local_position[0] - len(destruction_draw)//2 + number_line,
                                  explosion.local_position[1] - len(destruction_draw)//2 + number_tile]
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
            local_position = [explosion.local_position[0] - len(explosion_draw)//2 + number_line,
                              explosion.local_position[1] - len(explosion_draw)//2 + number_tile]
            if tile == 'e':
                activity_list.append(Action_in_map('explosion', step, explosion.global_position, local_position, chunk_size, 'динамит'))
            elif tile == 'd':
                activity_list.append(Action_in_map('dust', step, explosion.global_position, local_position, chunk_size, 'последствия взрыва'))

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
                        'waypoint':         ['w', 'вейпоинт',                    50,       False],
                        'explosion':        ['e', 'взрыв',                        1,        True],
                        'dust':             ['d', 'пыль',                        10,        True],
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

class Creature:
    """
    Мелкие, необсчитываемые за кадром существа и противники

    РЕАЛИЗОВАТЬ:
    1) Изменение режима передвижения с полёта, на хождение по земле.
    2) Изменение высоты полёта птиц, их иконки и тени под ними
    """
    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map, person_description, speed, deactivation_tiles, fly):
        self.global_position = global_position
        self.local_position = local_position
        self.waypoints = [] #На будущее
        self.local_waypoints = [] #На будущее
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
        self.world_position = [self.local_position[0] + self.global_position[0]*chunk_size, self.local_position[1] + self.global_position[1]*chunk_size]

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
                            False), #fly
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
                            False), #fly
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
                            True), #fly
                'snake_unknown':  Creature(global_position, local_position,
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
                            True), #fly
                }
    if key in npc_dict:
        return npc_dict[key]
    else:
        return npc_dict['snake_unknown']
        
class Enemy:
    """ Отвечает за всех NPC """
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map, person_description, speed):
        self.global_position = global_position
        self.local_position = local_position
        self.action_points = 10
        self.dynamic_chunk = False #УСТАРЕЛО
        self.waypoints = []
        self.local_waypoints = [] # [local_y, local_x, vertices, [global_y, global_x]]
        self.alarm = False
        self.pass_step = 0
        self.on_the_screen = False
        self.steps_to_new_step = 1
        self.level = 0
        self.vertices = 0
        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
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
        self.world_position = [self.local_position[0] + self.global_position[0]*chunk_size, self.local_position[1] + self.global_position[1]*chunk_size]
        
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
                            random.choice(['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок']),
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
                'coyot':    Enemy(global_position, local_position,
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
                'horse':    Enemy(global_position, local_position,
                            'horse',
                            random.choice(['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь']),       
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
                'unknown':  Enemy(global_position, local_position,
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
        
def master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, world):
    """
        Здесь происходят все события, связанные с NPC

        self.target = [] #[[global_y, global_x], vertices, [local_y, local_x]]
        self.local_waypoints = [] # [[local_y, local_x], vertices, [global_y, global_x]]
    """
    delete_list = []
    for number_enemy, enemy in enumerate(enemy_list):
        enemy.direction = 'center'
        enemy.all_description_calculation()
        if not enemy.delete:
            #Если это противник 
            if isinstance(enemy, Enemy):
                
                enemy.level = global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[0]].level
                enemy.vertices = global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[1]].vertices

                #Удаление реализованного глобального вейпоинта
                if enemy.waypoints and [enemy.global_position[0], enemy.global_position[1], enemy.vertices] == enemy.waypoints[0]:
                    enemy.waypoints.pop(0)

                #Удаление реализованной цели
                if enemy.target and enemy.target == [enemy.global_position, enemy.vertices, enemy.local_position] or enemy.target == [enemy.global_position, enemy.vertices, []]:
                    enemy.target = []
                if enemy.follow:
                    enemy_following(enemy, global_map, chunk_size, activity_list, step)
                else:
                    if not world.npc_path_calculation: #Если никто не считал вейпоинты на этом шаге
                        
                        #Если есть цель, но нет локальных вейпоинтов.
                        if enemy.target and not(enemy.local_waypoints):
                            enemy_move_calculaton(global_map, enemy, step)
                            world.npc_path_calculation = True
                        #Если цели нет и нет локальных вейпоинтов
                        if not enemy.target and not enemy.local_waypoints:
                            for vertices in global_map[enemy.global_position[0]][enemy.global_position[1]].vertices:
                                if vertices.number == enemy.vertices:
                                    if vertices.connections:
                                        #Определяем позицию искомого тайла, путём выбора из точек перехода искомой зоны доступности
                                        number_target = random.randrange(len(vertices.connections))
                                        target_tiles = []
                                        for target_vertices in global_map[vertices.connections[number_target].position[0]][vertices.connections[number_target].position[1]].vertices:
                                            if target_vertices == vertices.connections[number_target].number:
                                                for connect in target_vertices.connections:
                                                    if connect.number == vertices.number:
                                                        target_tiles = random.choice(connect.tiles)
                                        #Задаётся цель из существующих координат, существующих связей и существующих тайлов
                                        enemy.target = [vertices.connections[number_target].position, vertices.connections[number_target].number, target_tiles]
                        #Если есть количество глобальных вейпоинтов больше 1 и истекают локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
                        if len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 5: 
                            enemy_move_calculaton(global_map, enemy, step)
                            world.npc_path_calculation = True
                    #Если есть локальные вейпоинты
                    if enemy.local_waypoints:
                        #Добавляются следы
                        if random.randrange(21)//18 > 0:
                            if not global_map[enemy.global_position[0]][enemy.global_position[1]].chunk[enemy.local_position[0]][enemy.local_position[1]].icon in ('f', '~'):
                                activity_list.append(Action_in_map(enemy.activity_map['move'][0][1], step, copy.deepcopy(enemy.global_position),
                                                               copy.deepcopy(enemy.local_position), chunk_size, enemy.name_npc))
                        activity_list.append(Action_in_map('faint_footprints', step, copy.deepcopy(enemy.global_position), copy.deepcopy(enemy.local_position),
                                                           chunk_size, enemy.name_npc))
                        enemy_direction_calculation(enemy)
                        enemy.global_position = enemy.local_waypoints[0][3]
                        enemy.local_position = [enemy.local_waypoints[0][0], enemy.local_waypoints[0][1]]
                        enemy.local_waypoints.pop(0)

            #Если это существо        
            if isinstance(enemy, Creature):
                if enemy.fly:
                    #Если может летать
                    enemy.fly_simple_move(chunk_size)
                else:
                    #Если ходит по земле
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
        return math.sqrt((start_point[0] - finish_point[0])**2 + (start_point[1] - finish_point[1])**2)
    
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
    return [local_position[0] + global_position[0]*chunk_size, local_position[1] + global_position[1]*chunk_size]

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
            return math.sqrt((start_point[0] - finish_point[0])**2 + (start_point[1] - finish_point[1])**2)
        except TypeError:
            print(f"!!! TypeError start_point - {start_point} | finish_point - {finish_point}")
            return 999
    logging.debug(f"{character.name_npc}: character.waypoints - {character.waypoints}")
    #Если есть глобальные вейпоинты или оба персонажа находятся на одной глобальной позиции
    if character.waypoints or character.global_position == character.follow[0].global_position or character.local_waypoints:
        logging.debug(f"{character.name_npc}: Если есть глобальные вейпоинты или оба персонажа находятся на одной глобальной позиции")
        #print(f"{character.name_npc}: character.global_position = {character.global_position}, character.follow[0].global_position - {character.follow[0].global_position}")
        if character.local_waypoints:
            #Если персонаж и преследуемый находятся на одной локации
            if character.global_position == character.follow[0].global_position:
                logging.debug(f"{character.name_npc}: Если персонаж и преследуемый находятся на одной локации")
                length = path_length(world_position_calculate(character.local_waypoints[-1][3], [character.local_waypoints[-1][0],
                                    character.local_waypoints[-1][1]], chunk_size), character.follow[0].world_position)
                #Если преследуемый персонаж ушёл от последнего локального вейпоинта дальше чем на 3 тайла
                if length > 3:
                    logging.debug(f"{character.name_npc}: Если преследуемый персонаж ушёл от последнего локального вейпоинта дальше чем на 3 тайла")
                    character.waypoints = []
                    character.local_waypoints = []
                    character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                            finish_world=character.follow[0].world_position)
                #Если преследуемый не уходил от последнего вейпоинта
                else:
                    logging.debug(f"{character.name_npc}: Если преследуемый не уходил от последнего вейпоинта")
                    length_path = path_length(character.world_position, character.follow[0].world_position)
                    if length_path >= character.follow[2]:
                        character_move(character, activity_list, step, chunk_size)
            #Если персонаж и преследуемый находятся на разных локациях
            else:
                logging.debug(f"{character.name_npc}: Если персонаж и преследуемый находятся на разных локациях")
                #Если положение последнего глобального вейпоинта равно положению преследуемого
                if character.waypoints and [character.waypoints[-1][0], character.waypoints[-1][1]] == character.follow[0].global_position:
                    logging.debug(f"{character.name_npc}: Если положение последнего глобального вейпоинта равно положению преследуемого")
                    character_move(character, activity_list, step, chunk_size)
                #Если преследуемый перешёл на другую локацию
                else:
                    logging.debug(f"{character.name_npc}: Если преследуемый перешёл на другую локацию")
                    character.waypoints = []
                    character.local_waypoints = []
                    character_a_star_master(character, global_map, chunk_size, start_world=character.world_position,
                                    finish_world=character.follow[0].world_position)
        #Если нет локальных вейпоинтов
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
        #Добавляются следы
        if random.randrange(21)//18 > 0:
            activity_list.append(Action_in_map(character.activity_map['move'][0][1], step, copy.deepcopy(character.global_position),
                                               copy.deepcopy(character.local_position), chunk_size, character.name_npc))
        activity_list.append(Action_in_map('faint_footprints', step, copy.deepcopy(character.global_position), copy.deepcopy(character.local_position),
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
    logging.debug(f"{character.name_npc}: character.global_position - {character.global_position}, finish_global - {finish_global}, start_vertices - {start_vertices}, finish_vertices - {finish_vertices}")
    #Если есть вейпоинты
    if character.waypoints:
        logging.debug(f"{character.name_npc}: Если есть вейпоинты")
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                            character.local_position, character.vertices, finish_local, finish_vertices, start_global, finish_global, True)
    
    #Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности
    elif character.global_position != finish_global or (character.global_position == finish_global and start_vertices != finish_vertices):
        logging.debug(f"{character.name_npc}: Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности")
        #Сначала считаем глобальные вейпоинты
        vertices_enemy_a_star_move_global_calculations2(global_map, character, start_global, start_vertices, finish_global, finish_vertices) # Изменить функцию
        
        #А затем локальные
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                            character.local_position, character.vertices, finish_local, finish_vertices, start_global, finish_global, True)

    #Если равны глобальные позиции и зоны доступности
    elif character.global_position == finish_global and start_vertices == finish_vertices:
        logging.debug(f"{character.name_npc}: Если равны глобальные позиции и зоны доступности")

        #Считаем только локальные вейпоинты без перехода на другую локацию
        vertices_enemy_a_star_move_local_calculations2(global_map, character,
                            start_local, start_vertices, finish_local, finish_vertices, start_global, finish_global, False)
    




def vertices_enemy_a_star_move_global_calculations2(processed_map, enemy, start_global, start_vertices, finish_global, finish_vertices):
    """
        Подготавливает запрос и вызывает алгоритм А* для передвижения по глобальной карте
    """

    start_point = [start_global[0], start_global[1], start_vertices]
    finish_point = [finish_global[0], finish_global[1], finish_vertices]

    enemy.waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, 'global', enemy)

def vertices_enemy_a_star_move_local_calculations2(global_map, enemy, start_local, start_vertices, finish_local, finish_vertices,
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
                    if connect.position == [enemy.waypoints[0][0], enemy.waypoints[0][1]] and connect.number == start_vertices:
                        finish = random.choice(connect.tiles)
                        finish_point = [finish[0], finish[1], finish_vertices]
    else:
        finish_point = [finish_local[0], finish_local[1], finish_vertices]
    
    if finish_point:
        raw_local_waypoints, success = vertices_enemy_a_star_algorithm_move_calculation(processed_map, start_point, finish_point, 'local', enemy)
        
        #В каждую путевую точку добавляется глобальная позиция этой точки
        for waypoint in raw_local_waypoints:
            if enemy.local_waypoints:
                waypoint.append(enemy.local_waypoints[-1][3])
            else:
                waypoint.append(enemy.global_position)

        logging.debug(f"{enemy.name_npc}: start_point - {start_point}, finish_point - {finish_point}, success - {success}")
        logging.debug(f"{enemy.name_npc}: raw_local_waypoints 0 - {raw_local_waypoints}")
        #Если найден путь до края локации
        if raw_local_waypoints[-1][0] == 0 or raw_local_waypoints[-1][0] == chunk_size - 1 or raw_local_waypoints[-1][1] == 0 or raw_local_waypoints[-1][1] == chunk_size - 1:
            #Добавление вейпоинта, соседнего последнему, но на другой карте и с указанием других глобальных координат
            if moving_between_locations and success:
                if [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0] - 1, global_axis[1]]:
                    raw_local_waypoints.append([len(global_map[0][0].chunk) - 1, raw_local_waypoints[-1][1], finish_vertices, enemy.waypoints[0]])
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0] + 1, global_axis[1]]:
                    raw_local_waypoints.append([0, raw_local_waypoints[-1][1], finish_vertices, enemy.waypoints[0]])
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0], global_axis[1] - 1]:
                    raw_local_waypoints.append([raw_local_waypoints[-1][0], len(global_map[0][0].chunk) - 1, finish_vertices, enemy.waypoints[0]]) 
                elif [enemy.waypoints[0][0], enemy.waypoints[0][1]] == [global_axis[0], global_axis[1] + 1]:
                    raw_local_waypoints.append([raw_local_waypoints[-1][0], 0, finish_vertices, enemy.waypoints[0]])
                    
        logging.debug(f"{enemy.name_npc}: raw_local_waypoints 1 - {raw_local_waypoints}")
        #Добавление новых вейпоинтов в конец списка
        for local_waypoint in raw_local_waypoints:
            enemy.local_waypoints.append(local_waypoint)





    
def world_position_recalculation(world_position, chunk_size):
    """
        Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
    """
    global_position = [world_position[0]//chunk_size, world_position[1]//chunk_size]
    local_position = [world_position[0]%chunk_size, world_position[1]%chunk_size]
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
    #Если есть глобальные вейпоинты, но нет локальных - то считаем локальные вейпоинты
    if enemy.waypoints and not enemy.local_waypoints and [enemy.waypoints[0][0], enemy.waypoints[0][1]] != enemy.global_position:
        logging.debug(f"{step}: {enemy.name_npc} есть глобальные вейпоинты, но нет локальных - считаем локальные вейпоинты. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[0][0], enemy.waypoints[0][1]], enemy.waypoints[0][2]], True)
    #Если глобальных вейпоинтов больше 1го и есть локальные вейпоинты, то считаются локальные вейпоинты для следующей карты.
    elif len(enemy.waypoints) > 1 and len(enemy.local_waypoints) < 3:
        logging.debug(f"{step}: {enemy.name_npc} глобальных вейпоинтов больше 1го и есть локальные вейпоинты, считаются локальные вейпоинты для следующей карты. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[1][0], enemy.waypoints[1][1]], enemy.waypoints[1][2]], True)
    #Если следующий глобальный вейпоинт равен глобальной позиции персонажа, но не равен его зоне доступности, но глобальные вейпоинты сбрасываются для перессчёта
    elif enemy.waypoints and [enemy.waypoints[0][0], enemy.waypoints[0][1]] == enemy.global_position and enemy.waypoints[0][2] != enemy.vertices:
        enemy.waypoints = []
    #Если нет глобальных вейпоинтов
    else:
        logging.debug(f"{step}: {enemy.name_npc} нет глобальных вейпоинтов. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
        #Если глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности
        if enemy.target[0] != enemy.global_position or (enemy.target[0] == enemy.global_position and enemy.target[1] != enemy.vertices):
            logging.debug(f"{step}: {enemy.name_npc} глобальные позиции не равны или глобальные позиции равны, но не равны зоны доступности. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
            #Сначала считаем глобальные вейпоинты
            vertices_enemy_a_star_move_global_calculations(global_map, enemy,[enemy.target[0][0], enemy.target[0][1], enemy.target[1]])
            #А затем локальные
            vertices_enemy_a_star_move_local_calculations(global_map, enemy,
                                [[enemy.waypoints[0][0], enemy.waypoints[0][1]], enemy.waypoints[0][2]], True)
            #print(f"{enemy.name_npc} - посчитал глобальные, а затем локальные вейпоинты | {enemy.waypoints} | {enemy.dynamic_waypoints}")
        #Если равны глобальные позиции и зоны доступности
        elif enemy.target[0] == enemy.global_position and enemy.target[1] == enemy.vertices:
            logging.debug(f"{step}: {enemy.name_npc} глобальные позиции равны и равны зоны доступности. Его задача {enemy.target}. Его позиция {enemy.global_position}, {enemy.vertices}, {enemy.local_position}")
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
    chunk_size = len(global_map[0][0].chunk)
    
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

        #Если найден путь до края локации
        if raw_local_waypoints[-1][0] == 0 or raw_local_waypoints[-1][0] == chunk_size - 1 or raw_local_waypoints[-1][1] == 0 or raw_local_waypoints[-1][1] == chunk_size - 1:
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


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ПОЛЬЗОВАТЕЛЬСКИЙ ВВОД И ЕГО ОБРАБОТКА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step, enemy_list, mouse_position):

    person.level = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].level # Определение высоты персонажа
    person.vertices = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].vertices
    pressed_button = ''
    person.check_local_position()
    person.direction = 'center'
    person.global_position_calculation(chunk_size)
    person.activating_spawn = False
        
    
    mode_action, pressed_button, mouse_position = request_press_button(global_map, person, chunk_size, go_to_print, mode_action,
                                                                       interaction, mouse_position)
    
    if pressed_button != 'none':
        if mode_action == 'move':
            activity_list.append(Action_in_map('faint_footprints', step, person.global_position, person.local_position, chunk_size, person.name))
            if random.randrange(21)//18 > 0: # Оставление персонажем следов
                if not global_map[person.global_position[0]][person.global_position[1]].chunk[person.local_position[0]][person.local_position[1]].icon in ('f', '~'):
                    activity_list.append(Action_in_map('human_tracks', step, person.global_position, person.local_position, chunk_size, person.name))
            if random.randrange(40)//38 > 0: # Активация спавнов существ
                person.activating_spawn = True
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

    
    person.global_position_calculation(chunk_size)
    person.check_local_position()
    person.world_position_calculate(chunk_size)
    
    return mode_action, mouse_position

def wait_keyboard(person, mouse_position):
    """
        Ждёт нажатия клавиши или изменения положения указателя мыши
    """       
    pygame.key.set_repeat(1, 2)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                mouse_position = event.pos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    return 'a', mouse_position
                if event.key == pygame.K_RIGHT:
                    return 'd', mouse_position
                if event.key == pygame.K_UP:
                    return 'w', mouse_position
                if event.key == pygame.K_DOWN:
                    return 's', mouse_position
                if event.key == pygame.K_ESCAPE:
                    return 'escape', mouse_position
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return 'space', mouse_position
                if event.key == pygame.K_w:
                    return 'w', mouse_position
                if event.key == pygame.K_a:
                    return 'a', mouse_position
                if event.key == pygame.K_s:
                    return 's', mouse_position
                if event.key == pygame.K_d:
                    return 'd', mouse_position
                if event.key == pygame.K_t:
                    return 't', mouse_position
                if event.key == pygame.K_p:
                    return 'p', mouse_position
                if event.key == pygame.K_v:
                    return 'v', mouse_position
                if event.key == pygame.K_c:
                    return 'c', mouse_position
                if event.key == pygame.K_h:
                    return 'h', mouse_position
                if event.key == pygame.K_o:
                    return 'o', mouse_position
                if event.key == pygame.K_e:
                    return 'e', mouse_position
                if event.key == pygame.K_z:
                    return 'z', mouse_position
                if event.key == pygame.K_f:
                    return 'f', mouse_position
            if event.type == pygame.MOUSEMOTION:
                person.pointer_step = True
                return 'none', event.pos

def request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction, mouse_position):
    """
        Спрашивает ввод, возвращает тип активности и нажимаемую кнопку

    """
    pygame.event.clear()
    key, mouse_position = wait_keyboard(person, mouse_position)
   
    if key == 'w' or key == 'up' or key == 'ц':
        return (mode_action, 'up', mouse_position)
    elif key == 'a' or key == 'left' or key == 'ф':
        return (mode_action, 'left', mouse_position)
    elif key == 's' or key == 'down' or key == 'ы':
        return (mode_action, 'down', mouse_position)
    elif key == 'd' or key == 'right' or key == 'в':
        return (mode_action, 'right', mouse_position)
    elif key == 'space':
        return (mode_action, 'space', mouse_position)
    elif key == 'escape':
        return ('in_game_menu', 'escape', mouse_position)
    elif key == 'k' or key == 'л':
        if mode_action == 'move':
            person.pointer = [chunk_size//2, chunk_size//2]
            return ('pointer', 'button_pointer', mouse_position)
        elif mode_action == 'pointer':
            person.pointer = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer', mouse_position)
        else:
            person.pointer = [chunk_size//2, chunk_size//2]
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer', mouse_position)
    elif key == 'g' or key == 'п':
        if mode_action == 'move':
            person.gun = [chunk_size//2, chunk_size//2]
            return ('gun', 'button_gun', mouse_position)
        elif mode_action == 'gun':
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_gun', mouse_position)
        else:
            person.pointer = [chunk_size//2, chunk_size//2]
            person.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_gun', mouse_position)
    elif key == 'm' or key == 'ь':
        return (mode_action, 'button_map', mouse_position)
    elif key == 't' or key == 'е':
        if mode_action == 'test_move':
            return ('move', 'button_test', mouse_position)
        else:
            return ('test_move', 'button_test', mouse_position)
    elif key == 'p' or key == 'з':
        if mode_action == 'test_move':
            return ('test_move', 'button_purpose_task', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'v' or key == 'м':
        if mode_action == 'test_move':
            return ('test_move', 'button_test_visible', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'o' or key == 'щ':
        if mode_action == 'test_move':
            return ('test_move', 'view_waypoints', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'e' or key == 'у':
        if mode_action == 'test_move':
            return ('test_move', 'explosion', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'b' or key == 'и':
        if mode_action == 'test_move':
            return ('test_move', 'button_add_beacon', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'c' or key == 'с':
        if mode_action == 'test_move':
            return ('test_move', 'add_coyot', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'z' or key == 'я':
        if mode_action == 'test_move':
            return ('test_move', 'add_snake', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'f' or key == 'а':
        if mode_action == 'test_move':
            return ('test_move', 'follow_me', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'h' or key == 'р':
        if mode_action == 'test_move':
            return ('test_move', 'add_hunter', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    else:
        return (mode_action, 'none', mouse_position)

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
                person.type = 'u3'
            
    elif pressed_button == 'left':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] - 1].icon != '▲'and (person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] - 1].level or person.chunks_use_map[person.dynamic[0]][
                person.dynamic[1] - 1].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[1] >= chunk_size//2 and person.assemblage_point[1] > 0:
                person.dynamic[1] -= 1
                person.direction = 'left'
                person.type = 'l3'
            
    elif pressed_button == 'down':
        
        if person.chunks_use_map[person.dynamic[0] + 1][person.dynamic[1]].icon != '▲'and (person.level == person.chunks_use_map[
            person.dynamic[0] + 1][person.dynamic[1]].level or person.chunks_use_map[person.dynamic[0] + 1][
                person.dynamic[1]].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[0] <= (chunk_size + chunk_size//2) and person.assemblage_point[0] != (len(global_map) - 2):
                person.dynamic[0] += 1
                person.direction = 'down'
                person.type = 'd3'
            
    elif pressed_button == 'right':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] + 1].icon != '▲' and (person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] + 1].level or person.chunks_use_map[person.dynamic[0]][
                person.dynamic[1] + 1].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[1] <= (chunk_size + chunk_size//2) and person.assemblage_point[1] != (len(global_map) - 2):
                person.dynamic[1] += 1
                person.direction = 'right'
                person.type = 'r3'
    
    person.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод

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

    elif pressed_button == 'follow_me':
        interaction.append(['follow_me_all_enemies', [person, 'follow', 3]])

    elif pressed_button == 'button_add_beacon':
        activity_list.append(Action_in_map('test_beacon', step, person.global_position, person.local_position, chunk_size,
                f'\n оставлен вами в локальной точке - {[person.dynamic[0]%chunk_size, person.dynamic[1]%chunk_size]}| динамической - {person.dynamic}| глобальной - {person.global_position}'))
        
    elif pressed_button == 'button_test_visible':
        person.test_visible = not person.test_visible

    elif pressed_button == 'view_waypoints':
        interaction.append(['view_waypoints'])

    elif pressed_button == 'explosion':
        interaction.append(['add_global_interaction', 'explosion', person.global_position, person.local_position])

    elif pressed_button == 'add_hunter':
        global_position = copy.deepcopy(person.global_position)
        local_position = copy.deepcopy(person.local_position)
        if local_position[0] >= chunk_size:
            global_position[0] += 1
            local_position[0] = 0
        elif local_position[1] >= chunk_size:
            global_position[1] += 1
            local_position[1] = 0
        enemy_list.append(return_npc(global_position, local_position, 'riffleman'))
    elif pressed_button == 'add_coyot':
        global_position = copy.deepcopy(person.global_position)
        local_position = copy.deepcopy(person.local_position)
        if local_position[0] >= chunk_size:
            global_position[0] += 1
            local_position[0] = 0
        elif local_position[1] >= chunk_size:
            global_position[1] += 1
            local_position[1] = 0
        enemy_list.append(return_npc(global_position, local_position, 'coyot'))
    elif pressed_button == 'add_snake':
        global_position = copy.deepcopy(person.global_position)
        local_position = copy.deepcopy(person.local_position)
        if local_position[0] >= chunk_size:
            global_position[0] += 1
            local_position[0] = 0
        elif local_position[1] >= chunk_size:
            global_position[1] += 1
            local_position[1] = 0
        enemy_list.append(return_creature(global_position, local_position, 'snake'))

    person.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод

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
        person.zone_relationships = []
    for number_line in range(len(assemblage_chunk)):
        for chunk in range(len(assemblage_chunk)):
            person.zone_relationships.append(assemblage_chunk[number_line][chunk].vertices)
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
class Island_friends(pygame.sprite.Sprite):
    """ Содержит спрайты зон доступности """
    def add_color_dict(size):
        """ Создаёт единый на все экземпляры, словарь цветов """
        all_color_dict = {}
        for number in range(size):
            all_color_dict[len(all_color_dict)] = (random.randrange(255), random.randrange(255), random.randrange(255))
        all_color_dict[-1] = (0, 0, 0)
        all_color_dict[255] = (255, 0, 0)
        return all_color_dict
    
    all_color_dict = add_color_dict(200)

    def __init__(self, x, y, size_tile, number):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(number))
        self.image.set_alpha(60)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)
    
    def color_dict(self, number):
        if number in self.all_color_dict:
            return self.all_color_dict[number]
        else:
            return (random.randrange(256), random.randrange(256), random.randrange(256))


class Minimap_temperature(pygame.sprite.Sprite):
    """ Содержит спрайты температуры """

    def __init__(self, x, y, size_tile, temperature):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(temperature))
        self.image.set_alpha(95)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)
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
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill((239, 228, 176), special_flags=pygame.BLEND_RGB_ADD)
        self.image.set_alpha(25*level)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw( self, surface ):
        surface.blit(self.image, self.rect)

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
    
class Offset_sprites:
    """ Передаёт в следующий ход смещение выводимых на экран спрайтов """
    def __init__(self):
        self.all = [0, 0]

def person_walk_draw(entity, person, settings_for_intermediate_steps):
    """
        Меняет кадры анимации персонажа во время промежуточных кадров
    """
    direction_dict = {
                        'left': {0: 'l0',
                                 1: 'l1',
                                 2: 'l2',
                                 3: 'l3'},
                        'right':{0: 'r0',
                                 1: 'r1',
                                 2: 'r2',
                                 3: 'r3'},
                        'up':   {0: 'u0',
                                 1: 'u1',
                                 2: 'u2',
                                 3: 'u3'},
                        'down': {0: 'd0',
                                 1: 'd1',
                                 2: 'd2',
                                 3: 'd3'}
                     }

    intermediate_steps_dict = {
                                2: [0, 1],
                                3: [0, 1, 2],
                                5: [0, 1, 1, 2, 3],
                                6: [0, 1, 1, 2, 2, 3],
                                10:[0, 0, 1, 1, 1, 2, 2, 2, 3, 3],
                                15:[0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3],
                                30:[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
                              }

    entity.type = direction_dict[entity.direction][intermediate_steps_dict[settings_for_intermediate_steps[0]][person.pass_draw_move - 1]]

class Draw_open_image(pygame.sprite.Sprite):
    """ Отрисовывает полученное изображение """

    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)

class Draw_rect(pygame.sprite.Sprite):
    """ Отрисовывает любую поверхность """

    def __init__(self, x, y, x_size, y_size, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x_size, y_size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)

def master_pygame_draw(person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list, screen,
                        minimap_surface, minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                        entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap):
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

        РЕАЛИЗОВАТЬ:
        1) Изменение смещения и количества промежуточных шагов в зависимости от времени, потраченного на основной кадр

    """
    time_1 = time.time() #проверка времени выполнения
    
    size_tile = 30 # Настройка размера тайлов игрового окна
    size_tile_minimap = 15 # Настройка размера тайлов миникарты
    
    number_intermediate_steps = settings_for_intermediate_steps[0] #Количество промежуточных шагов
    step_direction = settings_for_intermediate_steps[1] #Смещение промежуточного шага

    if not person.pointer_step: #Если не шаг указателя
        if person.pass_draw_move: #Промежуточный кадр
            #Рассчет кадра движения персонажа
            if person.direction in ('left', 'right', 'down', 'up'):
                person_walk_draw(person, person, settings_for_intermediate_steps)
                
            working_minimap_surface = pygame.Surface.copy(minimap_surface) #Копирование поверхности миникарты
                
            blit_coordinates = (0, 0)
            
            if person.direction == 'up':
                offset_sprites.all[0] += step_direction
                blit_coordinates = (0, step_direction)
            elif person.direction == 'down':
                offset_sprites.all[0] -= step_direction
                blit_coordinates = (0, 0 - step_direction)
            elif person.direction == 'left':
                offset_sprites.all[1] += step_direction
                blit_coordinates = (step_direction, 0)
            elif person.direction == 'right':
                offset_sprites.all[1] -= step_direction
                blit_coordinates = (0 - step_direction, 0)
            
            working_surface = pygame.Surface.copy(finishing_surface)
            finishing_surface.blit(working_surface, blit_coordinates)

            screen.blit(finishing_surface, (0, 0))

            #Отрисовка активностей
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if activity_layer[number_line][number_tile].icon != '0':
                        print_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][activity_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line*size_tile + offset_sprites.all[0]
                        print_sprite.rect.left = number_tile*size_tile + offset_sprites.all[1]
                        print_sprite.draw(screen)
            
            #Отрисовка НПЦ
            entities_layer = entities_layer_calculations(person, chunk_size, go_to_print, enemy_list)
                        
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if entities_layer[number_line][number_tile].icon != '0':
                        if entities_layer[number_line][number_tile].name == 'riffleman':
                            if entities_layer[number_line][number_tile].direction in ('left', 'right', 'down', 'up'):
                                person_walk_draw(entities_layer[number_line][number_tile], person, settings_for_intermediate_steps)

                        offset_enemy = entities_layer[number_line][number_tile].offset
                        
                        if entities_layer[number_line][number_tile].direction == 'left':
                           offset_enemy[1] -= step_direction
                        elif entities_layer[number_line][number_tile].direction == 'right':
                            offset_enemy[1] += step_direction
                        elif entities_layer[number_line][number_tile].direction == 'up':
                            offset_enemy[0] -= step_direction
                        elif entities_layer[number_line][number_tile].direction == 'down':
                            offset_enemy[0] += step_direction
                        else:
                            offset_enemy = [0, 0]

                        print_sprite = sprites_dict[entities_layer[number_line][number_tile].icon][entities_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line*size_tile + offset_sprites.all[0] + offset_enemy[0]
                        print_sprite.rect.left = number_tile*size_tile + offset_sprites.all[1] + offset_enemy[1]
                        print_sprite.draw(screen)

            person.pass_draw_move -= 1
                
        else: #Основной кадр

            screen.fill((255, 255, 255))
            #Перерисовка миникарты
            working_minimap_surface = pygame.Surface.copy(minimap_surface) 
            #Количество промежуточных кадров
            person.pass_draw_move = number_intermediate_steps
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

            offset_sprites.all = [offset_y, offset_x]
            
            #minimap_sprite = pygame.sprite.Group()
            landscape_layer = landscape_layer_calculations(person, chunk_size, go_to_print)
            activity_layer = entities_layer_calculations(person, chunk_size, go_to_print, activity_list)
            #sky_layer = sky_layer_calculations(chunk_size)

            if person.recalculating_the_display: #Если нужно перерисовывать весь экран
                #Отрисовка ландшафта
                for number_line in range(chunk_size):
                    for number_tile in range(chunk_size):
                        print_sprite = sprites_dict[landscape_layer[number_line][number_tile].icon][landscape_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line*size_tile + offset_y
                        print_sprite.rect.left = number_tile*size_tile + offset_x
                        print_sprite.draw(finishing_surface)
                        
                        if landscape_layer[number_line][number_tile].level > 1:
                            Level_tiles(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile,
                                                        landscape_layer[number_line][number_tile].level - 1).draw(finishing_surface)

                screen.blit(finishing_surface, (0, 0)) #Отрисовка финишной поверхности

                #Отрисовка активностей
                for number_line in range(chunk_size):
                    for number_tile in range(chunk_size):
                        if activity_layer[number_line][number_tile].icon != '0':
                            activity_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][activity_layer[number_line][number_tile].type]
                            activity_sprite.rect.top = number_line*size_tile + offset_y
                            activity_sprite.rect.left = number_tile*size_tile + offset_x
                            activity_sprite.draw(screen)

            else: #Если нужно перерисовывать только линии или столбцы
                working_surface = pygame.Surface.copy(finishing_surface)
                number_line = 0
                number_tile = 0
                if person.direction == 'left':
                    number_line = 0
                    number_tile = chunk_size
                elif person.direction == 'right':
                    number_line = 0
                    number_tile = chunk_size - 1
                elif person.direction == 'up':
                    number_line = chunk_size
                    number_tile = 0
                elif person.direction == 'down':
                    number_line = chunk_size - 1
                    number_tile = 0

                finishing_surface.blit(working_surface, (number_line, number_tile))
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
                    print_sprite = sprites_dict[landscape_layer[number_line][number_tile].icon][landscape_layer[number_line][number_tile].type]
                    print_sprite.rect.top = number_line*size_tile
                    print_sprite.rect.left = number_tile*size_tile
                    print_sprite.draw(finishing_surface)
                    
                    if landscape_layer[number_line][number_tile].level > 1:
                        Level_tiles(number_tile*size_tile + offset_x, number_line*size_tile + offset_y, size_tile,
                                                        landscape_layer[number_line][number_tile].level - 1).draw(finishing_surface)
                    if activity_layer[number_line][number_tile].icon != '0':
                        print_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][activity_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line*size_tile
                        print_sprite.rect.left = number_tile*size_tile
                        print_sprite.draw(finishing_surface) 
            #Отрисовка НПЦ
            entities_layer = entities_layer_calculations(person, chunk_size, go_to_print, enemy_list) #Использование функции для отображения активностей
                        
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if entities_layer[number_line][number_tile].icon != '0':
                        enemy_offset_x = 0
                        enemy_offset_y = 0
                        if entities_layer[number_line][number_tile].direction == 'left':
                            enemy_offset_x = size_tile

                        elif entities_layer[number_line][number_tile].direction == 'right':
                            enemy_offset_x = 0 - size_tile

                        elif entities_layer[number_line][number_tile].direction == 'up':
                            enemy_offset_y = size_tile

                        elif entities_layer[number_line][number_tile].direction == 'down':
                            enemy_offset_y = 0 - size_tile

                        entities_layer[number_line][number_tile].offset = [enemy_offset_y, enemy_offset_x]
                        print_sprite = sprites_dict[entities_layer[number_line][number_tile].icon][entities_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line*size_tile + offset_sprites.all[0] + enemy_offset_y
                        print_sprite.rect.left = number_tile*size_tile + offset_sprites.all[1] + enemy_offset_x
                        print_sprite.draw(screen)
                        
        #Отрисовка зон доступности
        if person.test_visible:
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    Island_friends(number_tile*size_tile + offset_sprites.all[1], number_line*size_tile + offset_sprites.all[0], size_tile,
                                           landscape_layer[number_line][number_tile].vertices).draw(screen)
                    if landscape_layer[number_line][number_tile].stairs:
                        print_sprite = sprites_dict['stairs']['0']
                        print_sprite.rect.top = number_line*size_tile + offset_sprites.all[0]
                        print_sprite.rect.left = number_tile*size_tile + offset_sprites.all[1]
                        print_sprite.draw(screen)
                        
            if person.zone_relationships:
                person_offset = [0, 0]
                if person.direction == 'left':
                    person_offset = [0, 1]
                elif person.direction == 'right':
                    person_offset = [0, -1]
                elif person.direction == 'up':
                    person_offset = [1, 0]
                elif person.direction == 'down':
                    person_offset = [-1, 0]
                for number_vertices, vertices in enumerate(person.zone_relationships):
                    if person.number_chunk == number_vertices:
                        for vertice in vertices:
                            if vertice.connections:
                                for connect in vertice.connections:
                                    for tile in connect.tiles:
                                        if (person.local_position[0] - chunk_size//2) < tile[0] < (person.local_position[0] + chunk_size//2) and (
                                            person.local_position[1] - chunk_size//2) < tile[1] < (person.local_position[1] + chunk_size//2):
                                            offset = [tile[0] - person.local_position[0], tile[1] - person.local_position[1]]
                                            Island_friends((chunk_size//2 + offset[1] + person_offset[1])*size_tile + offset_sprites.all[1] + 10,
                                                           (chunk_size//2 + offset[0] + person_offset[0])*size_tile + offset_sprites.all[0] + 10,
                                                           10, connect.number).draw(screen)
                                
        #Отрисовка персонажа
        person_sprite = sprites_dict[person.icon][person.type]
        person_sprite.rect.top = chunk_size//2*size_tile
        person_sprite.rect.left = chunk_size//2*size_tile
        person_sprite.draw(screen)

        #Рисование белой рамки, закрывающей смещение
        for number_line in range(chunk_size + 1):
            for number_tile in range(chunk_size + 1):
                if 0 == number_line or number_line == chunk_size:
                    Draw_rect(number_line*size_tile, number_tile*size_tile, size_tile, size_tile, (255, 255, 255)).draw(screen)
                if 0 == number_tile or number_tile == chunk_size:
                    Draw_rect(number_line*size_tile, number_tile*size_tile, size_tile, size_tile, (255, 255, 255)).draw(screen)
                    
        #Печать персонажей на миникарту
        person_sprite = minimap_dict[person.icon][person.type]
        person_sprite.rect.top = person.global_position[0]*size_tile_minimap
        person_sprite.rect.left = person.global_position[1]*size_tile_minimap
        person_sprite.draw(working_minimap_surface)
        
        for enemy in enemy_list:
            enemy_sprite = minimap_dict[enemy.icon][enemy.type]
            enemy_sprite.rect.top = enemy.global_position[0]*size_tile_minimap
            enemy_sprite.rect.left = enemy.global_position[1]*size_tile_minimap
            enemy_sprite.draw(working_minimap_surface)
                
        screen.blit(working_minimap_surface, ((len(global_map) - 1)*size_tile, 0))

        #Отрисовка температуры на миникарте
        if person.test_visible:
            for number_minimap_line, minimap_line in enumerate(raw_minimap):
                for number_minimap_tile, minimap_tile in enumerate(minimap_line):
                    Minimap_temperature(number_minimap_tile*size_tile_minimap + (26*size_tile), number_minimap_line*size_tile_minimap,
                                                            size_tile_minimap, minimap_tile.temperature).draw(screen)

    time_2 = time.time() #проверка времени выполнения

    #Рассчёт количества промежуточных шагов в зависимости от скорости вывода основного шага    
    if not person.pointer_step:
        settings_for_intermediate_steps = frames_per_cycle_and_delays(person, time_1, time_2, settings_for_intermediate_steps)
    
    end = time.time() #проверка времени выполнения

    Draw_rect(30*26, 30*14, 1000, 500, (255, 255, 255)).draw(screen) # заливает белым область надписей
    
    print_time = f"{person.world_position} - person.world_position, {settings_for_intermediate_steps} - скорость шага, {mouse_position} - mouse_position" #{round(time_2 - time_1, 4)} - отрисовка"
    
    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(print_time, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30*34, 15*30)
    screen.blit(textSurfaceObj, textRectObj)

    print_pointer = F"Под ногами {pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position,'ground', raw_minimap)}"

    textSurfaceObj = fontObj.render(print_pointer, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30*34, 16*31)
    screen.blit(textSurfaceObj, textRectObj)
    
    print_pointer = F"Вы видите {pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position, 'pointer', raw_minimap)}"

    textSurfaceObj = fontObj.render(print_pointer, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30*34, 17*31)
    screen.blit(textSurfaceObj, textRectObj)
    
    pygame.display.flip()
            
    return screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps

def pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position, type_descrption, raw_minimap):
    """
        Собирает описание того что под ногами и того, куда указывает указатель
        coords - [x, y]
    """
    def coords_description(coords, area, chunk_size):
        """
            Принимает координаты и карту, возвращает описание.
        """
        if coords[0] < chunk_size and coords[1] < chunk_size:
            return area[coords[1]][coords[0]].description
        else:
            return ''
    
    person_coords = [chunk_size//2, chunk_size//2]
    mouse_coords = []
    for axis_position in mouse_position:
        mouse_coords.append(axis_position//size_tile)
    ground_description = ''
    pointer_description = ''
    if mouse_coords[0] < chunk_size and mouse_coords[1] < chunk_size:
        pointer_description += 'vertices = ' + str(landscape_layer[mouse_coords[1]][mouse_coords[0]].vertices) + ' ' + \
                               'world_vertices = ' + str(landscape_layer[mouse_coords[1]][mouse_coords[0]].world_vertices) + ' тут ' + \
                               str(landscape_layer[mouse_coords[1]][mouse_coords[0]].list_of_features) + ' '
        
    for area in (landscape_layer, activity_layer, entities_layer):
        ground_description += coords_description(person_coords, area, chunk_size)
        pointer_description += coords_description(mouse_coords, area, chunk_size)
    if mouse_coords[0] > chunk_size:
        minimap_coords = []
        axis_position_x, axis_position_y = mouse_position
        minimap_coords.append((axis_position_x - (chunk_size + 1)*size_tile)//15)
        minimap_coords.append(axis_position_y//15)
        pointer_description += coords_description(minimap_coords, raw_minimap, len(raw_minimap))
        if minimap_coords[0] < len(raw_minimap) and minimap_coords[1] < len(raw_minimap):
            pointer_description += f" | T = {int(raw_minimap[minimap_coords[1]][minimap_coords[0]].temperature)} градусов"
        
    if type_descrption == 'ground':
        return ground_description
    else:
        return pointer_description



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
    if not person.pointer_step and not person.pass_draw_move:
        step += 1
    return step

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    УПРАВЛЯЮЩИЙ БЛОК
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def save_map(global_map, minimap):
    """
        Сохранение игровой карты через pickle
    """
    all_save = [global_map, minimap]

    with open("saved_map.pkl", "wb") as fp:
        pickle.dump(all_save, fp)

def load_map():
    """
        Загрузка игровой карты через pickle
    """
    with open("saved_map.pkl", "rb") as fp:
        all_load = pickle.load(fp)
    
    return all_load[0], all_load[1]

def save_game(global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step):
    """
        Сохраняет игровой процесс
    """
    all_save = [global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step]

    with open("save_game.pkl", "wb") as fp:
        pickle.dump(all_save, fp)

def load_game():
    """
        Загружает игровой процесс
    """
    with open("save_game.pkl", "rb") as fp:
        all_load = pickle.load(fp)
        
    return all_load[0], all_load[1], all_load[2], all_load[3], all_load[4], all_load[5], all_load[6]
                  

def frames_per_cycle_and_delays(person, time_1, time_2, settings_for_intermediate_steps):
    """
        Рассчёт количества промежуточных шагов в зависимости от скорости вывода основного шага и
        установка задержек на промежуточные кадры для плавности перемещения
    """
    if not person.person_pass_step and not person.enemy_pass_step:
        if (time_2 - time_1) >= 0.075:
            settings_for_intermediate_steps = [2, 15]
        elif 0.075 > (time_2 - time_1) >= 0.05:
            settings_for_intermediate_steps = [3, 10]
        elif 0.05 > (time_2 - time_1) >= 0.03:
            settings_for_intermediate_steps = [5, 6]
        elif 0.03 > (time_2 - time_1) >= 0.025:
            settings_for_intermediate_steps = [6, 5]
        elif 0.025 > (time_2 - time_1) >= 0.015:
            settings_for_intermediate_steps = [10, 3]
        elif 0.015 > (time_2 - time_1) >= 0.01:
            settings_for_intermediate_steps = [15, 2]
        elif 0.01 > (time_2 - time_1):
            settings_for_intermediate_steps = [30, 1]
        person.pass_draw_move = settings_for_intermediate_steps[0]

    elif person.person_pass_step and person.enemy_pass_step: #Установка задержек на промежуточные кадры для плавности перемещения
        if settings_for_intermediate_steps == [2, 15] and (time_2 - time_1) < 0.1:
            time.sleep(0.1 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [3, 10] and (time_2 - time_1) < 0.08:
            time.sleep(0.08 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [5, 6] and (time_2 - time_1) < 0.03:
            time.sleep(0.03 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [6, 5] and (time_2 - time_1) < 0.025:
            time.sleep(0.025 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [10, 3] and (time_2 - time_1) < 0.015:
            time.sleep(0.015 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [15, 2] and (time_2 - time_1) < 0.01:
            time.sleep(0.01 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [30, 1] and (time_2 - time_1) < 0.005:
            time.sleep(0.005 - (time_2 - time_1))
    return settings_for_intermediate_steps

class button_rect(pygame.sprite.Sprite):
    """ Содержит спрайты поверхностей """

    def __init__(self, y, x, size_y, size_x, color, text):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font('freesansbold.ttf', 10)
        self.textSurf = self.font.render(text, 1, (255, 255, 255))
        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.image.blit(self.textSurf, [size_x/2 , size_y/2])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 0
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
            
def master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list, fill = True):
    """
        Отрисовывает игровое меню
    """
    if fill:
        screen.fill((255, 255, 255))
    step = 0
    for menu in menu_list:
        if menu == menu_selection:
            if button_selection:
                button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (155, 200, 155), menu).draw(screen)
            else:
                button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (200, 155, 155), menu).draw(screen)
        else:
            button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (155, 155, 155), menu).draw(screen)
        step += 100

    pygame.display.flip()

def settings_loop(screen, dispay_size, fast_generation:bool, global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid):
    """
        Здесь происходит переключение настроек
    """
    menu_selection = 'fast_generation'
    button_selection = False
    menu_list = ['fast_generation', 'exit_settings']
    master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
    settings_loop = True
    while settings_loop:
        time.sleep(0.2)
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        if menu_selection == 'exit_settings' and button_selection: #Выход из настроек
            settings_loop = False
        elif menu_selection == 'fast_generation' and button_selection:
            fast_generation = not fast_generation
        master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
        button_selection = False
        
                    
def preparing_a_new_game(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid, chunk_size, screen,
                         sprites_dict, minimap_dict):
    """
        Производит подготовку к началу новой игры и её запуск
    """
    global_map, raw_minimap = map_generator.master_map_generate(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid, screen)
        
    person = Person([2, 2], [2, 2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
    calculation_assemblage_point(global_map, person, chunk_size)
    enemy_list = [
                    return_npc([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 'horseman'),
                    return_npc([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 'riffleman'),
                    return_npc([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 'coyot'),
                    return_npc([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 'unknown'),
                 ]
    world = World() #Описание текущего состояния игрового мира

    game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, True, [],
              sprites_dict, minimap_dict)

def in_game_main_loop(screen, global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step):
    """
        Меню в уже загруженной игре
    """
    menu_selection = 'continue the game'
    button_selection = False
    menu_list = ['continue the game', 'save game', 'game settings', 'end game', 'leave the game']
    screen.fill((255, 255, 255))
    screen.set_alpha(60)
    master_game_menu_draw(screen, [1200, 750], menu_selection, button_selection, menu_list, False)
    in_game_main_loop = True
    game_loop = True
    while in_game_main_loop:
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        master_game_menu_draw(screen, [1200, 750], menu_selection, button_selection, menu_list, False)
        time.sleep(0.2)
        if menu_selection == 'continue the game' and button_selection:
            in_game_main_loop = False
        if menu_selection == 'save game' and button_selection:
            save_game(global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step)
            in_game_main_loop = False
        if menu_selection == 'end game' and button_selection: #Закрытие игры
            in_game_main_loop = False
            game_loop = False
        if menu_selection == 'leave the game' and button_selection: #Закрытие игры
            sys.exit()
        
        button_selection = False
    return game_loop

def menu_calculation(menu_list, menu_selection, button_selection):
    """
        Обрабатывает перемещение по любому игровому меню
    """
    pygame.event.clear()
    for number_menu, menu in enumerate(menu_list):
        if menu == menu_selection:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if number_menu < len(menu_list) - 1:
                                return menu_list[number_menu + 1], button_selection
                            else:
                                return menu_list[0], button_selection
                            
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            if number_menu > 0:
                                return menu_list[number_menu - 1], button_selection
                            else:
                                return menu_list[-1], button_selection
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            return menu_selection, True
            
    menu_selection, button_selection

def minimap_create(raw_map, minimap_dict, size_tile):
    """
        Создаёт игровую миникарту для постоянного использования
    """
    minimap_surface = pygame.Surface((len(raw_map)*size_tile, len(raw_map)*size_tile))
    for number_line, line in enumerate(raw_map):
        for number_tile, tile in enumerate(line):
            print_sprite = minimap_dict[tile.icon][tile.type]
            print_sprite.rect.top = number_line*size_tile
            print_sprite.rect.left = number_tile*size_tile
            print_sprite.draw(minimap_surface)
    return minimap_surface         
            
def main_loop():
    """
        Здесь работает игровое меню
        
    """
    logging.basicConfig(filename="logging.log", filemode="w", level=logging.DEBUG)
    
    global_region_grid = 3
    region_grid = 3
    chunks_grid = 3
    mini_region_grid = 5
    tile_field_grid = 5

    chunk_size = mini_region_grid * tile_field_grid #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    
    pygame.init()

    dispay_size = [1300, 730] #было [1200, 750]
    screen = pygame.display.set_mode(dispay_size)#, FULLSCREEN | DOUBLEBUF)
    pygame.display.set_caption("My Game")

    #Загрузка и создание поверхностей всех спрайтов
    sprites_dict = loading_all_sprites()
    minimap_dict = minimap_dict_create()

    fast_generation = False #Переключение отображения генерации между прогресс-баром и полным выводом на экран генерирующейся карты
    menu_selection = 'new_game'
    button_selection = False
    menu_list = ['new_game', 'load_game', 'load_map', 'settings', 'about', 'exit_game']
    #Предварительная отрисовка игрового меню
    master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

    while main_loop:
        button_selection = False
        time.sleep(0.2)
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
        
        if menu_selection == 'new_game' and button_selection: #Подготовка и запуск новой игры
            button_selection = False
            preparing_a_new_game(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid, chunk_size, screen,
                                 sprites_dict, minimap_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

        if menu_selection == 'load_game' and button_selection:
            menu_selection = 'new_game'
            button_selection = False
            global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step = load_game()
            world = World() #Описание текущего состояния игрового мира\

            game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, False,
                      [activity_list, step], sprites_dict, minimap_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
            
        if menu_selection == 'load_map' and button_selection:
            menu_selection = 'new_game'
            button_selection = False
            global_map, raw_minimap = load_map()
                
            person = Person([2, 2], [2, 2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
            calculation_assemblage_point(global_map, person, chunk_size)
            enemy_list = [
                    return_npc([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 'horseman'),
                    return_npc([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 'riffleman'),
                    return_npc([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 'coyot'),
                    return_npc([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 'unknown'),]
            world = World() #Описание текущего состояния игрового мира

            game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, True, [],
                      sprites_dict, minimap_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

        if menu_selection == 'exit_game' and button_selection: #Закрытие игры
            sys.exit()
        if menu_selection == 'settings' and button_selection:
            settings_loop(screen, dispay_size, fast_generation, global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid)
            button_selection = False
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

def game_loop(global_map:list, person, chunk_size:int, enemy_list:list, world, screen, raw_minimap,
              new_game:bool, load_pack:list, sprites_dict:dict, minimap_dict:dict):
    """
        Здесь происходят все игровые события
        
    """
    if new_game:
        activity_list = []
        step = 0
        save_map(global_map, raw_minimap) #тестовое сохранение карты
    else:
        activity_list = load_pack[0]
        step = load_pack[1]
        
    go_to_print = Interfase([], [], True)
    global changing_step
    mode_action = 'move'
    clock = pygame.time.Clock()#
    game_fps = 100#

    global_interaction = [] #Глобальные происшествия

    pygame.display.flip()

    offset_sprites = Offset_sprites()

    landscape_layer = [[[]]]
    activity_layer = [[[]]]
    entities_layer = [[[]]]
    
    minimap_surface = minimap_create(raw_minimap, minimap_dict, 15)
    finishing_surface = pygame.Surface(((chunk_size + 1)*30, (chunk_size + 1)*30))

    settings_for_intermediate_steps = [5, 6]
    mouse_position = (0, 0)

    #Предварительная отрисовка игрового окна
    screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps = master_pygame_draw(person, chunk_size,
                                            go_to_print, global_map, mode_action, enemy_list, activity_list, screen, minimap_surface,
                                            minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                                            entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap)
    
    print('game_loop запущен')
    game_loop = True
    while game_loop:
        clock.tick(game_fps)
        interaction = []
        person.pointer_step = False #Сбрасывается перехват шага выводом описания указателя
        world.npc_path_calculation = False #Сброс предыдущего состояния поиска пути NPC персонажами
        master_pass_step(person)
        
        if not person.person_pass_step:
            mode_action, mouse_position = master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step,
                                               enemy_list, mouse_position)
        if mode_action == 'in_game_menu':
            game_loop = in_game_main_loop(screen, global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step)
            mode_action = 'move'
            
        step = new_step_calculation(enemy_list, person, step)
            
        start = time.time() #проверка времени выполнения
        calculation_assemblage_point(global_map, person, chunk_size) # Рассчёт динамического чанка
        #all_pass_step_calculations(person, enemy_list, mode_action, interaction)
        if not person.enemy_pass_step and not person.pointer_step:
            master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, world, global_interaction)
        screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps = master_pygame_draw(
                                        person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list, screen, minimap_surface,
                                        minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                                        entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap)
        

        

main_loop()
    

