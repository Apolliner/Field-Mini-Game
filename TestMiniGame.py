import os
import copy


def draw_person(game_field_and_person, position):
    """
        Рисует персонажа на карте
    """
    game_field_and_person[position[0]][position[1]] = '@'

def calculation_move_person(position:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [x, y]
    """
    move = input('"W" - Вперёд, "A" - Влево, "S" - Назад, "D" - Вправо ')
    if move == 'w':
        position[0] -= 1
        return position
    elif move == 'a':
        position[1] -= 1
        return position
    elif move == 's':
        position[0] += 1
        return position
    elif move == 'd':
        position[1] += 1
        return position
    else:
        return position


def print_game_field(game_field_used:list, position:list):
    """
        Выводит изображение игрового поля на экран
    """
    draw_person(game_field_used, position)
    for line in game_field_used:
        for tile in line:
            print(tile, end='')
        print('')
    

def game_loop(game_field:list, start_position:list):
    """
        Здесь происходят все игровые события
    """
    position = list(start_position)
    while game_loop :
        game_field_used = copy.deepcopy(game_field)
        position = calculation_move_person(position)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position)

        


def main():
    """
        Запускает игру

        start_position = [x, y]
        
    """
    game_field = []
    for i in range(10):
        game_field.append(['.']*10)
    
    start_position = [4, 4]
    input('для запуска игры нажмите Enter')
    
    game_loop(game_field, start_position)
    print('Игра окончена!')

main()
    
