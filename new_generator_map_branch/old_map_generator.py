import os
import copy
import random
import string
import keyboard
import time
import math
import pygame

garbage = ['░', '▒', '▓', '█', '☺']

"""
    СТАРЫЙ ГЕНЕРАТОР ЛОКАЦИЙ
    
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

class Description_location:
    """ Содержит информацию для генератора локаций """
    __slots__ = ('name', 'temperature', 'main_tileset', 'random_tileset', 'icon', 'price_move')
    def __init__(self, description:list):
        self.name = description[0]
        self.temperature = description[1]
        self.main_tileset = description[2]
        self.random_tileset = description[3]
        self.icon = description[4]
        self.price_move = description[5]

class Description_point_map:
    """ Содержит информацию для генератора локаций """
    __slots__ = ('name', 'temperature', 'main_tileset', 'random_tileset', 'icon', 'price_move')
    def __init__(self, description:list):
        self.name = description[0]
        self.temperature = description[1]
        self.main_tileset = description[2]
        self.random_tileset = description[3]
        self.icon = description[4]
        self.price_move = description[5]


class Tile:
    """ Содержит изображение, описание и особое содержание тайла """
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
                        '~': ['солёная вода', 20],
                        'C': ['каньон', 20],
                        '??': ['ничего', 10],
                        }
        return ground_dict[icon][number]       
    

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ГЕНЕРАЦИЯ ИГРОВОЙ КАРТЫ ПРИ ЗАПУСКЕ ИГРЫ
    
    На выходе выдаёт класс Location
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""       

def mini_region_tile_merge(one_icon:str, two_icon:str):
    """
        случайно выбирает одну иконку тайла из двух
    """
    if two_icon != '':
        return random.choice([one_icon, two_icon, two_icon])
    else:
        return one_icon

def mini_region_generate(description, grid):
    """
        Генерирует карту мини регионов локации
    """
    mini_region_map = []
    for i in range(grid):
        mini_region_map.append([random.choice(description.main_tileset) for x in range(grid)])                    
    return mini_region_map

def post_mini_region_generate(global_mini_region_map):
    """
        Копирует значение боковых значений мини регионов в прилегающие края следующих мини регионов. Слева ==> направо, сверху ==> вниз

        Не заполняет нижнюю клетку по оси y
    """
    for axis_y in range(len(global_mini_region_map)):
        for axis_x in range(len(global_mini_region_map)):
            for number_line in range(len(global_mini_region_map[axis_y][axis_x][0])):
                for number_region in range(len(global_mini_region_map[axis_y][axis_x][0])):
                    if number_line == len(global_mini_region_map[axis_y][axis_x][0]) - 1:
                        if random.randrange(10)//3 and axis_y != len(global_mini_region_map) - 1:                           
                            global_mini_region_map[axis_y + 1][axis_x][0][0][number_region] = global_mini_region_map[axis_y][axis_x][0][number_line][number_region]
                    elif number_region == len(global_mini_region_map[axis_y][axis_x][0]) - 1:
                        if random.randrange(10)//3 and axis_x != len(global_mini_region_map) - 1:
                            global_mini_region_map[axis_y][axis_x + 1][0][number_line][0] = global_mini_region_map[axis_y][axis_x][0][number_line][number_region]


def random_location_post_generate(location:list, description:list):
    """
        Случайно заполняет готовую локацию из списка случайных тайлов
    """
    banned_list = ['~']
    for line in range(len(location)):
        for tile in range(len(location)):
            if random.randrange(10)//9 and not(location[line][tile].icon in banned_list):
                location[line][tile] = Tile(random.choice(description.random_tileset))
    return location

def master_location_generate(mini_region, game_field_size, grid):
    """
        Генерирует карту локации из минирегионов по такому же алгоритму, что и генератор глобальной карты из регионов.
    """
    return advanced_location_generate(mini_region, grid, game_field_size) #генератор по мини регионам


def advanced_location_generate(mini_region_map, grid, game_field_size):
    """
        Генерирует локацию по карте мини регионов
    """
    x = 0
    raw_location = []
    count_block = game_field_size // grid
    for number_line in range(grid): #Определям место в линии сидов
        region_location_line = []
        for number_seed in range(grid): #Определяем номер сида
            region_location = []
            for number_tile_line in range(count_block): #Создаём линии мини региона
                tile_line = []
                for number_tile in range(count_block): #Создаём тайлы линий
                    top_down_tile = ''
                    left_right_tile = ''                  
                    if number_tile_line <= 1: #Обрабатываем верхний край мини региона
                        if number_line != 0:
                            top_down_tile = Tile(mini_region_map[0][number_line - 1][number_seed])
                    elif number_tile_line >= (count_block - 1): #Обрабатываем нижний край мини региона
                        if number_tile != (count_block - 1):
                            top_down_tile = Tile(mini_region_map[0][number_line][number_seed])
                    if number_tile <= 1: #Обрабатываем левый край мини региона
                        if number_seed != 0:
                            left_right_tile = Tile(mini_region_map[0][number_line][number_seed - 1])
                    elif number_tile != (count_block - 1): #Обрабатываем правый край мини региона
                        if number_seed != (count_block - 1):
                            left_right_tile = Tile(mini_region_map[0][number_line][number_seed])
     
                    main_tile = Tile(mini_region_map[0][number_line][number_seed])
                    main_tile = mini_region_tile_merge(main_tile, top_down_tile)
                    main_tile = mini_region_tile_merge(main_tile, left_right_tile)
                    tile_line.append(main_tile)
                region_location.append(tile_line)
            region_location_line.append(region_location)
        raw_location.append(region_location_line)
        
    ready_location = Location(mini_region_map[1].name, 35, [], mini_region_map[1].icon, mini_region_map[1].price_move)
    ready_location.chunk = random_location_post_generate(gluing_location(raw_location, grid, count_block), mini_region_map[1])
    temperature = mini_region_map[1].temperature
    ready_location.temperature = [random.randrange(temperature[0], temperature[1])]

    return ready_location


def selecting_generator(seed):
    """
        Содержит и выдаёт значения семян генерации.
    """
    seed_dict = {  
                    0: ['desert',             [40.0,60.0], ['.'],                 ['j'],            'j',        20],
                    1: ['semidesert',         [35.0,50.0], ['.', ','],            ['▲', 'o', 'i'],  '.',        10],
                    2: ['cliff semi-desert',  [35.0,50.0], ['▲', 'A', '.', ','],  ['o', 'i'],       'A',         7],
                    3: ['snake semi-desert',  [35.0,50.0], ['A', '.', ','],       ['▲','o', 'i'],   'S',         7],
                    4: ['saline land',        [40.0,50.0], [';'],                 [':'],            ';',        15],
                    5: ['field',              [20.0,35.0], ['u', '„', ','],       ['ü', 'o'],       '„',         5],
                    6: ['dried field',        [30.0,40.0], ['„', ','],            ['o', 'u'],       ',',         2],
                    7: ['oasis',              [15.0,30.0], ['F', '„', '~'],       ['P', ','],       'P',         0],
                    8: ['salty lake',         [25.0,40.0], ['~'],                 ['„'],            '~',        20],
                    9: ['hills',              [20.0,35.0], ['▲', '▲', 'o'],       ['„', ','],       '▲',        20],
                    10:['canyons',            [20.0,35.0], ['C', '.', ','],       ['C'],            'C',        20],
                    11:['big canyons',        [20.0,35.0], ['C'],                 ['.', 'o', '▲'],  'R',        20],
                }
    return seed_dict[seed]


def description_seed_merge(one_description, two_description):
    """
        Принимает два описания локаций, склеивает их, сохраняя значение в первое.
    """
    if len(two_description) > 1:
        one_description[0] = one_description[0] + ' - ' + two_description[0]
        one_description[1] = [min(one_description[1][0], two_description[1][0]), max(one_description[1][1], two_description[1][1])]
        for char in range(len(two_description[2])):
            one_description[2].append(two_description[2][char])
        for char in range(len(two_description[3])):
            one_description[3].append(two_description[3][char])
        one_description[4] = random.choice([one_description[4], two_description[4]])
        if one_description[5] < two_description[5]:
            one_description[5] = random.uniform(one_description[5], two_description[5])
        elif one_description[5] > two_description[5]:
            one_description[5] = random.uniform(two_description[5], one_description[5])
        

def master_generate(value_region_box:int, game_field_size:int, grid):
    """
        Генерирует глобальную карту минирегионов, ориентируясь на карту регионов.
    """
    region_map = region_generate(value_region_box)
    
    raw_global_region_map = []

    for number_line in range(len(region_map)):
        region_line = []
        for number_seed in range(len(region_map[number_line])): #Определяем номер сида в линии сидов для создания девяти локаций
            region = []
            for number_location_line in range((len(region_map))): #Создаём линии региона
                location_line = []
                for number_location in range((len(region_map))): #Создаём значения линий
                    top_down_description = ''
                    left_right_description = ''                  
                    if number_location_line == 0: #Обрабатываем верхний край региона
                        if number_line != 0:
                            top_down_description = (selecting_generator(region_map[number_line - 1][number_seed]))
                    elif number_location_line == (len(region_map) - 1): #Обрабатываем нижний край региона
                        if number_line != (len(region_map) - 1):
                            top_down_description = (selecting_generator(region_map[number_line + 1][number_seed]))
                    if number_location == 0: #Обрабатываем левый край региона
                        if number_seed != 0:
                            left_right_description = (selecting_generator(region_map[number_line][number_seed - 1]))
                    elif number_location != (len(region_map) - 1): #Обрабатываем правый край региона
                        if number_seed != (len(region_map) - 1):
                            left_right_description = (selecting_generator(region_map[number_line][number_seed + 1]))
                    for_generator = selecting_generator(region_map[number_line][number_seed])
                    description_seed_merge(for_generator, top_down_description)
                    description_seed_merge(for_generator, left_right_description)
                    description_for_generator = Description_location(for_generator)
                    location_line.append([mini_region_generate(description_for_generator, grid), description_for_generator])
                region.append(location_line)
            region_line.append(region)
        raw_global_region_map.append(region_line)
    global_mini_region_map = gluing_location(raw_global_region_map, value_region_box, value_region_box)
    post_mini_region_generate(global_mini_region_map)
    global_map = []
    for number_line in range(len(global_mini_region_map)):
        location_line = []
        for number_seed in range(len(global_mini_region_map[number_line])): #Определяем номер региона в линии регионов
            location_line.append(master_location_generate(global_mini_region_map[number_line][number_seed], game_field_size, grid))
        global_map.append(location_line)

    master_postgenerate_field_tiles(global_map, value_region_box, game_field_size) #Постобработка многоуровневости
    
    return global_map

def location_generate(description, game_field_size):
    """
        Создаёт cлучайную локацию по описанию и размеру
    """
    ready_location = Location(description[0], 35, [], '')

    for i in range(game_field_size):
        ready_location.chunk.append([Tile(random.choice(description[2])) for x in range(game_field_size)])
    ready_location.temperature = [random.randrange(description[1][0], description[1][1])]
    ready_location.icon = description[4]
    ready_location.price_move = description[5]

    return ready_location

def region_generate(size_region_box):
    """
        Генерирует карту регионов
    """
    region_map = []
    for i in range(size_region_box):
        region_map.append([random.randrange(12) for x in range(size_region_box)])
    return region_map


def gluing_location(raw_gluing_map, grid, count_block):
    """
        Склеивает чанки и локации в единое поле из "сырых" карт
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

    ПОСТОБРАБОТКА ГОТОВОЙ ИГРОВОЙ КАРТЫ
    
    Определяет какие тайлы находятся на краю однородного тайлового поля и изменяет их .type что бы в дальнейшем присвоить соответствующий тайлсет.
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_postgenerate_field_tiles(global_map, value_region_box, chunk_size):
    """
        Обрабатывает готовую карту мира
    """
    detected_list = ['~', '▲', 'C']
    detected_list_2 = ['F', 'u', 'j']

    for number_global_line, global_line in enumerate(global_map):
        for number_global_location, location in enumerate(global_line):
            for number_line, line in enumerate(location.chunk):
                for number_tile, tile in enumerate(line):
                    if tile.icon in detected_list:
                        direction = {
                                    'up': False,
                                    'down': False,
                                    'left': False,
                                    'right': False,
                                    }
                        if 0 < number_global_line < len(global_map) - 1: # По оси Y
                            if number_line > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line - 1][number_tile].icon:
                                    direction['up'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line - 1][
                                    number_global_location].chunk[chunk_size - 1][number_tile].icon:
                                    direction['up'] = True

                            if number_line < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line + 1][number_tile].icon:
                                    direction['down'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line + 1][
                                        number_global_location].chunk[0][number_tile].icon:
                                    direction['down'] = True

                        elif number_global_line == 0:
                            if number_line > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line - 1][number_tile].icon:
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line + 1][number_tile].icon:
                                    direction['down'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line + 1][
                                        number_global_location].chunk[0][number_tile].icon:
                                    direction['down'] = True

                        elif number_global_line == len(global_map) - 1:
                            if number_line > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line - 1][number_tile].icon:
                                    direction['up'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line - 1][
                                        number_global_location].chunk[chunk_size - 1][number_tile].icon:
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line + 1][number_tile].icon:
                                    direction['down'] = True


                        if 0 < number_global_location < len(global_map[0]) - 1: # По оси Х
                            if number_tile > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile - 1].icon:
                                    direction['left'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line][
                                        number_global_location - 1].chunk[number_line][chunk_size - 1].icon:
                                    direction['left'] = True

                            if number_tile < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile + 1].icon:
                                    direction['right'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line][
                                        number_global_location + 1].chunk[number_line][0].icon:
                                    direction['right'] = True

                        elif number_global_location == 0:
                            if number_tile > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile - 1].icon:
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile + 1].icon:
                                    direction['right'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line][
                                        number_global_location + 1].chunk[number_line][0].icon:
                                    direction['right'] = True

                        elif number_global_location == len(global_map[0]) - 1:
                            if number_tile > 0:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile - 1].icon:
                                    direction['left'] = True
                            else:
                                if location.chunk[number_line][number_tile].icon == global_map[number_global_line][
                                        number_global_location - 1].chunk[number_line][chunk_size - 1].icon:
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if location.chunk[number_line][number_tile].icon == location.chunk[number_line][number_tile + 1].icon:
                                    direction['right'] = True


                        if direction['up'] and direction['down'] and direction['left'] and direction['right']:
                            tile.type = '1'
                        elif direction['up'] and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = '2'
                        elif direction['up'] and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = '3'
                        elif not(direction['up']) and direction['down'] and direction['left'] and direction['right']:
                            tile.type = '4'
                        elif direction['up'] and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = '5'
                        elif direction['up'] and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = '6'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = '7'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = '8'
                        elif not(direction['up']) and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = '9'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = 'A'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and not(direction['right']):
                            tile.type = 'B'
                        elif not(direction['up']) and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = 'C'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'D'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = 'E'
                        elif direction['up'] and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'F'
                        else:
                            tile.type = '0'
                            
                    elif tile.icon in detected_list_2:
                        if tile.icon == 'F':
                            tile.type = random.choice(['0', '1', '2', '3', '4', '5', '6', '7'])
                        if tile.icon == 'u':
                            tile.type = random.choice(['0', '1'])
                        if tile.icon == 'j':
                            tile.type = random.choice(['0', '1'])

    old_multilevelness_calculation(global_map, chunk_size)
    multilevelness_calculation(global_map, chunk_size, '▲') 
    multilevelness_calculation(global_map, chunk_size, '▲')
    multilevelness_calculation(global_map, chunk_size, '▲')
    multilevelness_calculation(global_map, chunk_size, '▲')
    multilevelness_calculation(global_map, chunk_size, '▲')
    multilevelness_calculation(global_map, chunk_size, 'C')


def timeit(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time() - start)
        return result
    return inner



@timeit
def multilevelness_calculation(global_map, chunk_size, search_tile):
    """
        Делает тайловые поля многоуровневыми 

        Проверяет является ли соседний тайл в выбраном направлении похожим на него или находится ли соседний тайл в списке изменненных.

        
    """
    detected_list = ['1', 'U']
    list_of_verified_titles = []


    for number_global_line, global_line in enumerate(global_map):
        for number_global_location, location in enumerate(global_line):
            for number_line, line in enumerate(location.chunk):
                for number_tile, tile in enumerate(line):
                    if tile.icon == search_tile and tile.type == '1' or tile.type == 'U':
                        direction = {
                                    'up': False,
                                    'down': False,
                                    'left': False,
                                    'right': False,
                                    }
                        if 0 < number_global_line < len(global_map) - 1: # По оси Y
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and ([number_global_line,
                                        number_global_location, number_line - 1, number_tile] in list_of_verified_titles or location.chunk[number_line - 1][
                                        number_tile].type in detected_list):
                                    direction['up'] = True
                            else:
                                if tile.icon == global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][
                                        number_tile].icon and ([number_global_line - 1, number_global_location, chunk_size - 1, number_tile
                                        ] in list_of_verified_titles or global_map[number_global_line - 1][number_global_location].chunk[
                                        chunk_size - 1][number_tile].type in detected_list):
                                    direction['up'] = True

                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and ([number_global_line, number_global_location,
                                        number_line + 1, number_tile] in list_of_verified_titles or location.chunk[number_line + 1][number_tile].type in detected_list):
                                    direction['down'] = True
                            else:
                                if tile.icon == global_map[number_global_line + 1][number_global_location].chunk[0][number_tile
                                        ].icon and ([number_global_line + 1, number_global_location, 0, number_tile] in list_of_verified_titles or global_map[
                                        number_global_line + 1][number_global_location].chunk[0][number_tile].type in detected_list):
                                    direction['down'] = True

                        elif number_global_line == 0:
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and ([number_global_line, number_global_location,
                                        number_line - 1, number_tile] in list_of_verified_titles or location.chunk[number_line - 1][number_tile].type in detected_list):
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and ([number_global_line, number_global_location,
                                        number_line + 1, number_tile] in list_of_verified_titles or location.chunk[number_line + 1][number_tile].type in detected_list):
                                    direction['down'] = True
                            else:
                                if tile.icon == global_map[number_global_line + 1][number_global_location].chunk[0][number_tile].icon and ([number_global_line + 1,
                                        number_global_location, 0, number_tile] in list_of_verified_titles or global_map[number_global_line + 1][
                                        number_global_location].chunk[0][number_tile].type in detected_list):
                                    direction['down'] = True

                        elif number_global_line == len(global_map) - 1:
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and ([number_global_line, number_global_location,
                                        number_line - 1, number_tile] in list_of_verified_titles or location.chunk[number_line - 1][number_tile
                                        ].type in detected_list):
                                    direction['up'] = True
                            else:
                                if tile.icon == global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].icon and ([
                                        number_global_line - 1, number_global_location, chunk_size - 1, number_tile] in list_of_verified_titles or global_map[
                                        number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].type in detected_list):
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and ([number_global_line, number_global_location,
                                        number_line + 1, number_tile] in list_of_verified_titles or location.chunk[number_line + 1][number_tile].type in detected_list):
                                    direction['down'] = True


                        if 0 < number_global_location < len(global_map[0]) - 1: # По оси Х
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and ([number_global_line, number_global_location, number_line,
                                        number_tile - 1] in list_of_verified_titles or location.chunk[number_line][number_tile - 1].type in detected_list):
                                    direction['left'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1
                                        ].icon and ([number_global_line, number_global_location - 1, number_line, chunk_size - 1] in list_of_verified_titles or global_map[
                                        number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].type in detected_list):
                                    direction['left'] = True

                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and ([number_global_line, number_global_location, number_line,
                                        number_tile + 1] in list_of_verified_titles or location.chunk[number_line][number_tile + 1].type in detected_list):
                                    direction['right'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location + 1].chunk[number_line][0].icon and ([number_global_line,
                                        number_global_location + 1, number_line, 0] in list_of_verified_titles or global_map[number_global_line][
                                        number_global_location + 1].chunk[number_line][0].type in detected_list):
                                    direction['right'] = True

                        elif number_global_location == 0:
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and ([number_global_line, number_global_location, number_line,
                                        number_tile - 1] in list_of_verified_titles or location.chunk[number_line][number_tile - 1].type in detected_list):
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and ([number_global_line, number_global_location, number_line,
                                        number_tile + 1] in list_of_verified_titles or location.chunk[number_line][number_tile + 1].type in detected_list):
                                    direction['right'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location + 1].chunk[number_line][0].icon and ([number_global_line,
                                        number_global_location + 1, number_line, 0] in list_of_verified_titles or global_map[number_global_line][
                                        number_global_location + 1].chunk[number_line][0].type in detected_list):
                                    direction['right'] = True

                        elif number_global_location == len(global_map[0]) - 1:
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and ([number_global_line, number_global_location,
                                        number_line, number_tile - 1] in list_of_verified_titles or location.chunk[number_line][number_tile - 1].type in detected_list):
                                    direction['left'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1
                                        ].icon and ([number_global_line, number_global_location - 1, number_line, chunk_size - 1] in list_of_verified_titles or global_map[
                                        number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].type in detected_list):
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and ([number_global_line, number_global_location, number_line,
                                        number_tile + 1] in list_of_verified_titles or location.chunk[number_line][number_tile + 1].type in detected_list):
                                    direction['right'] = True

                        
                        if direction['up'] and direction['down'] and direction['left'] and direction['right']:
                            tile.type = '1'
                        elif direction['up'] and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = 'G'
                        elif direction['up'] and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = 'H'
                        elif not(direction['up']) and direction['down'] and direction['left'] and direction['right']:
                            tile.type = 'I'
                        elif direction['up'] and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = 'J'
                        elif direction['up'] and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = 'K'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = 'L'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = 'M'
                        elif not(direction['up']) and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = 'N'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = 'O'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and not(direction['right']):
                            tile.type = 'P'
                        elif not(direction['up']) and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = 'Q'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'R'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = 'S'
                        elif direction['up'] and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'T'
                        else:
                            tile.type = 'U'
                        list_of_verified_titles.append([number_global_line, number_global_location, number_line, number_tile])



def multilevelness_calculation_alternative(global_map, chunk_size, search_tile):
    """
        Делает тайловые поля многоуровневыми

        Создает список подходящих тайлов, и для каждого из них проверяет находятся ли соседние тайлы в списке

        Время выполнения для одного слоя 17 секунд
        
    """
    list_of_verified_tiles = []


    for number_global_line, global_line in enumerate(global_map):
        for number_global_location, location in enumerate(global_line):
            for number_line, line in enumerate(location.chunk):
                for number_tile, tile in enumerate(line):
                    if tile.icon == search_tile and tile.type == '1':
                        list_of_verified_tiles.append([number_global_line, number_global_location, number_line, number_tile])
                        
    direction = {
                 'up': False,
                 'down': False,
                 'left': False,
                 'right': False,
                }

    for verified_tile in list_of_verified_tiles:

        if 0 < verified_tile[0] < len(global_map) - 1: # По оси Y
            print(f"0 < verified_tile[0] < len(global_map) - 1")
            if verified_tile[2] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2] - 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['up'] = True
            else:
                if [verified_tile[0] - 1, verified_tile[1], chunk_size - 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['up'] = True

            if verified_tile[2] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2] + 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['down'] = True
            else:
                if [verified_tile[0] + 1, verified_tile[1], 0, verified_tile[3]] in list_of_verified_tiles:
                    direction['down'] = True

        elif verified_tile[0] == 0:
            print(f"verified_tile[0] == 0")
            if verified_tile[2] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2] - 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['up'] = True
            if verified_tile[2] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2] + 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['down'] = True
            else:
                if [verified_tile[0] + 1, verified_tile[1], 0, verified_tile[3]] in list_of_verified_tiles:
                    direction['down'] = True

        elif verified_tile[0] == len(global_map) - 1:
            print(f"verified_tile[0] == len(global_map) - 1")
            if verified_tile[2] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2] - 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['up'] = True
            else:
                if [verified_tile[0] - 1, verified_tile[1], chunk_size - 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['up'] = True
            if verified_tile[2] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2] + 1, verified_tile[3]] in list_of_verified_tiles:
                    direction['down'] = True


        if 0 < verified_tile[1] < len(global_map[0]) - 1: # По оси Х
            print(f"0 < verified_tile[1] < len(global_map[0]) - 1")
            if verified_tile[3] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] - 1] in list_of_verified_tiles:
                    direction['left'] = True
            else:
                if [verified_tile[0], verified_tile[1] - 1, verified_tile[2], chunk_size - 1] in list_of_verified_tiles:
                    direction['left'] = True

            if verified_tile[3] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] + 1] in list_of_verified_tiles:
                    direction['right'] = True
            else:
                if [verified_tile[0], verified_tile[1] + 1, verified_tile[2], 0] in list_of_verified_tiles:
                    direction['right'] = True

        elif verified_tile[1] == 0:
            print(f"verified_tile[1] == 0")
            if verified_tile[3] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] - 1] in list_of_verified_tiles:
                    direction['left'] = True
            if verified_tile[3] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] + 1] in list_of_verified_tiles:
                    direction['right'] = True
            else:
                if [verified_tile[0], verified_tile[1] + 1, verified_tile[2], 0] in list_of_verified_tiles:
                    direction['right'] = True

        elif verified_tile[1] == len(global_map[0]) - 1:
            print(f"verified_tile[1] == len(global_map[0]) - 1")
            if verified_tile[3] > 0:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] - 1] in list_of_verified_tiles:
                    direction['left'] = True
            else:
                if [verified_tile[0], verified_tile[1] - 1, verified_tile[2], chunk_size - 1] in list_of_verified_tiles:
                    direction['left'] = True
            if verified_tile[3] < chunk_size - 1:
                if [verified_tile[0], verified_tile[1], verified_tile[2], verified_tile[3] + 1] in list_of_verified_tiles:
                    direction['right'] = True
        print(direction)
                        
        if direction['up'] and direction['down'] and direction['left'] and direction['right']:
            print(f'{verified_tile} изменился 1')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = '1'
        elif direction['up'] and not(direction['down']) and direction['left'] and direction['right']:
            print(f'{verified_tile} изменился G')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'G'
        elif direction['up'] and direction['down'] and not(direction['left']) and direction['right']:
            print(f'{verified_tile} изменился H')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'H'
        elif not(direction['up']) and direction['down'] and direction['left'] and direction['right']:
            print(f'{verified_tile} изменился I')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'I'
        elif direction['up'] and direction['down'] and direction['left'] and not(direction['right']):
            print(f'{verified_tile} изменился J')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'J'
        elif direction['up'] and not(direction['down']) and direction['left'] and not(direction['right']):
            print(f'{verified_tile} изменился K')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'K'
        elif direction['up'] and not(direction['down']) and not(direction['left']) and direction['right']:
            print(f'{verified_tile} изменился L')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'L'
        elif not(direction['up']) and direction['down'] and not(direction['left']) and direction['right']:
            print(f'{verified_tile} изменился M')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'M'
        elif not(direction['up']) and direction['down'] and direction['left'] and not(direction['right']):
            print(f'{verified_tile} изменился N')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'N'
        elif not(direction['up']) and not(direction['down']) and direction['left'] and not(direction['right']):
            print(f'{verified_tile} изменился O')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'O'
        elif direction['up'] and not(direction['down']) and not(direction['left']) and not(direction['right']):
            print(f'{verified_tile} изменился P')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'P'
        elif not(direction['up']) and not(direction['down']) and not(direction['left']) and direction['right']:
            print(f'{verified_tile} изменился Q')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'Q'
        elif not(direction['up']) and direction['down'] and not(direction['left']) and not(direction['right']):
            print(f'{verified_tile} изменился R')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'R'
        elif not(direction['up']) and not(direction['down']) and direction['left'] and direction['right']:
            print(f'{verified_tile} изменился S')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'S'
        elif direction['up'] and direction['down'] and not(direction['left']) and not(direction['right']):
            print(f'{verified_tile} изменился T')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'T'
        else:
            print(f'{verified_tile} не изменился')
            global_map[verified_tile[0]][verified_tile[1]].chunk[verified_tile[2]][verified_tile[3]].type = 'U'




def old_multilevelness_calculation(global_map, chunk_size):
    """
        Делает горы и водоёмы двухуровневыми
    """
    detected_list = ['1', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']


    for number_global_line, global_line in enumerate(global_map):
        for number_global_location, location in enumerate(global_line):
            for number_line, line in enumerate(location.chunk):
                for number_tile, tile in enumerate(line):
                    if (tile.icon == '▲' or tile.icon == '~')and tile.type == '1':
                        direction = {
                                    'up': False,
                                    'down': False,
                                    'left': False,
                                    'right': False,
                                    }
                        if 0 < number_global_line < len(global_map) - 1: # По оси Y
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and location.chunk[number_line - 1][number_tile].type in detected_list:
                                    direction['up'] = True
                            else:
                                if tile.icon == global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].icon and global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].type in detected_list:
                                    direction['up'] = True

                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and location.chunk[number_line + 1][number_tile].type in detected_list:
                                    direction['down'] = True
                            else:
                                if tile.icon == global_map[number_global_line + 1][number_global_location].chunk[0][number_tile].icon and global_map[number_global_line + 1][number_global_location].chunk[0][number_tile].type in detected_list:
                                    direction['down'] = True

                        elif number_global_line == 0:
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and location.chunk[number_line - 1][number_tile].type in detected_list:
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and tile.icon == location.chunk[number_line + 1][number_tile].type in detected_list:
                                    direction['down'] = True
                            else:
                                if tile.icon == global_map[number_global_line + 1][number_global_location].chunk[0][number_tile].icon and global_map[number_global_line + 1][number_global_location].chunk[0][number_tile].type in detected_list:
                                    direction['down'] = True

                        elif number_global_line == len(global_map) - 1:
                            if number_line > 0:
                                if tile.icon == location.chunk[number_line - 1][number_tile].icon and location.chunk[number_line - 1][number_tile].type in detected_list:
                                    direction['up'] = True
                            else:
                                if tile.icon == global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].icon and global_map[number_global_line - 1][number_global_location].chunk[chunk_size - 1][number_tile].type in detected_list:
                                    direction['up'] = True
                            if number_line < chunk_size - 1:
                                if tile.icon == location.chunk[number_line + 1][number_tile].icon and location.chunk[number_line + 1][number_tile].type in detected_list:
                                    direction['down'] = True


                        if 0 < number_global_location < len(global_map[0]) - 1: # По оси Х
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and location.chunk[number_line][number_tile - 1].type in detected_list:
                                    direction['left'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].icon and global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].type in detected_list:
                                    direction['left'] = True

                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and location.chunk[number_line][number_tile + 1].type in detected_list:
                                    direction['right'] = Truedetected_list = ['1', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location + 1].chunk[number_line][0].icon and global_map[number_global_line][number_global_location + 1].chunk[number_line][0].type in detected_list:
                                    direction['right'] = True

                        elif number_global_location == 0:
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and location.chunk[number_line][number_tile - 1].type in detected_list:
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and location.chunk[number_line][number_tile + 1].type in detected_list:
                                    direction['right'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location + 1].chunk[number_line][0].icon and global_map[number_global_line][number_global_location + 1].chunk[number_line][0].type in detected_list:
                                    direction['right'] = True

                        elif number_global_location == len(global_map[0]) - 1:
                            if number_tile > 0:
                                if tile.icon == location.chunk[number_line][number_tile - 1].icon and location.chunk[number_line][number_tile - 1].type in detected_list:
                                    direction['left'] = True
                            else:
                                if tile.icon == global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].icon and global_map[number_global_line][number_global_location - 1].chunk[number_line][chunk_size - 1].type in detected_list:
                                    direction['left'] = True
                            if number_tile < chunk_size - 1:
                                if tile.icon == location.chunk[number_line][number_tile + 1].icon and location.chunk[number_line][number_tile + 1].type in detected_list:
                                    direction['right'] = True


                        if direction['up'] and direction['down'] and direction['left'] and direction['right']:
                            tile.type = '1'
                        elif direction['up'] and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = 'G'
                        elif direction['up'] and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = 'H'
                        elif not(direction['up']) and direction['down'] and direction['left'] and direction['right']:
                            tile.type = 'I'
                        elif direction['up'] and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = 'J'
                        elif direction['up'] and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = 'K'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = 'L'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and direction['right']:
                            tile.type = 'M'
                        elif not(direction['up']) and direction['down'] and direction['left'] and not(direction['right']):
                            tile.type = 'N'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and not(direction['right']):
                            tile.type = 'O'
                        elif direction['up'] and not(direction['down']) and not(direction['left']) and not(direction['right']):
                            tile.type = 'P'
                        elif not(direction['up']) and not(direction['down']) and not(direction['left']) and direction['right']:
                            tile.type = 'Q'
                        elif not(direction['up']) and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'R'
                        elif not(direction['up']) and not(direction['down']) and direction['left'] and direction['right']:
                            tile.type = 'S'
                        elif direction['up'] and direction['down'] and not(direction['left']) and not(direction['right']):
                            tile.type = 'T'
                        else:
                            tile.type = 'U'
            


