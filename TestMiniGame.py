import os
import copy



def print_game_field(game_field_used:list, position:list):
    """
        Выводит изображение игрового поля на экран
    """
    draw_person(game_field_used, position)
    for line in game_field_used:
        for tile in line:
            print(tile, end='|')
        print('')

def draw_person(game_field_and_person, position):
    """
        Рисует персонажа на карте
    """
    game_field_and_person[position[0]][position[1]] = '@'

def calculation_move_person(position:list, game_field_size:int):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [y, x]
    """
    move = input('"W" - Вперёд, "A" - Влево, "S" - Назад, "D" - Вправо ')
    if move == 'w':
        if position[0] == 0:
            return position
        else:
            position[0] -= 1
            return position
    elif move == 'a':
        if position[1] == 0:
            return position
        else:
            position[1] -= 1
            return position
    elif move == 's':
        if position[0] == (game_field_size - 1):
            return position
        else:
            position[0] += 1
            return position
    elif move == 'd':
         if position[1] == (game_field_size - 1):
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
        position = calculation_move_person(position, game_field_size)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_game_field(game_field_used, position)

        


def main():
    """
        Запускает игру

        start_position = [y, x]
        
    """
    game_field = []
    game_field_size = 10
    for i in range(game_field_size):
        game_field.append(['_']*game_field_size)
    
    start_position = [game_field_size//2, game_field_size//2]
    input('для запуска игры нажмите Enter')
    
    game_loop(game_field, start_position, game_field_size)
    print('Игра окончена!')

main()
    
