import os
import copy
import random
import string
import keyboard

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ ГЛОБАЛЬНОЙ КАРТЫ БЕЗ ВСЕГО ОСТАЛЬНОГО
"""


class Description_location:
    """ Содержит информацию для генератора локаций """
    def __init__(self, description:list):
        self.name = description[0]
        self.temperature = description[1]
        self.tileset = description[2]
        self.icon = description[3]


class Location:
    """ Содержит описание локации """
    def __init__(self, name:str, temperature:float, chank:list, icon:str):
        self.name = name
        self.temperature = temperature
        self.chank = chank
        self.icon = icon


def TEST_print_global_map_biome(global_map):
    """
        Печатает упрощенную схему глобальной карты по биомам
    """
    print( )
    for number_line in range(len(global_map)):
        for biom in global_map[number_line]:
            print(biom.icon, end=' ')
        print('')
    print(' ')


def selecting_generator(seed):
    """
        Содержит и выдаёт значения семян генерации.
    """
    seed_dict = {
                    0: ['desert',             [40.0,60.0], ['j', 'j', 'j', '.', '.', '.', '.', '.', '.', '.'], 'j'],
                    1: ['semidesert',         [35.0,50.0], ['▲', ',', ',', 'ì', 'o', '.', '.', '.', '.', 'j'], '.'],
                    2: ['cliff semidesert',   [35.0,50.0], ['▲', '▲', '▲', '▲', ',', 'o', 'ì', '.', '.', '.'], 'A'],
                    3: ['saline land',        [40.0,50.0], [';', ';', ';', ';', ';', ':', ':', ':', ':', ':'], ';'],
                    4: ['dried field',        [30.0,40.0], ['u', '„', '„', 'o', ',', ',', ',', ',', ',', ','], ','],
                    5: ['field',              [20.0,35.0], ['ü', 'u', '„', '„', '„', '„', 'o', ',', ',', ','], '„'],
                    6: ['foothills',          [20.0,35.0], ['▲', '▲', '▲', '▲', '▲', '„', 'o', 'o', ',', ','], '▲'],
                    7: ['oasis',              [15.0,30.0], ['~', '~', 'F', 'F', 'P', '„', '„', '„', '„', ','], 'F'],
                    8: ['salty lake',         [25.0,40.0], ['~', '~', '~', '~', '~', '~', '~', '„', ',', '.'], '~'],
                    9: ['swamp',              [15.0,30.0], ['ü', 'ü', 'ü', 'u', 'u', '~', '~', '~', '~', ','], 'ü'],
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
        one_description[3] = random.choice([one_description[3], two_description[3]])


def master_generate(value_region_box:int, game_field_size:int):
    """
        Генерирует глобальную карту, ориентируясь на карту регионов.
    """
    region_map = region_generate(value_region_box)
    
    raw_global_map = []
    
     #Сначала создаются регионы

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
                            
                    description_for_generator = selecting_generator(region_map[number_line][number_seed])
                    description_seed_merge(description_for_generator, top_down_description)
                    description_seed_merge(description_for_generator, left_right_description)
                    location_line.append(location_generate(description_for_generator, game_field_size))
                region.append(location_line)
            region_line.append(region)
        raw_global_map.append(region_line)

    global_map = gluing_global_map(raw_global_map, value_region_box)
        
    return global_map

def gluing_global_map(raw_global_map, value_region_box):
    """
        Склеивает глобальную карту из регионов.
    """
    global_map = []
    for empry_line in range(value_region_box * value_region_box):
        global_map.append([])
    
    count_location = 0
    for number_region_line in range(value_region_box):
        for number_region in range(value_region_box):
            for number_location_line in range(value_region_box):
                for number_location in range(value_region_box):
                    gluing_index = (number_region_line + number_location_line + ((count_location//(value_region_box**3))*(value_region_box-1))) #определяет индекс
                    global_map[gluing_index].append(raw_global_map[number_region_line][number_region][number_location_line][number_location])
                    count_location += 1        
    return global_map

def location_generate(description, game_field_size):
    """
        Создаёт локацию по описанию и размеру
    """
    ready_location = Location(description[0], 35, [], '')

    for i in range(game_field_size):
        ready_location.chank.append([random.choice(description[2]) for x in range(game_field_size)])
    ready_location.temperature = [random.randrange(description[1][0], description[1][1])]
    ready_location.icon = description[3]

    return ready_location


def region_generate(size_region_box):
    """
        Генерирует карту регионов
    """
    region_map = []
    for i in range(size_region_box):
        region_map.append([random.randrange(10) for x in range(size_region_box)])
    print(region_map)
    return region_map



def create_game_field_empty(game_field_size): #Функция устарела
    """
        Создаёт пустое игровое поле 
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append(['.']*game_field_size)
    game_field_and_temperature = [30.0]
    game_field_and_temperature.append(game_field)
    return game_field_and_temperature

def create_game_field_fluctuations(game_field_size): #Функция устарела
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['▲', ',', ' ', '.', '.', '.', '.']) for x in range(game_field_size)])
    game_field_and_temperature = [random.randrange(20.0, 45.0)]
    game_field_and_temperature.append(game_field)
    return game_field_and_temperature



def print_game_field(game_field_used:list, position:list): #Требует обновления
    """
        Выводит изображение игрового поля на экран, прописывает описание неба и земли,
        температуру среды и температуру персонажа.

        all_temperature[global_temperature, person_temperature]
    """

    draw_person(game_field_used, position)
    for line in game_field_used:
        for tile in line:
            print(tile, end=' ')
        print('')

def draw_person(game_field_and_person:list, position:list):
    """
        Рисует персонажа на карте и определяет описание земли под ногами
    """
    game_field_and_person[position[0]][position[1]] = '☺'


def calculation_move_person(position:list, game_field_used:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [global_position[y, x], field_position[y, x]]
    """
    displacement_occurred = False
    print('Ваша позиция в мире и вообще: ', position)
    print('"w" - Вперёд, "a" - Влево, "s" - Назад, "d" - Вправо ')
    move = keyboard.read_key()
    if move == 'w' or move == 'up' or move == 'ц':
        if position[1][0] == 0:
            position[1][0] = (len(game_field_used[0]) - 1)
            position[0][0] -= 1
            displacement_occurred = True
        elif game_field_used[position[1][0] - 1][position[1][1]] == '▲':
            pass
        else:
            position[1][0] -= 1
    elif move == 'a' or move == 'left' or move == 'ф':
        if position[1][1] == 0:
            position[1][1] = (len(game_field_used[0]) - 1)
            position[0][1] -= 1
            displacement_occurred = True
        elif game_field_used[position[1][0]][position[1][1] - 1] == '▲':
            pass
        else:
            position[1][1] -= 1
    elif move == 's' or move == 'down' or move == 'ы':
        if position[1][0] == (len(game_field_used[0]) - 1):
            position[1][0] = 0
            position[0][0] += 1
            displacement_occurred = True
        elif game_field_used[position[1][0] + 1][position[1][1]] == '▲':
            pass
        else:
            position[1][0] += 1
    elif move == 'd' or move == 'right' or move == 'в':
        if position[1][1] == (len(game_field_used[0]) - 1):
            position[1][1] = 0
            position[0][1] += 1
            displacement_occurred = True
        elif game_field_used[position[1][0]][position[1][1] + 1] == '▲':
            pass
        else:
            position[1][1] += 1
    else: pass


def calculate_draw_position(global_map:list, position:list):
    """
        Рассчитывает какую локацию использовать для отображения
    """
    return global_map[position[0][0]][position[0][1]]

def game_loop(global_map:list, start_position:list):
    """
        Здесь происходят все игровые события

        all_temperature[global_temperature, person_temperature]
        
        position = [global_position[y, x], field_position[y, x]]

        global_map[location_line[Location(name:str, temperature:float, chank:list)...]...]
        
    """
    position = [[0, 0]]
    position.append(list(start_position))
    game_field_used = copy.deepcopy(calculate_draw_position(global_map, position).chank)
    
    while game_loop :
        calculation_move_person(position, game_field_used)
        game_field_used = copy.deepcopy(calculate_draw_position(global_map, position).chank)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position[1])
        print()
        print(calculate_draw_position(global_map, position).name)
        TEST_print_global_map_biome(global_map)
        


def main():
    """
        Запускает игру

        start_position = [y, x]

        global_map[line_map[dot_map[temperature_field, game_field[...]]...]...]
        
    """
    game_field_size = 20 #Определяет размер игрового поля
    value_region_box = 4 #Количество регионов в квадрате 

    global_map = master_generate(value_region_box, game_field_size)

    start_position = [game_field_size//2, game_field_size//2]
    
    game_loop(global_map, start_position)
    print('Игра окончена!')

main()
    
