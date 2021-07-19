import random
import time
import copy
import math
import pygame
import pickle
from pygame.locals import *
import sys

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ТЕСТ КОРРЕКТНОСТИ ОПРЕДЕЛЕНИЯ ЗОН ДОСТУПНОСТИ
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

class Tile:
    """ Содержит изображение, описание, особое содержание тайла, стоимость передвижения, тип, высоту и лестницу """
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1
        
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
                        'f': ['брод', 10],
                        'C': ['каньон', 20],
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

class Location:
    """ Содержит описание локации """
    __slots__ = ('name', 'temperature', 'chunk', 'icon', 'price_move', 'vertices', 'position')
    def __init__(self, name:str, temperature:float, chunk:list, icon:str, price_move:int, position):
        self.name = name
        self.temperature = temperature
        self.chunk = chunk
        self.icon = icon
        self.price_move = price_move
        self.vertices = []
        self.position = position
    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["temperature"] = self.temperature
        state["chunk"] = pickle.dumps(self.chunk)
        state["icon"] = self.icon
        state["price_move"] = self.price_move
        state["vertices"] = self.vertices
        state["position"] = self.position
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.temperature = state["temperature"]
        self.chunk = pickle.loads(state["chunk"])
        self.icon = state["icon"]
        self.price_move = state["price_move"]
        self.vertices = state["vertices"]
        self.position = state["position"]

def convert_tiles_to_class(processed_map):
    """
        Конвертирование тайлов в класс Tile
    """
    chunk_size = 25
    
    new_class_tiles_map = []
    for number_line in range(len(processed_map)):
        new_line = []
        for number_tile in range(len(processed_map[number_line])):
            new_line.append(Tile(processed_map[number_line][number_tile]))
        new_class_tiles_map.append(new_line)
    return new_class_tiles_map

def all_gluing_map(raw_gluing_map, grid, count_block):
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
                    try:
                        gluing_map[gluing_index].append(raw_gluing_map[number_region_line][number_region].chunk[number_location_line][number_location])
                    except IndexError:
                        print(f"len(gluing_map) = {len(gluing_map)} ||| gluing_index = {gluing_index}")
                        print(f"number_region_line - {number_region_line} | number_region - {number_region}, number_location_line - {number_location_line}, number_location - {number_location}")
                        print(gluing_map[gluing_index])
                    count_location += 1
    return gluing_map

def defining_vertices(processed_map):
    """
        Определение независимых областей на локациях и связей между ними для последующей работы с алгоритмом A*
    """
    def repeat_pass(global_tile, number):
        new_friends_list = []
        for number_line in range(len(global_tile.chunk)):
            for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                if number_line > 0 and tile.vertices != -1 and -1 != global_tile.chunk[number_line - 1][number_tile].vertices != tile.vertices:
                    if not ([global_tile.chunk[number_line - 1][number_tile].vertices, tile.vertices] in new_friends_list):
                        new_friends_list.append([global_tile.chunk[number_line - 1][number_tile].vertices, tile.vertices])
        if new_friends_list:
            for frends in new_friends_list:
                master = min(frends[0], frends[1])
                slave = max(frends[0], frends[1])
                for number_line in range(1, len(global_tile.chunk)):
                    for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                        
                        if tile.vertices == slave:
                            if number == 2:
                                tile.vertices = master
                        
    
    class Availability_field:
        def __init__(self, number, tile):
            self.number = number
            self.global_number = number
            self.tiles = [tile]
            
    banned_tuple = ('~', '▲', 'C')
    for number_global_line, global_line in enumerate(processed_map):
        for number_global_tile, global_tile in enumerate(global_line):
            number_field = 0
            list_availability_fields = []
            for number_line in range(len(global_tile.chunk)):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    if not(tile.icon in banned_tuple):
                            
                        #Обработка тайла слева
                        if number_tile > 0 and global_tile.chunk[number_line][number_tile - 1].vertices >= 0:
                            tile.vertices = global_tile.chunk[number_line][number_tile - 1].vertices
                            list_availability_fields[tile.vertices].tiles.append([number_line, number_tile])

                        #Обработка тайла сверху
                        if number_line > 0 and global_tile.chunk[number_line - 1][number_tile].vertices >= 0:
                            #Обработка крайней левой линии
                            if number_tile == 0 and number_line > 0:
                                tile.vertices = global_tile.chunk[number_line - 1][number_tile].vertices
                                list_availability_fields[tile.vertices].tiles.append([number_line, number_tile])
                            
                            #Если тайл обрабатывался
                            if tile.vertices >= 0:
                                up = global_tile.chunk[number_line - 1][number_tile].vertices
                                if list_availability_fields[tile.vertices].global_number < list_availability_fields[up].global_number:
                                    check_number = up
                                    while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                        if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                            check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                            list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                        else:
                                            break
                                    list_availability_fields[up].global_number = list_availability_fields[tile.vertices].global_number
                                    
                                elif list_availability_fields[tile.vertices].global_number > list_availability_fields[up].global_number:
                                    list_availability_fields[tile.vertices].global_number = list_availability_fields[up].global_number
                                    
                                        
                            #Если тайл не обрабатывался
                            elif tile.vertices == -1:
                                tile.vertices = global_tile.chunk[number_line - 1][number_tile].vertices
                                list_availability_fields[tile.vertices].tiles.append([number_line, number_tile])
                                
                        #Если тайл еще не обрабатывался
                        if tile.vertices == -1:
                            tile.vertices = number_field
                            list_availability_fields.append(Availability_field(number_field, [number_line, number_tile]))
                            number_field += 1
            
            for field in list_availability_fields:
                print(f"before number - {field.number}, global_number - {field.global_number}, tiles - field.tiles")
                if field.number != field.global_number:
                    field.global_number = list_availability_fields[field.global_number].global_number
                print(f"after number - {field.number}, global_number - {field.global_number}, tiles - field.tiles")
            print('\n \n')

            for availability_field in list_availability_fields:
                print(f"number - {availability_field.number}, global_number - {availability_field.global_number}, tiles - availability_field.tiles")
                for tile in availability_field.tiles:
                    global_tile.chunk[tile[0]][tile[1]].vertices = availability_field.global_number
            print('\n \n \n \n')
            
                    
            x = '''
            #Повторный проход для определения неопределённых связей

            new_friends_list = []
            for number_line in range(len(global_tile.chunk)):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    if number_line > 0 and tile.vertices != -1 and -1 != global_tile.chunk[number_line - 1][number_tile].vertices != tile.vertices:
                        if global_tile.chunk[number_line - 1][number_tile].level == tile.level or tile.stairs or global_tile.chunk[number_line - 1][number_tile].stairs:
                            if not ([global_tile.chunk[number_line - 1][number_tile].vertices, tile.vertices] in new_friends_list):
                                new_friends_list.append([global_tile.chunk[number_line - 1][number_tile].vertices, tile.vertices])
                            
                    elif number_line == 0 and tile.vertices != -1 and -1 != global_tile.chunk[number_line + 1][number_tile].vertices != tile.vertices:
                        if global_tile.chunk[number_line + 1][number_tile].level == tile.level or tile.stairs or global_tile.chunk[number_line + 1][number_tile].stairs:
                            if not ([global_tile.chunk[number_line + 1][number_tile].vertices, tile.vertices] in new_friends_list):
                                new_friends_list.append([global_tile.chunk[number_line + 1][number_tile].vertices, tile.vertices])
                    
            if new_friends_list:
                for frends in new_friends_list:
                    master = min(frends[0], frends[1])
                    slave = max(frends[0], frends[1])
                    for number_line in range(1, len(global_tile.chunk)):
                        for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                            
                            if tile.vertices == slave:
                                tile.vertices = master
            '''

def create_test_map():
    """
        Создаёт тестовый игровой мир из 4х файлов txt
    """
    test_maps = []
    count = 0
    for number_global_line in range(2):
        global_line = []
        for number_global_tile in range(2):
            file_draw_map = open(f"test_map_{count}.txt", encoding="utf-8")
            draw_map = file_draw_map.read().splitlines()
            test_map = []
            for number_line in range(len(draw_map)):
                test_line = []
                for number_tile in range(len(draw_map[number_line])):
                    test_line.append(draw_map[number_line][number_tile])
                test_map.append(test_line)
            class_test_map = convert_tiles_to_class(test_map)
            ready_test_map = Location('test_name', 25, class_test_map, '.', 0, [number_global_line, number_global_tile])
            global_line.append(ready_test_map)
            count += 1
        test_maps.append(global_line)
        
    return test_maps

def print_test_map(raw_print_map):
    """
        Выводит тестовую карту на экран
    """
    print_map = all_gluing_map(raw_print_map, len(raw_print_map), len(raw_print_map[0][0].chunk))
    print_box = ''
    for number_line, line in enumerate(print_map):
        print_line = ''
        for number_tile, tile in enumerate(line):
            if tile.vertices == -1:
                print_line += tile.icon + ' ' + '▲'
            else:
                if len(str(tile.vertices)) == 1:
                    print_line += tile.icon + ' ' + str(tile.vertices)
                elif len(str(tile.vertices)) == 2:
                    print_line += tile.icon + str(tile.vertices)                
        print_box += print_line + '\n'
    print(print_box)
            

def main():
    """
        Создаёт тестовую карту и прогоняет по ней определитель полей доступности
    """
    test_map = create_test_map()
    defining_vertices(test_map)
    print_test_map(test_map)
    
main()                    
            
            











    
