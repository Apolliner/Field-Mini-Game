import os
import copy
import random
import string
import keyboard
import sys

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ СО СВОБОДНОЙ КАМЕРОЙ И ГЛОБАЛЬНОЙ КАРТОЙ

    РЕАЛИЗОВАТЬ:
    1)Генерацию с чанками #РЕАЛИЗОВАНО
    2)Отображение минимального набора чанков и их выгрузку при удалении камеры - сделать это через срезы и готовый алгоритм распаковки сырой карты
    с регионами в готовую единую карту #РЕАЛИЗОВАНО
    3)Объединить версию со свободной камерой и версию с регионами #РЕАЛИЗОВАНО
    4)"подружить" друг с другом края локаций #РЕАЛИЗОВАНО
    5)Реализовать повторный пост-генератор карты минирегионов, который копирует значение боковых значений мини регионов
    в прилегающие края следующих мини регионов. Слева ==> направо, сверху ==> вниз #РЕАЛИЗОВАНО
    6)Подготовить код к вменяемому добавлению элементов геймплея. Отдельно генерация мира, отдельно управление и рассчёт положения, отдельно печать на экран
    7)Добавить элементы геймплея
    8)Реализовать вывод всего изображения за один проход в струкрурированный интерфейс
"""


class Temperature:
    """ Содержит температуру среды и температуру персонажа """
    def __init__(self, temperature_environment, temperature_person):
        self.environment = temperature_environment
        self.person = temperature_person

class Position:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    def __init__(self, assemblage_point:list, dynamic:list, chanks_use_map:list):
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chank = chanks_use_map

class Location:
    """ Содержит описание локации """
    def __init__(self, name:str, temperature:float, chank:list, icon:str):
        self.name = name
        self.temperature = temperature
        self.chank = chank
        self.icon = icon

class Description_location:
    """ Содержит информацию для генератора локаций """
    def __init__(self, description:list):
        self.name = description[0]
        self.temperature = description[1]
        self.main_tileset = description[2]
        self.random_tileset = description[3]
        self.icon = description[4]

class Interfase:
    """ Содержит элементы для последующего вывода на экран """
    def __init__(self, game_field, biom_map, minimap_on, text1, text2, text3, text4, text5, text6, text7, text8, text9, text10):
        self.game_field = game_field
        self.biom_map = biom_map
        self.minimap_on = minimap_on
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
    for line in range(len(location)):
        for tile in range(len(location)):
            if random.randrange(10)//9:
                location[line][tile] = random.choice(description.random_tileset)
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
                            top_down_tile = mini_region_map[0][number_line - 1][number_seed]
                    elif number_tile_line >= (count_block - 1): #Обрабатываем нижний край мини региона
                        if number_tile != (count_block - 1):
                            top_down_tile = mini_region_map[0][number_line][number_seed]
                    if number_tile <= 1: #Обрабатываем левый край мини региона
                        if number_seed != 0:
                            left_right_tile = mini_region_map[0][number_line][number_seed - 1]
                    elif number_tile != (count_block - 1): #Обрабатываем правый край мини региона
                        if number_seed != (count_block - 1):
                            left_right_tile = mini_region_map[0][number_line][number_seed]
     
                    main_tile = mini_region_map[0][number_line][number_seed]
                    main_tile = mini_region_tile_merge(main_tile, top_down_tile)
                    main_tile = mini_region_tile_merge(main_tile, left_right_tile)
                    tile_line.append(main_tile)
                region_location.append(tile_line)
            region_location_line.append(region_location)
        raw_location.append(region_location_line)
        
    ready_location = Location(mini_region_map[1].name, 35, [], '')
    ready_location.chank = random_location_post_generate(gluing_location(raw_location, grid, count_block), mini_region_map[1])
    temperature = mini_region_map[1].temperature
    ready_location.temperature = [random.randrange(temperature[0], temperature[1])]
    ready_location.icon = mini_region_map[1].icon
    return ready_location


def selecting_generator(seed):
    """
        Содержит и выдаёт значения семян генерации.
    """
    seed_dict = {
                    0: ['desert',             [40.0,60.0], ['.'],                   ['j'],              'j'],
                    1: ['semidesert',         [35.0,50.0], ['.', ','],              ['▲', 'o', 'i'],    '.'],
                    2: ['cliff semidesert',   [35.0,50.0], ['▲', 'A', '.', ','],    ['o', 'i'],         'A'],
                    3: ['saline land',        [40.0,50.0], [';'],                   [':'],              ';'],
                    4: ['dried field',        [30.0,40.0], ['„', ','],              ['o', 'u'],         ','],
                    5: ['field',              [20.0,35.0], ['u', '„', ','],         ['ü', 'o'],         '„'],
                    6: ['hills',              [20.0,35.0], ['▲', 'o'],              ['„', ','],         '▲'],
                    7: ['oasis',              [15.0,30.0], ['F', '„', '~'],         ['P', ','],         'P'],
                    8: ['salty lake',         [25.0,40.0], ['~', ','],              ['„', '.'],         '~'],
                    9: ['swamp',              [15.0,30.0], ['ü', 'u', '~'],         ['„', ','],         'ü'],
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

def master_generate(value_region_box:int, game_field_size:int, grid):
    """
        Генерирует глобальную карту минирегионов, ориентируясь на карту регионов.
    """
    region_map = region_generate(value_region_box)

    progress_bar(20, 'Регионы сгенерированы')
    
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
    progress_bar(40, 'Глобальная карта мини регионов построена')
    global_mini_region_map = gluing_location(raw_global_region_map, value_region_box, value_region_box)
    progress_bar(60, 'Постобработка мини регионов')
    post_mini_region_generate(global_mini_region_map)
    global_map = []
    progress_bar(80, 'Глобальные регионы отданы на генерацию локаций')
    for number_line in range(len(global_mini_region_map)):
        location_line = []
        for number_seed in range(len(global_mini_region_map[number_line])): #Определяем номер региона в линии регионов
            location_line.append(master_location_generate(global_mini_region_map[number_line][number_seed], game_field_size, grid))
        global_map.append(location_line)
    progress_bar(100, 'Игровая карта готова')
    return global_map

def location_generate(description, game_field_size):
    """
        Создаёт cлучайную локацию по описанию и размеру
    """
    ready_location = Location(description[0], 35, [], '')

    for i in range(game_field_size):
        ready_location.chank.append([random.choice(description[2]) for x in range(game_field_size)])
    ready_location.temperature = [random.randrange(description[1][0], description[1][1])]
    ready_location.icon = description[4]

    return ready_location

def region_generate(size_region_box):
    """
        Генерирует карту регионов
    """
    region_map = []
    for i in range(size_region_box):
        region_map.append([random.randrange(10) for x in range(size_region_box)])
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

    МЕСТОПОЛОЖЕНИЕ ПЕРСОНАЖА И ЗАГРУЗКА ДИНАМИЧЕСКОЙ КАРТЫ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""



def calculation_assemblage_point(global_map:list, position, chank_size:int, change):
    """
        Перерассчитывает положение точки сборки, динамические координаты, при необходимости перерассчитывает динамический чанк.
    """
    
    if position.dynamic[0] > (chank_size//2 + chank_size - 1):
        position.assemblage_point[0] += 1
        position.dynamic[0] -= chank_size
            
    elif position.dynamic[0] < chank_size//2:
        position.assemblage_point[0] -= 1
        position.dynamic[0] += chank_size
    else:
        change -= 1
        
    if position.dynamic[1] > (chank_size//2 + chank_size - 1):
        position.assemblage_point[1] += 1
        position.dynamic[1] -= chank_size
            
    elif position.dynamic[1] < chank_size//2:
        position.assemblage_point[1] -= 1
        position.dynamic[1] += chank_size
    else:
        change -= 1

    if change != 0:
        assemblage_chank = []

        line_slice = global_map[position.assemblage_point[0]:(position.assemblage_point[0] + 2)]
    
        for line in line_slice:
            line = line[position.assemblage_point[1]:(position.assemblage_point[1] + 2)]
            assemblage_chank.append(line)
        for number_line in range(len(assemblage_chank)):
            for chank in range(len(assemblage_chank)):
                assemblage_chank[number_line][chank] = assemblage_chank[number_line][chank].chank
        position.chanks_use_map = gluing_location(assemblage_chank, 2, chank_size)

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА ИГРОВЫХ СОБЫТИЙ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def game_events():
    pass


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ВВОД ИГРОКА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""        

def request_move_person(global_map:list, position, chank_size:int, go_to_print):
    """
        Спрашивает ввод, меняет динамическое местоположение персонажа

    """
    keyboard_loop = True
    while keyboard_loop:
        move = keyboard.read_key()
        if move == 'w' or move == 'up' or move == 'ц':
            if position.chanks_use_map[position.dynamic[0] - 1][position.dynamic[1]] == '▲':
                pass
            else:
                position.dynamic[0] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 'a' or move == 'left' or move == 'ф':
            if position.chanks_use_map[position.dynamic[0]][position.dynamic[1] - 1] == '▲':
                pass
            else:
                position.dynamic[1] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 's' or move == 'down' or move == 'ы':
            if position.chanks_use_map[position.dynamic[0] + 1][position.dynamic[1]] == '▲':
                pass
            else:
                position.dynamic[0] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 'd' or move == 'right' or move == 'в':
            if position.chanks_use_map[position.dynamic[0]][position.dynamic[1] + 1] == '▲':
                pass
            else:
                position.dynamic[1] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
        elif move == 'space':
            keyboard_loop = False
        elif move == 'm' or move == 'ь':
            go_to_print.minimap_on = (go_to_print.minimap_on == False)
            keyboard_loop = False
        else: pass


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ФОРМИРОВАНИЕ БЛОКОВ ДЛЯ ВЫВОДА НА ЭКРАН

    Работает с классом Interfase, содержащимся в go_to_print
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""      

def progress_bar(percent, description):
    """
        Отображает вывод на экран прогресс бара
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    progress = description + '\n['
    for five_percent in range(percent//2):
        progress += '█'
    for empty_percent in range((50 - percent//2)):
        progress += '░'
    progress += ']'

    print(progress)

def test_print_chank(position):
    """
        Печатает загруженный кусок карты

    """
    draw_box = ''
    for line in position.chanks_use_map:
        print_line = ''
        for tile in line:
            print_line += tile + ' '
        draw_box += print_line + '\n'

    print(draw_box)

def test_print_global_map_biome(global_map, position, go_to_print):
    """
        Печатает упрощенную схему глобальной карты по биомам

    """

    minimap = []
    for number_line in range(len(global_map)):
        print_line = ''
        for biom in range(len(global_map[number_line])):
            if number_line == position.assemblage_point[0] and biom == position.assemblage_point[1]:
                go_to_print.text2 = global_map[number_line][biom].name
                go_to_print.text3 = [global_map[number_line][biom].temperature, 36.6]
                print_line += '☺ '
                
            else:
                print_line += global_map[number_line][biom].icon + ' '
        minimap.append((print_line))
    go_to_print.biom_map = minimap


def ground_dict(tile):

    ground_dict =   {
                    'j': 'бархан',
                    '.': 'горячий песок',
                    ',': 'жухлая трава',
                    'o': 'валун',
                    'A': 'холм',
                    '▲': 'скала',
                    'i': 'кактус',
                    ':': 'солончак',
                    ';': 'солончак',
                    '„': 'трава',
                    'u': 'высокая трава',
                    'ü': 'колючая трава',
                    'F': 'чахлое дерево',
                    'P': 'раскидистое дерево',
                    '~': 'солёная вода',                 
                    }
    if tile in  ground_dict:
        return ground_dict[tile]
    else:
        return 'нечто непонятное'

def draw_field_calculations(position:list, views_field_size:int):
    """
        Формирует итоговое изображение игрового поля на печать
    """
    half_views = (views_field_size//2)
    start_stop = [(position.dynamic[0] - half_views), (position.dynamic[1] - half_views), (position.dynamic[0] + half_views + 1),(position.dynamic[1] + half_views + 1)]
    line_views = position.chanks_use_map[start_stop[0]:start_stop[2]]
    
    draw_field = []
    for line in line_views:
        line = line[start_stop[1]:start_stop[3]]
        draw_field.append(line)
    return draw_field 

def draw_game_field(position, views_field_size:int, go_to_print):
    """
        Выводит изображение игрового поля на экран
    """

    draw_field = draw_field_calculations(position, views_field_size)
    draw_box = []
    for line in range(len(draw_field)):
        print_line = ''
        for tile in range(len(draw_field)):
            if line == views_field_size//2 and tile == views_field_size//2:
                ground = draw_field[line][tile]
                print_line += '☺' + ' '
            else:
                print_line += draw_field[line][tile] + ' '
        draw_box.append(print_line)
    go_to_print.game_field = draw_box
    go_to_print.text1 = (position.assemblage_point, ' - Позиция точки сборки | ', position.dynamic, ' - динамическая позиция | под ногами:', ground_dict(ground) )

    
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ИНТЕРФЕЙС И ВЫВОД ИТОГОВОГО ИЗОБРАЖЕНИЯ НА ЭКРАН
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def print_interfase(go_to_print, frame_size):
    """
        Отвечает за итоговый вывод содержимого на экран
    """
    

    raw_frame = []
    
    for line in range(frame_size[0]):
        if line < 3:
            raw_frame.append('')
        else:
            raw_frame.append('')
    #print game_field
    for line in range(len(go_to_print.game_field)):
        raw_frame[(line + 3)] += '      ' + go_to_print.game_field[line]

    if go_to_print.minimap_on: #print biom_map
        for line in range(len(go_to_print.biom_map)):
            raw_frame[(line + 3)] += '      ' + go_to_print.biom_map[line]

    raw_frame[4+len(go_to_print.game_field)] += '   ' + str(go_to_print.text1)

    raw_frame[5+len(go_to_print.game_field)] += '   Вы находитесь в ' + str(go_to_print.text2)

    if go_to_print.minimap_on:
        raw_frame[6+len(go_to_print.game_field)] += '   Температура среды: ' + str(go_to_print.text3[0][0]) + ' градусов. Температура персонажа: ' + str(go_to_print.text3[1]) + ' градусов.'

    frame = ''
    for line in raw_frame:
        frame += line + '\n'



        
    os.system('cls' if os.name == 'nt' else 'clear')
    print(frame)



"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    УПРАВЛЯЮЩИЙ БЛОК
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


def game_loop(global_map:list, position:list, chank_size, frame_size):
    """
        Здесь происходят все игровые события
        
    """
    go_to_print = Interfase([], [], False, '', '', '', '', '', '', '', '', '', '')

    
    while game_loop :
        request_move_person(global_map, position, chank_size, go_to_print)
        draw_game_field(position, chank_size, go_to_print)
        if go_to_print.minimap_on:
            test_print_global_map_biome(global_map, position, go_to_print)
        print_interfase(go_to_print, frame_size)
        
        

def main():
    """
        Запускает игру
        
    """
    chank_size = 35         #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    value_region_box = 5    #Количество регионов в квадрате.
    grid = 5                #Можно любое, но лучше кратное размеру игрового экрана. Иначе обрежет область видимости.
    frame_size = [44, 40]   #Размер одного кадра [высота, ширина].


    progress_bar(5, 'Запуск игры') 
    global_map = master_generate(value_region_box, chank_size, grid)

    
    position = Position([value_region_box//2, value_region_box//2], [chank_size//2, chank_size//2], [])
    #test_print_global_map_biome(global_map, position)
    calculation_assemblage_point(global_map, position, chank_size, 3)
    
    game_loop(global_map, position, chank_size, frame_size)
    
    print('Игра окончена!')

main()
    
