import os
import copy
import random
import string
import keyboard

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ ГЛОБАЛЬНОЙ КАРТЫ БЕЗ ВСЕГО ОСТАЛЬНОГО
"""

def region_generation(value_region_box):
    """
        Генерирует карту регионов
    """
    region_map = []
    for i in range(value_region_box):
        region_map.append([random.randrange(10) for x in range(value_region_box)])
    print(region_map)
    return region_map


def global_map_generation(game_field_size:int, value_region_box:int):
    """
        Основываясь на карте регионов, генерирует все области слева->направо, сверху->вниз
    """
    
    #region_map = region_generation(value_region_box)

    global_map = []
    for i in range((value_region_box * 3)):
        global_map.append([create_game_field_fluctuations(game_field_size) for x in range((value_region_box * 3))])
    print(len(global_map))
    return global_map
    

def create_game_field_empty(game_field_size):
    """
        Создаёт пустое игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append(['.']*game_field_size)
    game_field_and_temperature = [30.0]
    game_field_and_temperature.append(game_field)
    return game_field_and_temperature

def create_game_field_fluctuations(game_field_size):
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['▲', ',', ' ', '.', '.', '.', '.']) for x in range(game_field_size)])
    game_field_and_temperature = [random.randrange(20.0, 45.0)]
    game_field_and_temperature.append(game_field)
    return game_field_and_temperature



def print_game_field(game_field_used:list, position:list):
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
    return global_map[position[0][0]][position[0][1]][1]

def game_loop(global_map:list, start_position:list):
    """
        Здесь происходят все игровые события

        all_temperature[global_temperature, person_temperature]
        
        position = [global_position[y, x], field_position[y, x]]

        global_map[line_map[dot_map[temperature_field, game_field[...]]...]...]
        
    """


    position = [[0, 0]]
    position.append(list(start_position))
    game_field_used = copy.deepcopy(calculate_draw_position(global_map, position))
    
    while game_loop :
        calculation_move_person(position, game_field_used)
        game_field_used = copy.deepcopy(calculate_draw_position(global_map, position))
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position[1])
        

        


def main():
    """
        Запускает игру

        start_position = [y, x]

        global_map[line_map[dot_map[temperature_field, game_field[...]]...]...]
        
    """
    game_field_size = 10 #Определяет размер игрового поля
    value_region_box = 3 #Количество регионов в квадрате

    global_map = global_map_generation(game_field_size, value_region_box)

    
    start_position = [game_field_size//2, game_field_size//2]
    
    game_loop(global_map, start_position)
    print('Игра окончена!')

main()
    
