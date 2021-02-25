import os
import copy
import random
import string
import keyboard



def create_game_field_empty(game_field_size):
    """
        Создаёт пустое игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append(['_']*game_field_size)
    return game_field

def create_game_field_fluctuations(game_field_size):
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['█', '.', '.', '.', '.', '.', '.']) for x in range(game_field_size)])
    return game_field


def print_game_field(game_field_used:list, position:list):
    """
        Выводит изображение игрового поля на экран
    """
    draw_person(game_field_used, position)
    for line in game_field_used:
        for tile in line:
            print(tile, end=' ')
        print('')

def draw_person(game_field_and_person, position):
    """
        Рисует персонажа на карте
    """
    game_field_and_person[position[0]][position[1]] = '@'

def calculation_move_person(position:list, game_field_size:int, game_field_used:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [y, x]
    """
    print('"w" - Вперёд, "a" - Влево, "s" - Назад, "d" - Вправо ')
    move = keyboard.read_key()
    if move == 'w':
        if position[0] == 0 or game_field_used[position[0] - 1][position[1]] == '█':
            return position
        else:
            position[0] -= 1
            return position
    elif move == 'a':
        if position[1] == 0 or game_field_used[position[0]][position[1] - 1] == '█':
            return position
        else:
            position[1] -= 1
            return position
    elif move == 's':
        if position[0] == (game_field_size - 1) or game_field_used[position[0] + 1][position[1]] == '█':
            return position
        else:
            position[0] += 1
            return position
    elif move == 'd':
         if position[1] == (game_field_size - 1) or game_field_used[position[0]][position[1] + 1] == '█':
            return position
         else:
            position[1] += 1
            return position
    else:
        return position
    

def game_loop(game_field:list, start_position:list, game_field_size:int):
    """
        Здесь происходят все игровые события
    """
    position = list(start_position)
    while game_loop :
        game_field_used = copy.deepcopy(game_field)
        position = calculation_move_person(position, game_field_size, game_field_used)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position)

        


def main():
    """
        Запускает игру

        start_position = [y, x]
        
    """
    game_field_size = 10
    type_game_field = input('Выберите тип поля: 0 - пустой, 1 - случайный')
    if type_game_field == 0:
        game_field = create_game_field_empty(game_field_size)
    else:
        game_field = create_game_field_fluctuations(game_field_size)
    

    start_position = [game_field_size//2, game_field_size//2]
    
    game_loop(game_field, start_position, game_field_size)
    print('Игра окончена!')

main()
    
