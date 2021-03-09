import os
import copy
import random
import string
import keyboard
import time

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
    9)Отдельная карта мира для закадровой симуляции NPC #ПОДОШЛА ОБЫЧНАЯ
    10)При закадровой обработке, NPC персонажи оставляют следы своей деятельности. Эти следы помнят на каком шаге были прозведены
    и исчезают по прошествии определённого количества шагов #РЕАЛИЗОВАНО
    11)Встречи с NPC на динамическом чанке
    12)Стрельба
    13)Свободный просмотр клеток вокруг #РЕАЛИЗОВАНО
    14)Противники и NPC
    15)Возможность спрятаться
    16)Возможность посмотреть на небо
    17)Перехват шага у игрока
    18)Золотоискатели, находясь в горах начинают искать золото
    19)Встречи NPC друг с другом на глобальной карте
    20)Остановку при достижении края карты #РЕАЛИЗОВАНО
    21)Реализовать вывод во что то, что быстрее и адекватнее консоли выводит картинку
    22)Перерассчёт глобального положения противников при премещении по динамическому чанку
    23)NPC не должны появляться и передвигаться по тайлам, передвижение по которым невозможно
    24)Добавить необсчитываемых персонажей, являющихся мелкими зверьми. Например: змей и гремучих змей
    25)Переделать вывод игрового содержимого на экран

    ТЕМАТИКА:
    Игра о человеке, который сбежал от погони в пустынную область, имея только флягу с водой и револьвер с 5ю патронами.
    Он не может покинуть область "потому что его ищут" и поэтому должен выживать здесь.
    Он может сталкиваться со зверьми и с людьми. В горных областях с золотоискателями, а в зелёных областях со всадниками,
    которые были отправлены его убить. Столкновение с NPC является нежелательным, ведь их оснащённость и шансы на выживание сильно больше.

    ЛОГИКА ПЕРЕМЕЩЕНИЯ NPC
    NPC делятся на охотников и хаотичных.
    
    Хаотичные NPC двигаются по старым правилам случайного выбора направления в рамках благоприятных биомов. К хаотичным NPC относятся животные и
    золотоискатели. Предположительно, они обитают в одном месте и изображают свою деятельность.
    
    Перемещаясь по глобальной карте, NPC охотники получают задачу достигнуть точки на карте, и, они пытаются её достичь обходя неблагоприятные биомы
    и стараясь перемещаться по благоприятным. Попутно они делают остановки, оставляющие свои следы.
    Если достичь точки через благоприятные или нейтральные биомы невозможно, точка следования сменяется и так до конца игры или их гибели.
    Появившись на динамическом чанке игрока, NPC продолжают следование выбранным курсом и так же делают короткие (а то и длинные) остановки
    и совершают действия. NPC могут быть застигнуты врасплох во время сна, но это сложно сделать, потому что сон их чуток.

    НЕОБЧИТЫВАЕМЫЕ СУЩНОСТИ:
    Помимо NPC, жизнь имитируют пявляющиеся в зависимости от биома существа. Ими могут быть птицы, скорпионы и змеи.
    Они могут появиться из соответствующих им тайлов даже если они нахоятся в зоне видимости игрока.
    Некоторые тайлы будут опасны возможностью появления из них необчитываемых противников.

    СТРЕЛЬБА:
    Стрельба осуществляется нажатием клавиши "g", наведением курсора на противника и выстрелом "от бедра", при такой стрельбе довольно большой шанс промаха.
    Можно прицелиться, повысив свои шансы, но пропустив один ход. Попадание либо сразу убивает персонажа, либо наносит ему критический урон,
    несовместимый с дальнейшим выживанием.
    
"""


class Temperature:
    """ Содержит температуру среды и температуру персонажа """
    def __init__(self, temperature_environment, temperature_person):
        self.environment = temperature_environment
        self.person = temperature_person

class Position:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    def __init__(self, assemblage_point:list, dynamic:list, chanks_use_map:list, pointer:list, gun:list):
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chank = chanks_use_map
        self.pointer = pointer
        self.gun = gun
        self.global_position = assemblage_point
        self.number_chank = 1
        self.check_encounter_position = [[self.global_position[0] - 1, self.global_position[1] - 1], [self.global_position[0] - 1, self.global_position[1]],
                                        [self.global_position[0] - 1, self.global_position[1] + 1], [self.global_position[0], self.global_position[1] - 1],
                                        [self.global_position[0], self.global_position[1]], [self.global_position[0], self.global_position[1] + 1],
                                        [self.global_position[0] + 1, self.global_position[1] - 1], [self.global_position[0] + 1, self.global_position[1]],
                                        [self.global_position[0] + 1, self.global_position[1] + 1]]
        
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
            self.number_chank = 1
        elif self.dynamic[0] > chank_size > self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1]]
            self.number_chank = 3
        elif self.dynamic[0] < chank_size < self.dynamic[1]:
            self.global_position = [self.assemblage_point[0], self.assemblage_point[1] + 1]
            self.number_chank = 2
        elif self.dynamic[0] > chank_size < self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1] + 1]
            self.number_chank = 4

        
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
                    0: ['desert',             [40.0,60.0], ['.'],                 ['j'],                 'j'],
                    1: ['semidesert',         [35.0,50.0], ['.', ','],            ['▲', 'o', 'i'],       '.'],
                    2: ['cliff semidesert',   [35.0,50.0], ['▲', 'A', '.', ','],  ['o', 'i'],            'A'],
                    3: ['saline land',        [40.0,50.0], [';'],                 [':'],                 ';'],
                    4: ['dried field',        [30.0,40.0], ['„', ','],            ['o', 'u'],            ','],
                    5: ['field',              [20.0,35.0], ['u', '„', ','],       ['ü', 'o'],            '„'],
                    6: ['hills',              [20.0,35.0], ['▲', 'o'],            ['„', ','],            '▲'],
                    7: ['oasis',              [15.0,30.0], ['F', '„', '~'],       ['P', ','],            'P'],
                    8: ['salty lake',         [25.0,40.0], ['~', ','],            ['„', '.'],            '~'],
                    9: ['swamp',              [15.0,30.0], ['ü', 'u', '~'],       ['„', ','],            'ü'],
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

    #progress_bar(20, 'Регионы сгенерированы')
    
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
    #progress_bar(40, 'Глобальная карта мини регионов построена')
    global_mini_region_map = gluing_location(raw_global_region_map, value_region_box, value_region_box)
    #progress_bar(60, 'Постобработка мини регионов')
    post_mini_region_generate(global_mini_region_map)
    global_map = []
    #progress_bar(80, 'Глобальные регионы отданы на генерацию локаций')
    for number_line in range(len(global_mini_region_map)):
        location_line = []
        for number_seed in range(len(global_mini_region_map[number_line])): #Определяем номер региона в линии регионов
            location_line.append(master_location_generate(global_mini_region_map[number_line][number_seed], game_field_size, grid))
        global_map.append(location_line)
    #progress_bar(100, 'Игровая карта готова')
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

    ОБРАБОТКА ИГРОВЫХ СОБЫТИЙ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


def person_dict():

    person_dict =   {
                    '☺ ': 'person',
                    '☺r': 'revolver',
                    '☺-': 'riffle',
                    '☺—': 'long riffle',
                    '☺=': 'double-barreled shotgun',
                    '☺/': 'spear',
                    '☺h': 'horseman',
                    '☺‰': 'dart',
                    '☺Ð': 'archer',
                    '☻ ': 'enemy'
                    }

class Action_in_map:
    """ Содержит в себе описание активности и срок её жизни """
    def __init__(self, name, birth, position_npc, chank_size):
        self.name = name
        self.icon = action_dict(name, 0)
        self.description = action_dict(name, 1)
        self.lifetime = action_dict(name, 2)
        self.birth = birth
        self.global_position = position_npc
        self.local_position = [random. randrange(chank_size), random. randrange(chank_size)]

        
def action_dict(action, number):
    """ Принимает название активности, возвращает её иконку, описание и срок жизни"""

    action_dict =   {
                    'camp':             ['/', 'следы лагеря',               150],
                    'bonfire':          ['+', 'следы костра',               150],
                    'rest_stop':        ['№', 'следы остановки человека',   150],
                    'horse_tracks':     ['%', 'следы лошади',               150],
                    'animal_traces':    ['@', 'следы зверя',                150],
                    'gnawed bones':     ['#', 'обглоданные зверем кости',   150],
                    'defecate':         ['&', 'справленная нужда',          150],
                    'animal_rest_stop': ['$', 'следы животной лежанки',     150],
                    'dead_man':         ['D', 'мёртвый человек',            150],
                    'unknown':          ['?', 'неизвестно',                 150]
                    }

    if action in action_dict:
        return action_dict[action][number]
    else:
        return action_dict['unknown'][number]

class Enemy:
    """ Отвечает за всех NPC """
    def __init__(self, enemy, global_position, action_points):
        self.enemy = enemy
        self.global_position = global_position
        self.action_points = action_points
        self.dynamic_chank = False
        self.dynamic_chank_position = [0, 0]
        self.old_position_assemblage_point = [1, 1]
        self.step_exit_from_assemblage_point = 0

class Horseman(Enemy):
    """ Отвечает за всадников """
    def __init__(self):
        self.name = 'horseman'
        self.name_npc = random.choice(['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок'])
        self.precedence_biom = [',', '„', 'P']
        self.icon = '☻h'
        self.activity = [['кормит лошадь', 'action_points', -2, 'horse_tracks'], ['чистит оружие', 'action_points',  -2, 'rest_stop'],
                         ['пьёт', 'thirst', 20, 'horse_tracks'], ['готовит еду', 'hunger', 20, 'bonfire'],
                         ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 10
        self.type = 'hunter'
        self.task = [0, 0]

class Riffleman(Enemy):
    """ Отвечает за стрелков """
    def __init__(self):
        self.name = 'riffleman'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.precedence_biom = ['.', 'A', '▲']
        self.icon = '☻-'
        self.activity = [['чистит оружие', 'action_points', -2, 'rest_stop'], ['пьёт', 'thirst', 20, 'rest_stop'],
                         ['готовит еду', 'hunger', 20, 'bonfire'], ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type = 'hunter'
        self.task = [0, 0]

class Gold_digger(Enemy):
    """ Отвечает за золотоискателей """
    def __init__(self):
        self.name = 'gold_digger'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.precedence_biom = ['.', 'A', '▲']
        self.icon = '☻='
        self.activity = [['чистит оружие', 'action_points', -2, 'rest_stop'], ['пьёт', 'thirst', 20, 'rest_stop'],
                         ['готовит еду', 'hunger', 20, 'bonfire'], ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type = 'chaotic'

class Horse(Enemy):
    """ Отвечает за коней """
    def __init__(self):
        self.name = 'horse'
        self.name_npc = random.choice(['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь'])
        self.precedence_biom = [',', '„', 'P']
        self.icon = 'ho'
        self.activity = [['пугатся и убегает', 'fatigue', -10, 'horse_tracks'], ['пьёт', 'thirst', 20, 'horse_tracks'],
                         ['ест траву', 'hunger', 20, 'horse_tracks'], ['отдыхает', 'fatigue', 20, 'animal_rest_stop']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 0
        self.type = 'chaotic'

class Coyot(Enemy):
    """ Отвечает за койотов """
    def __init__(self):
        self.name = 'coyot'
        self.name_npc = random.choice(['Плешивый койот', 'Молодой койот', 'Подраный койот'])
        self.precedence_biom = ['.', ',', '„', 'P', 'A']
        self.icon = 'co'
        self.activity = [['охотится', 'action_points', -2, 'gnawed bones'], ['пьёт', 'thirst', 20, 'animal_traces'],
                         ['ест', 'hunger', 20, 'animal_traces'], ['чешется', 'action_points', -2, 'animal_traces'],
                         ['отдыхает', 'fatigue', 20, 'animal_rest_stop']]
        self.hunger = 200
        self.thirst = 200
        self.fatigue = 200
        self.reserves = 0
        self.type = 'chaotic'

def master_game_events(global_map, enemy_list, position, go_to_print, step, activity_list, chank_size):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    enemy_dynamic_chank_check(global_map, enemy_list, position, step, chank_size)
    activity_list_check(activity_list, step)
    go_to_print.text5 = ''
    
    for enemy in enemy_list:
        if enemy.dynamic_chank:
            enemy_in_dynamic_chank(global_map, enemy, position, chank_size, step)
            pass
        else:
            if enemy.enemy.type == 'hunter':
                enemy_hunter_emulation_life(global_map, enemy, go_to_print, step, activity_list, chank_size)
            else:
                enemy_chaotic_emulation_life(global_map, enemy, go_to_print, step, activity_list, chank_size)

def enemy_ideal_move_calculation():
    """
        Рассчитывает идеальную траекторию движения NPC
    """
    pass

def enemy_not_ideal_move_recalculation():
    """
        Перерассчитывает идеальную траекторию под неидеальную местность
    """
    pass

def enemy_in_dynamic_chank(global_map, enemy, position, chank_size, step):
    """
        Обрабатывает поведение NPC на динамическом чанке игрока
    """
    enemy_recalculation_dynamic_chank_position(global_map, enemy, position, chank_size, step)
    print(enemy.enemy.name, ' находится в динамической позиции: ', enemy.dynamic_chank_position)



    enemy.dynamic_chank_position[1] += 1


    enemy_global_position_recalculation(global_map, enemy, position, chank_size)

def enemy_global_position_recalculation(global_map, enemy, position, chank_size):
    """
        Перерассчитывает глобальную позицию NPC при их перемещении на динамическом чанке
    """
    enemy.global_position = [(position.assemblage_point[0] + enemy.dynamic_chank_position[0]//chank_size),
                             (position.assemblage_point[1] + enemy.dynamic_chank_position[1]//chank_size)]

def enemy_recalculation_dynamic_chank_position(global_map, enemy, position, chank_size, step):
    """
        Перерассчитывает позицию NPC при перерассчёте динамического чанка
    """
    if enemy.old_position_assemblage_point != position.assemblage_point:
        if position.assemblage_point[0] == (enemy.old_position_assemblage_point[0] - 1):
           enemy.dynamic_chank_position[0] += chank_size
        elif position.assemblage_point[0] == (enemy.old_position_assemblage_point[0] + 1):
           enemy.dynamic_chank_position[0] -= chank_size
        if position.assemblage_point[1] == (enemy.old_position_assemblage_point[1] - 1):
           enemy.dynamic_chank_position[1] += chank_size
        elif position.assemblage_point[1] == (enemy.old_position_assemblage_point[1] + 1):
           enemy.dynamic_chank_position[1] -= chank_size

    if (0 <= enemy.dynamic_chank_position[0] >= chank_size*2) and (0 <= enemy.dynamic_chank_position[1] >= chank_size*2):
        enemy.step_exit_from_assemblage_point = step
    enemy.old_position_assemblage_point = copy.deepcopy(position.assemblage_point)
    
def enemy_dynamic_chank_check(global_map, enemy_list, position, step, chank_size):
    """
        Проверяет нахождение NPC на динамическом чанке игрока
    """
    for enemy in enemy_list:
        number_encounter_chank_ok = 99
        for number_encounter_chank in range(len(position.check_encounter_position)):
            if position.check_encounter_position[number_encounter_chank] == enemy.global_position:
                number_encounter_chank_ok = number_encounter_chank 
        if enemy.dynamic_chank == False and number_encounter_chank_ok != 99:
            enemy.old_position_assemblage_point = copy.deepcopy(position.assemblage_point)
            enemy.dynamic_chank = True
            if number_encounter_chank_ok == 0:
                enemy.dynamic_chank_position = [position.dynamic[0] - chank_size, position.dynamic[1] - chank_size]
            elif number_encounter_chank_ok == 1:
                enemy.dynamic_chank_position = [position.dynamic[0] - chank_size, position.dynamic[1]]
            elif number_encounter_chank_ok == 2:
                enemy.dynamic_chank_position = [position.dynamic[0] - chank_size, position.dynamic[1] + chank_size]
            elif number_encounter_chank_ok == 3:
                enemy.dynamic_chank_position = [position.dynamic[0], position.dynamic[1] - chank_size]
            elif number_encounter_chank_ok == 4:
                enemy.dynamic_chank_position = [position.dynamic[0], position.dynamic[1]]
            elif number_encounter_chank_ok == 5:
                enemy.dynamic_chank_position = [position.dynamic[0], position.dynamic[1] + chank_size]
            elif number_encounter_chank_ok == 6:
                enemy.dynamic_chank_position = [position.dynamic[0] + chank_size, position.dynamic[1] - chank_size]
            elif number_encounter_chank_ok == 7:
                enemy.dynamic_chank_position = [position.dynamic[0] + chank_size, position.dynamic[1]]
            elif number_encounter_chank_ok == 8:
                enemy.dynamic_chank_position = [position.dynamic[0] + chank_size, position.dynamic[1] + chank_size]

        elif enemy.dynamic_chank  and number_encounter_chank_ok != 99:
            pass
        
        elif (step - enemy.step_exit_from_assemblage_point) < 15 and enemy.step_exit_from_assemblage_point and step > 15:
            pass
        
        elif (step - enemy.step_exit_from_assemblage_point) == 15 and step != 15:
            enemy.step_exit_from_assemblage_point = 0
            enemy.dynamic_chank = False
        else:
            enemy.dynamic_chank = False
def enemy_hunter_emulation_life(global_map, enemy, go_to_print, step, activity_list, chank_size):
    """
        Обрабатывает жизнь hunter NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """
    pass
    

def enemy_chaotic_emulation_life(global_map, enemy, go_to_print, step, activity_list, chank_size):
    """
        Обрабатывает жизнь chaotic NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """

    enemy.action_points += 1
    enemy.enemy.hunger -= 1
    enemy.enemy.thirst -= 1
    enemy.enemy.fatigue -= 1
    
    if enemy.action_points >= 5:
        if random.randrange(10)//6 == 1 or (global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.enemy.precedence_biom and random.randrange(10)//8 == 1):
            move_biom_enemy(global_map, enemy)
            enemy.action_points -= 5
            go_to_print.text5 += str(enemy.enemy.name_npc) + ' передвигается' + '\n'
      
        elif(enemy.enemy.thirst < 10 or enemy.enemy.hunger < 10) and enemy.enemy.reserves > 0:
            enemy.enemy.reserves -= 1
            enemy.enemy.hunger = 100
            enemy.enemy.thirst = 100
            enemy.action_points -= 3
            go_to_print.text5 += str(enemy.enemy.name_npc)+ ' достаёт припасы \n'
        elif enemy.enemy.fatigue < 10:
            enemy.enemy.fatigue = 50
            enemy.action_points -= 20
            go_to_print.text5 += str(enemy.enemy.name_npc)+ ' уснул от усталости \n'
            activity_list.append(Action_in_map('rest_stop', step, enemy.global_position, chank_size))
        else:
            activity = random.choice(enemy.enemy.activity)
            if activity[1] == 'action_points':
                enemy.action_points += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chank_size))
            elif activity[1] == 'thirst':
                enemy.enemy.thirst += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chank_size))
            elif activity[1] == 'hunger':
                enemy.enemy.hunger += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chank_size))
            elif activity[1] == 'fatigue':
                enemy.action_points -= 5
                enemy.enemy.fatigue += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chank_size))
            go_to_print.text5 += str(enemy.enemy.name_npc)+ ' ' + str(activity[0]) + ' его голод: ' + str(enemy.enemy.hunger) + ' его жажда: ' + str(enemy.enemy.thirst) + ' его усталость: ' + str(enemy.enemy.fatigue) + '\n'
            enemy.action_points -= 3
    

def move_biom_enemy(global_map, enemy):
    """
        Обрабатывает перемещение NPC за кадром между биомами
    """

    if global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.enemy.precedence_biom:
        direction_moved = []
        if global_map[enemy.global_position[0] - 1][enemy.global_position[1]].icon in enemy.enemy.precedence_biom and enemy.global_position[0] - 1 > 0:
            direction_moved.append([enemy.global_position[0] - 1, enemy.global_position[1]])
        if global_map[enemy.global_position[0] + 1][enemy.global_position[1]].icon in enemy.enemy.precedence_biom and enemy.global_position[0] + 1 < len(global_map) - 1:
            direction_moved.append([enemy.global_position[0] + 1, enemy.global_position[1]]) 
        if global_map[enemy.global_position[0]][enemy.global_position[1] - 1].icon in enemy.enemy.precedence_biom and enemy.global_position[1] - 1 > 0:
            direction_moved.append([enemy.global_position[0], enemy.global_position[1] - 1])
        if global_map[enemy.global_position[0]][enemy.global_position[1] + 1].icon in enemy.enemy.precedence_biom and enemy.global_position[1] + 1 < len(global_map) - 1:
            direction_moved.append([enemy.global_position[0], enemy.global_position[1] + 1])
        if len(direction_moved) != 0:
            enemy.global_position = random.choice(direction_moved)
        if len(direction_moved) == 0:
            if random.randrange(10)//8 == 1:
                direction_moved = []
                if enemy.global_position[0] - 1 > 0:
                    direction_moved.append([enemy.global_position[0] - 1, enemy.global_position[1]])
                elif enemy.global_position[0] + 1 < len(global_map) - 1:
                    direction_moved.append([enemy.global_position[0] + 1, enemy.global_position[1]])
                elif enemy.global_position[1] - 1 > 0:
                    direction_moved.append([enemy.global_position[0], enemy.global_position[1] - 1])
                elif enemy.global_position[1] + 1 < len(global_map) - 1:
                    direction_moved.append([enemy.global_position[0], enemy.global_position[1] + 1])
                enemy.global_position = random.choice(direction_moved)
    else:
        if random.randrange(10)//8 == 1:
            direction_moved = []
            if enemy.global_position[0] - 1 > 0:
                direction_moved.append([enemy.global_position[0] - 1, enemy.global_position[1]])
            if enemy.global_position[0] + 1 < len(global_map) - 1:
                direction_moved.append([enemy.global_position[0] + 1, enemy.global_position[1]])
            if enemy.global_position[1] - 1 > 0:
                direction_moved.append([enemy.global_position[0], enemy.global_position[1] - 1])
            if enemy.global_position[1] + 1 < len(global_map) - 1:
                direction_moved.append([enemy.global_position[0], enemy.global_position[1] + 1])
            enemy.global_position = random.choice(direction_moved)


def activity_list_check(activity_list, step):
    """
        Проверяет активности на истечение времени
    """
    for activity in activity_list:
        if step - activity.lifetime > activity.birth:
            activity_list.remove(activity)


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ПОЛЬЗОВАТЕЛЬСКИЙ ВВОД И ЕГО ОБРАБОТКА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_player_action(global_map, position, chank_size, go_to_print, changing_step, mode_action):


    pressed_button = ''
    mode_action, pressed_button = request_press_button(global_map, position, chank_size, go_to_print, changing_step, mode_action)

    if mode_action == 'move':
        request_move(global_map, position, chank_size, go_to_print, pressed_button, changing_step)
    elif mode_action == 'test_move':
        test_request_move(global_map, position, chank_size, go_to_print, pressed_button, changing_step)
    elif mode_action == 'pointer':    
        request_pointer(position, chank_size, go_to_print, pressed_button, changing_step)
    elif mode_action == 'gun':
        request_gun(global_map, position, chank_size, go_to_print, pressed_button, changing_step)
    if pressed_button == 'button_map':
        go_to_print.minimap_on = (go_to_print.minimap_on == False)
    request_processing(pressed_button)

    return mode_action


def request_press_button(global_map, position, chank_size, go_to_print, changing_step, mode_action):
    """
        Спрашивает ввод, возвращает тип активности и нажимаемую кнопку

    """
    key = keyboard.read_key()
    
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
            position.pointer = [chank_size//2, chank_size//2]
            return ('pointer', 'button_pointer')
        elif mode_action == 'pointer':
            position.pointer = [chank_size//2, chank_size//2]
            return ('move', 'button_pointer')
        else:
            position.pointer = [chank_size//2, chank_size//2]
            position.gun = [chank_size//2, chank_size//2]
            return ('move', 'button_pointer')
    elif key == 'g' or key == 'п':
        if mode_action == 'move':
            position.gun = [chank_size//2, chank_size//2]
            return ('gun', 'button_gun')
        elif mode_action == 'gun':
            position.gun = [chank_size//2, chank_size//2]
            return ('move', 'button_gun')
        else:
            position.pointer = [chank_size//2, chank_size//2]
            position.gun = [chank_size//2, chank_size//2]
            return ('move', 'button_gun')
    elif key == 'm' or key == 'ь':
        return (mode_action, 'button_map')
    elif key == 't' or key == 'е':
        if mode_action == 'test_move':
            return ('move', 'button_test')
        else:
            return ('test_move', 'button_test')
    else:
        return (mode_action, 'none')


def request_move(global_map:list, position, chank_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет динамическое местоположение персонажа
    """
    
    if pressed_button == 'up':
        
        if position.chanks_use_map[position.dynamic[0] - 1][position.dynamic[1]] != '▲':
            if position.dynamic[0] >= chank_size//2 and position.assemblage_point[0] > 0:
                position.dynamic[0] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'left':
        
        if position.chanks_use_map[position.dynamic[0]][position.dynamic[1] - 1] != '▲':
            if position.dynamic[1] >= chank_size//2 and position.assemblage_point[1] > 0:
                position.dynamic[1] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'down':
        
        if position.chanks_use_map[position.dynamic[0] + 1][position.dynamic[1]] != '▲':
            if position.dynamic[0] <= (chank_size + chank_size//2) and position.assemblage_point[0] != (len(global_map) - 2):
                position.dynamic[0] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'right':
        
        if position.chanks_use_map[position.dynamic[0]][position.dynamic[1] + 1] != '▲':
            if position.dynamic[1] <= (chank_size + chank_size//2) and position.assemblage_point[1] != (len(global_map) - 2):
                position.dynamic[1] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)

def test_request_move(global_map:list, position, chank_size:int, go_to_print, pressed_button, changing_step): #тестовый быстрый режим премещения
    """
        Меняет динамическое местоположение персонажа в тестовом режиме, без ограничений. По полчанка за раз.
    """
    
    if pressed_button == 'up':
        
        if position.dynamic[0] >= chank_size//2 and position.assemblage_point[0] > 0:
            position.dynamic[0] -= chank_size//2
            calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'left':
        
        if position.dynamic[1] >= chank_size//2 and position.assemblage_point[1] > 0:
            position.dynamic[1] -= chank_size//2
            calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'down':
        
        if position.dynamic[0] <= (chank_size + chank_size//2) and position.assemblage_point[0] != (len(global_map) - 2):
            position.dynamic[0] += chank_size//2
            calculation_assemblage_point(global_map, position, chank_size, 2)
            
    elif pressed_button == 'right':
        
        if position.dynamic[1] <= (chank_size + chank_size//2) and position.assemblage_point[1] != (len(global_map) - 2):
            position.dynamic[1] += chank_size//2
            calculation_assemblage_point(global_map, position, chank_size, 2)

def request_pointer(position, chank_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет местоположение указателя
    """
    if pressed_button == 'up' and position.pointer[0] > 0:
        position.pointer[0] -= 1
    elif pressed_button == 'left' and position.pointer[1] > 0:
        position.pointer[1] -= 1 
    elif pressed_button == 'down' and position.pointer[0] < chank_size - 1:
        position.pointer[0] += 1
    elif pressed_button == 'right' and position.pointer[1] < chank_size - 1:
        position.pointer[1] += 1

def request_gun(global_map:list, position, chank_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет местоположение указателя оружия
    """
    if pressed_button == 'up' and position.gun[0] > chank_size//2 - 5:
        position.gun[0] -= 1
            
    elif pressed_button == 'left' and position.gun[1] > chank_size//2 - 5:
        position.gun[1] -= 1
            
    elif pressed_button == 'down' and position.gun[0] < chank_size//2 + 5:
        position.gun[0] += 1
            
    elif pressed_button == 'right' and position.gun[1] < chank_size//2 + 5:
        position.gun[1] += 1

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

    position.global_position_calculation(chank_size) #Рассчитывает глобальное положение и номер чанка через метод
    position.check_encounter() #Рассчитывает порядок и координаты точек проверки

        
def request_processing(pressed_button):
    """
        Обрабатывает пользовательский запрос
    """
    pass

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


def print_minimap(global_map, position, go_to_print, enemy_list):
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
                    enemy_here = enemy_list[enemy].enemy.icon
            if number_line == position.global_position[0] and biom == position.global_position[1]:
                go_to_print.text2 = global_map[number_line][biom].name
                go_to_print.text3 = [global_map[number_line][biom].temperature, 36.6]
                print_line += '☺ '
            elif enemy_here != '--':
                print_line += enemy_here
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
                    
                    '/': 'следы лагеря',
                    '+': 'следы костра',
                    '%': 'следы лошади',
                    '@': 'следы зверя',
                    '#': 'обглоданные зверем кости',
                    '№': 'следы остановки человека',
                    '&': 'справленная нужда',
                    '$': 'следы животной лежанки',
                    'D': 'мёртвый человек',
                    'd': 'мёртвое животное',
                    '?': 'неизвестно что',
                    }

    if tile in  ground_dict:
        return ground_dict[tile]
    else:
        return 'нечто'                 

def draw_field_calculations(position:list, views_field_size:int, go_to_print):
    """
        Формирует изображение игрового поля на печать
    """
    
    
    half_views = (views_field_size//2)
    start_stop = [(position.dynamic[0] - half_views), (position.dynamic[1] - half_views),
                  (position.dynamic[0] + half_views + 1),(position.dynamic[1] + half_views + 1)]
    line_views = position.chanks_use_map[start_stop[0]:start_stop[2]]

    go_to_print.point_to_draw = [(position.dynamic[0] - half_views), (position.dynamic[1] - half_views)]
    
    draw_field = []
    for line in line_views:
        line = line[start_stop[1]:start_stop[3]]
        draw_field.append(line)
    return draw_field

def draw_additional_static_entities(position, chank_size:int, go_to_print, enemy_list, activity_list):
    """
        Отрисовывает на динамическом чанке дополнительные статические сущности
    """
    
    for activity in activity_list:
        if position.global_position == activity.global_position:
            if position.number_chank == 1:
                position.chanks_use_map[activity.local_position[0]][activity.local_position[1]] = activity.icon
            if position.number_chank == 2:
                position.chanks_use_map[activity.local_position[0]][activity.local_position[1] + chank_size] = activity.icon
            if position.number_chank == 3:
                position.chanks_use_map[activity.local_position[0] + chank_size][activity.local_position[1]] = activity.icon
            if position.number_chank == 4:
                position.chanks_use_map[activity.local_position[0] + chank_size][activity.local_position[1] + chank_size] = activity.icon
                    
def draw_additional_dynamic_entities(position, chank_size:int, go_to_print, enemy_list, activity_list, draw_field):
    """
        Перерасчёт координат динамических сущностей для отрисовки на итоговом выводе
    """
    enemy_position_draw = []
    
    for enemy in enemy_list:
        if position.global_position == enemy.global_position:
            if go_to_print.point_to_draw[0] <= enemy.dynamic_chank_position[0] <= go_to_print.point_to_draw[0] + chank_size - 1:
                if go_to_print.point_to_draw[1] <= enemy.dynamic_chank_position[1] < go_to_print.point_to_draw[1] + chank_size - 1:
                    draw_field[enemy.dynamic_chank_position[0] - go_to_print.point_to_draw[0]][enemy.dynamic_chank_position[1] - go_to_print.point_to_draw[1]] = enemy.enemy.icon
              

def master_draw(position, chank_size:int, go_to_print, global_map, mode_action, enemy_list, activity_list):
    """
        Формирует итоговое изображение игрового поля для вывода на экран
    """
    if go_to_print.minimap_on:
        print_minimap(global_map, position, go_to_print, enemy_list)

    draw_additional_static_entities(position, chank_size, go_to_print, enemy_list, activity_list)
    
    draw_field = draw_field_calculations(position, chank_size, go_to_print)

    draw_additional_dynamic_entities(position, chank_size, go_to_print, enemy_list, activity_list, draw_field)
    
    draw_box = []
    pointer_vision = ' '
    for line in range(len(draw_field)):
        print_line = ''
        for tile in range(len(draw_field)):
            if line == chank_size//2 and tile == chank_size//2:
                ground = draw_field[line][tile]
                print_line += '☺'
                if mode_action == 'pointer' and position.pointer == [chank_size//2, chank_size//2]:
                    print_line += '<'
                    pointer_vision = draw_field[line][tile]
                elif mode_action == 'gun' and position.gun == [chank_size//2, chank_size//2]:
                    print_line += '+'    
                else:
                    print_line += ' '
            elif line == position.pointer[0] and tile == position.pointer[1]:
                print_line += draw_field[line][tile] + '<'
                pointer_vision = draw_field[line][tile]
            elif line == position.gun[0] and tile == position.gun[1]:
                print_line += draw_field[line][tile] + '+'
            else:
                if len(draw_field[line][tile]) == 2:
                    print_line += draw_field[line][tile]
                else:
                    print_line += draw_field[line][tile] + ' '
        draw_box.append(print_line)
    go_to_print.game_field = draw_box
    go_to_print.text1 = (position.assemblage_point, ' - Позиция точки сборки | ', position.dynamic, ' - динамическая позиция | под ногами:', ground_dict(ground) )
    go_to_print.text4 = ground_dict(pointer_vision)
    
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ИНТЕРФЕЙС И ВЫВОД ИТОГОВОГО ИЗОБРАЖЕНИЯ НА ЭКРАН
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def print_frame(go_to_print, frame_size, activity_list):
    """
        Отвечает за итоговый вывод содержимого на экран
    """

    raw_frame = []
    
    for line in range(frame_size[0]):
        raw_frame.append('')
    
    for line in range(len(go_to_print.game_field)): #Добавление изображения с игрового экрана
        raw_frame[(line + 3)] += '      ' + go_to_print.game_field[line]

    if go_to_print.minimap_on: #Добавление изображения миникарты
        for line in range(len(go_to_print.biom_map)):
            raw_frame[(line + 3)] += '      ' + go_to_print.biom_map[line]

    raw_frame[4+len(go_to_print.game_field)] += '   ' + str(go_to_print.text1)

    raw_frame[5+len(go_to_print.game_field)] += '   Вы видите ' + str(go_to_print.text4)

    raw_frame[6+len(go_to_print.game_field)] += '   Вы находитесь в ' + str(go_to_print.text2)

    if go_to_print.minimap_on:
        raw_frame[7+len(go_to_print.game_field)] += '   Температура среды: ' + str(go_to_print.text3[0][0]) + ' градусов. Температура персонажа: ' + str(go_to_print.text3[1]) + ' градусов.'
    raw_frame[8+len(go_to_print.game_field)] += str(go_to_print.text5)
    raw_frame[8+len(go_to_print.game_field)] += 'на карте: ' + str(len(activity_list)) + ' активностей'
    
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

def game_loop(global_map:list, position:list, chank_size:int, frame_size:list, enemy_list:list):
    """
        Здесь происходят все игровые события
        
    """
    go_to_print = Interfase([], [], False, '', '', '', '', '', '', '', '', '', '')
    activity_list = []
    not_intercept_step = [True]
    step = 0
    print('game_loop запущен')
    global changing_step
    mode_action = 'move'
    while game_loop:
        changing_step = True
        if not_intercept_step[0]:
            mode_action = master_player_action(global_map, position, chank_size, go_to_print, changing_step, mode_action)
        #start = time.time() #проверка времени выполнения
        if changing_step:
            master_game_events(global_map, enemy_list, position, go_to_print, step, activity_list, chank_size)
            step += 1
        #test1 = time.time() #проверка времени выполнения
        master_draw(position, chank_size, go_to_print, global_map, mode_action, enemy_list, activity_list)
        #test2 = time.time() #проверка времени выполнения
        print_frame(go_to_print, frame_size, activity_list)
        #print('step = ', step)
        #end = time.time() #проверка времени выполнения
        #print(test1 - start, ' - test1 ', test2 - start, ' - test2 ', end - start, ' - end ') #
             

def main():
    """
        Запускает игру
        
    """
    chank_size = 25         #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    value_region_box = 4    #Количество регионов в квадрате.
    grid = 5                #Можно любое, но лучше кратное размеру игрового экрана. Иначе обрежет область видимости.
    frame_size = [35, 40]   #Размер одного кадра [высота, ширина].


    #progress_bar(5, 'Запуск игры') 
    global_map = master_generate(value_region_box, chank_size, grid)
    position = Position([value_region_box//2, value_region_box//2], [chank_size//2, chank_size//2], [], [chank_size//2, chank_size//2], [chank_size//2, chank_size//2])
    calculation_assemblage_point(global_map, position, chank_size, 3)
    enemy_list = [Enemy(Horseman(),[len(global_map)//2, len(global_map)//2] , 5), Enemy(Horseman(),[len(global_map)//3, len(global_map)//3] , 5),
                  Enemy(Riffleman(),[len(global_map)//4, len(global_map)//4] , 2), Enemy(Coyot(),[len(global_map)//5, len(global_map)//5] , 0)]
    game_loop(global_map, position, chank_size, frame_size, enemy_list)
    
    print('Игра окончена!')

main()
    
