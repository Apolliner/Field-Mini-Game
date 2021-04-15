import random
import time


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    НОВЫЙ ГЕНЕРАТОР ИГРОВОЙ КАРТЫ
    
    На выходе выдаёт класс Location
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

""" 

def timeit(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time() - start)
        return result
    return inner


def master_map_generate(global_region_grid, region_grid, chunks_grid, mini_grid, tiles_field_size):
    """
        Новый генератор игровой карты, изначально учитывающий все особенности, определенные при создании и расширении предыдущего генератора.

        1) генерирует карту супер регионов, отвечающих за однородность и логичность содержащихся в них и объединяемых друг с другом биомов;
        2) на основании карты глобальных регионов, генерирует карту регионов содержащих информацию о возможных к появлению в них локаций;
        3) на основании карты регионов генерирует карту локаций;
        4) на основании карты локаций, генерирует карту минирегионов, являющихся однородными тайловыми полями;
        5) генерирует полную тайловую карту;
        6) режет тайловую карту на отдельные локации.
        
    """
    global_region_map = global_region_generate(global_region_grid)

    print(f"global_region_map \n {global_region_map}")

    region_map = region_generate(global_region_map, global_region_grid, region_grid)

    print(f"region_map \n {region_map}")
    
    chunks_map = chunks_map_generate(region_map, (global_region_grid*region_grid), chunks_grid)

    print(f"chunks_map \n {chunks_map}")
    
    mini_region_map = mini_region_map_generate(chunks_map, (global_region_grid*region_grid*chunks_grid), mini_grid)

    print(f"mini_region_map \n {mini_region_map}")

    all_tiles_map = tiles_map_generate(mini_region_map, (global_region_grid*region_grid*chunks_grid*mini_grid), tiles_field_size)

    print(f"all_tiles_map \n {all_tiles_map}")
    #ready_global_map = cutting_tiles_map(tiles_map)

@timeit
def global_region_generate(global_grid):
    """
        Генерирует карту глобальных регионов

        Типы глобальных регионов:   0 - пустынный
                                    1 - горный
                                    2 - влажный
                                    3 - солёный
    """
    global_region_map = []
    for i in range(global_grid):
        global_region_map.append([random.randrange(4) for x in range(global_grid)])
    return global_region_map

@timeit
def region_generate(global_region_map, global_region_grid, region_grid):
    """
        На основании карты глобальных регионов, генерирует карту регионов содержащих зёрна возможных локаций
    """
    seed_list = {  
                    0: ['j', '.', 'A', 'S'], # Пустынный
                    1: ['A', '▲', 'C', 'R'], # Горный
                    2: ['„', ',', 'P'],    # Влажный
                    3: ['~', ';'],     # Солёный
                }

    raw_region_map = all_map_master_generate(global_region_map, region_grid, False, seed_list)

    region_map = all_gluing_map(raw_region_map, global_region_grid, region_grid)

    return region_map

@timeit
def chunks_map_generate(global_region_map, initial_size, chunk_size):
    """
        на основании карты глобальных регионов генерирует карту локаций
    """
    seed_list = {  
                    'j': ['j'],    # desert
                    '.': ['.'],    # semidesert 
                    'A': ['A'],    # cliff semi-desert
                    'S': ['S'],    # snake semi-desert
                    '▲': ['▲'],    # hills
                    'C': ['C'],    # canyons
                    'R': ['R'],    # big canyons
                    '„': ['„'],    # field
                    ',': [','],    # dried field
                    'P': ['P'],    # oasis
                    '~': ['~'],    # salty lake
                    ';': [';'],    # saline land
                }

    raw_chunks_map = all_map_master_generate(global_region_map, chunk_size, True, seed_list)
    chunks_map = all_gluing_map(raw_chunks_map, initial_size, chunk_size)

    return chunks_map

@timeit
def mini_region_map_generate(chunks_map, initial_size, mini_grid):
    """
        на основании карты локаций, генерирует карту минирегионов, являющихся однородными тайловыми полями
    """
    seed_list = {  
                    'j': ['.'],                   # desert
                    '.': ['.', ','],              # semidesert 
                    'A': ['▲', 'A', '.', ','],    # cliff semi-desert
                    'S': ['A', '.', ','],         # snake semi-desert
                    '▲': ['▲', 'o'],              # hills
                    'C': ['C', '.', ','],         # canyons
                    'R': ['C', 'o', '.'],         # big canyons
                    '„': ['u', '„', ','],         # field
                    ',': ['„', ','],              # dried field
                    'P': ['F', '„', '~'],         # oasis
                    '~': ['~', ','],              # salty lake
                    ';': [';'],                   # saline land
                }

    raw_mini_region_map = all_map_master_generate(chunks_map, mini_grid, True, seed_list)
    #print(raw_mini_region_map)
    mini_region_map = all_gluing_map(raw_mini_region_map, initial_size, mini_grid)

    return mini_region_map

@timeit
def tiles_map_generate(mini_region_map, initial_size, chunk_size):
    """
        генерирует полную тайловую карту
    """
    
    seed_list = {  
                    '.': ['.'],
                    ',': [','],
                    '„': ['„'],
                    'A': ['A'],
                    '▲': ['▲'],
                    'C': ['C'],
                    ';': [';'],
                    'S': ['S'],
                    'o': ['o'],
                    'F': ['F'],
                    '~': ['~'],
                    'u': ['u'],
                }

    raw_all_tiles_map = all_map_master_generate(mini_region_map, chunk_size, True, seed_list)
    all_tiles_map = all_gluing_map(raw_all_tiles_map, initial_size, chunk_size)

    return all_tiles_map

def cutting_tiles_map(tiles_map):
    """
        Режет готовую тайловую карту
    """
    pass

def all_gluing_map(raw_gluing_map, grid, count_block):
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
                    try:
                        gluing_map[gluing_index].append(raw_gluing_map[number_region_line][number_region][number_location_line][number_location])
                    except IndexError:
                        print(f"len(gluing_map) = {len(gluing_map)} ||| gluing_index = {gluing_index}")
                        print(f"number_region_line - {number_region_line} | number_region - {number_region}, number_location_line - {number_location_line}, number_location - {number_location}")
                        print(gluing_map[gluing_index])
                    count_location += 1
    return gluing_map

def all_map_master_generate(previous_map, grid, merge, seed_list):
    """
        Генерирует карту следующего уровня приближения на основе карты предыдущего уровня приближения.
    """
    raw_generated_map = []

    for number_line in range(len(previous_map)):
        region_line = []
        for number_region in range(len(previous_map[number_line])):
            region = []
            for number_point_map_line in range(grid): #Создаём линии региона
                point_map_line = []
                for number_point_map in range(grid): #Создаём значения линий
                    number_new_seed = random.choice(seed_list[previous_map[number_line][number_region]])
                    if merge:
                        top_down_seed = ''
                        left_right_seed = ''                  
                        if number_point_map_line == 0 and number_line != 0:                                             #Обрабатываем верхний край региона
                            top_down_seed = random.choice(seed_list[previous_map[number_line - 1][number_region]])
                        elif number_point_map_line == (len(previous_map) - 1) and number_line != (len(previous_map) - 1):   #Обрабатываем нижний край региона
                            top_down_seed = random.choice(seed_list[previous_map[number_line + 1][number_region]])
                        if number_point_map == 0 and number_region != 0:                                                  #Обрабатываем левый край региона
                            left_right_seed = random.choice(seed_list[previous_map[number_line][number_region - 1]])
                        elif number_point_map != (len(previous_map) - 1) and number_region != (len(previous_map) - 1):        #Обрабатываем правый край региона
                            left_right_seed = random.choice(seed_list[previous_map[number_line][number_region + 1]])
                        if random.randrange(11)//5 > 0:
                            number_new_seed = merge_description_for_generator(number_new_seed, top_down_seed)
                        if random.randrange(11)//5 > 0:
                            number_new_seed = merge_description_for_generator(number_new_seed, left_right_seed)

                    point_map_line.append(number_new_seed)
                region.append(point_map_line)
            region_line.append(region)
        raw_generated_map.append(region_line)
    
    return raw_generated_map

def merge_description_for_generator(description_one, description_two):
    """
        Соединяет два описания для генератора
    """
    if description_two:
        #print(f'{description_one}')
        description_one = random.choice([description_one, description_two])
        #print(f'стало {description_one}')
    return description_one


master_map_generate(1, 1, 2, 2, 4)


def selecting_seed(seed_list, seed):
    """
        Содержит и выдаёт значения семян генерации.
    """
    seed_dict = {  
                    0: ['desert',             [40.0,60.0], ['.'],                 ['j'],            'j',        20],
                    1: ['semidesert',         [35.0,50.0], ['.', ','],            ['▲', 'o', 'i'],  '.',        10],
                    2: ['cliff semi-desert',  [35.0,50.0], ['▲', 'A', '.', ','],  ['o', 'i'],       'A',         7],
                    3: ['snake semi-desert',  [35.0,50.0], ['A', '.', ','],       ['▲','o', 'i'],   'S',         7],
                    4: ['hills',              [20.0,35.0], ['▲', 'o'],            ['„', ','],       '▲',        20],
                    5: ['canyons',            [20.0,35.0], ['C', '.', ','],       ['C'],            'C',        20],
                    6: ['big canyons',        [20.0,35.0], ['C'],                 ['.', 'o', '▲'],  'R',        20],
                    7: ['field',              [20.0,35.0], ['u', '„', ','],       ['ü', 'o'],       '„',         5],
                    8: ['dried field',        [30.0,40.0], ['„', ','],            ['o', 'u'],       ',',         2],
                    9: ['oasis',              [15.0,30.0], ['F', '„', '~'],       ['P', ','],       'P',         0],
                    10:['salty lake',         [25.0,40.0], ['~', ','],            ['„', '.'],       '~',        20],
                    11:['saline land',        [40.0,50.0], [';'],                 [':'],            ';',        15],
                    
                }
    return seed_dict[seed][0]
