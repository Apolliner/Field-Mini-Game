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
        game_field.append(['.']*game_field_size)
    return game_field

def create_game_field_fluctuations(game_field_size):
    """
        Создаёт случайное игровое поле
    """
    game_field = []
    for i in range(game_field_size):
        game_field.append([random.choice(['█', '.', '.', '.', '.', '.', '.']) for x in range(game_field_size)])
    return game_field

def live_one_small_bird(bird:list, game_field_used:list):
    """
        обрабатывает жизнь одной маленькой птички
    """

    bird[0] += random.randrange(1, -2, -1)
    if bird[0] == -1:
        bird[0] +=1
    elif bird[0] == (len(game_field_used) - 1):
        bird[0] -=1

    bird[1] += random.randrange(1, -2, -1)
    if bird[1] == -1:
        bird[1] +=1
    elif bird[1] == (len(game_field_used) - 1):
        bird[1] -=1
    

def draw_birds(game_field_used:list, bird_quantity_and_position:list):
    """
        Рисует всех птиц
    """
    for bird in bird_quantity_and_position:
        live_one_small_bird(bird, game_field_used)
        game_field_used[bird[0]][bird[1]] = 'v'
        

def print_game_field(game_field_used:list, position:list, bird_quantity_and_position:list):
    """
        Выводит изображение игрового поля на экран
    """

    draw_person(game_field_used, position)
    draw_birds(game_field_used, bird_quantity_and_position)
    for line in game_field_used:
        for tile in line:
            print(tile, end=' ')
        print('')

def draw_person(game_field_and_person, position):
    """
        Рисует персонажа на карте
    """
    game_field_and_person[position[0]][position[1]] = '@'


def calculation_move_person(position:list, game_field_used:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [y, x]
    """
    print('"w" - Вперёд, "a" - Влево, "s" - Назад, "d" - Вправо ')
    move = keyboard.read_key()
    if move == 'w' or move == 'up':
        if position[0] == 0 or game_field_used[position[0] - 1][position[1]] == '█':
            return position
        else:
            position[0] -= 1
            return position
    elif move == 'a' or move == 'left':
        if position[1] == 0 or game_field_used[position[0]][position[1] - 1] == '█':
            return position
        else:
            position[1] -= 1
            return position
    elif move == 's' or move == 'down':
        if position[0] == (len(game_field_used[0]) - 1) or game_field_used[position[0] + 1][position[1]] == '█':
            return position
        else:
            position[0] += 1
            return position
    elif move == 'd' or move == 'right':
         if position[1] == (len(game_field_used[0]) - 1) or game_field_used[position[0]][position[1] + 1] == '█':
            return position
         else:
            position[1] += 1
            return position
    else:
        return position
    

def game_loop(game_field:list, start_position:list, bird_quantity_and_position:list):
    """
        Здесь происходят все игровые события
    """
    position = list(start_position)
    while game_loop :
        game_field_used = copy.deepcopy(game_field)
        position = calculation_move_person(position, game_field_used)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position, bird_quantity_and_position)

        


def main():
    """
        Запускает игру

        start_position = [y, x]
        
    """
    game_field_size = 30 #Определяет размер игрового поля

    print('Выберите тип поля: 0 - пустой, 1 - случайный')
    type_game_field = keyboard.read_key()
    
    if type_game_field == '0':
        game_field = create_game_field_empty(game_field_size)
    else:
        game_field = create_game_field_fluctuations(game_field_size)
    
    bird_quantity_and_position = []
    for bird in range(random.randrange(1, game_field_size//2)): #Количество птиц
        bird_quantity_and_position.append([random.randrange(game_field_size) for x in range(2)])
    
    start_position = [game_field_size//2, game_field_size//2]
    
    game_loop(game_field, start_position, bird_quantity_and_position)
    print('Игра окончена!')

main()
    
