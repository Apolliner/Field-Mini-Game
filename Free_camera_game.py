import os
import copy
import random
import string
import keyboard
import sys

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ СО СВОБОДНОЙ КАМЕРОЙ

    РЕАЛИЗОВАТЬ:
    1)Генерацию с чанками #РЕАЛИЗОВАНО
    2)Отображение минимального набора чанков и их выгрузку при удалении камеры - сделать это через срезы и готовый алгоритм распаковки сырой карты
    с регионами в готовую единую карту #РЕАЛИЗОВАНО
    3)Объединить версию со свободной камерой и версию с регионами
"""


class Position:
    """ Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного участка карты и координаты используемых чанков """
    def __init__(self, assemblage_point:list, dynamic:list, chank:list):
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chank = chank


def global_map_generation(game_field_size:int, value_region_box:int):
    """
        Старый генератор. Генерирует локации слева->направо, сверху->вниз
    """
    global_map = []
    for i in range((value_region_box * 3)):
        global_map.append([create_game_field_fluctuations(game_field_size) for x in range((value_region_box * 3))])
    return global_map


def create_game_field_fluctuations(game_field_size):
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['▲', ',', ' ', '.', '.', '.', '.']) for x in range(game_field_size)])
    return game_field

def draw_person(position):
    """
        Рисует персонажа на карте
    """
    position.chank[position.dynamic[0]][position.dynamic[1]] = '☺'

def draw_field_calculations(position:list, views_field_size:int):
    """
        Формирует итоговое изображение на печать
    """
    half_views = (views_field_size//2)
    start_stop = [(position.dynamic[0] - half_views), (position.dynamic[1] - half_views), (position.dynamic[0] + half_views + 1),(position.dynamic[1] + half_views + 1)]
    line_views = position.chank[start_stop[0]:start_stop[2]]
    
    draw_field = []
    for line in line_views:
        line = line[start_stop[1]:start_stop[3]]
        draw_field.append(line)
    return draw_field

def gluing_location(raw_gluing_map, grid, count_block): #АКТУАЛЬНЫЙ
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

        position.chank = gluing_location(assemblage_chank, 2, chank_size)
        

def request_move_person(global_map:list, position, chank_size:int):
    """
        Спрашивает ввод, меняет динамическое местоположение персонажа

    """
    keyboard_loop = True
    while keyboard_loop:
        move = keyboard.read_key()
        if move == 'w' or move == 'up' or move == 'ц':
            if position.chank[position.dynamic[0] - 1][position.dynamic[1]] == '▲':
                pass
            else:
                position.dynamic[0] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 'a' or move == 'left' or move == 'ф':
            if position.chank[position.dynamic[0]][position.dynamic[1] - 1] == '▲':
                pass
            else:
                position.dynamic[1] -= 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 's' or move == 'down' or move == 'ы':
            if position.chank[position.dynamic[0] + 1][position.dynamic[1]] == '▲':
                pass
            else:
                position.dynamic[0] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
            
        elif move == 'd' or move == 'right' or move == 'в':
            if position.chank[position.dynamic[0]][position.dynamic[1] + 1] == '▲':
                pass
            else:
                position.dynamic[1] += 1
                calculation_assemblage_point(global_map, position, chank_size, 2)
                keyboard_loop = False
        elif move == 'space':
            keyboard_loop = False
            
        else: pass


def test_print_chank(position):
    draw_box = ''
    for line in position.chank:
        print_line = ''
        for tile in line:
            print_line += tile + ' '
        draw_box += print_line + '\n'

    print(draw_box)

def print_game_field(position, views_field_size:int):
    """
        Выводит изображение игрового поля на экран
    """

    draw_field = draw_field_calculations(copy.deepcopy(position), views_field_size)
    draw_box = ''
    for line in range(len(draw_field)):
        print_line = ''
        for tile in range(len(draw_field)):
            if line == views_field_size//2 and tile == views_field_size//2:
                print_line += '☺' + ' '
            else:
                print_line += draw_field[line][tile] + ' '
        draw_box += print_line + '\n'
    os.system('cls' if os.name == 'nt' else 'clear')
    print(draw_box)
    print(position.assemblage_point, ' - Позиция точки сборки | ', position.dynamic, ' - динамическая позиция ')




def game_loop(global_map:list, position:list, chank_size:int):
    """
        Здесь происходят все игровые события
        
    """
    
    while game_loop :
        request_move_person(global_map, position, chank_size)
        print_game_field(position, chank_size)
        
        

def main():
    """
        Запускает игру
        
    """
    chank_size = 20 #Определяет размер одного игрового поля и окна просмотра
    value_region_box = 20 #Количество регионов в квадрате

    global_map = global_map_generation(chank_size, value_region_box)
    
    position = Position([value_region_box//2, value_region_box//2], [chank_size//2, chank_size//2], [])
    calculation_assemblage_point(global_map, position, chank_size, 3)
    
    game_loop(global_map, position, chank_size)
    
    print('Игра окончена!')

main()
    
