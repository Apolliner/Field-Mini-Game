import os
import copy
import random
import string
import keyboard

garbage = ['░', '▒', '▓', '█', '☺']

"""
    ИЗВЕСТНЫЕ ПРОБЛЕМЫ:
    1) Птицы иногда рождаются за пределами карты и крашат игру при запуске; #ИСПРАВЛЕНО

    РЕАЛИЗОВАТЬ:
    1) Температуру на карте;
    2) Температуру и её изменение у персонажа;
    3) Генерацию глобальной карты;
    4) Переход между локациями;
    5) Генерацию разных локаций;

    ТЕМАТИКА:
    1) Пустыня, пустынная область;
    2) Жара;
"""



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


def global_temperature_change(global_temperature:float, local_temperature:float):
    """
        Cо случайным шансом изменяет глобальную температуру, постепенно приравнивая её к температуре региона.
    """
    if random.randrange(20)//10 >= 1:
        if global_temperature <= local_temperature:
            global_temperature += ( -0.3 + random.random())
        else:
            global_temperature -= ( -0.3 + random.random())
    return global_temperature
    

def person_temperature_change(all_temperature:list[float, float],  ground_descr:str, sky_descr:str):
    """
        Изменяет температуру персонажа в зависимости от глобальной температуры и нахождении на/под тайлами.

        all_temperature[global_temperature, person_temperature]
    """
    change_temperarure_dict = {
        'Под ногами горячий песок': 0.1,
        'Под ногами верхушка скалы': 0.05,
        'Осторожно! Под ногами нет ничего!': -0.1,
        'Под ногами жухлая трава': 0.01,
        'Под ногами нечто непонятное': 0,
        'Над головой палящее солнце': 0.1,
        'На голове тень от маленькой птички': -0.3,
        'На голове тень от облака': -0.7,
        }
    
    if all_temperature[1] <= all_temperature[0]:
        all_temperature[1] += float(random.randrange(0, 3)) / 10
    else:
        all_temperature[1] -= float(random.randrange(0, 3)) / 10
    all_temperature[1] += change_temperarure_dict[ground_descr] #Считаем от описания земли
    all_temperature[1] += change_temperarure_dict[sky_descr] #Считаем от описания неба
    return all_temperature[1]



def beget_cloud(game_field_used:list, clouds_position:list):
    """
        Рожает облако
    """
    clouds_position.append([random.randrange(len(game_field_used[0])), 0])


def move_clouds(clouds_position:list, game_field_used:list):
    """
        Двигает все облака
    """
    departing_clouds = []

    for number_cloud in range(len(clouds_position)):
        if clouds_position[number_cloud][1] == (len(game_field_used[0]) - 1):
            departing_clouds.insert(0, number_cloud)
        else:
            clouds_position[number_cloud][1] += 1

    for depart in departing_clouds:
        del clouds_position[depart]


def ground_description(game_field_used:list, position:list):
    """
        Рассказывает о том, что находится под ногами персонажа
    """
    ground_dict = {
        '.': 'Под ногами горячий песок',
        '▲': 'Под ногами верхушка скалы',
        ' ': 'Осторожно! Под ногами нет ничего!',
        ',': 'Под ногами жухлая трава',
        }

    ground = game_field_used[position[0]][position[1]]
    if ground in ground_dict:
        return ground_dict[ground]
    return 'Под ногами нечто непонятное'

def sky_description(game_field_used:list, position:list):
    """
        Рассказывает о том, что находится в небе над персонажем
    """
    sky_dict = {
        'v': 'На голове тень от маленькой птички',
        'O': 'На голове тень от облака',
        }

    sky = game_field_used[position[0]][position[1]]
    if sky in sky_dict:
        return sky_dict[sky]
    return 'Над головой палящее солнце'
        

def live_one_small_bird(bird:list, game_field_used:list):
    """
        обрабатывает жизнь одной маленькой птички
    """

    bird[0] += random.randrange(-1, 2)
    if bird[0] == -1:
        bird[0] +=1
    elif bird[0] == (len(game_field_used) - 1):
        bird[0] -=1

    bird[1] += random.randrange(-1, 2)
    if bird[1] == -1:
        bird[1] +=1
    elif bird[1] == (len(game_field_used) - 1):
        bird[1] -=1
    

def draw_birds_and_clouds(game_field_used:list, bird_quantity_and_position:list, clouds_position:list):
    """
        Рисует всех птиц и все облака. Облака летят выше птиц.
    """
    for bird in bird_quantity_and_position:
        live_one_small_bird(bird, game_field_used)
        game_field_used[bird[0]][bird[1]] = 'v'

    for cloud in clouds_position:
        game_field_used[cloud[0]][cloud[1]] = 'O'
        

def print_game_field(game_field_used:list, position:list, bird_quantity_and_position:list,
                     clouds_position:list, all_temperature:list):
    """
        Выводит изображение игрового поля на экран, прописывает описание неба и земли,
        температуру среды и температуру персонажа.

        all_temperature[global_temperature, person_temperature]
    """
    ground_descr = ground_description(game_field_used, position)
    draw_person(game_field_used, position, ground_descr)
    draw_birds_and_clouds(game_field_used, bird_quantity_and_position, clouds_position)
    sky_descr = sky_description(game_field_used, position)
    person_temperature = person_temperature_change(all_temperature, ground_descr, sky_descr)
    for line in game_field_used:
        for tile in line:
            print(tile, end=' ')
        print('')
    print(ground_descr)
    print(sky_descr)
    print('Температура', '%.1f' % all_temperature[0], 'градусов')
    if person_temperature > 15 and person_temperature < 40:
        print('Температура персонажа', '%.1f' % person_temperature, 'градусов. Всё в порядке!')
    elif person_temperature < 15.0:
        print('Температура персонажа', '%.1f' % person_temperature, 'градусов. Холодно!')
    else:
        print('Температура персонажа', '%.1f' % person_temperature, 'градусов. Слишком жарко!')

def draw_person(game_field_and_person:list, position:list, ground_descr:list):
    """
        Рисует персонажа на карте и определяет описание земли под ногами
    """
    game_field_and_person[position[0]][position[1]] = '☺'


def calculation_move_person(position:list, game_field_used:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа

        position = [y, x]
    """
    print('"w" - Вперёд, "a" - Влево, "s" - Назад, "d" - Вправо ')
    move = keyboard.read_key()
    if move == 'w' or move == 'up' or move == 'ц':
        if position[0] == 0 or game_field_used[position[0] - 1][position[1]] == '▲':
            return position
        else:
            position[0] -= 1
            return position
    elif move == 'a' or move == 'left' or move == 'ф':
        if position[1] == 0 or game_field_used[position[0]][position[1] - 1] == '▲':
            return position
        else:
            position[1] -= 1
            return position
    elif move == 's' or move == 'down' or move == 'ы':
        if position[0] == (len(game_field_used[0]) - 1) or game_field_used[position[0] + 1][position[1]] == '▲':
            return position
        else:
            position[0] += 1
            return position
    elif move == 'd' or move == 'right' or move == 'в':
         if position[1] == (len(game_field_used[0]) - 1) or game_field_used[position[0]][position[1] + 1] == '▲':
            return position
         else:
            position[1] += 1
            return position
    else:
        return position
    

def game_loop(game_field_and_temperature:list, start_position:list, bird_quantity_and_position:list):
    """
        Здесь происходят все игровые события

        all_temperature[global_temperature, person_temperature]
    """
    position = list(start_position)
    clouds_position = []
    all_temperature = [35.0, 36.6]
    local_temperature = (game_field_and_temperature[0])
    while game_loop :
        game_field_used = copy.deepcopy(game_field_and_temperature[1])
        position = calculation_move_person(position, game_field_used)
        os.system('cls' if os.name == 'nt' else 'clear')
        move_clouds(clouds_position, game_field_used)
        all_temperature[0] = global_temperature_change(all_temperature[0], local_temperature)
        if (random.randrange(11)+ (len(game_field_used[0]) - 1)//10)//10 >= 1:
            beget_cloud(game_field_used, clouds_position)
        print_game_field(game_field_used, position, bird_quantity_and_position, clouds_position, all_temperature)
        

        


def main():
    """
        Запускает игру

        start_position = [y, x]
        
    """
    game_field_size = 20 #Определяет размер игрового поля

    print('Выберите тип поля: 0 - пустой, 1 - случайный')
    type_game_field = keyboard.read_key()
    
    if type_game_field == '0':
        game_field_and_temperature = create_game_field_empty(game_field_size)
    else:
        game_field_and_temperature = create_game_field_fluctuations(game_field_size)
    
    bird_quantity_and_position = []
    for bird in range(random.randrange(1, game_field_size//2)): #Количество птиц
        bird_quantity_and_position.append([random.randrange(game_field_size - 1) for x in range(2)])
    
    start_position = [game_field_size//2, game_field_size//2]
    
    game_loop(game_field_and_temperature, start_position, bird_quantity_and_position)
    print('Игра окончена!')

main()
    
