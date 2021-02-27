import os
import copy
import random
import string
import keyboard

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ВЕРСИЯ СО СВОБОДНОЙ КАМЕРОЙ
"""

def create_game_field_fluctuations(game_field_size):
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['▲', ',', ' ', '.', '.', '.', '.']) for x in range(game_field_size)])
    return game_field

def draw_person(game_field_used:list, position:list):
    """
        Рисует персонажа на карте
    """
    game_field_used[position[0]][position[1]] = '☺'

def draw_field_calculations(game_field_used:list, position:list, views_field_size:int):
    """
        Формирует итоговое изображение на печать
    """
    half_views = (views_field_size//2)
    start_stop = [(position[0] - half_views), (position[1] - half_views), (position[0] + half_views + 1),(position[1] + half_views + 1)]
    line_views = game_field_used[start_stop[0]:start_stop[2]]
    
    draw_field = []
    for line in line_views:
        line = line[start_stop[1]:start_stop[3]]
        draw_field.append(line)
    return draw_field


def calculation_move_person(game_field_used:list, position:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [y, x]
    """

    move = keyboard.read_key()
    if move == 'w' or move == 'up' or move == 'ц':
        if game_field_used[position[0] - 1][position[1]] == '▲':
            pass
        else:
            position[0] -= 1
    elif move == 'a' or move == 'left' or move == 'ф':
        if game_field_used[position[0]][position[1] - 1] == '▲':
            pass
        else:
            position[1] -= 1
    elif move == 's' or move == 'down' or move == 'ы':
        if game_field_used[position[0] + 1][position[1]] == '▲':
            pass
        else:
            position[0] += 1
    elif move == 'd' or move == 'right' or move == 'в':
        if game_field_used[position[0]][position[1] + 1] == '▲':
            pass
        else:
            position[1] += 1
    else: pass



def print_game_field(game_field_used:list, position:list, views_field_size:int):
    """
        Выводит изображение игрового поля на экран
    """
    draw_person(game_field_used, position)
    draw_field = draw_field_calculations(game_field_used, position, views_field_size)
    for line in draw_field:
        for tile in line:
            print(tile, end=' ')
        print('')



def game_loop(game_field:list, start_position:list, views_field_size:int):
    """
        Здесь происходят все игровые события
        
    """
    
    position = list(start_position)
    game_field_used = copy.deepcopy(game_field)
    
    while game_loop :
        game_field_used = copy.deepcopy(game_field)
        print_game_field(game_field_used, position, views_field_size)
        calculation_move_person(game_field_used, position)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        

        


def main():
    """
        Запускает игру

        start_position = [y, x]
        
    """
    game_field_size = 100 #Определяет размер игрового поля
    views_field_size = 20 #Определяет размер окна просмотра

    game_field = create_game_field_fluctuations(game_field_size)
    
    start_position = [game_field_size//2, game_field_size//2]

    game_loop(game_field, start_position, views_field_size)
    print('Игра окончена!')

main()
    
