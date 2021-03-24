import os
import copy
import random
import string
import keyboard
import time
import math

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ ДЛЯ ОТРАБОТКИ ПЕРЕМЕЩЕНИЯ NPC

    ИЗВЕСТНЫЕ БАГИ:
    1)Проверка доступности тайла для шага за пределами карты в стандартном алгоритме
    2)Попытка отрисовки за пределами динамического чанка #ИСПРАВЛЕНО
    3)Отталкивание наверх по глобальным координатам при попытке приблизиться #ИСПРАВЛЕНО
    

    РЕАЛИЗОВАТЬ:

    1)Перехват шага у игрока
    2)Золотоискатели, находясь в горах начинают искать золото
    3)Встречи NPC друг с другом на глобальной карте
    4)Остановку при достижени NPC края карты #РЕАЛИЗОВАНО
    5)NPC не должны появляться и передвигаться по тайлам, передвижение по которым невозможно 
    6)Добавить необсчитываемых персонажей, являющихся мелкими зверьми. Например: змей и гремучих змей
    7)Реализовать алгоритм поиска пути A* #РЕАЛИЗОВАНО
    8)Перемещение NPC на динамическом чанке игрока в соответствии с просчитанным на глобальной карте путём #РЕАЛИЗОВАНО
    9)"Стоимость" перемещения по разным тайлам #РЕАЛИЗОВАНО
    10)Переделать алгоритм А* что бы он работал как на глобальной карте, так и на динамической #РЕАЛИЗОВАНО
    11)Улучшить логику нахождения финишной точки при передвижении по динамическому чанку. Она должна определяться в зависимости от следующего
    за ней вейпоинта, текущего положения персонажа и "стоимости" финишного вейпоинта.
    12)Реализовать проверку на возможность пройти от одной динамической точки до другой напрямую, путём проверки нет ли на прямой линии х и у
    путевой точки с бОльшим индексом.

    ЛОГИКА ПЕРЕМЕЩЕНИЯ NPC
    NPC делятся на охотников и хаотичных.
    
    Хаотичные NPC двигаются по старым правилам случайного выбора направления в рамках благоприятных биомов. К хаотичным NPC относятся животные и
    золотоискатели. Предположительно, они обитают в одном месте и изображают свою деятельность.
    
    Перемещаясь по глобальной карте, NPC охотники получают задачу достигнуть точки на карте, и, они пытаются её достичь обходя неблагоприятные биомы
    и стараясь перемещаться по благоприятным. Попутно они делают остановки, оставляющие свои следы.
    Если достичь точки через благоприятные или нейтральные биомы невозможно, точка следования сменяется и так до конца игры или их гибели.
    Появившись на динамическом чанке игрока, NPC продолжают следование выбранным курсом и так же делают короткие (а то и длинные) остановки
    и совершают действия. NPC могут быть застигнуты врасплох во время сна, но это сложно сделать, потому что сон их чуток.

    СИСТЕМА ВЕЙПОИНТОВ:
    Персонажи получают точку прибытия и рассчитывают маршрут из точек (список), по которым им надо пройти. Они перемещаются в точку
    с индексом 0 и удаляют её.

    ПЕРЕМЕЩЕНИЕ NPC ПО ДИНАМИЧЕСКОМУ ЧАНКУ:
    При составлении списка динамических вейпоинтов, NPC подгружает два чанка, по которым ему необходимо пройти и рассчитывает путь

    СИСТЕМА ШУМА:
    Находящиеся недалеко от стреляющего персонажа NPC слышат выстрелы, и, либо спешат посмотреть на того, кто стрелял, либо спешат убраться восвояси.

    НЕОБЧИТЫВАЕМЫЕ СУЩНОСТИ:
    Помимо NPC, жизнь имитируют появляющиеся в зависимости от биома существа. Ими могут быть птицы, скорпионы и змеи.
    Они могут появиться из соответствующих им тайлов даже если они нахоятся в зоне видимости игрока.
    Некоторые тайлы будут опасны возможностью появления из них необчитываемых противников.

    РАЗНЫЕ РЕЖИМЫ СЛЕДОВАНИЯ:
    Патруль, спешка, поиск. Разная скорость премещения по вейпоинтам и разные следы. Нужно придумать причины выбора и смены режимов.

    ТЕМАТИКА:
    Всё, что мне нравится. Персонажи как в хороший плохой злой, вяленое конское мясо и гремучие змеи!

    
"""


class Temperature:
    """ Содержит температуру среды и температуру персонажа """
    def __init__(self, temperature_environment, temperature_person):
        self.environment = temperature_environment
        self.person = temperature_person

class Position:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    __slots__ = ('assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position', 'number_chunk', 'check_encounter_position')
    def __init__(self, assemblage_point:list, dynamic:list, chunks_use_map:list, pointer:list, gun:list):
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
        elif self.dynamic[0] > chank_size > self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1]]
            self.number_chunk = 3
        elif self.dynamic[0] < chank_size < self.dynamic[1]:
            self.global_position = [self.assemblage_point[0], self.assemblage_point[1] + 1]
            self.number_chunk = 2
        elif self.dynamic[0] > chank_size < self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1] + 1]
            self.number_chunk = 4

        
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

class Tile:
    """ Содержит изображение, описание и особое содержание тайла """
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)

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
    for line in range(len(location)):
        for tile in range(len(location)):
            if random.randrange(10)//9:
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
                    2: ['cliff semidesert',   [35.0,50.0], ['▲', 'A', '.', ','],  ['o', 'i'],       'A',        7],
                    3: ['saline land',        [40.0,50.0], [';'],                 [':'],            ';',        15],
                    4: ['field',              [20.0,35.0], ['u', '„', ','],       ['ü', 'o'],       '„',         5],
                    5: ['dried field',        [30.0,40.0], ['„', ','],            ['o', 'u'],       ',',         2],
                    6: ['oasis',              [15.0,30.0], ['F', '„', '~'],       ['P', ','],       'P',         0],
                    7: ['salty lake',         [25.0,40.0], ['~', ','],            ['„', '.'],       '~',        20],
                    8: ['hills',              [20.0,35.0], ['▲', 'o'],            ['„', ','],       '▲',        20],
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
        region_map.append([random.randrange(9) for x in range(size_region_box)])
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

def master_game_events(global_map, enemy_list, position, go_to_print, step, activity_list, chunk_size, interaction):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    interaction_processing(global_map, interaction, enemy_list)
    activity_list_check(activity_list, step)
    master_npc_calculation(global_map, enemy_list, position, go_to_print, step, activity_list, chunk_size, interaction)

def interaction_processing(global_map, interaction, enemy_list):
    """
        Обрабатывает взаимодействие игрока с миром
    """
    if len(interaction) != 0:
        for interact in interaction:
            if interact[0] == 'task_point_all_enemies':
                for enemy in enemy_list:
                    print(f"{enemy.enemy.name} получил задачу")
                    print(f"interact[1] = {interact[1]}")
                    if enemy.enemy.type == 'hunter':
                        enemy.waypoints = enemy_a_star_algorithm_move_calculation(global_map, enemy.global_position, interact[1], enemy.enemy.banned_biom)


def activity_list_check(activity_list, step):
    """
        Проверяет активности на истечение времени
    """
    for activity in activity_list:
        if step - activity.lifetime > activity.birth:
            activity_list.remove(activity)

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ОБРАБОТКА NPC
        
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
                    '☻ ': 'enemy',
                    's ': 'snake',
                    'S ': 'rattlesnake'
                    }

class Action_in_map:
    """ Содержит в себе описание активности и срок её жизни """
    __slots__ = ('name', 'icon', 'description', 'lifetime', 'birth', 'global_position', 'local_position')
    def __init__(self, name, birth, position_npc, chunk_size):
        self.name = name
        self.icon = action_dict(name, 0)
        self.description = action_dict(name, 1)
        self.lifetime = action_dict(name, 2)
        self.birth = birth
        self.global_position = position_npc
        self.local_position = [random. randrange(chunk_size), random. randrange(chunk_size)]

        
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
        self.dynamic_chunk = False
        self.dynamic_chunk_position = [0, 0]
        self.old_position_assemblage_point = [1, 1]
        self.step_exit_from_assemblage_point = 0
        self.waypoints = []
        self.dynamic_waypoints = []

class Horseman(Enemy):
    """ Отвечает за всадников """
    def __init__(self):
        self.name = 'horseman'
        self.name_npc = random.choice(['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['▲']
        self.icon = '☻h'
        self.activity = [['кормит лошадь', 'action_points', -2, 'horse_tracks'], ['чистит оружие', 'action_points',  -2, 'rest_stop'],
                         ['пьёт', 'thirst', 20, 'horse_tracks'], ['готовит еду', 'hunger', 20, 'bonfire'],
                         ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 10
        self.type = 'hunter'
        self.description = f"Знаменитый охотник за головами {self.name_npc}"

class Riffleman(Enemy):
    """ Отвечает за стрелков """
    def __init__(self):
        self.name = 'riffleman'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻-'
        self.activity = [['чистит оружие', 'action_points', -2, 'rest_stop'], ['пьёт', 'thirst', 20, 'rest_stop'],
                         ['готовит еду', 'hunger', 20, 'bonfire'], ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type = 'hunter'
        self.description = f"Шериф одного мрачного города {self.name_npc}"

class Gold_digger(Enemy):
    """ Отвечает за золотоискателей """
    def __init__(self):
        self.name = 'gold_digger'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻='
        self.activity = [['чистит оружие', 'action_points', -2, 'rest_stop'], ['пьёт', 'thirst', 20, 'rest_stop'],
                         ['готовит еду', 'hunger', 20, 'bonfire'], ['отдыхает', 'fatigue', 10, 'rest_stop'], ['разбил лагерь', 'fatigue', 20, 'camp']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 5
        self.type = 'chaotic'
        self.description = f"Отчаяный золотоискатель {self.name_npc}"

class Horse(Enemy):
    """ Отвечает за коней """
    def __init__(self):
        self.name = 'horse'
        self.name_npc = random.choice(['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['~', ';']
        self.icon = 'ho'
        self.activity = [['пугатся и убегает', 'fatigue', -10, 'horse_tracks'], ['пьёт', 'thirst', 20, 'horse_tracks'],
                         ['ест траву', 'hunger', 20, 'horse_tracks'], ['отдыхает', 'fatigue', 20, 'animal_rest_stop']]
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 0
        self.type = 'chaotic'
        self.description = f"{self.name_npc}"

class Coyot(Enemy):
    """ Отвечает за койотов """
    def __init__(self):
        self.name = 'coyot'
        self.name_npc = random.choice(['плешивый койот', 'молодой койот', 'подраный койот'])
        self.priority_biom = ['.', ',', '„', 'P', 'A']
        self.banned_biom = ['~', ';']
        self.icon = 'co'
        self.activity = [['охотится', 'action_points', -2, 'gnawed bones'], ['пьёт', 'thirst', 20, 'animal_traces'],
                         ['ест', 'hunger', 20, 'animal_traces'], ['чешется', 'action_points', -2, 'animal_traces'],
                         ['отдыхает', 'fatigue', 20, 'animal_rest_stop']]
        self.hunger = 200
        self.thirst = 200
        self.fatigue = 200
        self.reserves = 0
        self.type = 'chaotic'
        self.description = f"Голодный и злой {self.name_npc}"

def master_npc_calculation(global_map, enemy_list, position, go_to_print, step, activity_list, chunk_size, interaction):
    """
        Здесь происходят все события, связанные с NPC
    """
    enemy_dynamic_chunk_check(global_map, enemy_list, position, step, chunk_size)
    go_to_print.text5 = ''
    
    
    for enemy in enemy_list:
        if enemy.dynamic_chunk:
            enemy_in_dynamic_chunk(global_map, enemy, position, chunk_size, step)
            pass
        else:
            if enemy.enemy.type == 'hunter':
                enemy_hunter_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size)
            else:
                enemy_chaotic_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size)


def enemy_move_calculation(global_map, enemy, task):
    """
        Рассчитывает всю траекторию движения NPC. НЕ АКТУАЛЬНО
    """      

    def calculating_the_path(global_map, start_point, finish_point, not_ok):
        """
            Просчитывает путь. Не важно, туда или обратно. НЕ АКТУАЛЬНО
        """
    
        waypoints = enemy_ideal_move_calculation(start_point, finish_point)
        not_ok, waypoints = checking_the_path(global_map, waypoints, enemy)

        if not_ok:
    
            attempt_counter = 0
            calculating_the_path = True
            completed_path = [waypoints[-1]]
            previous_point = [0, 0]

            while calculating_the_path:
                priority_parties = [] # Рассчёт приоритетных направлений
                if task[0] - completed_path[-1][0] >= 0:
                    priority_parties.append(1)
                else:
                    priority_parties.append(-1)
                if task[1] - completed_path[-1][1] >= 0:
                    priority_parties.append(1)
                else:
                    priority_parties.append(-1)
                priority_part = [] # Формирование списка с возможными приоритетными направлениями
                if 0 < completed_path[-1][0] < (len(global_map) - 1):
                    if not(global_map[completed_path[-1][0] + priority_parties[0]][completed_path[-1][1]].icon in enemy.enemy.banned_biom):
                        priority_part.append([completed_path[-1][0] + priority_parties[0], completed_path[-1][1]])
                if 0 < completed_path[-1][1] < (len(global_map) - 1):
                    if not(global_map[completed_path[-1][0]][completed_path[-1][1] + priority_parties[1]].icon in enemy.enemy.banned_biom):
                        priority_part.append([completed_path[-1][0], completed_path[-1][1] + priority_parties[1]])
                if previous_point in priority_part:
                    priority_part.remove(previous_point)
                for part in priority_part:
                    if part in completed_path:
                        priority_part.remove(part)
              
                if len(priority_part) > 0: # Если возможно пройти приоритетным путём
                    previous_point = completed_path[-1]
                    completed_path.append(priority_part[random.randrange(len(priority_part))])
                    sub_waypoints = enemy_ideal_move_calculation(completed_path[-1], finish_point)
                    sub_not_ok = False
                    sub_not_ok, sub_waypoints = checking_the_path(global_map, sub_waypoints, enemy)
                    if not(sub_not_ok): # Если всё в порядке, то добавляются все высчитанные точки
                        for number_added_point in range(1, len(completed_path)):
                            waypoints.append(completed_path[number_added_point])
                        for added_point in sub_waypoints:
                            waypoints.append(added_point)
                            not_ok = False # Объявление что всё в порядке
                            calculating_the_path = False # Прерывание цикла с готовым путём
                else: # Если не возможно пройти приоритетным путём, выбираются обычные
                    normal_paths = []
                    if 0 < completed_path[-1][0] < (len(global_map) - 1):
                        if not(global_map[completed_path[-1][0] + 1][completed_path[-1][1]].icon in enemy.enemy.banned_biom):
                            normal_paths.append([completed_path[-1][0] + 1, completed_path[-1][1]])
                        if not(global_map[completed_path[-1][0] - 1][completed_path[-1][1]].icon in enemy.enemy.banned_biom):
                            normal_paths.append([completed_path[-1][0] - 1, completed_path[-1][1]])
                    if 0 < completed_path[-1][1] < (len(global_map) - 1):
                        if not(global_map[completed_path[-1][0]][completed_path[-1][1] + 1].icon in enemy.enemy.banned_biom):
                            normal_paths.append([completed_path[-1][0], completed_path[-1][1] + 1])
                        if not(global_map[completed_path[-1][0]][completed_path[-1][1] - 1].icon in enemy.enemy.banned_biom):
                            normal_paths.append([completed_path[-1][0], completed_path[-1][1] - 1])
                    if previous_point in normal_paths:    
                        normal_paths.remove(previous_point)
                    if len(normal_paths) > 1:
                        for part in normal_paths:
                            if part in completed_path:
                                normal_paths.remove(part)
                    if len(normal_paths) > 0: # Если возможно куда то пойти
                        previous_point = completed_path[-1]
                        completed_path.append(normal_paths[random.randrange(len(normal_paths))])
                    else: # Если нет, то путь сбрасывается в начало
                        print('Путь не найден. Сброс в начало')
                        previous_point = [completed_path[-1]]
                        completed_path = [completed_path[0]]

                attempt_counter += 1
                if attempt_counter == 100:
                    calculating_the_path = False # Вынужденное прерывание цикла без готового пути

        if not_ok:
            print(f'{enemy.enemy.name} не нашел путь')
            for number_added_point in range(1, len(completed_path)):
                waypoints.append(completed_path[number_added_point])
        else:
            print(f'{enemy.enemy.name} нашел путь')
        return not_ok, waypoints
    

    not_ok = False
    not_ok, waypoints = calculating_the_path(global_map, enemy.global_position, task, not_ok) # рассчитывается прямой путь
    if not_ok:
        not_ok, reversed_waypoints = calculating_the_path(global_map, task, enemy.global_position, not_ok) # рассчитывается обратный путь
        if not_ok:
            not_ok, chanse_waypoints = calculating_the_path(global_map, waypoints[-1], task, False) # рассчитывается путь от последней точки
            if not_ok:
                print(f'{enemy.enemy.name} не нашел никакой путь')
            for chanse_waypoint in chanse_waypoints:
                waypoints.append(chanse_waypoint)
            return waypoints
        else:
            return reversed_waypoints.reverse()
    else:
        return waypoints
       
class Node:
    """Содержит узлы графа"""
    __slots__ = ('number', 'position', 'friends', 'price', 'direction')
    def __init__(self, number, position, price, direction):
        self.number = number
        self.position = position
        self.friends = []
        self.price = price
        self.direction = direction

def enemy_a_star_algorithm_move_calculation(calculation_map, start_point, finish_point, banned_list):
    """
        Рассчитывает поиск пути по алгоритму A*
    """
    def path_length(start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0])**2 + (start_point[1] - finish_point[1])**2)
        
    def node_friends_calculation(calculation_map, graph, node, verified_node, banned_list):
        """
            Вычисляет соседние узлы графа
        """
        friends = []
        if 0 <= node.position[0] < len(calculation_map):
            if node.position[0] + 1 < len(calculation_map):
                if not(calculation_map[node.position[0] + 1][node.position[1]].icon in banned_list) and not([node.position[0] + 1, node.position[1]] in verified_node):
                    friend = Node(len(graph), [node.position[0] + 1, node.position[1]], calculation_map[
                             node.position[0] + 1][node.position[1]].price_move + path_length([node.position[0] + 1, node.position[1]], finish_point), [-1, 0])
                    friends.append(friend)
                    graph.append(friend)                                                                                              
            if node.position[0] - 1 >= 0:                                                                                                   
                if not(calculation_map[node.position[0] - 1][node.position[1]].icon in banned_list) and not([node.position[0] - 1, node.position[1]] in verified_node):
                    friend = Node(len(graph), [node.position[0] - 1, node.position[1]], calculation_map[
                            node.position[0] - 1][node.position[1]].price_move + path_length([node.position[0] - 1, node.position[1]], finish_point), [1, 0])
                    friends.append(friend)
                    graph.append(friend)                
        if 0 <= node.position[1] < len(calculation_map):
            if node.position[1] + 1 < len(calculation_map):
                if not(calculation_map[node.position[0]][node.position[1] + 1].icon in banned_list) and not([node.position[0], node.position[1] + 1] in verified_node):
                    friend = Node(len(graph), [node.position[0], node.position[1] + 1], calculation_map[
                            node.position[0]][node.position[1] + 1].price_move + path_length([node.position[0], node.position[1] + 1], finish_point), [0, -1])
                    friends.append(friend)
                    graph.append(friend)
            if node.position[1] - 1 >= 0:
                if not(calculation_map[node.position[0]][node.position[1] - 1].icon in banned_list) and not([node.position[0], node.position[1] - 1] in verified_node):
                    friend = Node(len(graph), [node.position[0], node.position[1] - 1], calculation_map[
                            node.position[0]][node.position[1] - 1].price_move + path_length([node.position[0], node.position[1] - 1], finish_point), [0, 1])
                    friends.append(friend)
                    graph.append(friend)                
        return friends

    graph = []
    verified_node = []
    start_node = Node(0, start_point, 0, [0, 0])
    start_node.friends = node_friends_calculation(calculation_map, graph, start_node, verified_node, banned_list)
    graph.append(start_node)
    verified_node.append(start_node.position)
    finding_a_path = True
    finish_node = 0
    sucess = True
    step_count = 0
    reversed_waypoints = []
    while finding_a_path:
        min_price = 99999
        node = graph[-1]
        for number_node in range(len(graph)):
            if not(graph[number_node].position in verified_node):
                if graph[number_node].price < min_price:
                    min_price = graph[number_node].price
                    node = graph[number_node]
        if min_price == 99999:
            sucess = False
            finding_a_path = False
            
        verified_node.append(node.position)
        node.friends = node_friends_calculation(calculation_map, graph, node, verified_node, banned_list)
        if node.position == finish_point:
            finding_a_path = False
            finish_node = node.number
        step_count += 1
        if step_count == 250:
            sucess = False
            finding_a_path = False
    if sucess:
        check_node = graph[-1]
        while check_node.position != start_node.position:
            reversed_waypoints.append(graph[finish_node].position)
            preview_node = [graph[finish_node].position[0] + graph[finish_node].direction[0], graph[finish_node].position[1] + graph[finish_node].direction[1]]
            for number_node in range(len(graph)):
                if graph[number_node].position == preview_node:
                    finish_node = number_node
                    check_node = graph[number_node]
        test_print = ''
        for number_line in range(len(calculation_map)):
            for number_tile in range(len(calculation_map[number_line])):
                
                if [number_line, number_tile] in reversed_waypoints:
                    test_print += calculation_map[number_line][number_tile].icon + 'v'
                elif [number_line, number_tile] in verified_node:
                    test_print += calculation_map[number_line][number_tile].icon + 'x'
                else:
                    test_print += calculation_map[number_line][number_tile].icon + ' '
            test_print += '\n'
 
        print(test_print)
    else:
        print(f"По алгоритму А* не нашлось пути. На входе было: start_point - {start_point}, finish_point - {finish_point}")
        test_print = ''
        for number_line in range(len(calculation_map)):
            for number_tile in range(len(calculation_map[number_line])):
                if [number_line, number_tile] in verified_node:
                    test_print += calculation_map[number_line][number_tile].icon + 'x'
                else:
                    test_print += calculation_map[number_line][number_tile].icon + ' '
            test_print += '\n'
 
        print(test_print)

            
    return list(reversed(reversed_waypoints))

def path_straightener(calculation_map, waypoints, banned_list):
    """
        Проверяет, можно ли из путевой точки с малым индексом, срезать напрямую до точки с большим индексом.
        Сначала находит все точки, которые можно достичь прямыми путями из стартовой точки, и, начинает проверять
        с точки с бОльшим индексом.
    """
    def straight_path(calculation_map, start_point, second_point, finish_point, banned_list):
        """
            Проверяет доступность прямого пути между двумя точками. В случае удачи строит между ними путь не включая начальную и конечную.
        """
        new_waypoints = [start_point]
        not_ok = False
        if start_point[0] == finish_point[0]:
            if start_point[1] < finish_point[1]:
                while new_waypoints[-1][1] < finish_point[1]:
                    new_waypoint = [new_waypoints[-1][0], new_waypoints[-1][1] + 1]
                    if not(calculation_map[new_waypoint[0]][new_waypoint[1]].icon in banned_list) and calculation_map[new_waypoint[0]][new_waypoint[1]].price_move <= 10 and not(new_waypoint == second_point):
                        new_waypoints.append(new_waypoint)
                    else:
                        not_ok = True
                        break
            else:
                while new_waypoints[-1][1] > finish_point[1]:
                    new_waypoint = [new_waypoints[-1][0], new_waypoints[-1][1] - 1]
                    if not(calculation_map[new_waypoint[0]][new_waypoint[1]].icon in banned_list) and calculation_map[new_waypoint[0]][new_waypoint[1]].price_move <= 10 and not(new_waypoint == second_point):
                        new_waypoints.append(new_waypoint)
                    else:
                        not_ok = True
                        break
                
        elif start_point[1] == finish_point[1]:
            if start_point[0] < finish_point[0]:
                while new_waypoints[-1][0] < finish_point[0]:
                    new_waypoint = [new_waypoints[-1][0] + 1, new_waypoints[-1][1]]
                    if not(calculation_map[new_waypoint[0]][new_waypoint[1]].icon in banned_list) and calculation_map[new_waypoint[0]][new_waypoint[1]].price_move <= 10 and not(new_waypoint == second_point):
                        new_waypoints.append(new_waypoint)
                    else:
                        not_ok = True
                        break
            else:
                while new_waypoints[-1][0] > finish_point[0]:
                    new_waypoint = [new_waypoints[-1][0] - 1, new_waypoints[-1][1]]
                    if not(calculation_map[new_waypoint[0]][new_waypoint[1]].icon in banned_list) and calculation_map[new_waypoint[0]][new_waypoint[1]].price_move <= 10 and not(new_waypoint == second_point):
                        new_waypoints.append(new_waypoint)
                    else:
                        not_ok = True
                        break
        if not_ok:
            return []
        else:
            return new_waypoints
        
    verified_points = []
    start_check = 0
    for number_check_waypoint in range(start_check, len(waypoints) - 1):
        found_points = []
        if number_check_waypoint >= start_check:
            for number_waypoint in range(number_check_waypoint + 2, len(waypoints)):
                if waypoints[number_check_waypoint][0] == waypoints[number_waypoint][0]:
                    found_points.append(number_waypoint)
                if waypoints[number_check_waypoint][1] == waypoints[number_waypoint][1]:
                    found_points.append(number_waypoint)
            while found_points:
                check_point = max(found_points)
                found_points.remove(check_point)
                new_waypoints = straight_path(calculation_map, waypoints[number_check_waypoint], waypoints[number_check_waypoint + 1], waypoints[check_point], banned_list)
                if new_waypoints:
                    first_waypoints = waypoints[0: number_check_waypoint]
                    #print(f'first_waypoints - {first_waypoints}')
                    second_waypoints = waypoints[check_point: (len(waypoints) + 1)]
                    #print(f'second_waypoints - {second_waypoints}')
                    waypoints = []
                    for first_waypoint in first_waypoints:
                        waypoints.append(first_waypoint)
                    for new_waypoint in new_waypoints:
                        waypoints.append(new_waypoint)
                    for second_waypoint in second_waypoints:
                        waypoints.append(second_waypoint)
                    start_check = check_point
                found_points = []
            #print('Цикл while found_points кончился')
    return waypoints
                 
    

def enemy_in_dynamic_chunk(global_map, enemy, position, chunk_size, step):
    """
        Обрабатывает поведение NPC на динамическом чанке игрока
    """
    #print(f"{enemy.enemy.name} сначала имеет вейпоинты: {enemy.dynamic_waypoints}")
    #print(f"{enemy.enemy.name} сначала находился в динамической позиции: {enemy.dynamic_chunk_position} и глобальной: {enemy.global_position}")
    enemy_recalculation_dynamic_chank_position(global_map, enemy, position, chunk_size, step)
    print(f"{enemy.enemy.name} теперь находится в динамической позиции: {enemy.dynamic_chunk_position} и глобальной: {enemy.global_position}")
    print(f"{enemy.enemy.name} имеет динамические вейпоинты: {enemy.dynamic_waypoints}")
    print(f"{enemy.enemy.name} имеет глобальные вейпоинты: {enemy.waypoints}")
    if len(enemy.waypoints) > 0:
        if enemy.global_position == enemy.waypoints[0]:
            enemy.waypoints.pop(0)
    if len(enemy.waypoints) > 0:
        if len(enemy.dynamic_waypoints) > 0:   
            enemy.dynamic_chunk_position = enemy.dynamic_waypoints[0]
            enemy.dynamic_waypoints.pop(0)
        else:
            enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size)
    enemy_global_position_recalculation(global_map, enemy, position, chunk_size)
    #print(f"{enemy.enemy.name} проверка вейпоинтов: {enemy.dynamic_waypoints}")
    #print(f"{enemy.enemy.name} проверка нахождения в динамической позиции: {enemy.dynamic_chunk_position} и глобальной: {enemy.global_position}")



def enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size):
    """
        Рассчитывает передвижение по динамическому чанку с помощью алгоритма А*
    """
    use_calculation_map = global_map[enemy.global_position[0]][enemy.global_position[1]].chunk
    paired_map = global_map[enemy.waypoints[0][0]][enemy.waypoints[0][1]].chunk
    start_point = [enemy.dynamic_chunk_position[0]%chunk_size, enemy.dynamic_chunk_position[1]%chunk_size]
    banned_list = ['▲']
    direction = ''
    suitable_points = []
    reserve_points = []
    if enemy.global_position[0] > enemy.waypoints[0][0]:
        direction = 'up'
        for number_tile in range(len(use_calculation_map[0])):
            if not(use_calculation_map[0][number_tile].icon in banned_list) and not(paired_map[len(paired_map) - 1][number_tile].icon in banned_list):
                if use_calculation_map[0][number_tile].price_move <= 10:
                    suitable_points.append([0, number_tile])
                else:
                    reserve_points.append([0, number_tile])
        

    elif enemy.global_position[0] < enemy.waypoints[0][0]:
        direction = 'down'
        for number_tile in range(len(use_calculation_map[0])):
            if not(use_calculation_map[len(use_calculation_map) - 1][number_tile].icon in banned_list) and not(paired_map[0][number_tile].icon in banned_list):
                if use_calculation_map[len(use_calculation_map) - 1][number_tile].price_move <= 10:
                    suitable_points.append([len(use_calculation_map) - 1, number_tile])
                else:
                    reserve_points.append([len(use_calculation_map) - 1, number_tile])

    elif enemy.global_position[1] > enemy.waypoints[0][1]:
        direction = 'left'
        for number_line in range(len(use_calculation_map)):
            if not(use_calculation_map[number_line][0].icon in banned_list) and not(paired_map[number_line][len(paired_map[0]) - 1].icon in banned_list):
                if use_calculation_map[number_line][0].price_move <= 10:
                    suitable_points.append([number_line, 0])
                else:
                    reserve_points.append([number_line, 0])
                                 
    elif enemy.global_position[1] < enemy.waypoints[0][1]:
        direction = 'right'
        for number_line in range(len(use_calculation_map)):
            if not(use_calculation_map[number_line][len(use_calculation_map) - 1].icon in banned_list) and not(paired_map[number_line][0].icon in banned_list):
                if use_calculation_map[number_line][len(use_calculation_map) - 1].price_move <= 10:
                    suitable_points.append([number_line, len(use_calculation_map[0]) - 1])
                else:
                    reserve_points.append([number_line, len(use_calculation_map[0]) - 1])

    if suitable_points:   
        finish_point = random.choice(suitable_points)
    elif reserve_points:
        finish_point = random.choice(reserve_points)
    else:
        finish_point = [random.randrange(len(use_calculation_map)), random.randrange(len(use_calculation_map))]

    #надо посчитать координаты внутри используемого чанка, а потом пересчитать вейпоинты на динамические

    number_of_chunks_y = enemy.dynamic_chunk_position[0]//chunk_size
    number_of_chunks_x = enemy.dynamic_chunk_position[1]//chunk_size

    raw_waypoints = enemy_ideal_move_calculation(start_point, finish_point)
    not_ok, raw_waypoints = checking_the_path(use_calculation_map, raw_waypoints, banned_list)
    if raw_waypoints:
        if raw_waypoints[-1] != finish_point:
            calculation_waypoints = enemy_a_star_algorithm_move_calculation(use_calculation_map, raw_waypoints[-1], finish_point, banned_list)
            for waypoint in calculation_waypoints:
                raw_waypoints.append(waypoint)
    else:
        raw_waypoints = enemy_a_star_algorithm_move_calculation(use_calculation_map, start_point, finish_point, banned_list)

    if raw_waypoints:
        if direction == 'up':
            raw_waypoints.append([raw_waypoints[-1][0] - 1, raw_waypoints[-1][1]])
        elif direction == 'down':
            raw_waypoints.append([raw_waypoints[-1][0] + 1, raw_waypoints[-1][1]])
        elif direction == 'left':
            raw_waypoints.append([raw_waypoints[-1][0], raw_waypoints[-1][1] - 1])
        elif direction == 'right':
            raw_waypoints.append([raw_waypoints[-1][0], raw_waypoints[-1][1] + 1])

    test_print = '' # Печать рассчитанной карты
    for number_line in range(len(use_calculation_map)):
        for number_tile in range(len(use_calculation_map[number_line])):
            if [number_line, number_tile] in raw_waypoints:
                test_print += use_calculation_map[number_line][number_tile].icon + 'L'
            else:
                test_print += use_calculation_map[number_line][number_tile].icon + ' '
        test_print += '\n'
    print(test_print)

    raw_waypoints = path_straightener(use_calculation_map, raw_waypoints, banned_list)

    test_print = '' # Печать перессчитанной карты
    for number_line in range(len(use_calculation_map)):
        for number_tile in range(len(use_calculation_map[number_line])):
            if [number_line, number_tile] in raw_waypoints:
                test_print += use_calculation_map[number_line][number_tile].icon + 'M'
            else:
                test_print += use_calculation_map[number_line][number_tile].icon + ' '
        test_print += '\n'
    print(test_print)
    print(raw_waypoints)
    enemy.dynamic_waypoints = []
    for waypoint in raw_waypoints:
        enemy.dynamic_waypoints.append([waypoint[0] + (number_of_chunks_y * chunk_size), waypoint[1] + (number_of_chunks_x * chunk_size)])


    

def enemy_ideal_move_calculation(start_point, finish_point):
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

def checking_the_path(calculation_map, waypoints, banned_list):
        """
            Проверяет путь на отсутствие преград.
        """
        not_ok = False
        for number_waypoint in range(len(waypoints)):
            print(f'number_waypoint - {number_waypoint}, waypoints - {waypoints}')
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
    
def enemy_global_position_recalculation(global_map, enemy, position, chunk_size):
    """
        Перерассчитывает глобальную позицию NPC при их перемещении на динамическом чанке
    """
    enemy.global_position = [(position.assemblage_point[0] + enemy.dynamic_chunk_position[0]//chunk_size),
                             (position.assemblage_point[1] + enemy.dynamic_chunk_position[1]//chunk_size)]

def enemy_recalculation_dynamic_chank_position(global_map, enemy, position, chunk_size, step):
    """
        Перерассчитывает позицию NPC и его динамические путевые точки при перерассчёте динамического чанка
    """
    if enemy.old_position_assemblage_point != position.assemblage_point:
        if position.assemblage_point[0] == (enemy.old_position_assemblage_point[0] - 1):
            enemy.dynamic_chunk_position[0] += chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][0] += chunk_size
           
        elif position.assemblage_point[0] == (enemy.old_position_assemblage_point[0] + 1):
            enemy.dynamic_chunk_position[0] -= chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][0] -= chunk_size
                
        if position.assemblage_point[1] == (enemy.old_position_assemblage_point[1] - 1):
            enemy.dynamic_chunk_position[1] += chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][1] += chunk_size
            
        elif position.assemblage_point[1] == (enemy.old_position_assemblage_point[1] + 1):
            enemy.dynamic_chunk_position[1] -= chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][1] -= chunk_size

    if (0 <= enemy.dynamic_chunk_position[0] >= chunk_size*2) and (0 <= enemy.dynamic_chunk_position[1] >= chunk_size*2):
        enemy.step_exit_from_assemblage_point = step
    enemy.old_position_assemblage_point = copy.deepcopy(position.assemblage_point)
    
def enemy_dynamic_chunk_check(global_map, enemy_list, position, step, chunk_size):
    """
        Проверяет нахождение NPC на динамическом чанке игрока
    """
    for enemy in enemy_list:
        number_encounter_chank_ok = 99
        for number_encounter_chunk in range(len(position.check_encounter_position)):
            if position.check_encounter_position[number_encounter_chunk] == enemy.global_position:
                number_encounter_chank_ok = number_encounter_chunk 
        if enemy.dynamic_chunk == False and number_encounter_chank_ok != 99:
            enemy.old_position_assemblage_point = copy.deepcopy(position.assemblage_point)
            enemy.dynamic_chunk = True
            if number_encounter_chank_ok == 0:
                enemy.dynamic_chunk_position = [position.dynamic[0] - chunk_size, position.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 1:
                enemy.dynamic_chunk_position = [position.dynamic[0] - chunk_size, position.dynamic[1]]
            elif number_encounter_chank_ok == 2:
                enemy.dynamic_chunk_position = [position.dynamic[0] - chunk_size, position.dynamic[1] + chunk_size]
            elif number_encounter_chank_ok == 3:
                enemy.dynamic_chunk_position = [position.dynamic[0], position.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 4:
                enemy.dynamic_chunk_position = [position.dynamic[0], position.dynamic[1]]
            elif number_encounter_chank_ok == 5:
                enemy.dynamic_chunk_position = [position.dynamic[0], position.dynamic[1] + chunk_size]
            elif number_encounter_chank_ok == 6:
                enemy.dynamic_chunk_position = [position.dynamic[0] + chunk_size, position.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 7:
                enemy.dynamic_chunk_position = [position.dynamic[0] + chunk_size, position.dynamic[1]]
            elif number_encounter_chank_ok == 8:
                enemy.dynamic_chunk_position = [position.dynamic[0] + chunk_size, position.dynamic[1] + chunk_size]

        elif enemy.dynamic_chunk and number_encounter_chank_ok != 99:
            pass
        
        elif (step - enemy.step_exit_from_assemblage_point) < 30 and enemy.step_exit_from_assemblage_point and step > 30:
            pass
        
        elif (step - enemy.step_exit_from_assemblage_point) == 30 and step != 30:
            enemy.step_exit_from_assemblage_point = 0
            enemy.dynamic_waypoints = []
            enemy.dynamic_chunk = False
        else:
            enemy.dynamic_waypoints = []
            enemy.dynamic_chunk = False
            
def enemy_hunter_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size):
    """
        Обрабатывает жизнь hunter NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """
    enemy.action_points += 1
    enemy.enemy.hunger -= 1
    enemy.enemy.thirst -= 1
    enemy.enemy.fatigue -= 1
    
    if enemy.action_points >= 5:
        if random.randrange(10) > -1:
            move_hunter_enemy(global_map, enemy)
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
            activity_list.append(Action_in_map('rest_stop', step, enemy.global_position, chunk_size))
        else:
            activity = random.choice(enemy.enemy.activity)
            if activity[1] == 'action_points':
                enemy.action_points += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'thirst':
                enemy.enemy.thirst += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'hunger':
                enemy.enemy.hunger += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'fatigue':
                enemy.action_points -= 5
                enemy.enemy.fatigue += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            go_to_print.text5 += str(enemy.enemy.name_npc)+ ' ' + str(activity[0]) + ' его голод: ' + str(enemy.enemy.hunger) + ' его жажда: ' + str(enemy.enemy.thirst) + ' его усталость: ' + str(enemy.enemy.fatigue) + '\n'
            enemy.action_points -= 3

            
def move_hunter_enemy(global_map, enemy):
    """
        Обрабатывает передвижение NPC по вейпоинтам
    """
    if enemy.waypoints:
        number_slice = 0
        for number_waypoint in range(len(enemy.waypoints)):
            if enemy.global_position == enemy.waypoints[number_waypoint]:
                number_slice = number_waypoint - 1
        if number_slice > 0:
            enemy.waypoints[number_slice: len(enemy.waypoints)]
        
        enemy.global_position = enemy.waypoints[0]
        enemy.waypoints.pop(0)


def enemy_chaotic_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size):
    """
        Обрабатывает жизнь chaotic NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """

    enemy.action_points += 1
    enemy.enemy.hunger -= 1
    enemy.enemy.thirst -= 1
    enemy.enemy.fatigue -= 1
    
    if enemy.action_points >= 5:
        if random.randrange(10)//6 == 1 or (global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.enemy.priority_biom and random.randrange(10)//8 == 1):
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
            activity_list.append(Action_in_map('rest_stop', step, enemy.global_position, chunk_size))
        else:
            activity = random.choice(enemy.enemy.activity)
            if activity[1] == 'action_points':
                enemy.action_points += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'thirst':
                enemy.enemy.thirst += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'hunger':
                enemy.enemy.hunger += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            elif activity[1] == 'fatigue':
                enemy.action_points -= 5
                enemy.enemy.fatigue += activity[2]
                activity_list.append(Action_in_map(activity[3], step, enemy.global_position, chunk_size))
            go_to_print.text5 += str(enemy.enemy.name_npc)+ ' ' + str(activity[0]) + ' его голод: ' + str(enemy.enemy.hunger) + ' его жажда: ' + str(enemy.enemy.thirst) + ' его усталость: ' + str(enemy.enemy.fatigue) + '\n'
            enemy.action_points -= 3
    

def move_biom_enemy(global_map, enemy):
    """
        Обрабатывает перемещение NPC за кадром между биомами
    """

    if global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.enemy.priority_biom:
        direction_moved = []
        if global_map[enemy.global_position[0] - 1][enemy.global_position[1]].icon in enemy.enemy.priority_biom and enemy.global_position[0] - 1 > 0:
            direction_moved.append([enemy.global_position[0] - 1, enemy.global_position[1]])
        if global_map[enemy.global_position[0] + 1][enemy.global_position[1]].icon in enemy.enemy.priority_biom and enemy.global_position[0] + 1 < len(global_map) - 1:
            direction_moved.append([enemy.global_position[0] + 1, enemy.global_position[1]]) 
        if global_map[enemy.global_position[0]][enemy.global_position[1] - 1].icon in enemy.enemy.priority_biom and enemy.global_position[1] - 1 > 0:
            direction_moved.append([enemy.global_position[0], enemy.global_position[1] - 1])
        if global_map[enemy.global_position[0]][enemy.global_position[1] + 1].icon in enemy.enemy.priority_biom and enemy.global_position[1] + 1 < len(global_map) - 1:
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
                enemy.waypoints = [random.choice(direction_moved)]
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
            enemy.waypoints = [random.choice(direction_moved)]



"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ПОЛЬЗОВАТЕЛЬСКИЙ ВВОД И ЕГО ОБРАБОТКА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def master_player_action(global_map, position, chunk_size, go_to_print, changing_step, mode_action, interaction):


    pressed_button = ''
    mode_action, pressed_button = request_press_button(global_map, position, chunk_size, go_to_print, changing_step, mode_action, interaction)

    if mode_action == 'move':
        request_move(global_map, position, chunk_size, go_to_print, pressed_button, changing_step)
    elif mode_action == 'test_move':
        test_request_move(global_map, position, chunk_size, go_to_print, pressed_button, changing_step, interaction)
    elif mode_action == 'pointer':    
        request_pointer(position, chunk_size, go_to_print, pressed_button, changing_step)
    elif mode_action == 'gun':
        request_gun(global_map, position, chunk_size, go_to_print, pressed_button, changing_step)
    if pressed_button == 'button_map':
        go_to_print.minimap_on = (go_to_print.minimap_on == False)
    request_processing(pressed_button)

    calculation_assemblage_point(global_map, position, chunk_size)
    
    return mode_action


def request_press_button(global_map, position, chunk_size, go_to_print, changing_step, mode_action, interaction):
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
            position.pointer = [chunk_size//2, chunk_size//2]
            return ('pointer', 'button_pointer')
        elif mode_action == 'pointer':
            position.pointer = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer')
        else:
            position.pointer = [chunk_size//2, chunk_size//2]
            position.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_pointer')
    elif key == 'g' or key == 'п':
        if mode_action == 'move':
            position.gun = [chunk_size//2, chunk_size//2]
            return ('gun', 'button_gun')
        elif mode_action == 'gun':
            position.gun = [chunk_size//2, chunk_size//2]
            return ('move', 'button_gun')
        else:
            position.pointer = [chunk_size//2, chunk_size//2]
            position.gun = [chunk_size//2, chunk_size//2]
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
            
    else:
        return (mode_action, 'none')


def request_move(global_map:list, position, chunk_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет динамическое местоположение персонажа
    """
    if pressed_button == 'up':
        
        if position.chunks_use_map[position.dynamic[0] - 1][position.dynamic[1]].icon != '▲':
            if position.dynamic[0] >= chunk_size//2 and position.assemblage_point[0] > 0:
                position.dynamic[0] -= 1
            
    elif pressed_button == 'left':
        
        if position.chunks_use_map[position.dynamic[0]][position.dynamic[1] - 1].icon != '▲':
            if position.dynamic[1] >= chunk_size//2 and position.assemblage_point[1] > 0:
                position.dynamic[1] -= 1
            
    elif pressed_button == 'down':
        
        if position.chunks_use_map[position.dynamic[0] + 1][position.dynamic[1]].icon != '▲':
            if position.dynamic[0] <= (chunk_size + chunk_size//2) and position.assemblage_point[0] != (len(global_map) - 2):
                position.dynamic[0] += 1
            
    elif pressed_button == 'right':
        
        if position.chunks_use_map[position.dynamic[0]][position.dynamic[1] + 1].icon != '▲':
            if position.dynamic[1] <= (chunk_size + chunk_size//2) and position.assemblage_point[1] != (len(global_map) - 2):
                position.dynamic[1] += 1
    

def test_request_move(global_map:list, position, chunk_size:int, go_to_print, pressed_button, changing_step, interaction): #тестовый быстрый режим премещения
    """
        Меняет динамическое местоположение персонажа в тестовом режиме, без ограничений. По полчанка за раз.
        При нажатии на 'p' назначает всем NPC точку следования.
    """
    
    if pressed_button == 'up':
        if position.dynamic[0] >= chunk_size//2 and position.assemblage_point[0] > 0:
            position.dynamic[0] -= chunk_size//2
            
    elif pressed_button == 'left':
        if position.dynamic[1] >= chunk_size//2 and position.assemblage_point[1] > 0:
            position.dynamic[1] -= chunk_size//2
            
    elif pressed_button == 'down': 
        if position.dynamic[0] <= (chunk_size + chunk_size//2) and position.assemblage_point[0] != (len(global_map) - 2):
            position.dynamic[0] += chunk_size//2
            
    elif pressed_button == 'right':
        if position.dynamic[1] <= (chunk_size + chunk_size//2) and position.assemblage_point[1] != (len(global_map) - 2):
            position.dynamic[1] += chunk_size//2

    elif pressed_button == 'button_purpose_task':
        interaction.append(['task_point_all_enemies', position.global_position])
        

def request_pointer(position, chunk_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет местоположение указателя
    """
    if pressed_button == 'up' and position.pointer[0] > 0:
        position.pointer[0] -= 1
    elif pressed_button == 'left' and position.pointer[1] > 0:
        position.pointer[1] -= 1 
    elif pressed_button == 'down' and position.pointer[0] < chunk_size - 1:
        position.pointer[0] += 1
    elif pressed_button == 'right' and position.pointer[1] < chunk_size - 1:
        position.pointer[1] += 1

def request_gun(global_map:list, position, chunk_size:int, go_to_print, pressed_button, changing_step):
    """
        Меняет местоположение указателя оружия
    """
    if pressed_button == 'up' and position.gun[0] > chunk_size//2 - 5:
        position.gun[0] -= 1
            
    elif pressed_button == 'left' and position.gun[1] > chunk_size//2 - 5:
        position.gun[1] -= 1
            
    elif pressed_button == 'down' and position.gun[0] < chunk_size//2 + 5:
        position.gun[0] += 1
            
    elif pressed_button == 'right' and position.gun[1] < chunk_size//2 + 5:
        position.gun[1] += 1

def calculation_assemblage_point(global_map:list, position, chunk_size:int):
    """
        Перерассчитывает положение точки сборки, динамические координаты, перерассчитывает динамический чанк.
    """
    
    if position.dynamic[0] > (chunk_size//2 + chunk_size - 1):
        position.assemblage_point[0] += 1
        position.dynamic[0] -= chunk_size        
    elif position.dynamic[0] < chunk_size//2:
        position.assemblage_point[0] -= 1
        position.dynamic[0] += chunk_size
        
    if position.dynamic[1] > (chunk_size//2 + chunk_size - 1):
        position.assemblage_point[1] += 1
        position.dynamic[1] -= chunk_size   
    elif position.dynamic[1] < chunk_size//2:
        position.assemblage_point[1] -= 1
        position.dynamic[1] += chunk_size


    assemblage_chunk = []

    line_slice = global_map[position.assemblage_point[0]:(position.assemblage_point[0] + 2)]
    
    for line in line_slice:
        line = line[position.assemblage_point[1]:(position.assemblage_point[1] + 2)]
        assemblage_chunk.append(line)
    for number_line in range(len(assemblage_chunk)):
        for chunk in range(len(assemblage_chunk)):
            assemblage_chunk[number_line][chunk] = assemblage_chunk[number_line][chunk].chunk
    position.chunks_use_map = gluing_location(assemblage_chunk, 2, chunk_size)

    position.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод
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
    line_views = position.chunks_use_map[start_stop[0]:start_stop[2]]

    go_to_print.point_to_draw = [(position.dynamic[0] - half_views), (position.dynamic[1] - half_views)]
    
    draw_field = []
    for line in line_views:
        line_icon = []
        line = line[start_stop[1]:start_stop[3]]
        for tile in line:
            line_icon.append(tile)
        draw_field.append(line_icon)
    return draw_field

def draw_additional_entities(position, chunk_size:int, go_to_print, enemy_list, activity_list):
    """
        Отрисовывает на динамическом чанке дополнительные статические сущности
    """
    
    for activity in activity_list:
        if activity.global_position[0] == position.assemblage_point[0] and activity.global_position[1] == position.assemblage_point[1]:
            position.chunks_use_map[activity.local_position[0]][activity.local_position[1]] = activity
        elif activity.global_position[0] == position.assemblage_point[0] and activity.global_position[1] == position.assemblage_point[1] + 1:
            position.chunks_use_map[activity.local_position[0]][activity.local_position[1] + chunk_size] = activity
        elif activity.global_position[0] == position.assemblage_point[0] + 1 and activity.global_position[1] == position.assemblage_point[1]:
            position.chunks_use_map[activity.local_position[0] + chunk_size][activity.local_position[1]] = activity
        elif activity.global_position[0] == position.assemblage_point[0] + 1 and activity.global_position[1] == position.assemblage_point[1] + 1:
            position.chunks_use_map[activity.local_position[0] + chunk_size][activity.local_position[1] + chunk_size] = activity

    for enemy in enemy_list:
        if enemy.global_position in position.check_encounter_position:
            if (0 <= enemy.dynamic_chunk_position[0] < chunk_size * 2) and (0 <= enemy.dynamic_chunk_position[1] < chunk_size * 2 - 2):
                position.chunks_use_map[enemy.dynamic_chunk_position[0]][enemy.dynamic_chunk_position[1]] = enemy.enemy
                               

def master_draw(position, chunk_size:int, go_to_print, global_map, mode_action, enemy_list, activity_list):
    """
        Формирует итоговое изображение игрового поля для вывода на экран
    """
    if go_to_print.minimap_on:
        print_minimap(global_map, position, go_to_print, enemy_list)

    draw_additional_entities(position, chunk_size, go_to_print, enemy_list, activity_list)

    draw_field = draw_field_calculations(position, chunk_size, go_to_print)

    draw_box = []
    pointer_vision = Tile('??')
    for line in range(len(draw_field)):
        print_line = ''
        for tile in range(len(draw_field)):
            if line == chunk_size//2 and tile == chunk_size//2:
                ground = draw_field[line][tile].description
                print_line += '☺'
                if mode_action == 'pointer' and position.pointer == [chunk_size//2, chunk_size//2]:
                    print_line += '<'
                    pointer_vision = draw_field[line][tile]
                elif mode_action == 'gun' and position.gun == [chunk_size//2, chunk_size//2]:
                    print_line += '+'    
                else:
                    print_line += ' '
            elif line == position.pointer[0] and tile == position.pointer[1]:
                print_line += draw_field[line][tile].icon + '<'
                pointer_vision = draw_field[line][tile]
            elif line == position.gun[0] and tile == position.gun[1]:
                print_line += draw_field[line][tile].icon + '+'
            else:
                if len(draw_field[line][tile].icon) == 2:
                    print_line += draw_field[line][tile].icon
                else:
                    print_line += draw_field[line][tile].icon + ' '
        draw_box.append(print_line)
    go_to_print.game_field = draw_box
    go_to_print.text1 = (f"{position.assemblage_point} - Позиция точки сборки | {position.dynamic} - динамическая позиция | под ногами: {ground}")
    go_to_print.text4 = pointer_vision.description
    
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

def game_loop(global_map:list, position:list, chunk_size:int, frame_size:list, enemy_list:list):
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
        interaction = []
        changing_step = True
        if not_intercept_step[0]:
            mode_action = master_player_action(global_map, position, chunk_size, go_to_print, changing_step, mode_action, interaction)
        start = time.time() #проверка времени выполнения
        if changing_step:
            master_game_events(global_map, enemy_list, position, go_to_print, step, activity_list, chunk_size, interaction)
            step += 1
        test1 = time.time() #проверка времени выполнения
        master_draw(position, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list)
        test2 = time.time() #проверка времени выполнения
        print_frame(go_to_print, frame_size, activity_list)
        #print('step = ', step)
        end = time.time() #проверка времени выполнения
        print(test1 - start, ' - test1 ', test2 - start, ' - test2 ', end - start, ' - end ') #
             

def main():
    """
        Запускает игру
        
    """
    chunk_size = 25         #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    value_region_box = 5    #Количество регионов в квадрате.
    grid = 5                #Должно быть кратно размеру игрового экрана.
    frame_size = [35, 40]   #Размер одного кадра [высота, ширина].


    #progress_bar(5, 'Запуск игры') 
    global_map = master_generate(value_region_box, chunk_size, grid)
    position = Position([value_region_box//2, value_region_box//2], [chunk_size//2, chunk_size//2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
    calculation_assemblage_point(global_map, position, chunk_size)
    enemy_list = [Enemy(Horseman(),[len(global_map)//2, len(global_map)//2] , 5), Enemy(Horseman(),[len(global_map)//3, len(global_map)//3] , 5),
                  Enemy(Riffleman(),[len(global_map)//4, len(global_map)//4] , 2), Enemy(Coyot(),[len(global_map)//5, len(global_map)//5] , 0)]
    game_loop(global_map, position, chunk_size, frame_size, enemy_list)
    
    print('Игра окончена!')

main()
    

