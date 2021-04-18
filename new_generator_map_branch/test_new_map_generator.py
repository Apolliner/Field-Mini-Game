import random
import time


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    НОВЫЙ ГЕНЕРАТОР ИГРОВОЙ КАРТЫ
    
    На выходе выдаёт класс Location


    ИЗВЕСТНЫЕ ОШИБКИ:
    1)Ошибка при попытке соединить два описания при генерации полной тайловой карты. Выбирается вариант с соединением полного описания которого нет.
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

""" 

def timeit(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time() - start)
        return result
    return inner

def print_map(printing_map):
    
    if type(printing_map[0][0]) == list:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile][0]) + ' '
            test_print += '\n'
        print(test_print)
    else:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile]) + ' '
            test_print += '\n'
        print(test_print)
    

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

    seed_dict1 = {# seed  |icon  | name                 |tileset               |random tileset   |price_move |temperature
                    'j': ['j',  'desert',              ['.'],                 ['j'],             20,        [40.0,60.0]],
                    '.': ['.',  'semidesert',          ['.', ','],            ['▲', 'o', 'i'],   10,        [35.0,50.0]],
                    'A': ['A',  'cliff semi-desert',   ['▲', 'A', '.', ','],  ['o', 'i'],         7,        [35.0,50.0]],
                    'S': ['S',  'snake semi-desert',   ['A', '.', ','],       ['▲','o', 'i'],     7,        [35.0,50.0]],
                    '▲': ['▲',  'hills',               ['▲', 'o'],            ['„', ','],        20,        [20.0,35.0]],
                    'C': ['C',  'canyons',             ['C', '.', ','],       ['C'],             20,        [20.0,35.0]],
                    'R': ['R',  'big canyons',         ['C'],                 ['.', 'o', '▲'],   20,        [20.0,35.0]],
                    '„': ['„',  'field',               ['u', '„', ','],       ['ü', 'o'],         5,        [20.0,35.0]],
                    ',': [',',  'dried field',         ['„', ','],            ['o', 'u'],         2,        [30.0,40.0]],
                    'P': ['P',  'oasis',               ['F', '„', '~'],       ['P', ','],         0,        [15.0,30.0]],
                    '~': ['~',  'salty lake',          ['~', ','],            ['„', '.'],        20,        [25.0,40.0]],
                    ';': [';',  'saline land',         [';'],                 [':'],             15,        [40.0,50.0]],
                }

    seed_dict = {# seed  |icon  | name                 |tileset               |random tileset   |price_move |temperature
                    'j': ['j',  'desert',              ['j'],                 ['j'],             20,        [40.0,60.0]],
                    '.': ['.',  'semidesert',          ['.'],                 ['▲', 'o', 'i'],   10,        [35.0,50.0]],
                    'A': ['A',  'cliff semi-desert',   ['A'],                 ['o', 'i'],         7,        [35.0,50.0]],
                    'S': ['S',  'snake semi-desert',   ['A'],                 ['▲','o', 'i'],     7,        [35.0,50.0]],
                    '▲': ['▲',  'hills',               ['▲'],                 ['„', ','],        20,        [20.0,35.0]],
                    'C': ['C',  'canyons',             ['C'],                 ['C'],             20,        [20.0,35.0]],
                    'R': ['R',  'big canyons',         ['C'],                 ['.', 'o', '▲'],   20,        [20.0,35.0]],
                    '„': ['„',  'field',               ['„'],                 ['ü', 'o'],         5,        [20.0,35.0]],
                    ',': [',',  'dried field',         [','],                 ['o', 'u'],         2,        [30.0,40.0]],
                    'P': ['P',  'oasis',               ['F'],                 ['P', ','],         0,        [15.0,30.0]],
                    '~': ['~',  'salty lake',          ['~'],                 ['„', '.'],        20,        [25.0,40.0]],
                    ';': [';',  'saline land',         [';'],                 [':'],             15,        [40.0,50.0]],
                }
    
    global_region_map = global_region_generate(global_region_grid)

    print(f"global_region_map")
    print_map(global_region_map)
    
    region_map = region_generate(global_region_map, global_region_grid, region_grid)

    print(f"region_map")
    print_map(region_map)
    
    #Содержит в себе описание локации
    chunks_map = chunks_map_generate(region_map, (global_region_grid*region_grid), chunks_grid, seed_dict) 
    
    print(f"chunks_map")
    print_map(chunks_map)
    
    mini_region_map = mini_region_map_generate(chunks_map, (global_region_grid*region_grid*chunks_grid), mini_grid, seed_dict)

    print(f"mini_region_map")
    print_map(mini_region_map)
    
    #Готовая глобальная тайловая карта
    all_tiles_map = tiles_map_generate(mini_region_map, (global_region_grid*region_grid*chunks_grid*mini_grid), tiles_field_size) 

    print(f"all_tiles_map")
    print_map(all_tiles_map)
    
    #Добавление тайлов из списка рандомного заполнения
    add_random_all_tiles_map = add_random_tiles(all_tiles_map, chunks_map, chunks_grid*mini_grid)

    print(f"add_random_all_tiles_map")
    print_map(add_random_all_tiles_map)
    


    
    #ready_global_map = cutting_tiles_map(tiles_map)


@timeit
def add_random_tiles(processed_map, chunks_map, chunk_size1):
    """
        Добавляет случайные тайлы на готовую тайловую карту, основываясь на информации из карты локаций
    """
    chunk_size = len(processed_map)//len(chunks_map)

    banned_list = ['~']
    
    for number_seed_line in range(len(chunks_map)):
        for number_seed in range(len(chunks_map[number_seed_line])):
            for number_line in range((number_seed_line)*chunk_size, (number_seed_line)*chunk_size + chunk_size):
                for number_tile in range((number_seed)*chunk_size, (number_seed)*chunk_size + chunk_size):
                    if random.randrange(10)//9 and not(processed_map[number_line][number_tile] in banned_list):
                        processed_map[number_line][number_tile] = random.choice(chunks_map[number_seed_line][number_seed][3])
            
    return processed_map


@timeit
def global_region_generate(global_grid):
    """
        Генерирует карту глобальных регионов

        Типы глобальных регионов:   0 - пустынный
                                    1 - горный
                                    2 - влажный
                                    3 - солёный
                                    4 - каньонный
    """
    global_region_map = []
    for i in range(global_grid):
        global_region_map.append([random.randrange(5) for x in range(global_grid)])
    return global_region_map

@timeit
def region_generate(global_region_map, global_region_grid, region_grid):
    """
        На основании карты глобальных регионов, генерирует карту регионов содержащих зёрна возможных локаций
    """
    seed_dict1 = {  
                    0: [['j', '.', 'S']], # Пустынный
                    1: [['A', '▲']], # Горный
                    2: [['„', ',', 'P', '~']], # Влажный
                    3: [['~', ';']], # Солёный
                    4: [['C', 'R', ]], # Каньонный
                }
    seed_dict = {  
                    0: [['j']], # Пустынный
                    1: [['A']], # Горный
                    2: [['„']], # Влажный
                    3: [['~']], # Солёный
                    4: [['C']], # Каньонный
                }

    raw_region_map = all_map_master_generate(global_region_map, region_grid, False, seed_dict, 0, False)
    region_map = all_gluing_map(raw_region_map, global_region_grid, region_grid)

    return region_map

@timeit
def chunks_map_generate(region_map, initial_size, chunks_grid, seed_dict):
    """
        на основании карты глобальных регионов генерирует карту локаций
    """
    raw_chunks_map = all_map_master_generate(region_map, chunks_grid, True, seed_dict, 0, True)
    chunks_map = all_gluing_map(raw_chunks_map, initial_size, chunks_grid)

    return chunks_map

@timeit
def mini_region_map_generate(chunks_map, initial_size, mini_grid, seed_dict):
    """
        на основании карты локаций, генерирует карту минирегионов, являющихся однородными тайловыми полями
    """

    raw_mini_region_map = all_map_master_generate(chunks_map, mini_grid, False, seed_dict, 2, False)
    mini_region_map = all_gluing_map(raw_mini_region_map, initial_size, mini_grid)

    return mini_region_map

@timeit
def tiles_map_generate(mini_region_map, initial_size, chunk_size):
    """
        генерирует полную тайловую карту
    """
    
    seed_dict1 = {  
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
    seed_dict = {  
                    'j': ['j'],
                    '.': ['.'],
                    'A': ['A'],
                    'S': ['S'],
                    '▲': ['▲'],
                    'C': ['C'],
                    'R': ['R'],
                    '„': ['„'],
                    ',': [','],
                    'P': ['P'],
                    '~': ['~'],
                    ';': [';'],
                }

    raw_all_tiles_map = all_map_master_generate(mini_region_map, chunk_size, False, seed_dict, 0, False)
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

def all_map_master_generate(previous_map, grid, merge, seed_dict, number_in_list, all_description):
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
                    if all_description: #Работа с полным описанием (Для локаций)
                        packed_all_description = seed_dict[previous_map[number_line][number_region]]
                        if merge:
                            top_down_description = ''
                            left_right_description = ''                  
                            if number_point_map_line == 0 and number_line > 0:                                             #Обрабатываем верхний край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line - 1][number_region]][0]:
                                    top_down_description = seed_dict[previous_map[number_line - 1][number_region]]
                            elif number_point_map_line == (len(previous_map) - 1) and number_line < (len(previous_map) - 1):   #Обрабатываем нижний край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line + 1][number_region]][0]:
                                    top_down_description = seed_dict[previous_map[number_line + 1][number_region]]
                            if number_point_map == 0 and number_region > 0:                                                  #Обрабатываем левый край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line][number_region - 1]][0]:
                                    left_right_description = seed_dict[previous_map[number_line][number_region - 1]]
                            elif number_point_map == (len(previous_map) - 1) and number_region < (len(previous_map) - 1):        #Обрабатываем правый край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line][number_region + 1]][0]:
                                    left_right_description = seed_dict[previous_map[number_line][number_region + 1]]

                            if random.randrange(11)//5 > 0: # Настройка шанса смешения
                                packed_all_description = merge_all_description_for_generator(packed_all_description, top_down_description)
                            if random.randrange(11)//5 > 0: # Настройка шанса смешения
                                packed_all_description = merge_all_description_for_generator(packed_all_description, left_right_description)
                                
                        point_map_line.append(packed_all_description)

                    else: # Простое описание
                        if type(previous_map[number_line][number_region]) != list: # Описание через словарь
                            number_new_seed = random.choice(seed_dict[previous_map[number_line][number_region]][number_in_list])
                            if merge:
                                top_down_seed = ''
                                left_right_seed = ''
                                if number_point_map_line == 0 and number_line > 0:
                                    top_down_seed = random.choice(seed_dict[previous_map[number_line - 1][number_region]][number_in_list])
                                elif number_point_map_line == (len(previous_map) - 1) and number_line < (len(previous_map) - 1):
                                    top_down_seed = random.choice(seed_dict[previous_map[number_line + 1][number_region]][number_in_list])
                                if number_point_map == 0 and number_region > 0:
                                    left_right_seed = random.choice(seed_dict[previous_map[number_line][number_region - 1]][number_in_list])
                                elif number_point_map == (len(previous_map) - 1) and number_region < (len(previous_map) - 1): 
                                    left_right_seed = random.choice(seed_dict[previous_map[number_line][number_region + 1]][number_in_list])

                                if random.randrange(11)//2 > 0: # Настройка шанса смешения
                                    number_new_seed = merge_description_for_generator(number_new_seed, top_down_seed)
                                if random.randrange(11)//2 > 0: # Настройка шанса смешения
                                    number_new_seed = merge_description_for_generator(number_new_seed, left_right_seed)
                        else: # Описание из предыдущей карты
                            number_new_seed = random.choice(previous_map[number_line][number_region][number_in_list])
                            if merge:
                                top_down_seed = ''
                                left_right_seed = ''                  
                                if number_point_map_line == 0 and number_line > 0:
                                    top_down_seed = random.choice(previous_map[number_line - 1][number_region][number_in_list])
                                elif number_point_map_line == (len(previous_map) - 1) and number_line < (len(previous_map) - 1):
                                    top_down_seed = random.choice(previous_map[number_line + 1][number_region][number_in_list])
                                if number_point_map == 0 and number_region > 0:
                                    left_right_seed = random.choice(previous_map[number_line][number_region - 1][number_in_list])
                                elif number_point_map == (len(previous_map) - 1) and number_region < (len(previous_map) - 1):
                                    left_right_seed = random.choice(previous_map[number_line][number_region + 1][number_in_list])
                                if random.randrange(11)//2 > 0: # Настройка шанса смешения
                                    number_new_seed = merge_description_for_generator(number_new_seed, top_down_seed)
                                if random.randrange(11)//2 > 0: # Настройка шанса смешения
                                    number_new_seed = merge_description_for_generator(number_new_seed, left_right_seed)
                        point_map_line.append(number_new_seed)
                            
                        
                region.append(point_map_line)
            region_line.append(region)
        raw_generated_map.append(region_line)
    
    return raw_generated_map

def merge_all_description_for_generator(description_one, description_two):
    """
        Принимает два описания локаций, склеивает их, сохраняя значение в первое.
    """
    if description_two:
        #description_one[0] = random.choice([description_one[0], description_two[0]])
        description_one[0] = '8'
        #description_one[1] = description_one[1] + ' - ' + description_two[1]
        description_one[2].append(random.choice(description_two[2]))
        description_one[3].append(random.choice(description_two[3]))
        if description_one[4] < description_two[4]:
            description_one[4] = random.randrange(description_one[4], description_two[4])
        elif description_one[4] > description_two[4]:
            description_one[4] = random.randrange(description_two[4], description_one[4])
        #if description_one[5] < description_two[5]:
            #try:
                #description_one[5] = [random.randrange(description_one[5][0], description_two[5][0]),
                                  #random.randrange(description_one[5][1], description_two[5][1])]
            #except ValueError:
                #print(F"description_one - {description_one} | description_two - {description_two}")
        #elif description_one[5] > description_two[5]:
            #try:
                #description_one[5] = [random.randrange(description_two[5][0], description_one[5][0]),
                                  #random.randrange(description_two[5][1], description_one[5][1])]
            #except ValueError:
                #print(F"description_one - {description_one} | description_two - {description_two}")
    return description_one

def merge_description_for_generator(description_one, description_two):
    """
        Соединяет два описания для генератора
    """
    if description_two:
        description_one = random.choice([description_one, description_two])
    return description_one



#                   global_region_grid | region_grid | chunks_grid | mini_region_grid | tile_field_grid
master_map_generate(        3,                4,            3,            2,                 1)

