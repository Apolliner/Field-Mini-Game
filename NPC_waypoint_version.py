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
    путевой точки с бОльшим индексом. #РЕАЛИЗОВАНО
    13)Разобраться с наследованим классов и привести код в соответствие с их правильным применением.
    14)Добавить для NPC режим поиска, который включается когда NPC обнаруживает незнакомые следы или видит незнакомого NPC или персонажа.
    15)Объединить всё что касается персонажа в класс Person

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


class Person:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    __slots__ = ('assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position', 'number_chunk',
                 'check_encounter_position', 'environment_temperature', 'person_temperature', 'person_pass_step', 'enemy_pass_step', 'speed')
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
        self.environment_temperature = 36.6
        self.person_temperature = 36.6
        self.person_pass_step = 0
        self.enemy_pass_step = 0
        self.speed = 1


        
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
    banned_list = ['~', '▲']
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
                    2: ['cliff semidesert',   [35.0,50.0], ['▲', 'A', '.', ','],  ['o', 'i'],       'A',         7],
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

def master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step):
    """
        Здесь происходят все события, не связанные с пользовательским вводом
    """
    interaction_processing(global_map, interaction, enemy_list)
    activity_list_check(activity_list, step)
    master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step)

def interaction_processing(global_map, interaction, enemy_list):
    """
        Обрабатывает взаимодействие игрока с миром
    """
    if len(interaction) != 0:
        for interact in interaction:
            if interact[0] == 'task_point_all_enemies':
                for enemy in enemy_list:
                    #print(f"{enemy.name} получил задачу")
                    #print(f"interact[1] = {interact[1]}")
                    if enemy.type == 'hunter':
                        enemy.waypoints = enemy_a_star_algorithm_move_calculation(global_map, enemy.global_position, interact[1], enemy.banned_biom)


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
    __slots__ = ('name', 'icon', 'description', 'lifetime', 'birth', 'global_position', 'local_position', 'caused', 'lifetime_description')
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

    def all_description(self):
        self.description = f'{self.lifetime_description} {self.action_dict(1)} похоже на {self.caused}'

        
    def action_dict(self, number):
        """ Принимает название активности, возвращает её иконку, описание и срок жизни"""

        action_dict =   {
                        'camp':             ['/', 'следы лагеря',               150],
                        'bonfire':          ['+', 'следы костра',               150],
                        'rest_stop':        ['№', 'следы остановки человека',   150],
                        'horse_tracks':     ['%', 'следы лошади',               150],
                        'human_tracks':     ['8', 'следы человека',             150],
                        'animal_traces':    ['@', 'следы зверя',                150],
                        'gnawed bones':     ['#', 'обглоданные зверем кости',   500],
                        'defecate':         ['&', 'справленная нужда',          150],
                        'animal_rest_stop': ['$', 'следы животной лежанки',     150],
                        'dead_man':         ['D', 'мёртвый человек',           1000],
                        'test_beacon':      ['B', 'маяк для теста',            1000],
                        'unknown':          ['?', 'неизвестно',                 150],
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
    def __init__(self, global_position, action_points):
        self.global_position = global_position
        self.action_points = action_points
        self.dynamic_chunk = False
        self.dynamic_chunk_position = [0, 0]
        self.old_position_assemblage_point = [1, 1]
        self.step_exit_from_assemblage_point = 0
        self.waypoints = []
        self.dynamic_waypoints = []
        self.alarm = False
        self.pass_step = 0
        self.on_the_screen = False
        self.steps_to_new_step = 1

    def all_description_calculation(self):
        self.description = f"{self.pass_description} {self.person_description}"

class Horseman(Enemy):
    """ Отвечает за всадников """
    
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, action_points):
        super().__init__(global_position, action_points)
        self.name = 'horseman'
        self.name_npc = random.choice(['Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['▲']
        self.icon = '☻h'
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
        self.type = 'hunter'
        self.pass_description = ''
        self.person_description = f"Знаменитый охотник за головами {self.name_npc}"
        self.description = ''
        self.speed = 2

class Riffleman(Enemy):
    """ Отвечает за стрелков """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, action_points):
        super().__init__(global_position, action_points)
        self.name = 'riffleman'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻-'
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
        self.type = 'hunter'
        self.pass_description = ''
        self.person_description = f"Шериф одного мрачного города {self.name_npc}"
        self.description = ''
        self.speed = 1

class Gold_digger(Enemy):
    """ Отвечает за золотоискателей """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, action_points):
        super().__init__(global_position, action_points)
        self.name = 'gold_digger'
        self.name_npc = random.choice(['Бедовая Джейн', 'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт'])
        self.priority_biom = ['.', 'A', '▲']
        self.banned_biom = ['~']
        self.icon = '☻='
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
        self.type = 'chaotic'
        self.pass_description = ''
        self.person_description = f"Отчаяный золотоискатель {self.name_npc}"
        self.description = ''
        self.speed = 1

class Horse(Enemy):
    """ Отвечает за коней """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, action_points):
        super().__init__(global_position, action_points)
        self.name = 'horse'
        self.name_npc = random.choice(['Стреноженая белая лошадь', 'Стреноженая гнедая лошадь', 'Стреноженая черная лошадь'])
        self.priority_biom = [',', '„', 'P']
        self.banned_biom = ['~', ';']
        self.icon = 'ho'
        self.activity_map = {
                            'move': [['передвигается', 'horse_tracks', 0, 0]],
                            'hunger': [['ест траву', 'horse_tracks', 80, 5]],
                            'thirst': [['пьёт', 'horse_tracks', 80, 5]],
                            'fatigue': [['отдыхает', 'animal_rest_stop', 80, 20]],
                            'other': [['пугатся и убегает', 'horse_trucks', 0, 0]],
                            }
        self.hunger = 100
        self.thirst = 100
        self.fatigue = 100
        self.reserves = 0
        self.type = 'chaotic'
        self.pass_description = ''
        self.person_description = f"{self.name_npc}"
        self.description = ''
        self.speed = 2

class Coyot(Enemy):
    """ Отвечает за койотов """
        
    """ activity_map содержит следующие значения [описание активности, название активности, добавляемые очки, количество пропускаемых шагов] """
    def __init__(self, global_position, action_points):
        super().__init__(global_position, action_points)
        self.name = 'coyot'
        self.name_npc = random.choice(['плешивый койот', 'молодой койот', 'подраный койот'])
        self.priority_biom = ['.', ',', '„', 'P', 'A']
        self.banned_biom = ['~', ';']
        self.icon = 'co'
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
        self.type = 'chaotic'
        self.pass_description = ''
        self.person_description = f"Голодный и злой {self.name_npc}"
        self.description = ''
        self.speed = 1

def master_npc_calculation(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step):
    """
        Здесь происходят все события, связанные с NPC
    """
    enemy_dynamic_chunk_check(global_map, enemy_list, person, step, chunk_size)
    go_to_print.text5 = ''
    for enemy in enemy_list:
        if enemy.speed == 2 and enemy.on_the_screen:
            max_speed_enemy_visible = True
        else:
            max_speed_enemy_visible = False
    
    for enemy in enemy_list:
        if enemy.dynamic_chunk:
            enemy_in_dynamic_chunk(global_map, enemy, person, chunk_size, step, activity_list, new_step, max_speed_enemy_visible)
            pass
        else:
            enemy_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size)
       
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
 
        #print(test_print)
    else:
        #print(f"По алгоритму А* не нашлось пути. На входе было: start_point - {start_point}, finish_point - {finish_point}")
        test_print = ''
        for number_line in range(len(calculation_map)):
            for number_tile in range(len(calculation_map[number_line])):
                if [number_line, number_tile] in verified_node:
                    test_print += calculation_map[number_line][number_tile].icon + 'x'
                else:
                    test_print += calculation_map[number_line][number_tile].icon + ' '
            test_print += '\n'
 
       # print(test_print)

            
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
        
        if start_point[0] < len(calculation_map) and start_point[1] < len(calculation_map[0]) and finish_point[0] < len(calculation_map) and finish_point[1] < len(calculation_map[0]):
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
                new_waypoints = straight_path(calculation_map, waypoints[number_check_waypoint], waypoints[number_check_waypoint + 1],
                                              waypoints[check_point], banned_list)
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

def enemy_on_the_screen(enemy, person, chunk_size):
    """
        Проверяет NPC на видимость игроком
    """
    if (person.dynamic[0] - chunk_size//2 - 1 < enemy.dynamic_chunk_position[0] < person.dynamic[0] + chunk_size//2 + 1) and (
        person.dynamic[1] - chunk_size//2 - 1 < enemy.dynamic_chunk_position[1] < person.dynamic[1] + chunk_size//2 + 1):
        enemy.on_the_screen = True
    else:
        enemy.on_the_screen = False
    print(f"{enemy.name} enemy.on_the_screen = {enemy.on_the_screen}")


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

    if enemy.on_the_screen or max_speed_enemy_visible:
        print(f"{enemy.name} сработало условие 'enemy.on_the_screen or max_speed_enemy_visible'")
        if enemy.steps_to_new_step:
            print(f"{enemy.name} сработало условие 'enemy.steps_to_new_step'")
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
                        if random.randrange(101)//99 > 0:
                            action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size)
                    else:
                        enemy.pass_step -= 1
                else:
                    enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size, 'moving_between_locations', [chunk_size//2, chunk_size//2])
            enemy.steps_to_new_step -= 1
        
    else:
        print(f"{enemy.name} сработало условие 'else'")
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
                        if random.randrange(101)//99 > 0:
                            action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size)
                    else:
                        enemy.pass_step -= 1
                else:
                    enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size, 'moving_between_locations', [chunk_size//2, chunk_size//2])
    enemy_global_position_recalculation(global_map, enemy, person, chunk_size)

def enemy_a_star_move_dynamic_calculations(global_map, enemy, chunk_size, mode, target_point):
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
    if mode == 'moving_between_locations':
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
    else:
        finish_point = target_point

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
    #print(test_print)

    raw_waypoints = path_straightener(use_calculation_map, raw_waypoints, banned_list)

    test_print = '' # Печать перессчитанной карты
    for number_line in range(len(use_calculation_map)):
        for number_tile in range(len(use_calculation_map[number_line])):
            if [number_line, number_tile] in raw_waypoints:
                test_print += use_calculation_map[number_line][number_tile].icon + 'M'
            else:
                test_print += use_calculation_map[number_line][number_tile].icon + ' '
        test_print += '\n'
    #print(test_print)
    #print(raw_waypoints)
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
    
def enemy_global_position_recalculation(global_map, enemy, person, chunk_size):
    """
        Перерассчитывает глобальную позицию NPC при их перемещении на динамическом чанке
    """
    enemy.global_position = [(person.assemblage_point[0] + enemy.dynamic_chunk_position[0]//chunk_size),
                             (person.assemblage_point[1] + enemy.dynamic_chunk_position[1]//chunk_size)]

def enemy_recalculation_dynamic_chank_position(global_map, enemy, person, chunk_size, step):
    """
        Перерассчитывает позицию NPC и его динамические путевые точки при перерассчёте динамического чанка
    """
    if enemy.old_position_assemblage_point != person.assemblage_point:
        if person.assemblage_point[0] == (enemy.old_position_assemblage_point[0] - 1):
            enemy.dynamic_chunk_position[0] += chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][0] += chunk_size
           
        elif person.assemblage_point[0] == (enemy.old_position_assemblage_point[0] + 1):
            enemy.dynamic_chunk_position[0] -= chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][0] -= chunk_size
                
        if person.assemblage_point[1] == (enemy.old_position_assemblage_point[1] - 1):
            enemy.dynamic_chunk_position[1] += chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][1] += chunk_size
            
        elif person.assemblage_point[1] == (enemy.old_position_assemblage_point[1] + 1):
            enemy.dynamic_chunk_position[1] -= chunk_size
            for number_dynamic_waypoint in range(len(enemy.dynamic_waypoints)):
                enemy.dynamic_waypoints[number_dynamic_waypoint][1] -= chunk_size

    if (0 <= enemy.dynamic_chunk_position[0] >= chunk_size*2) and (0 <= enemy.dynamic_chunk_position[1] >= chunk_size*2):
        enemy.step_exit_from_assemblage_point = step
    enemy.old_position_assemblage_point = copy.deepcopy(person.assemblage_point)
    
def enemy_dynamic_chunk_check(global_map, enemy_list, person, step, chunk_size):
    """
        Проверяет нахождение NPC на динамическом чанке игрока
    """
    for enemy in enemy_list:
        number_encounter_chank_ok = 99
        for number_encounter_chunk in range(len(person.check_encounter_position)):
            if person.check_encounter_position[number_encounter_chunk] == enemy.global_position:
                number_encounter_chank_ok = number_encounter_chunk 
        if enemy.dynamic_chunk == False and number_encounter_chank_ok != 99:
            enemy.old_position_assemblage_point = copy.deepcopy(person.assemblage_point)
            enemy.dynamic_chunk = True
            if number_encounter_chank_ok == 0:
                enemy.dynamic_chunk_position = [person.dynamic[0] - chunk_size, person.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 1:
                enemy.dynamic_chunk_position = [person.dynamic[0] - chunk_size, person.dynamic[1]]
            elif number_encounter_chank_ok == 2:
                enemy.dynamic_chunk_position = [person.dynamic[0] - chunk_size, person.dynamic[1] + chunk_size]
            elif number_encounter_chank_ok == 3:
                enemy.dynamic_chunk_position = [person.dynamic[0], person.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 4:
                enemy.dynamic_chunk_position = [person.dynamic[0], person.dynamic[1]]
            elif number_encounter_chank_ok == 5:
                enemy.dynamic_chunk_position = [person.dynamic[0], person.dynamic[1] + chunk_size]
            elif number_encounter_chank_ok == 6:
                enemy.dynamic_chunk_position = [person.dynamic[0] + chunk_size, person.dynamic[1] - chunk_size]
            elif number_encounter_chank_ok == 7:
                enemy.dynamic_chunk_position = [person.dynamic[0] + chunk_size, person.dynamic[1]]
            elif number_encounter_chank_ok == 8:
                enemy.dynamic_chunk_position = [person.dynamic[0] + chunk_size, person.dynamic[1] + chunk_size]

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

def action_in_dynamic_chank(global_map, enemy, activity_list, step, chunk_size):
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


def enemy_emulation_life(global_map, enemy, go_to_print, step, activity_list, chunk_size):
    """
        Обрабатывает жизнь chaotic NPC за кадром, на глобальной карте
        step нужен для запоминания следами деятельности времени в которое появились
    """

    enemy.action_points += 1
    enemy.hunger -= 1
    enemy.thirst -= 1
    enemy.fatigue -= 1
    
    if enemy.action_points >= 5:
        if enemy.type == 'chaotic' and (global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.priority_biom and random.randrange(10)//8 == 1) and len(enemy.waypoints) == 0:
            move_biom_enemy(global_map, enemy)
            enemy.action_points -= 5
            go_to_print.text5 += str(enemy.name_npc) + ' передвигается' + '\n'
        elif enemy.type == 'hunter':
            if random.randrange(10)//8 > 0:
                if len(enemy.waypoints) > 0:
                    move_hunter_enemy(global_map, enemy)
                    enemy.action_points -= 5
                else:
                    move_biom_enemy(global_map, enemy)
                    enemy.action_points -= 5
                go_to_print.text5 += str(enemy.name_npc) + ' передвигается' + '\n'
      
        elif(enemy.thirst < 10 or enemy.hunger < 10) and enemy.reserves > 0:
            enemy.reserves -= 1
            enemy.hunger = 100
            enemy.thirst = 100
            enemy.action_points -= 3
            go_to_print.text5 += str(enemy.name_npc)+ ' достаёт припасы \n'
        elif enemy.fatigue < 10:
            enemy.fatigue = 50
            enemy.action_points -= 20
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

                
def move_biom_enemy(global_map, enemy):
    """
        Обрабатывает перемещение NPC за кадром между биомами
    """

    if global_map[enemy.global_position[0]][enemy.global_position[1]].icon in enemy.priority_biom:
        direction_moved = []
        if global_map[enemy.global_position[0] - 1][enemy.global_position[1]].icon in enemy.priority_biom and enemy.global_position[0] - 1 > 0:
            direction_moved.append([enemy.global_position[0] - 1, enemy.global_position[1]])
        if global_map[enemy.global_position[0] + 1][enemy.global_position[1]].icon in enemy.priority_biom and enemy.global_position[0] + 1 < len(global_map) - 1:
            direction_moved.append([enemy.global_position[0] + 1, enemy.global_position[1]]) 
        if global_map[enemy.global_position[0]][enemy.global_position[1] - 1].icon in enemy.priority_biom and enemy.global_position[1] - 1 > 0:
            direction_moved.append([enemy.global_position[0], enemy.global_position[1] - 1])
        if global_map[enemy.global_position[0]][enemy.global_position[1] + 1].icon in enemy.priority_biom and enemy.global_position[1] + 1 < len(global_map) - 1:
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

def master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step):


    pressed_button = ''
    mode_action, pressed_button = request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction)

    if mode_action == 'move':
        request_move(global_map, person, chunk_size, go_to_print, pressed_button)
        if random.randrange(21)//18 > 0: # Оставление персонажем следов
            activity_list.append(Action_in_map('human_tracks', step, person.global_position, person.dynamic, chunk_size, 'ваши'))
    
    elif mode_action == 'test_move':
        test_request_move(global_map, person, chunk_size, go_to_print, pressed_button, interaction)
        if pressed_button == 'button_add_beacon':
            activity_list.append(Action_in_map('test_beacon', step, person.global_position, person.dynamic, chunk_size, f'\n оставлен вами в локальной точке - {[person.dynamic[0]%chunk_size, person.dynamic[1]%chunk_size]}| динамической - {person.dynamic}| глобальной - {person.global_position}'))

    elif mode_action == 'pointer':    
        request_pointer(person, chunk_size, go_to_print, pressed_button)
    elif mode_action == 'gun':
        request_gun(global_map, person, chunk_size, go_to_print, pressed_button)
    if pressed_button == 'button_map':
        go_to_print.minimap_on = (go_to_print.minimap_on == False)
    request_processing(pressed_button)

    calculation_assemblage_point(global_map, person, chunk_size)
    
    return mode_action


def request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction):
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
    elif key == 'b' or 'и':
        if mode_action == 'test_move':
            return ('test_move', 'button_add_beacon')
        else:
            return (mode_action, 'none')
            
    else:
        return (mode_action, 'none')


def request_move(global_map:list, person, chunk_size:int, go_to_print, pressed_button):
    """
        Меняет динамическое местоположение персонажа
    """
    if pressed_button == 'up':
        
        if person.chunks_use_map[person.dynamic[0] - 1][person.dynamic[1]].icon != '▲':
            if person.dynamic[0] >= chunk_size//2 and person.assemblage_point[0] > 0:
                person.dynamic[0] -= 1
            
    elif pressed_button == 'left':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] - 1].icon != '▲':
            if person.dynamic[1] >= chunk_size//2 and person.assemblage_point[1] > 0:
                person.dynamic[1] -= 1
            
    elif pressed_button == 'down':
        
        if person.chunks_use_map[person.dynamic[0] + 1][person.dynamic[1]].icon != '▲':
            if person.dynamic[0] <= (chunk_size + chunk_size//2) and person.assemblage_point[0] != (len(global_map) - 2):
                person.dynamic[0] += 1
            
    elif pressed_button == 'right':
        
        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] + 1].icon != '▲':
            if person.dynamic[1] <= (chunk_size + chunk_size//2) and person.assemblage_point[1] != (len(global_map) - 2):
                person.dynamic[1] += 1    

def test_request_move(global_map:list, person, chunk_size:int, go_to_print, pressed_button, interaction): #тестовый быстрый режим премещения
    """
        Меняет динамическое местоположение персонажа в тестовом режиме, без ограничений. По полчанка за раз.
        При нажатии на 'p' назначает всем NPC точку следования.
    """
    
    if pressed_button == 'up':
        if person.dynamic[0] >= chunk_size//2 and person.assemblage_point[0] > 0:
            person.dynamic[0] -= chunk_size//2
            
    elif pressed_button == 'left':
        if person.dynamic[1] >= chunk_size//2 and person.assemblage_point[1] > 0:
            person.dynamic[1] -= chunk_size//2
            
    elif pressed_button == 'down': 
        if person.dynamic[0] <= (chunk_size + chunk_size//2) and person.assemblage_point[0] != (len(global_map) - 2):
            person.dynamic[0] += chunk_size//2
            
    elif pressed_button == 'right':
        if person.dynamic[1] <= (chunk_size + chunk_size//2) and person.assemblage_point[1] != (len(global_map) - 2):
            person.dynamic[1] += chunk_size//2

    elif pressed_button == 'button_purpose_task':
        interaction.append(['task_point_all_enemies', person.global_position])
        

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

    person.global_position_calculation(chunk_size) #Рассчитывает глобальное положение и номер чанка через метод
    person.check_encounter() #Рассчитывает порядок и координаты точек проверки

        
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
                print_line += '☺ '
            elif enemy_here != '--':
                print_line += enemy_here
            else:
                print_line += global_map[number_line][biom].icon + ' '
        minimap.append((print_line))
    go_to_print.biom_map = minimap

def print_help(go_to_print):
    help_dict = ['**************************************************',
                 '*                 ОБЫЧНЫЙ РЕЖИМ                  *',
                 '*                                                *',
                 '* wasd - управление персонажем;                  *',
                 '* m - ВКЛ/ВЫКЛ миникарта биомов;                 *',
                 '* k - ВКЛ/ВЫКЛ режим курсора;                    *',
                 '* g - ВКЛ/ВЫКЛ режим прицеливания;               *',
                 '*                                                *',
                 '*                                                *',
                 '*                ТЕСТОВЫЙ РЕЖИМ                  *',
                 '*                                                *',
                 '* t - ВКЛ/ВЫКЛ тестовый режим перемещения;       *',
                 '* p - назначение точки прибытия для hunter NPC;  *',
                 '* m - установка тестового маяка;                 *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '*                                                *',
                 '**************************************************'
                 ]

    go_to_print.biom_map = help_dict


def draw_field_calculations(person:list, views_field_size:int, go_to_print):
    """
        Формирует изображение игрового поля на печать
    """
    
    half_views = (views_field_size//2)
    start_stop = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views),
                  (person.dynamic[0] + half_views + 1),(person.dynamic[1] + half_views + 1)]
    line_views = person.chunks_use_map[start_stop[0]:start_stop[2]]

    go_to_print.point_to_draw = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views)]
    
    draw_field = []
    for line in line_views:
        line_icon = []
        line = line[start_stop[1]:start_stop[3]]
        for tile in line:
            line_icon.append(tile)
        draw_field.append(line_icon)
    return draw_field

def draw_additional_entities(person, chunk_size:int, go_to_print, enemy_list, activity_list):
    """
        Отрисовывает на динамическом чанке дополнительные статические сущности
    """
    
    for activity in activity_list:
        if activity.global_position[0] == person.assemblage_point[0] and activity.global_position[1] == person.assemblage_point[1]:
            person.chunks_use_map[activity.local_position[0]][activity.local_position[1]] = activity
            if activity.icon == 'B':
                print(f'Для тестового маяка сработало условие отображения 1')
            
        elif activity.global_position[0] == person.assemblage_point[0] and activity.global_position[1] == person.assemblage_point[1] + 1:
            person.chunks_use_map[activity.local_position[0]][activity.local_position[1] + chunk_size] = activity
            if activity.icon == 'B':
                print(f'Для тестового маяка сработало условие отображения 2')
            
        elif activity.global_position[0] == person.assemblage_point[0] + 1 and activity.global_position[1] == person.assemblage_point[1]:
            person.chunks_use_map[activity.local_position[0] + chunk_size][activity.local_position[1]] = activity
            if activity.icon == 'B':
                print(f'Для тестового маяка сработало условие отображения 3')
            
        elif activity.global_position[0] == person.assemblage_point[0] + 1 and activity.global_position[1] == person.assemblage_point[1] + 1:
            person.chunks_use_map[activity.local_position[0] + chunk_size][activity.local_position[1] + chunk_size] = activity
            if activity.icon == 'B':
                print(f'Для тестового маяка сработало условие отображения 4')

    for enemy in enemy_list:
        if enemy.global_position in person.check_encounter_position:
            if (0 <= enemy.dynamic_chunk_position[0] < chunk_size * 2) and (0 <= enemy.dynamic_chunk_position[1] < chunk_size * 2 - 2):
                person.chunks_use_map[enemy.dynamic_chunk_position[0]][enemy.dynamic_chunk_position[1]] = enemy
                               

def master_draw(person, chunk_size:int, go_to_print, global_map, mode_action, enemy_list, activity_list):
    """
        Формирует итоговое изображение игрового поля для вывода на экран
    """
    if go_to_print.minimap_on:
        print_minimap(global_map, person, go_to_print, enemy_list)
    else:
        print_help(go_to_print)

    draw_additional_entities(person, chunk_size, go_to_print, enemy_list, activity_list)

    draw_field = draw_field_calculations(person, chunk_size, go_to_print)

    draw_box = []
    pointer_vision = Tile('??')
    for line in range(len(draw_field)):
        print_line = ''
        for tile in range(len(draw_field)):
            if line == chunk_size//2 and tile == chunk_size//2:
                ground = draw_field[line][tile].description
                print_line += '☺'
                if mode_action == 'pointer' and person.pointer == [chunk_size//2, chunk_size//2]:
                    print_line += '<'
                    pointer_vision = draw_field[line][tile]
                elif mode_action == 'gun' and person.gun == [chunk_size//2, chunk_size//2]:
                    print_line += '+'    
                else:
                    print_line += ' '
            elif line == person.pointer[0] and tile == person.pointer[1]:
                print_line += draw_field[line][tile].icon + '<'
                pointer_vision = draw_field[line][tile]
            elif line == person.gun[0] and tile == person.gun[1]:
                print_line += draw_field[line][tile].icon + '+'
            else:
                if len(draw_field[line][tile].icon) == 2:
                    print_line += draw_field[line][tile].icon
                else:
                    print_line += draw_field[line][tile].icon + ' '
        draw_box.append(print_line)
    go_to_print.game_field = draw_box
    go_to_print.text1 = (f"{person.assemblage_point} - Позиция точки сборки | {person.dynamic} - динамическая позиция | под ногами: {ground}")
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

    for line in range(len(go_to_print.biom_map)): #Добавление изображения миникарты или помощи
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

    РАСЧЁТ ПРОПУСКА ХОДА
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
class Interaction:
    
    def __init__(self, perform, whom, type_interaction, description):
        self.perform = perform
        self.whom = whom
        self.type = type_interaction
        self.description = description

class Pass_step:
    """ Содержит информацию о том, сколько шагов должен сделать персонаж пред тем, как ход окончится """
    def __init__(self, creature, step):
        self.creature = creature
        self.step = step

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

def new_step_calculation(enemy_list, person):
    """
        Считает когда начинается новый шаг
    """
    new_step = True
    person.person_pass_step = False
    for enemy in enemy_list:
        if (enemy.on_the_screen and enemy.steps_to_new_step) or (enemy.speed > 1 and enemy.steps_to_new_step == 1 and enemy.dynamic_chunk and enemy.steps_to_new_step):
            new_step = False
            person.person_pass_step = True
    return new_step
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    УПРАВЛЯЮЩИЙ БЛОК
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def game_loop(global_map:list, person:list, chunk_size:int, frame_size:list, enemy_list:list):
    """
        Здесь происходят все игровые события
        
    """
    go_to_print = Interfase([], [], False, '', '', '', '', '', '', '', '', '', '')
    activity_list = []
    step = 0
    print('game_loop запущен')
    global changing_step
    mode_action = 'move'
    
    while game_loop:
        interaction = []
        new_step = new_step_calculation(enemy_list, person)
        if not person.person_pass_step:
            mode_action = master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step)
        #start = time.time() #проверка времени выполнения
        all_pass_step_calculations(person, enemy_list, mode_action, interaction)
        if not person.enemy_pass_step:
            master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size, interaction, new_step)
            step += 1
        #test1 = time.time() #проверка времени выполнения
        master_draw(person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list)
        #test2 = time.time() #проверка времени выполнения
        print_frame(go_to_print, frame_size, activity_list)
        #print('step = ', step)
        #end = time.time() #проверка времени выполнения
        #print(test1 - start, ' - test1 ', test2 - start, ' - test2 ', end - start, ' - end ') #
             

def main():
    """
        Запускает игру
        
    """
    chunk_size = 25         #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    value_region_box = 5    #Количество регионов в квадрате.
    grid = 5                #Должно быть кратно размеру игрового экрана.
    frame_size = [35, 40]   #Размер одного кадра [высота, ширина].

    print('Подождите, генерируется локация для игры')
    #progress_bar(5, 'Запуск игры') 
    global_map = master_generate(value_region_box, chunk_size, grid)
    person = Person([value_region_box//2, value_region_box//2], [chunk_size//2, chunk_size//2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
    calculation_assemblage_point(global_map, person, chunk_size)
    enemy_list = [Horseman([len(global_map)//2, len(global_map)//2] , 5), Horseman([len(global_map)//3, len(global_map)//3] , 5),
                  Riffleman([len(global_map)//4, len(global_map)//4] , 2), Coyot([len(global_map)//5, len(global_map)//5] , 0)]
    game_loop(global_map, person, chunk_size, frame_size, enemy_list)
    
    print('Игра окончена!')

main()
    

