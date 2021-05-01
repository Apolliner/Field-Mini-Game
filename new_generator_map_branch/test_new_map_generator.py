import random
import time
import copy


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    НОВЫЙ ГЕНЕРАТОР ИГРОВОЙ КАРТЫ
    
    На выходе выдаёт класс Location


    ИЗВЕСТНЫЕ ОШИБКИ:
    1)Ошибка при попытке соединить два описания при генерации полной тайловой карты. Выбирается вариант с соединением полного описания которого нет. #ИСПРАВЛЕНО
    2)Ошибка мерджа вообще всех локаций. #ИСПРАВЛЕНО


    РЕАЛИЗОВАТЬ:
    1)Для разных тайлов - разные списки типов, являющихся лестницами
    2)Тайловые поля, не изменяющие свою высоту
    3)Возможность того, что два разных тайла являются одним тайловым полем (хотя надо ли оно, можно то же самое реализовать рандомным выбором иконки)
    4)Генерация разных типов тайлов в одном тайловом поле без учёта краёв.
    5)Адекватность генерации супер биомов друг рядом с другом. Возможно, сначала должен идти выбор главных, не соприкасающихся друг с другом
      супер биомов, а ведомые супер биомы подстраиваются под них.
    6)Настройку количества слоёв для каждого типа тайла
    7)Добавление нарисованых заранее кусков карт
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""





class Tile:
    """ Содержит изображение, описание, особое содержание тайла, стоимость передвижения, тип, высоту и лестницу """
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        
    def getting_attributes(self, icon, number):
        ground_dict =   {
                        'j': ['бархан', 1],
                        '.': ['горячий песок', 1],
                        ',': ['жухлая трава', 1],
                        'o': ['валун', 15],
                        'A': ['холм', 15],
                        '▲': ['скала', 20],
                        'i': ['кактус', 1],
                        ':': ['солончак', 1],
                        ';': ['солончак', 1],
                        '„': ['трава', 1],
                        'u': ['высокая трава', 1],
                        'ü': ['колючая трава', 10],
                        'F': ['чахлое дерево', 1],
                        'P': ['раскидистое дерево', 1],
                        '~': ['солёная вода', 20],
                        'C': ['каньон', 20],
                        '??': ['ничего', 10],
                        }
        try:
            return ground_dict[icon][number]
        except TypeError:
            print(f"icon - {icon}, number - {number}")

class Location:
    """ Содержит описание локации """
    __slots__ = ('name', 'temperature', 'chunk', 'icon', 'price_move')
    def __init__(self, name:str, temperature:float, chunk:list, icon:str, price_move:int):
        self.name = name
        self.temperature = temperature
        self.chunk = chunk
        self.icon = icon
        self.price_move = price_move


def timeit(func):
    """
    Декоратор. Считает время выполнения функции.
    """
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time() - start)
        return result
    return inner


def print_map(printing_map):
    """
    Инструмент на время разработки, для наглядного отображения получившейся карты.
    """
    
    if type(printing_map[0][0]) == list:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile][0]) + ' '
            test_print += '\n'
        print(test_print)

    elif isinstance(printing_map[0][0], Tile):
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                #test_print += str(printing_map[number_line][number_tile].icon) + str(printing_map[number_line][number_tile].type)
                test_print += str(printing_map[number_line][number_tile].icon) + str(abs(printing_map[number_line][number_tile].level))
                #test_print += ' ' + str(abs(printing_map[number_line][number_tile].level))
            test_print += '\n'
        print(test_print)
    else:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile]) + ' '
            test_print += '\n'
        print(test_print)


@timeit
def master_map_generate(global_region_grid, region_grid, chunks_grid, mini_grid, tiles_field_size):
    """
        Новый генератор игровой карты, изначально учитывающий все особенности, определенные при создании и расширении предыдущего генератора.

        1) генерирует карту глобальных регионов, отвечающих за однородность и логичность содержащихся в них и объединяемых друг с другом биомов;
        2) на основании карты глобальных регионов, генерирует карту регионов содержащих информацию о возможных к появлению в них локаций;
        3) на основании карты регионов генерирует карту локаций, которая содержит полную информацию о локациях;
        4) на основании карты локаций, генерирует карту минирегионов, являющихся однородными тайловыми полями;
        5) генерирует полную тайловую карту;
        6) на основании информации из карты локаций, наносит на полную тайловую карту тайлы из списка случайного заполнения.
        7) на полной тайловой карте вычисляет однородные тайловые поля, их высоты, склоны и лестницы. Возвращает полную тайловую карту высот
        6) режет полную тайловую карту на отдельные локации.
        
    """

    global_region_map = global_region_generate(global_region_grid)
    
    region_map = region_generate(global_region_map, global_region_grid, region_grid)

    #Содержит в себе описание локации
    chunks_map = chunks_map_generate(region_map, (global_region_grid*region_grid), chunks_grid) 

    mini_region_map = mini_region_map_generate(chunks_map, (global_region_grid*region_grid*chunks_grid), mini_grid)

    
    #Готовая глобальная тайловая карта
    all_tiles_map = tiles_map_generate(mini_region_map, (global_region_grid*region_grid*chunks_grid*mini_grid), tiles_field_size) 
    
    #Добавление тайлов из списка рандомного заполнения
    add_random_all_tiles_map = add_random_tiles(all_tiles_map, chunks_map)


    #Добавление заранее нарисованной карты
    add_draw_location(add_random_all_tiles_map, chunks_map)
    
    #Создание перевалов
    #mountain_method_generation(add_random_all_tiles_map, chunks_map)

    #Генерация гор по методу горных озёр
    mountains_generate(add_random_all_tiles_map, chunks_map)

    #Рисование реки
    river_map_generation(add_random_all_tiles_map, 5)
    
    #Конвертирование тайлов в класс
    all_class_tiles_map = convert_tiles_to_class(add_random_all_tiles_map, chunks_map)
    
    #Рассчёт уровней, склонов и лестниц
    levelness_calculation(all_class_tiles_map, ('~', '▲', 'C'), False, False)
    levelness_calculation(all_class_tiles_map, ('~', 'C'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)

    #Разрезание глобальной карты на карту классов Location
    ready_global_map = cutting_tiles_map(all_class_tiles_map, chunks_map)

    return ready_global_map

def mountains_generate(all_tiles_map, chunks_map):
    """
        Генерация гор по методу горных озёр
    """
    def mountain_gen(processed_map, position_y, position_x, size, add_position_y_to_step, start_quantity_step, add_icon, filling_icon):
        """
            Генерация гор
        """
        quantity_step = start_quantity_step
        type_generate = 'evenly'
        for step in range(size):
            processed_map[position_y][position_x - 1] = filling_icon
            processed_map[position_y][position_x - 2] = filling_icon
            if add_position_y_to_step == 2:
                processed_map[position_y + 1][position_x - 1] = filling_icon
                processed_map[position_y + 1][position_x - 2] = filling_icon
            for i in range(quantity_step + 1):
                processed_map[position_y][position_x + i] = add_icon
                processed_map[position_y][position_x + i + 1] = filling_icon
                processed_map[position_y][position_x + i + 2] = filling_icon
                if add_position_y_to_step == 2:
                    processed_map[position_y + 1][position_x + i] = add_icon
                    processed_map[position_y + 1][position_x + i + 1] = filling_icon
                    processed_map[position_y + 1][position_x + i + 2] = filling_icon
                if step == 0:
                    processed_map[position_y - 1][position_x + i] = filling_icon
                if step == size - 1:
                    processed_map[position_y + 1][position_x + i] = filling_icon

            if random.randrange(20)//15 > 0:
                type_generate = 'left'
            elif random.randrange(20)//15 > 0:
                type_generate = 'right'
                
            if type_generate == 'evenly':
                if size//2 > step + 1:
                    position_x -= 1
                    quantity_step += 2
                elif size//2 < step + 1:
                    position_x += 1
                    quantity_step -= 2
                position_y += add_position_y_to_step
            if type_generate == 'left':
                if size//2 > step + 1:
                    position_x -= 2
                    quantity_step += 2
                elif size//2 < step + 1:
                    position_x += 2
                    quantity_step -= 2
                position_y += add_position_y_to_step
            if type_generate == 'right':
                if size//2 > step + 1:
                    quantity_step += 2
                elif size//2 < step + 1:
                    quantity_step -= 2
                position_y += add_position_y_to_step

    
    chunk_size = len(all_tiles_map)//len(chunks_map)
    for number_line in range(len(chunks_map) - 1):
        for number_tile in range(len(chunks_map[number_line]) - 1):
            if chunks_map[number_line][number_tile][0] == '▲':
                mountain_gen(all_tiles_map, number_line*chunk_size, number_tile*chunk_size, random.randrange(10, 20), 2, 0, '▲', 'o')
            elif chunks_map[number_line][number_tile][0] == 'P' and random.randrange(20)//10 > 0:
                mountain_gen(all_tiles_map, number_line*chunk_size, number_tile*chunk_size, random.randrange(10, 20), 1, 2, '~', 'u')
            


    
@timeit
def mountain_method_generation(processed_map, chunks_map):
    """
        Генерация гор
    """
    def mountain_passes_generate(processed_map, quantity):
        """
            Генерация перевалов
        """
        step = len(processed_map)//quantity
        for number_mountain_passes in range(quantity):
        
            position_y = 1
            position_x = step*number_mountain_passes
            for number_line in range(len(processed_map)):
                position_y = number_line
                processed_map[position_y][position_x] = random.choice(['0', 'o', ',', 'A'])
                processed_map[position_y - 1][position_x] = random.choice(['0', 'o', ',', 'A'])
                processed_map[position_y][position_x + 1] = random.choice(['0', 'o', ',', 'A'])
                if random.randrange(50)//10 > 0:
                    if 0 < position_x < len(processed_map) - 2:
                        position_x += random.randrange(-1, 2)
                    elif position_x == 0:
                        position_x += random.randrange(2)
                    elif position_x == len(processed_map) - 2:
                        position_x += random.randrange(-1, 1)
        return processed_map
                        
    def mountain_map_generate(chunk_size):
        mountain_map = []
        for line in range(chunk_size):
            mountain_map_line = []
            for tile in range(chunk_size):
                mountain_map_line.append('▲')
            mountain_map.append(mountain_map_line)
        return mountain_map
    def mountain_lake(processed_map, position_y, position_x, size):
        """
            Генерация горных озёр
        """
        quantity_step = 2
        type_generate = 'evenly'
        for step in range(size):
            processed_map[position_y][position_x - 1] = 'o'
            for i in range(quantity_step + 1):
                processed_map[position_y][position_x + i] = '~'
                processed_map[position_y][position_x + i + 1] = 'o'
                if step == 0:
                    processed_map[position_y - 1][position_x + i] = 'o'
                if step == size - 1:
                    processed_map[position_y + 1][position_x + i] = 'o'

            if random.randrange(20)//15 > 0:
                type_generate = 'left'
            if random.randrange(20)//15 > 0:
                type_generate = 'right'
                
            if type_generate == 'evenly':
                if size//2 > step + 1:
                    position_x -= 1
                    quantity_step += 2
                elif size//2 < step + 1:
                    position_x += 1
                    quantity_step -= 2
                position_y += 1
            if type_generate == 'left':
                if size//2 > step + 1:
                    position_x -= 2
                    quantity_step += 2
                elif size//2 < step + 1:
                    position_x += 1
                    quantity_step -= 2
                position_y += 1
            if type_generate == 'right':
                if size//2 > step + 1:
                    quantity_step += 2
                elif size//2 < step + 1:
                    quantity_step -= 2
                position_y += 1
         

    chunk_size = len(processed_map)//len(chunks_map)

    for number_chunks_line, chunks_line in enumerate(chunks_map):
        for number_chunks_tile, chunks_tile in enumerate(chunks_line):
            if chunks_tile[0] == '▲':
                for line in range(chunk_size):
                    for tile in range(chunk_size):
                        mountain_map = mountain_map_generate(chunk_size)
                        mountain_passes = mountain_passes_generate(mountain_map, 2)
                        if random.randrange(10)//5 > 0:
                            mountain_lake(mountain_passes, 1, chunk_size//2, random.randrange(6, 11, 2))
                        for number_all_line in range(chunk_size):
                            for number_all_tile in range(chunk_size):
                                if not (mountain_passes[number_all_line][number_all_tile] in ('0')):
                                    try:
                                        processed_map[number_chunks_line*chunk_size + number_all_line][number_chunks_tile*chunk_size + number_all_tile] = mountain_passes[number_all_line][number_all_tile]
                                    except IndexError:
                                        print(F"{processed_map[number_chunks_line*chunk_size + number_all_line][number_chunks_tile*chunk_size + number_all_tile]}")
def river_map_generation(processed_map, number_of_rivers):
    """
        Генерирует реки
    """
    minirivers = []
    for river in range(number_of_rivers):
        position_y = 1
        position_x = random.randrange(25, len(processed_map) - 25)
        print(f"position_x - {position_x}")
        for number_line in range(len(processed_map)):
            position_y = number_line
            if processed_map[position_y][position_x - 1] != '~':
                processed_map[position_y][position_x - 1] = random.choice([',', '„', '.', 'u', 'ü'])
            processed_map[position_y][position_x] = '~'
            processed_map[position_y - 1][position_x] = '~'
            processed_map[position_y][position_x + 1] = '~'
            processed_map[position_y][position_x + 2] = '~'
            processed_map[position_y][position_x + 3] = '~'
            processed_map[position_y - 1][position_x + 3] = '~'
            if processed_map[position_y][position_x + 4] != '~':
                processed_map[position_y][position_x + 4] = random.choice([',', '„', '.', 'u', 'ü'])
            if random.randrange(50)//30 > 0:
                if 4 < position_x < len(processed_map) - 10:
                    position_x += random.randrange(-1, 2)
                elif position_x == 10:
                    position_x += random.randrange(2)
                elif position_x == len(processed_map) - 10:
                    position_x += random.randrange(-1, 1)
            if random.randrange(500)//495 > 0:
                minirivers.append([position_y, position_x])
    for miniriver in minirivers:
        position_y = miniriver[0]
        position_x = miniriver[1]
        direction = random.choice(['left', 'right'])
        step = 0
        for number_line in range(position_y, len(processed_map)):
            position_y = number_line
            if processed_map[position_y][position_x] == '~' and step > 25:
                break
            if random.randrange(500)//495 > 0:
                break
            processed_map[position_y][position_x] = '~'
            processed_map[position_y - 1][position_x] = '~'
            if random.randrange(500)//495 > 0:
                minirivers.append([position_y, position_x])
            if random.randrange(50)//30 > 0:
                if direction == 'left':
                    if 4 < position_x < len(processed_map) - 10:
                        position_x += random.randrange(-1, 2)
                    elif position_x == 10:
                        pass
                    elif position_x == len(processed_map) - 10:
                        position_x += random.randrange(-1, 1)
                if direction == 'right':
                    if 4 < position_x < len(processed_map) - 10:
                        position_x += random.randrange(2)
                    elif position_x == len(processed_map) - 10:
                        pass
            step += 1
              
def add_draw_location(processed_map, chunks_map):
    """
        Добавляет заранее нарисованную локацию на карту
    """
    chunk_size = len(processed_map)//len(chunks_map)
    draw_number_line = 100
    draw_number_tile = 100
    
    file_draw_map = open("new_generator_map_branch\draw_map\hills_1.txt", encoding="utf-8") #new_generator_map_branch\
    raw_draw_map = file_draw_map.read().splitlines()
    draw_map = []

    for line in raw_draw_map:
        map_line = []
        for tile in line:
            map_line.append(tile)
        draw_map.append(map_line)


    for number_line in range(draw_number_line, (draw_number_line + len(draw_map))):
        for number_tile in range(draw_number_line, (draw_number_tile + len(draw_map) - 4)):
            try:
                processed_map[number_line][number_tile] = draw_map[number_line - draw_number_line - 1][number_tile - draw_number_tile - 1]
            except IndexError:
                print(F"len(draw_map) - {len(draw_map)}, len(processed_map) - {len(processed_map)}, number_line - {number_line}, number_tile - {number_line}")

@timeit
def global_region_generate(global_grid):
    """
        Генерирует карту глобальных регионов

        Типы глобальных регионов:   0 - пустынный
                                    1 - горный
                                    2 - живой
                                    3 - солёный
                                    4 - каньонный
                                    5 - водяной
    """
    global_region_map = []
    for i in range(global_grid):
        global_region_map.append([random.randrange(6) for x in range(global_grid)])
    return global_region_map

@timeit
def region_generate(global_region_map, global_region_grid, region_grid):
    """
        На основании карты глобальных регионов, генерирует карту регионов содержащих зёрна возможных локаций
    """
    seed_dict = {  
                    0: [['j', '.', 'S']],   # Пустынный
                    1: [['A', '▲', 'B']],   # Горный
                    2: [['„', ',', 'P']],   # Живой
                    3: [[';', '.']],        # Солёный
                    4: [['C', 'R', ]],      # Каньонный
                    5: [['~']]              # Водяной
                }

    raw_region_map = all_map_master_generate(global_region_map, region_grid, False, seed_dict, 0, False)
    region_map = all_gluing_map(raw_region_map, global_region_grid, region_grid)

    return region_map

@timeit
def chunks_map_generate(region_map, initial_size, chunks_grid):
    """
        на основании карты глобальных регионов генерирует карту локаций
    """
    seed_dict = {# seed  |icon  | name                 |tileset               |random tileset   |price_move |temperature
                    'j': ['j',  'desert',              ['.'],                 ['j'],             20,        [40.0,60.0]],
                    '.': ['.',  'semi-desert',         ['.', ','],            ['▲', 'o', 'i'],   10,        [35.0,50.0]],
                    'A': ['A',  'cliff semi-desert',   ['▲', 'A', '.', ','],  ['o', 'i'],         7,        [35.0,50.0]],
                    'S': ['S',  'snake semi-desert',   ['A', '.', ','],       ['▲','o', 'i'],     7,        [35.0,50.0]],
                    '▲': ['▲',  'hills',               ['▲', 'o', ','],       ['„', ','],        20,        [20.0,35.0]],
                    'B': ['▲',  'big hills',           ['▲'],                 ['o'],             20,        [20.0,35.0]],
                    'C': ['C',  'canyons',             ['C', '.', ','],       ['C'],             20,        [20.0,35.0]],
                    'R': ['R',  'big canyons',         ['C'],                 ['.', 'o', '▲'],   20,        [20.0,35.0]],
                    '„': ['„',  'field',               ['u', '„', ','],       ['ü', 'o'],         5,        [20.0,35.0]],
                    ',': [',',  'dried field',         ['„', ','],            ['o', 'u'],         2,        [30.0,40.0]],
                    'P': ['P',  'oasis',               ['F', '„'],       ['P', ','],         0,        [15.0,30.0]],
                    '~': ['~',  'salty lake',          ['~'],                 ['„', '.'],        20,        [25.0,40.0]],
                    ';': [';',  'saline land',         [';'],                 [':'],             15,        [40.0,50.0]],
                }
    raw_chunks_map = all_map_master_generate(region_map, chunks_grid, True, seed_dict, 0, True)
    chunks_map = all_gluing_map(raw_chunks_map, initial_size, chunks_grid)

    return chunks_map

@timeit
def mini_region_map_generate(chunks_map, initial_size, mini_grid):
    """
        на основании карты локаций, генерирует карту минирегионов, являющихся однородными тайловыми полями
    """

    raw_mini_region_map = all_map_master_generate(chunks_map, mini_grid, True, {}, 2, False)
    mini_region_map = all_gluing_map(raw_mini_region_map, initial_size, mini_grid)

    return mini_region_map

@timeit
def tiles_map_generate(mini_region_map, initial_size, chunk_size):
    """
        генерирует полную тайловую карту
    """
    
    seed_dict = {  
                    '.': '.',
                    ',': ',',
                    '„': '„',
                    'A': 'A',
                    '▲': '▲',
                    'C': 'C',
                    ';': ';',
                    'S': 'S',
                    'o': 'o',
                    'F': 'F',
                    '~': '~',
                    'u': 'u',
                }

    raw_all_tiles_map = all_map_master_generate(mini_region_map, chunk_size, True, seed_dict, 0, False)
    all_tiles_map = all_gluing_map(raw_all_tiles_map, initial_size, chunk_size)

    return all_tiles_map

@timeit
def add_random_tiles(processed_map, chunks_map):
    """
        Добавляет случайные тайлы на готовую тайловую карту, основываясь на информации из карты локаций
    """
    chunk_size = len(processed_map)//len(chunks_map)

    banned_list = ['~', '▲']
    
    for number_seed_line in range(len(chunks_map)):
        for number_seed in range(len(chunks_map[number_seed_line])):
            for number_line in range((number_seed_line)*chunk_size, (number_seed_line)*chunk_size + chunk_size):
                for number_tile in range((number_seed)*chunk_size, (number_seed)*chunk_size + chunk_size):
                    if random.randrange(10)//9 and not(processed_map[number_line][number_tile] in banned_list):
                        processed_map[number_line][number_tile] = random.choice(chunks_map[number_seed_line][number_seed][3])
            
    return processed_map

@timeit
def convert_tiles_to_class(processed_map, chunks_map):
    """
        Конвертирование тайлов в класс Tile
    """
    chunk_size = len(processed_map)//len(chunks_map) #Для дальнейшей возможности поместить в тайл сущность или предмет
    
    new_class_tiles_map = []
    for number_line in range(len(processed_map)):
        new_line = []
        for number_tile in range(len(processed_map[number_line])):
            new_line.append(Tile(processed_map[number_line][number_tile]))
        new_class_tiles_map.append(new_line)
    return new_class_tiles_map

@timeit
def levelness_calculation(processed_map, field_tiles_tuple, not_the_first_layer, random_pass):
    """
        Рассчёт уровней, склонов и лестниц. levelness - количество уровней.

        not_the_first_layer кортеж тайлов, по которым производится рассчёт

        not_the_first_layer - False если слой первый и единственный. True если слой расчитывается на предыдущем слое.

        random_pass - При включении случайным образом пропускается повышение уровня тайлов
    """
    minus_level_list = ['~', 'C']
    plus_level_list = ['▲']
    stairs_list = ['O', 'A', 'P', 'B', 'Q', 'C', 'R', 'D']

    # Поднимание\опускание расчётного слоя на свою высоту.
    detection = ['0']
    if not_the_first_layer:
        detection = ['1']  
    for number_line, line in enumerate(processed_map):
        for number_tile, tile in enumerate(line):
            not_pass = True
            if random_pass and random.randrange(500)//490 > 0: #Добавлена случайность срабатывания
                not_pass = False
            if (tile.icon in field_tiles_tuple) and tile.type in detection and not_pass:
                if tile.icon in plus_level_list:
                    tile.level += 1
                elif tile.icon in minus_level_list:
                    tile.level -= 1
    # На рассчитанной высоте, определяются склоны.
    for number_line, line in enumerate(processed_map):
        for number_tile, tile in enumerate(line):
            if (tile.icon in field_tiles_tuple) and tile.type in ['0', '1']:
                change = False
                direction = {
                                    'up'   : False,
                                    'down' : False,
                                    'left' : False,
                                    'right': False,
                            }
                if 0 < number_line < len(processed_map) - 1:
                    if tile.icon == processed_map[number_line - 1][number_tile].icon and tile.level == processed_map[number_line - 1][number_tile].level:
                        direction['up'] = True
                    if tile.icon == processed_map[number_line + 1][number_tile].icon and tile.level == processed_map[number_line + 1][number_tile].level:
                        direction['down'] = True
                if 0 < number_tile < len(line) - 1:
                    if tile.icon == processed_map[number_line][number_tile - 1].icon and tile.level == processed_map[number_line][number_tile - 1].level:
                        direction['left'] = True
                    if tile.icon == processed_map[number_line][number_tile + 1].icon and tile.level == processed_map[number_line][number_tile + 1].level:
                        direction['right'] = True

                if direction['up'] and direction['down'] and direction['left'] and direction['right']:
                    tile.type = '1'
                elif direction['up'] and not(direction['down']) and direction['left'] and direction['right']:
                    if tile.type == '1':
                        tile.type = 'G'
                    else:
                        tile.type = '2'
                elif direction['up'] and direction['down'] and not(direction['left']) and direction['right']:
                    if tile.type == '1':
                        tile.type = 'H'
                    else:
                        tile.type = '3'
                elif not(direction['up']) and direction['down'] and direction['left'] and direction['right']:
                    if tile.type == '1':
                        tile.type = 'I'
                    else:
                        tile.type = '4'
                elif direction['up'] and direction['down'] and direction['left'] and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'J'
                    else:
                        tile.type = '5'
                elif direction['up'] and not(direction['down']) and direction['left'] and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'K'
                    else:
                        tile.type = '6'
                elif direction['up'] and not(direction['down']) and not(direction['left']) and direction['right']:
                    if tile.type == '1':
                        tile.type = 'L'
                    else:
                        tile.type = '7'
                elif not(direction['up']) and direction['down'] and not(direction['left']) and direction['right']:
                    if tile.type == '1':
                        tile.type = 'M'
                    else:
                        tile.type = '8'
                elif not(direction['up']) and direction['down'] and direction['left'] and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'N'
                    else:
                        tile.type = '9'
                elif not(direction['up']) and not(direction['down']) and direction['left'] and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'O'
                    else:
                        tile.type = 'A'
                elif direction['up'] and not(direction['down']) and not(direction['left']) and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'P'
                    else:
                        tile.type = 'B'
                elif not(direction['up']) and not(direction['down']) and not(direction['left']) and direction['right']:
                    if tile.type == '1':
                        tile.type = 'Q'
                    else:
                        tile.type = 'C'
                elif not(direction['up']) and direction['down'] and not(direction['left']) and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'R'
                    else:
                        tile.type = 'D'
                elif not(direction['up']) and not(direction['down']) and direction['left'] and direction['right']:
                    if tile.type == '1':
                        tile.type = 'S'
                    else:
                        tile.type = 'E'
                elif direction['up'] and direction['down'] and not(direction['left']) and not(direction['right']):
                    if tile.type == '1':
                        tile.type = 'T'
                    else:
                        tile.type = 'F'
                else:
                    if tile.type == '1':
                        tile.type = 'U'
                        if 1 < number_line < len(processed_map) and 1 < number_tile < len(processed_map):
                            if processed_map[number_line - 1][number_tile] == 'G' and processed_map[number_line + 1][number_tile
                                ] == 'I' and processed_map[number_line][number_tile - 1] == 'J' and processed_map[number_line][number_tile + 1] == 'H':
                                tile.level -= 1
                    else:
                        tile.type = '0'

                if tile.type in stairs_list:
                    tile.stairs = True

def cutting_tiles_map(processed_map, chunks_map):
    """
        Режет готовую тайловую карту
    """
    chunk_size = len(processed_map)//len(chunks_map)
    global_map = []
    for number_seed_line, seed_line in enumerate(chunks_map):
        new_global_line = []
        for number_seed, seed in enumerate(seed_line):
            new_global_location = Location(seed[1], random.uniform(min(seed[5][0], seed[5][1]), max(seed[5][0], seed[5][1])), [], seed[0], seed[4])
            for number_line in range((number_seed_line)*chunk_size, (number_seed_line)*chunk_size + chunk_size):
                location_line = []
                for number_tile in range((number_seed)*chunk_size, (number_seed)*chunk_size + chunk_size):
                    location_line.append(processed_map[number_line][number_tile])
                new_global_location.chunk.append(location_line) 
            new_global_line.append(new_global_location)
        global_map.append(new_global_line)
            
    return global_map

def all_gluing_map(raw_gluing_map, grid, count_block):
    """
        Склеивает чанки и локации в единое поле из "сырых" карт

        grid - количество кластеров в одной стороне квадратной склеиваемой карты
        count_block - количество сущностей на одной стороне квадратного кластера
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
                        packed_all_description = copy.deepcopy(seed_dict[previous_map[number_line][number_region]])
                        if merge:
                            top_down_description = ''
                            left_right_description = ''                  
                            if number_point_map_line == 0 and number_line > 0:                                             #Обрабатываем верхний край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line - 1][number_region]][0]:
                                    top_down_description = seed_dict[previous_map[number_line - 1][number_region]]
                            elif number_point_map_line == (grid - 1) and number_line < (len(previous_map) - 1):   #Обрабатываем нижний край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line + 1][number_region]][0]:
                                    top_down_description = seed_dict[previous_map[number_line + 1][number_region]]
                            if number_point_map == 0 and number_region > 0:                                                  #Обрабатываем левый край региона
                                if packed_all_description[0] != seed_dict[previous_map[number_line][number_region - 1]][0]:
                                    left_right_description = seed_dict[previous_map[number_line][number_region - 1]]
                            elif number_point_map == (grid - 1) and number_region < (len(previous_map) - 1):        #Обрабатываем правый край региона
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
                                if type(number_new_seed) == list:
                                    print(number_new_seed)
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
        description_one[0] = random.choice([description_one[0], description_two[0]])
        description_one[1] = description_one[1] + ' - ' + description_two[1]
        description_one[2].append(random.choice(description_two[2]))
        description_one[3].append(random.choice(description_two[3]))
        if description_one[4] < description_two[4]:
            description_one[4] = random.randrange(description_one[4], description_two[4])
        elif description_one[4] > description_two[4]:
            description_one[4] = random.randrange(description_two[4], description_one[4])
        if description_one[5][0] < description_two[5][0]:
            description_one[5][0] = random.randrange(description_one[5][0], description_two[5][0])
        elif description_one[5][0] > description_two[5][0]:
            description_one[5][0] = random.randrange(description_two[5][0], description_one[5][0])
        if description_one[5][1] < description_two[5][1]:
            description_one[5][1] = random.randrange(description_one[5][1], description_two[5][1])
        elif description_one[5][1] > description_two[5][1]:
            description_one[5][1] = random.randrange(description_two[5][1], description_one[5][1])
        

    return description_one

def merge_description_for_generator(description_one, description_two):
    """
        Соединяет два описания для генератора
    """
    if description_two:
        description_one = random.choice([description_one, description_two])
    return description_one

def print_map(printing_map):
    """
    Инструмент на время разработки, для наглядного отображения получившейся карты.
    """
    
    if type(printing_map[0][0]) == list:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile][0]) + ' '
            test_print += '\n'
        print(test_print)

    elif isinstance(printing_map[0][0], Tile):
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                #test_print += str(printing_map[number_line][number_tile].icon) + str(printing_map[number_line][number_tile].type)
                test_print += str(printing_map[number_line][number_tile].icon) + str(abs(printing_map[number_line][number_tile].level))
                #test_print += ' ' + str(abs(printing_map[number_line][number_tile].level))
            test_print += '\n'
        print(test_print)
    else:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile]) + ' '
            test_print += '\n'
        print(test_print)


"""
=========================================================================================================================================================
"""

#                                global_region_grid | region_grid | chunks_grid | mini_region_grid | tile_field_grid
#global_map = master_map_generate(        2,                2,            2,            2,                 2)

