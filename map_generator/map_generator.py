import random
import time
import copy
import math
import pygame
import pickle
import sys
if __name__ == '__main__':
    import map_patch
    from pygame.locals import *
    import sys
else:
    from map_generator import map_patch


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    НОВЫЙ ГЕНЕРАТОР ИГРОВОЙ КАРТЫ
    
    На выходе выдаёт класс Location


    ИЗВЕСТНЫЕ ОШИБКИ:
    1)Ошибка при попытке соединить два описания при генерации полной тайловой карты. Выбирается вариант с соединением полного описания которого нет. #ИСПРАВЛЕНО
    2)Ошибка мерджа вообще всех локаций. #ИСПРАВЛЕНО


    РЕАЛИЗОВАТЬ:
    1)Для разных тайлов - разные списки типов, являющихся лестницами
    2)Тайловые поля, не изменяющие свою высоту #РЕАЛИЗОВАНО
    3)Возможность того, что два разных тайла являются одним тайловым полем (хотя надо ли оно, можно то же самое реализовать рандомным выбором иконки)
    4)Генерация разных типов тайлов в одном тайловом поле без учёта краёв.
    5)Адекватность генерации супер биомов друг рядом с другом. Возможно, сначала должен идти выбор главных, не соприкасающихся друг с другом
      супер биомов, а ведомые супер биомы подстраиваются под них.
    6)Настройку количества слоёв для каждого типа тайла
    7)Добавление нарисованых заранее кусков карт #РЕАЛИЗОВАНО
    
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

class Tile:
    """ Содержит изображение, описание, особое содержание тайла, стоимость передвижения, тип, высоту и лестницу """
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices', 'world_vertices')
    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1
        self.world_vertices = -2
        
    def getting_attributes(self, icon, number):
        ground_dict =   {
                        'j': ['бархан', 1],
                        's': ['ракушка', 1],
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
                        '~': ['вода', 20],
                        '`': ['солёная вода', 20],
                        'f': ['брод', 7],
                        'C': ['каньон', 7],
                        '??': ['ничего', 10],
                        }
        return ground_dict[icon][number]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["icon"] = self.icon
        state["description"] = self.description
        state["list_of_features"] = self.list_of_features
        state["price_move"] = self.price_move
        state["type"] = self.type
        state["level"] = self.level
        state["stairs"] = self.stairs
        state["vertices"] = self.vertices
        state["world_vertices"] = self.world_vertices
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.icon = state["icon"] 
        self.description = state["description"]
        self.list_of_features = state["list_of_features"]
        self.price_move = state["price_move"]
        self.type = state["type"]
        self.level = state["level"]
        self.stairs = state["stairs"]
        self.vertices = state["vertices"]
        self.world_vertices = state["world_vertices"]

class Tile_minimap:
    """ Содержит изображение, описание, особое содержание тайла миникарты"""
    __slots__ = ('icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices', 'temperature')
    def __init__(self, icon, name, price_move, temperature):
        self.icon = icon
        self.description = name
        self.list_of_features = []
        self.price_move = price_move
        self.temperature = temperature
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1
        
    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["icon"] = self.icon
        state["description"] = self.description
        state["list_of_features"] = self.list_of_features
        state["price_move"] = self.price_move
        state["temperature"] = self.temperature
        state["type"] = self.type
        state["level"] = self.level
        state["stairs"] = self.stairs
        state["vertices"] = self.vertices
        
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.icon = state["icon"] 
        self.description = state["description"]
        self.list_of_features = state["list_of_features"]
        self.price_move = state["price_move"]
        self.temperature = state["temperature"]
        self.type = state["type"]
        self.level = state["level"]
        self.stairs = state["stairs"]
        self.vertices = state["vertices"]

class Location:
    """ Содержит описание локации """
    __slots__ = ('name', 'temperature', 'chunk', 'icon', 'price_move', 'vertices', 'position')
    def __init__(self, name:str, temperature:float, chunk:list, icon:str, price_move:int, position):
        self.name = name
        self.temperature = temperature
        self.chunk = chunk
        self.icon = icon
        self.price_move = price_move
        self.vertices = []
        self.position = position
    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["temperature"] = self.temperature
        state["chunk"] = pickle.dumps(self.chunk)
        state["icon"] = self.icon
        state["price_move"] = self.price_move
        state["vertices"] = self.vertices
        state["position"] = self.position
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.temperature = state["temperature"]
        self.chunk = pickle.loads(state["chunk"])
        self.icon = state["icon"]
        self.price_move = state["price_move"]
        self.vertices = state["vertices"]
        self.position = state["position"]

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


@timeit
def master_map_generate(global_region_grid, region_grid, chunks_grid, mini_grid, tiles_field_size, screen):
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
    draw_map_generation(screen, [[0]], 'none', 'Генерация глобальных регионов')
    
    #Глобальные регионы
    #progress_bar(screen, 0, 'Глобальные регионы')
    global_region_map = global_region_generate(global_region_grid)
    draw_map_generation(screen, global_region_map, 'Global_regions', 'Генерация регионов')
    
    #Регионы
    #progress_bar(screen, 5, 'Регионы')
    region_map = region_generate(global_region_map, global_region_grid, region_grid)
    draw_map_generation(screen, region_map, 'Regions', 'Генерация локаций')
    

    #Карта локаций. Содержит в себе описание локации
    #progress_bar(screen, 11, 'Карта локаций. Содержит в себе описание локации')
    chunks_map = chunks_map_generate(region_map, (global_region_grid*region_grid), chunks_grid)
    draw_map_generation(screen, chunks_map, 'Locations', 'Генерация карты мини-регионов')


    #Карта мини-регионов
    #progress_bar(screen, 16, 'Карта мини-регионов')
    mini_region_map = mini_region_map_generate(chunks_map, (global_region_grid*region_grid*chunks_grid), mini_grid)
    draw_map_generation(screen, mini_region_map, 'Mini_regions', 'Генерация больших структур по методу горных озёр')
    

    #Генерация больших структур по методу горных озёр
    #progress_bar(screen, 22, 'Генерация больших структур по методу горных озёр')
    big_structures_generate(mini_region_map, global_region_map)
    draw_map_generation(screen, mini_region_map, 'Mini_regions', 'Генерация готовой глобальной тайловой карты')
    
    
    #Готовая глобальная тайловая карта
    #progress_bar(screen, 27, 'Готовая глобальная тайловая карта')
    all_tiles_map = tiles_map_generate(mini_region_map, (global_region_grid*region_grid*chunks_grid*mini_grid), tiles_field_size)
    draw_map_generation(screen, all_tiles_map, 'All_tiles', 'Отрисовка больших структур на карте локаций')
    

    #Отрисовка больших структур на карте локаций
    #progress_bar(screen, 23, 'Отрисовка больших структур на карте локаций')
    big_structures_writer(chunks_map, mini_region_map)
    simple_draw_map_generation(screen, 'Добавление тайлов из списка рандомного заполнения')
    
    
    #Добавление тайлов из списка рандомного заполнения
    #progress_bar(screen, 28, 'Добавление тайлов из списка рандомного заполнения')
    add_random_all_tiles_map = add_random_tiles(all_tiles_map, chunks_map)
    draw_map_generation(screen, all_tiles_map, 'All_tiles', 'Генерация гор и озёр по методу горных озёр')
    

    #Генерация гор и озёр по методу горных озёр
    #progress_bar(screen, 34, 'Генерация гор и озёр по методу горных озёр')
    mountains_generate(add_random_all_tiles_map, chunks_map)
    draw_map_generation(screen, all_tiles_map, 'All_tiles', 'Генерация продвинутой реки')
    

    #Рисование продвинутой реки
    #progress_bar(screen, 39, 'Рисование продвинутой реки')
    rivers_waypoints = advanced_river_generation(add_random_all_tiles_map, chunks_map, 1)
    draw_map_generation(screen, all_tiles_map, 'All_tiles', 'Конвертирование тайлов в класс')
    
    
    #Конвертирование тайлов в класс
    #progress_bar(screen, 45, 'Конвертирование тайлов в класс')
    all_class_tiles_map = convert_tiles_to_class(add_random_all_tiles_map, chunks_map)
    simple_draw_map_generation(screen, 'Рассчёт уровней, склонов и лестниц')
    
    
    #Рассчёт уровней, склонов и лестниц
    #progress_bar(screen, 50, 'Рассчёт уровней, склонов и лестниц')
    levelness_calculation(all_class_tiles_map, ('~', '▲', 'C', ':', 'o', ',', '„', '`'), False, False)
    levelness_calculation(all_class_tiles_map, ('~', 'C', '`'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, False)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    levelness_calculation(all_class_tiles_map, ('▲'), True, True)
    simple_draw_map_generation(screen, 'Разнообразие тайловых полей, не требующих границ')
    

    #Разнообразие тайловых полей, не требующих границ
    #progress_bar(screen, 56, 'Разнообразие тайловых полей, не требующих границ')
    diversity_field_tiles(all_class_tiles_map)
    simple_draw_map_generation(screen, 'Разрезание глобальной карты на карту классов Location')
    

    #Разрезание глобальной карты на карту классов Location
    #progress_bar(screen, 62, 'Разрезание глобальной карты на карту классов Location')
    ready_global_map = cutting_tiles_map(all_class_tiles_map, chunks_map)
    simple_draw_map_generation(screen, 'Добавление бродов в реки')
    
    
    #Добавление бродов в реки
    #progress_bar(screen, 67, 'Добавление бродов в реки')
    add_fords_in_rivers(ready_global_map, rivers_waypoints)
    simple_draw_map_generation(screen, 'Определение независимых областей на локациях')
    

    #Определение независимых областей на локациях
    #progress_bar(screen, 74, 'Определение независимых областей на локациях')
    defining_vertices(ready_global_map)

    world_vertices_calculation(ready_global_map)
    draw_vertices_generation(screen, ready_global_map, 'Определение связей между локациями')
    #simple_draw_map_generation(screen, 'Определение связей между локациями')


    #Определение связей между локациями
    #progress_bar(screen, 80, 'Определение связей между локациями')
    defining_zone_relationships(ready_global_map)
    simple_draw_map_generation(screen, 'Создание миникарты')


    #Добавление существ в тайлы
    #progress_bar(screen, 85, 'Добавление существ в тайлы')
    creature_spawn_add(ready_global_map)
    simple_draw_map_generation(screen, 'Добавление существ в тайлы')

    
    #Создание миникарты
    #progress_bar(screen, 90, 'Создание миникарты')
    minimap = minimap_create(ready_global_map)
    simple_draw_map_generation(screen, 'Карта готова')

    request_for_a_key_press(screen)
    
    #progress_bar(screen, 100, 'Карта готова')

    return ready_global_map, minimap


    
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    Визуализация генерации карты
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
class Button_rect(pygame.sprite.Sprite):
    """ Отрисовывает поверхности """

    def __init__(self, y, x, size_y, size_x, color):
        pygame.sprite.Sprite.__init__(self)
        self.y = y
        self.x = x
        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.speed = 0
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Draw_region(pygame.sprite.Sprite):
    """ Содержит спрайты миникарты """

    def __init__(self, y, x, size_tile, key, type_region):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(key, type_region))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)
    def color_dict(self, key, type_region):
        """
                                    0 - пустынный
                                    1 - горный
                                    2 - зелёный
                                    3 - солёный
                                    4 - каньонный
                                    5 - водяной
        """
        global_region_dict =   {
                        0: (239, 228, 176),
                        1: (50, 50, 50),
                        2: (0, 255, 0),
                        3: (230, 230, 230),
                        4: (255, 150, 0),
                        5: (0, 0, 255),
                        }

        location_dict = {
                        'j': (239, 228, 200),
                        '.': (239, 228, 176),
                        'F': (200, 100, 0),
                        'P': (0, 255, 0),
                        ',': (209, 169, 126),
                        '„': (100, 255, 0),
                        'A': (200, 200, 100),
                        'S': (200, 200, 150),
                        '▲': (150, 150, 150),
                        '~': (0, 0, 200),
                        'C': (185, 122, 87),
                        ';': (220, 220, 220),
                       }
        tiles_dict = {  
                        '.': (239, 228, 176),
                        ',': (209, 169, 126),
                        '„': (100, 255, 0),
                        'A': (200, 200, 100),
                        '▲': (150, 150, 150),
                        'C': (185, 122, 87),
                        ':': (245, 245, 245),
                        ';': (235, 235, 235),
                        'S': (200, 200, 150),
                        'o': (170, 170, 170),
                        'F': (200, 100, 0),
                        'P': (0, 255, 0),
                        '~': (0, 0, 200),
                        '`': (0, 0, 210),
                        'u': (80, 235, 0),
                        's': (255, 255, 255),
                        }
        if type_region == 'none':
            return (150, 150, 150)               
        elif type_region == 'Global_regions':
            if key in global_region_dict:
                return global_region_dict[key]
            else:
                return (random.randrange(256), random.randrange(256), random.randrange(256))
        elif type_region == 'Regions':
            if key in location_dict:
                return location_dict[key]
            else:
                return (random.randrange(256), random.randrange(256), random.randrange(256))
        elif type_region == 'Locations':
            if key[0] in location_dict:
                return location_dict[key[0]]
            else:
                return (random.randrange(256), random.randrange(256), random.randrange(256))
        elif type_region == 'Mini_regions' or type_region == 'All_tiles':
            if key in tiles_dict:
                return tiles_dict[key]
            else:
                return (random.randrange(256), random.randrange(256), random.randrange(256))

class Island_friends(pygame.sprite.Sprite):
    """ Содержит спрайты зон доступности """
    def add_color_dict(size):
        """ Создаёт единый на все экземпляры, словарь цветов """
        all_color_dict = {}
        for number in range(size):
            all_color_dict[len(all_color_dict)] = (random.randrange(255), random.randrange(255), random.randrange(255))
        all_color_dict[-1] = (0, 0, 0)
        all_color_dict[255] = (255, 0, 0)
        return all_color_dict
    
    all_color_dict = add_color_dict(200)

    def __init__(self, y, x, size_tile, number):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(number))
        self.image.set_alpha(60)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0
    def draw( self, surface ):
        surface.blit(self.image, self.rect)
    
    def color_dict(self, number):
        if number in self.all_color_dict:
            return self.all_color_dict[number]
        else:
            return (random.randrange(256), random.randrange(256), random.randrange(256))
def draw_map_generation(screen, draw_map, type_map, description):
    """
        Отрисовывает этапы генерации карты
    """
    size_tile = 750/len(draw_map)
    screen.fill((255, 255, 255))
    
    for number_line, line in enumerate(draw_map):
        for number_tile, tile in enumerate(line):
            Draw_region(number_line*size_tile, number_tile*size_tile, size_tile, tile, type_map).draw(screen)

    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(description, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.top = 100
    textRectObj.left = 760
    screen.blit(textSurfaceObj, textRectObj) 
            
    pygame.display.flip()
    
def simple_draw_map_generation(screen, description):
    """
        Отрисовывает этапы генерации карты без перерисовки карты
    """
    Button_rect(50, 750, 100, 1000, (255, 255, 255)).draw(screen)
    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(description, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.top = 100
    textRectObj.left = 760
    screen.blit(textSurfaceObj, textRectObj) 
            
    pygame.display.flip()

def draw_vertices_generation(screen, draw_map, description):
    """
        Отрисовывает определённые зоны доступности
    """
    size_tile = 750/(len(draw_map) * len(draw_map[0][0].chunk))
    chunk_size = len(draw_map[0][0].chunk)
    Button_rect(50, 750, 100, 1000, (255, 255, 255)).draw(screen)
    
    for number_global_line, global_line in enumerate(draw_map):
        for number_global_tile, global_tile in enumerate(global_line):
            for number_line, line in enumerate(global_tile.chunk):
                for number_tile, tile in enumerate(line):
                    Island_friends((number_global_line*chunk_size + number_line)*size_tile, (number_global_tile*chunk_size + number_tile)*size_tile, size_tile, tile.vertices).draw(screen)

    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(description, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.top = 100
    textRectObj.left = 760
    screen.blit(textSurfaceObj, textRectObj) 
            
    pygame.display.flip()

def request_for_a_key_press(screen):
    """
        Спрашивает ввод space перед началом игры
    """
    Button_rect(50, 750, 100, 1000, (255, 255, 255)).draw(screen)
    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render('Для продолжения нажмите "SPACE"', True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.top = 100
    textRectObj.left = 760
    screen.blit(textSurfaceObj, textRectObj) 
            
    pygame.display.flip()
    request = True
    while request:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                        request = False
        
def progress_bar(screen, percent, description):
    """
        Отрисовывает прогресс-бар для визуализации генерации карты
    """
    screen.fill((255, 255, 255))
    x_size, y_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    Button_rect(y_size//2, x_size//2, 200, 1000, (150, 150, 150)).draw(screen)
    Button_rect(y_size//2, x_size//2, 200, percent*10, (200, 100, 100)).draw(screen)
    
    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(description, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (x_size//2, y_size//2 - 125)
    screen.blit(textSurfaceObj, textRectObj) 
    
    pygame.display.flip()

            

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ГЕНЕРАЦИЯ ЛОКАЛЬНЫХ И ГЛОБАЛЬНЫХ СТРУКТУР
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

def creature_spawn_add(global_map):
    """
        Помещает мелких существ в тайлы

        added_dict = {биом локации: [(кортеж типов тайлов), (кортеж существ)]}
    """
    added_typle = ('S', 'F', 'P')
    added_dict = {
                    'S': [('o', ), ('snake', 'rattlesnake')],
                    'F': [('P', ), ('bird', )],
                    'P': [('F', ), ('bird', )],

                 }
    for global_line in global_map:
        for global_tile in global_line:
            if global_tile.icon in added_typle:
                for line in global_tile.chunk:
                    for tile in line:
                        if tile.icon in added_dict[global_tile.icon][0]: #and random.randrange(20)//18 > 0:
                            tile.list_of_features.append(random.choice(added_dict[global_tile.icon][1]))
                            

@timeit
def add_fords_in_rivers(processed_map, rivers_waypoints):
    if rivers_waypoints:
        for river_waypoint in rivers_waypoints:
            river_map = processed_map[river_waypoint[0]][river_waypoint[1]].chunk
            for number_line, line in enumerate(river_map):
                for number_tile, tile in enumerate(line):
                    if tile.icon == '~' and number_line < len(river_map) - 7 and number_tile < len(river_map) - 7 and random.randrange(30)//29 > 0:
                        draw_ford = map_patch.map_patch('ford_river_5x5')
                        for number_patch_line in range(len(draw_ford)):
                            for number_patch_tile in range(len(draw_ford[number_patch_line])):
                                if draw_ford[number_patch_line][number_patch_tile] == 'f' and river_map[number_line + number_patch_line][number_tile + number_patch_tile].icon == '~':
                                    river_map[number_line + number_patch_line][number_tile + number_patch_tile].icon = 'f'
                                    river_map[number_line + number_patch_line][number_tile + number_patch_tile].description = 'брод'
                                    river_map[number_line + number_patch_line][number_tile + number_patch_tile].price_move = 10
                                    river_map[number_line + number_patch_line][number_tile + number_patch_tile].level = 0
                                

def draw_ready_map(processed_map, file_draw_map, number_line, number_tile, chunk_size):
    """
        Рисует готовую карту на указанном чанке.
    """
    draw_map = file_draw_map.read().splitlines()
    for number_all_line in range(len(draw_map)):
        for number_all_tile in range(len(draw_map[number_all_line])):
            if draw_map[number_all_line][number_all_tile] != '0':
                processed_map[number_line*chunk_size + number_all_line][number_tile*chunk_size + number_all_tile] = draw_map[number_all_line][number_all_tile]
            
@timeit
def advanced_river_generation(global_tiles_map, chunks_map, number_of_rivers):
    """
        Использование старой версии алгоритма поиска пути, для определения движения продвинутых рек.

        Типы глобальных регионов:   0 - пустынный
                                    1 - горный
                                    2 - зелёный
                                    3 - солёный
                                    4 - каньонный
                                    5 - водяной
    """
    class River_for_generator:
        """ Содержит описание реки для генератора """
        def __init__(self, global_start_point, global_finish_point, width, coast):
            self.global_start_point = global_start_point
            self.global_finish_point = global_finish_point
            self.global_path = []
            self.local_path = []
            self.width = width
            self.coast = coast
            self.depth = 1

    class Fantom_tile:
        """ Приводит тайлы к виду, необходимому для генератора """
        def __init__(self, icon, price):
            self.icon = icon
            self.price_move = price

    chunk_size = len(global_tiles_map)//len(chunks_map)

    banned_list = ['▲']

    rivers_waypoints = []

    #Приведение глобальной карты к необходимому виду
    global_map = []
    for number_line in range(len(chunks_map)):
        global_line = []
        for number_tile in range(len(chunks_map[number_line])): #0, 4
            #Приведение локации к необходимому для генератора виду
            location = Fantom_tile(chunks_map[number_line][number_tile][0], chunks_map[number_line][number_tile][4])
            global_line.append(location)
        global_map.append(global_line)
                                              

    for another_one_river in range(number_of_rivers):
        global_start_point = [0, random.randrange(len(chunks_map))]
        global_finish_point = [len(chunks_map) - 1, random.randrange(len(chunks_map))]
        width = random.randrange(3, 10)
        coast = 2
        river = River_for_generator(global_start_point, global_finish_point, width, coast)
        #Определение глобального пути                      
        
        river.global_path = a_star_algorithm_river_calculation(global_map, river.global_start_point, river.global_finish_point, ['C'])
        river.global_path.insert(0, river.global_start_point)
        if len(river.global_path) > 1:

            #Отрисовка реки на будущей миникарте
            for step_path in river.global_path:
                chunks_map[step_path[0]][step_path[1]][0] = '~'
                chunks_map[step_path[0]][step_path[1]][1] += ' - river'

            for number_step_path, step_path in enumerate(river.global_path):
                
                #Вырезание участка карты, будущей локации и приведение тайлов к необходимому для генератора виду
                processed_map = []
                for number_line in range(step_path[0]*chunk_size, step_path[0]*chunk_size + chunk_size):
                    tiles_line = []
                    for number_tile in range(step_path[1]*chunk_size, step_path[1]*chunk_size + chunk_size):
                        
                        #Приведение тайла к необходимому для генератора виду
                        tile = Tile(global_tiles_map[number_line][number_tile])
                        tiles_line.append(tile)
                    processed_map.append(tiles_line)
                    
                #Определение стартовой локальной точки
                if number_step_path == 0:
                    local_start_point = [0, random.randrange(chunk_size)]
                else:
                    local_start_point = river.local_path[-1]

                #Определение финишной локальной точки
                if number_step_path < len(river.global_path) - 1:
                    if river.global_path[number_step_path + 1] == [step_path[0] - 1, step_path[1]]:
                        preferred_candidates = []
                        candidates = []
                        for finish_number_tile in range(chunk_size):
                            if not processed_map[0][finish_number_tile].icon in banned_list:
                                if processed_map[0][finish_number_tile].price_move <= 10:
                                    preferred_candidates.append(finish_number_tile)
                                else:
                                    candidates.append(finish_number_tile)
                        if preferred_candidates:
                            local_finish_point = [0, random.choice(preferred_candidates)]
                        elif candidates:
                            local_finish_point = [0, random.choice(candidates)]
                        else:
                            local_finish_point = [0, random.randrange(chunk_size)]
                        direction = 'up'
                    elif river.global_path[number_step_path + 1] == [step_path[0] + 1, step_path[1]]:
                        preferred_candidates = []
                        candidates = []
                        for finish_number_tile in range(chunk_size):
                            if not processed_map[chunk_size - 1][finish_number_tile].icon in banned_list:
                                if processed_map[chunk_size - 1][finish_number_tile].price_move <= 10:
                                    preferred_candidates.append(finish_number_tile)
                                else:
                                    candidates.append(finish_number_tile)
                        if preferred_candidates:
                            local_finish_point = [chunk_size - 1, random.choice(preferred_candidates)]
                        elif candidates:
                            local_finish_point = [chunk_size - 1, random.choice(candidates)]
                        else:
                            local_finish_point = [chunk_size - 1, random.randrange(chunk_size)]
                        direction = 'down'
                    elif river.global_path[number_step_path + 1] == [step_path[0], step_path[1] - 1]:
                        preferred_candidates = []
                        candidates = []
                        for finish_number_line in range(chunk_size):
                            if not processed_map[finish_number_line][0].icon in banned_list:
                                if processed_map[finish_number_line][0].price_move <= 10:
                                    preferred_candidates.append(finish_number_line)
                                else:
                                    candidates.append(finish_number_line)
                        if preferred_candidates:
                            local_finish_point = [random.choice(preferred_candidates), 0]
                        elif candidates:
                            local_finish_point = [random.choice(candidates), 0]
                        else:
                            local_finish_point = [random.randrange(chunk_size), 0]
                        direction = 'left'
                    elif river.global_path[number_step_path + 1] == [step_path[0], step_path[1] + 1]:
                        preferred_candidates = []
                        candidates = []
                        for finish_number_line in range(chunk_size):
                            if not processed_map[finish_number_line][chunk_size - 1].icon in banned_list:
                                if processed_map[finish_number_line][chunk_size - 1].price_move <= 10:
                                    preferred_candidates.append(finish_number_line)
                                else:
                                    candidates.append(finish_number_line)
                        if preferred_candidates:
                            local_finish_point = [random.choice(preferred_candidates), chunk_size - 1]
                        elif candidates:
                            local_finish_point = [random.choice(candidates), chunk_size - 1]
                        else:
                            local_finish_point = [random.randrange(chunk_size), chunk_size - 1]
                        direction = 'right'
                    else:
                        local_finish_point = [random.randrange(chunk_size), random.randrange(chunk_size)]
                        direction = 'right'
                elif number_step_path == len(river.global_path) - 1:
                    local_finish_point = [chunk_size - 1, random.randrange(chunk_size)]
                #Получение сырых локальных вейпоинтов
                river_raw_path = a_star_algorithm_river_calculation(processed_map, local_start_point, local_finish_point, banned_list)
                
                #Если расчёт алгоритмом А* не был успешен, то происходит расчёт прямого пути
                if not river_raw_path:
                    river_raw_path = enemy_ideal_move_calculation(local_start_point, local_finish_point)

                river_raw_path.insert(0, local_start_point)
                    
                added_point = []
                if number_step_path < len(river.global_path) - 1:
                    if direction == 'up':
                        added_point = [chunk_size - 1, river_raw_path[-1][1]]
                    elif direction == 'down':
                        added_point = [0, river_raw_path[-1][1]]
                    elif direction == 'left':
                        added_point = [river_raw_path[-1][0], chunk_size - 1]
                    else:
                        added_point = [river_raw_path[-1][0], 0]
                for river_raw in river_raw_path:
                    river.local_path.append([river_raw[0] + step_path[0]*chunk_size, river_raw[1] + step_path[1]*chunk_size])
                if added_point:
                    river.local_path.append(added_point)

            #Добавление вейпоинтов в список всех вейпоинтов с реками
            for river_waypoint in river.global_path:
                if not river_waypoint in rivers_waypoints:
                    rivers_waypoints.append(river_waypoint)
            #Отрисовка реки по рассчитанным координатам


            river_dict = {
                          1: 'river_1x1',
                          2: 'river_2x2',
                          3: 'river_3x3',
                          4: 'river_4x4',
                          5: 'river_5x5',
                          6: 'river_6x6',
                          7: 'river_7x7',
                          8: 'river_8x8',
                          9: 'river_9x9',
                         }

            for step_local_path in river.local_path:
                if 10 < step_local_path[0] < len(global_tiles_map) - 15 and 10 < step_local_path[1] < (len(global_tiles_map) - 15):
                    draw_map = map_patch.map_patch(river_dict[river.width])
                    for number_draw_line in range(len(draw_map)):
                        for number_draw_tile in range(len(draw_map[number_draw_line])):
                            if draw_map[number_draw_line][number_draw_tile] != '0':
                                if draw_map[number_draw_line][number_draw_tile] != 'b':
                                    global_tiles_map[step_local_path[0] + number_draw_line][step_local_path[1] + number_draw_tile] = draw_map[number_draw_line][number_draw_tile]
                                elif draw_map[number_draw_line][number_draw_tile] == 'b' and global_tiles_map[step_local_path[0] + number_draw_line][step_local_path[1] + number_draw_tile] != '~':
                                    global_tiles_map[step_local_path[0] + number_draw_line][step_local_path[1] + number_draw_tile] = random.choice((',', '„', '.', 'u', 'ü'))
                    #Изменение ширины реки
                    if random.randrange(100)//99 > 0:
                        if river.width <= 3:
                            river.width += 1
                        elif river.width >= 9:
                            river.width -= 1
                        else:
                            river.width += random.randrange(-1, 2)

    return rivers_waypoints

def enemy_ideal_move_calculation(start_point, finish_point):
    """
        Рассчитывает идеальную траекторию движения NPC.
    """
    
    axis_y = finish_point[0] - start_point[0] # длинна стороны и количество шагов
    axis_x = finish_point[1] - start_point[1] # длинна стороны и количество шагов
    if abs(axis_y) > abs(axis_x):
        if axis_x != 0:
            length_step = abs(axis_y)//abs(axis_x) # на один X столько то Y
        else:
            length_step = abs(axis_y)
        long_side = 'y'
    else:
        if axis_y != 0:
            length_step = abs(axis_x)//abs(axis_y) # на один Y столько то X
        else:
            length_step = abs(axis_x)
        long_side = 'x'
        
    waypoints = [start_point]
        
    for step in range((abs(axis_y) + abs(axis_x))):
        if (step + 1)%(length_step + 1) == 0:
            if long_side == 'y':
                if axis_y >= 0 and axis_x >= 0 or axis_y < 0 and axis_x >= 0:
                    waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                else:
                    waypoints.append([waypoints[step][0], waypoints[step][1] - 1])    
            elif long_side == 'x':
                if axis_x >= 0 and axis_y >= 0 or axis_x < 0 and axis_y >= 0:
                    waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                else:
                    waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
        else:
            if long_side == 'y':
                if axis_y >= 0 and axis_x >= 0 or axis_y >= 0 and axis_x < 0:
                    waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                else:
                    waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
            elif long_side == 'x':
                if axis_x >= 0 and axis_y >= 0 or axis_x >= 0 and axis_y < 0:
                    waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                else:
                    waypoints.append([waypoints[step][0], waypoints[step][1] - 1])

    return waypoints

def a_star_algorithm_river_calculation(calculation_map, start_point, finish_point, banned_list):
    """
        Рассчитывает движение реки по алгоритму A*

        Использование старой версии алгоритма поиска пути, для определения движения продвинутых рек.


        ОСОБЕННОСТИ:
        Река избегает пустынных биомов и каньонов, а так же биомов с высокой температурой.
        Температура локации определяет стоимость перемещения.

    """
    class Node:
        """Содержит узлы графа"""
        __slots__ = ('number', 'position', 'friends', 'price', 'direction')
        def __init__(self, number, position, price, direction):
            self.number = number
            self.position = position
            self.friends = []
            self.price = price
            self.direction = direction
            
    def path_length(start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0])**2 + (start_point[1] - finish_point[1])**2)
        
    def node_friends_calculation(calculation_map, graph, node, verified_node, banned_list):
        """
            Вычисляет соседние узлы графа
        """
        friends = []
        try:
            if 0 <= node.position[0] < len(calculation_map):
                if node.position[0] + 1 < len(calculation_map):
                    if not(calculation_map[node.position[0] + 1][node.position[1]].icon in banned_list) and not([node.position[0] + 1, node.position[1]] in verified_node):
                        friend = Node(len(graph), [node.position[0] + 1, node.position[1]], calculation_map[
                                 node.position[0] + 1][node.position[1]].price_move + path_length([node.position[0] + 1, node.position[1]], finish_point), [-1, 0])
                        friends.append(friend)
                        graph.append(friend)                                                                                              
                if node.position[0] - 1 >= 0:                                                                                                   
                    if not(calculation_map[node.position[0] - 1][node.position[1]].icon in banned_list) and not([node.position[0] - 1, node.position[1]] in verified_node):
                        friend = Node(len(graph), [node.position[0] - 1, node.position[1]], calculation_map[
                                node.position[0] - 1][node.position[1]].price_move + path_length([node.position[0] - 1, node.position[1]], finish_point), [1, 0])
                        friends.append(friend)
                        graph.append(friend)                
            if 0 <= node.position[1] < len(calculation_map):
                if node.position[1] + 1 < len(calculation_map):
                    if not(calculation_map[node.position[0]][node.position[1] + 1].icon in banned_list) and not([node.position[0], node.position[1] + 1] in verified_node):
                        friend = Node(len(graph), [node.position[0], node.position[1] + 1], calculation_map[
                                node.position[0]][node.position[1] + 1].price_move + path_length([node.position[0], node.position[1] + 1], finish_point), [0, -1])
                        friends.append(friend)
                        graph.append(friend)

                if node.position[1] - 1 >= 0:
                    if not(calculation_map[node.position[0]][node.position[1] - 1].icon in banned_list) and not([node.position[0], node.position[1] - 1] in verified_node):
                        friend = Node(len(graph), [node.position[0], node.position[1] - 1], calculation_map[
                                node.position[0]][node.position[1] - 1].price_move + path_length([node.position[0], node.position[1] - 1], finish_point), [0, 1])
                        friends.append(friend)
                        graph.append(friend)
        except IndexError:
            print(f"!!! \n !!! \n IndexError len(calculation_map) - {len(calculation_map)}, node.position - {node.position}  \n !!! \n !!!")
        return friends

    graph = []
    verified_node = []
    start_node = Node(0, start_point, 0, [0, 0])
    start_node.friends = node_friends_calculation(calculation_map, graph, start_node, verified_node, banned_list)
    graph.append(start_node)
    verified_node.append(start_node.position)
    finding_a_path = True
    finish_node = 0
    sucess = True
    step_count = 0
    reversed_waypoints = []
    while finding_a_path:
        min_price = 99999
        node = graph[-1]
        for number_node in range(len(graph)):
            if not(graph[number_node].position in verified_node):
                if graph[number_node].price < min_price:
                    min_price = graph[number_node].price
                    node = graph[number_node]
        if min_price == 99999:
            sucess = False
            finding_a_path = False
            
        verified_node.append(node.position)
        node.friends = node_friends_calculation(calculation_map, graph, node, verified_node, banned_list)
        if node.position == finish_point:
            finding_a_path = False
            finish_node = node.number
        step_count += 1
        if step_count == 250:
            sucess = False
            finding_a_path = False
    if sucess:
        check_node = graph[-1]
        while check_node.position != start_node.position:
            reversed_waypoints.append(graph[finish_node].position)
            preview_node = [graph[finish_node].position[0] + graph[finish_node].direction[0], graph[finish_node].position[1] + graph[finish_node].direction[1]]
            for number_node in range(len(graph)):
                if graph[number_node].position == preview_node:
                    finish_node = number_node
                    check_node = graph[number_node]
            
    return list(reversed(reversed_waypoints))


class Global_vertices:
    """ Содержит описание зоны доступности """
    def __init__(self, number, position, connections):
        self.number = number
        self.position = position
        self.connections = [connections]

class Connections:
    """Содержит описание связей зоны доступности"""
    def __init__(self, number, position, tile):
        self.number = number
        self.position = position
        self.tiles = [tile]

@timeit
def defining_zone_relationships(processed_map):
    """
        Определение связей между зонами доступности на краях локаций и сохранение информации об этом в описание локации
    """

    def defining_connections(processed_map, tile_number, tile_position, defining_local_position, local_position, connect_number, connect_position, global_tile):
        """
            Определяет связи
        """
        if tile_number != -1 and processed_map[connect_position[0]][connect_position[1]].chunk[defining_local_position[0]][defining_local_position[1]].vertices != -1:
            global_not_ok = True
            if global_tile.vertices:                                
                for vertices in global_tile.vertices:
                    if tile_number == vertices.number:
                        not_ok = True
                        if vertices.connections:
                            for connection in vertices.connections:
                                if connection.number == connect_number and connection.position == connect_position:
                                    connection.tiles.append(local_position)
                                    not_ok = False
                                    global_not_ok = False
                        if not_ok:
                            vertices.connections.append(Connections(connect_number, connect_position, local_position))
                            global_not_ok = False
            if global_not_ok:
                global_tile.vertices.append(Global_vertices(tile_number, global_tile.position, Connections(connect_number,
                                                    connect_position, local_position)))

    
    for number_global_line, global_line in enumerate(processed_map):
        for number_global_tile, global_tile in enumerate(global_line):
            #Обработка верхних и нижних краёв
            for number_line in (0, len(global_tile.chunk) - 1):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    tile_number = tile.vertices
                    tile_position = [number_global_line, number_global_tile]
                    local_position = [number_line, number_tile]
                    #Обработка верха
                    if number_global_line > 0 and number_line == 0:
                        if tile.level == processed_map[number_global_line - 1][number_global_tile].chunk[len(global_tile.chunk) - 1][number_tile
                                ].level or tile.stairs or processed_map[number_global_line - 1][number_global_tile].chunk[len(global_tile.chunk) - 1][
                                number_tile].stairs:
                            defining_local_position = [len(global_tile.chunk) - 1, number_tile]
                            connect_number = processed_map[number_global_line - 1][number_global_tile].chunk[len(global_tile.chunk) - 1][number_tile].vertices
                            connect_position = [number_global_line - 1, number_global_tile]

                            defining_connections(processed_map, tile_number, tile_position, defining_local_position, local_position, connect_number,
                                    connect_position, global_tile)

                    #Обработка низа
                    if number_global_line < len(processed_map) - 1 and number_line == len(global_tile.chunk) - 1:
                        if tile.level == processed_map[number_global_line + 1][number_global_tile].chunk[0][number_tile].level or tile.stairs or processed_map[
                            number_global_line + 1][number_global_tile].chunk[0][number_tile].stairs:
                            defining_local_position = [0, number_tile]
                            connect_number = processed_map[number_global_line + 1][number_global_tile].chunk[0][number_tile].vertices
                            connect_position = [number_global_line + 1, number_global_tile]

                            defining_connections(processed_map, tile_number, tile_position, defining_local_position, local_position, connect_number,
                                    connect_position, global_tile)

            #Обработка правых и левых краёв
            for number_line in range(len(global_tile.chunk)):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    tile_number = global_tile.chunk[number_line][number_tile].vertices
                    tile_position = [number_global_line, number_global_tile]
                    local_position = [number_line, number_tile]
                    #Обработка левой стороны
                    if number_global_tile > 0 and number_tile == 0:
                        if tile.level == processed_map[number_global_line][number_global_tile - 1].chunk[number_line][len(global_tile.chunk) - 1
                                ].level or tile.stairs or processed_map[number_global_line][number_global_tile - 1].chunk[number_line][
                                len(global_tile.chunk) - 1].stairs:
                            defining_local_position = [number_line, len(global_tile.chunk) - 1]#
                            connect_number = processed_map[number_global_line][number_global_tile - 1].chunk[number_line][len(global_tile.chunk) - 1].vertices
                            connect_position = [number_global_line, number_global_tile - 1]

                            defining_connections(processed_map, tile_number, tile_position, defining_local_position, local_position, connect_number,
                                connect_position, global_tile)

                    #Обработка правой стороны
                    if number_global_tile < len(processed_map[0]) - 1 and number_tile == len(global_tile.chunk[0]) - 1:
                        if tile.level == processed_map[number_global_line][number_global_tile + 1].chunk[number_line][0].level or tile.stairs or processed_map[
                            number_global_line][number_global_tile + 1].chunk[number_line][0].stairs:
                            defining_local_position = [number_line, 0]
                            connect_number = processed_map[number_global_line][number_global_tile + 1].chunk[number_line][0].vertices
                            connect_position = [number_global_line, number_global_tile + 1]

                            defining_connections(processed_map, tile_number, tile_position, defining_local_position, local_position, connect_number,
                                connect_position, global_tile)


def world_vertices_calculation(global_map):
    """
        Добавляет зонам доступности сквозную нумерацию и заменяет номера тайлов
    """
    number_world_vertices = []
    for number_global_line, global_line in enumerate(global_map):
        for number_global_tile, global_tile in enumerate(global_line):
            matching_dict = {}
            print(f"global_tile.vertices  {global_tile.vertices}")
            for vertice in global_tile.vertices:
                matching_dict[vertice.number] = number_world_vertices
                print(f"matching_dict - {matching_dict}, vertice.number - {vertice.number}, number_world_vertices - {number_world_vertices}")
                vertice.number = number_world_vertices
                number_world_vertices += 1
            print(f"matching_dict - {matching_dict}")

            
            #Добавление в тайлы мировых номеров зон доступности
            for number_line, line in enumerate(global_tile.chunk):
                for number_tile, tile in enumerate(line):
                    if tile.vertices in matching_dict:
                        try:
                            tile.vertices = matching_dict[tile.vertices]
                        except:
                            print(f"tile.vertices - {tile.vertices}, matching_dict - {matching_dict}")

@timeit
def defining_vertices(processed_map):
    """
        Определение независимых областей на локациях и связей между ними для последующей работы с алгоритмом A*
    """ 
    class Availability_field:
        def __init__(self, number, tile):
            self.number = number
            self.global_number = number
            self.tiles = [tile]
            
    banned_tuple = ('~', '▲')
    for number_global_line, global_line in enumerate(processed_map):
        for number_global_tile, global_tile in enumerate(global_line):
            number_field = 0
            list_availability_fields = []
            for number_line in range(len(global_tile.chunk)):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    if not(tile.icon in banned_tuple):
                            
                        #Обработка тайла слева
                        if number_tile > 0 and global_tile.chunk[number_line][number_tile - 1].vertices >= 0:
                            if tile.level == global_tile.chunk[number_line][number_tile - 1].level or tile.stairs or global_tile.chunk[number_line][number_tile - 1].stairs:
                                tile.vertices = global_tile.chunk[number_line][number_tile - 1].vertices
                                list_availability_fields[tile.vertices].tiles.append([number_line, number_tile])

                        #Обработка тайла сверху
                        if number_line > 0 and global_tile.chunk[number_line - 1][number_tile].vertices >= 0:
                            if tile.level == global_tile.chunk[number_line - 1][number_tile].level or tile.stairs or global_tile.chunk[number_line - 1][number_tile].stairs:
                                #Обработка крайней левой линии
                                if number_tile == 0 and number_line > 0:
                                    tile.vertices = global_tile.chunk[number_line - 1][number_tile].vertices
                                    list_availability_fields[tile.vertices].tiles.append([number_line, number_tile]) 
                                
                                #Если тайл обрабатывался
                                if tile.vertices >= 0:
                                    up = global_tile.chunk[number_line - 1][number_tile].vertices
                                    if list_availability_fields[tile.vertices].global_number < list_availability_fields[up].global_number:
                                        check_number = up
                                        count = 0 
                                        while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                            if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                                check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                                list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                            else:
                                                break
                                            if count == 20:
                                                break
                                            count += 1
                                        list_availability_fields[up].global_number = list_availability_fields[tile.vertices].global_number
                                        
                                    elif list_availability_fields[tile.vertices].global_number > list_availability_fields[up].global_number:
                                        check_number = tile.vertices
                                        count = 0 
                                        while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                            if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                                check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                                list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                            else:
                                                break
                                            if count == 20:
                                                break
                                            count += 1
                                        list_availability_fields[tile.vertices].global_number = list_availability_fields[up].global_number
                                            
                                #Если тайл не обрабатывался
                                elif tile.vertices == -1:
                                    tile.vertices = global_tile.chunk[number_line - 1][number_tile].vertices
                                    list_availability_fields[tile.vertices].tiles.append([number_line, number_tile])
                                
                                
                        #Если тайл еще не обрабатывался
                        if tile.vertices == -1:
                            tile.vertices = number_field
                            list_availability_fields.append(Availability_field(number_field, [number_line, number_tile]))
                            number_field += 1
            
            #Повторный проход по лестницам
            for number_line in range(len(global_tile.chunk)):
                for number_tile, tile in enumerate(global_tile.chunk[number_line]):
                    if tile.stairs:
                        if 0 < number_line and global_tile.chunk[number_line - 1][number_tile].vertices >= 0:
                            up = global_tile.chunk[number_line - 1][number_tile]
                            if list_availability_fields[tile.vertices].global_number < list_availability_fields[up.vertices].global_number:
                                check_number = up.vertices
                                count = 0 
                                while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                    if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                        check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                        list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                    else:
                                        break
                                    if count == 20:
                                        break
                                    count += 1
                                list_availability_fields[up.vertices].global_number = list_availability_fields[tile.vertices].global_number

                            elif list_availability_fields[tile.vertices].global_number > list_availability_fields[up.vertices].global_number:
                                check_number = tile.vertices
                                count = 0 
                                while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                    if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                        check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                        list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                    else:
                                        break
                                    if count == 20:
                                        break
                                    count += 1
                                list_availability_fields[tile.vertices].global_number = list_availability_fields[up.vertices].global_number

                        if number_line < (len(global_tile.chunk) - 1) and global_tile.chunk[number_line + 1][number_tile].vertices >= 0:
                            down = global_tile.chunk[number_line + 1][number_tile]
                            if list_availability_fields[tile.vertices].global_number < list_availability_fields[down.vertices].global_number:
                                check_number = down.vertices
                                count = 0 
                                while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                    if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                        check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                        list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                    else:
                                        break
                                    if count == 20:
                                        break
                                    count += 1
                                list_availability_fields[down.vertices].global_number = list_availability_fields[tile.vertices].global_number

                            elif list_availability_fields[tile.vertices].global_number > list_availability_fields[down.vertices].global_number:
                                check_number = tile.vertices
                                count = 0 
                                while True: #Цикл, который проверит номер и глобальный номер на одинаковость и если нет, то повторит это с указанным глобальным номером
                                    if list_availability_fields[check_number].global_number != list_availability_fields[check_number].number:
                                        check_number = list_availability_fields[list_availability_fields[check_number].global_number].global_number
                                        list_availability_fields[list_availability_fields[check_number].global_number].global_number = list_availability_fields[tile.vertices].global_number
                                    else:
                                        break
                                    if count == 20:
                                        break
                                    count += 1
                                list_availability_fields[tile.vertices].global_number = list_availability_fields[down.vertices].global_number
                            
                   
            for field in list_availability_fields:
                if field.number != field.global_number:
                    field.global_number = list_availability_fields[field.global_number].global_number
            
            for availability_field in list_availability_fields:
                for tile in availability_field.tiles:
                    global_tile.chunk[tile[0]][tile[1]].vertices = availability_field.global_number
            
                            
def diversity_field_tiles(processed_map):
    """
        Делает тайлы разнообразными в тайловых полях, не требующих определения краёв.
    """
    tiles_dict =    {
                    'F': ('0', '1', '2', '3', '4', '5', '6', '7'),
                    'u': ('0', '1'),
                    'j': ('0', '1'),
                    'A': ('0', '1'),
                    'i': ('0', '1', '2', '3'),
                    }
    for number_line in range(len(processed_map)):
        for number_tile in range(len(processed_map[number_line])):
            if processed_map[number_line][number_tile].icon in tiles_dict:
                processed_map[number_line][number_tile].type = random.choice(tiles_dict[processed_map[number_line][number_tile].icon])

def big_structures_generate(processed_map, managing_map):
    """
        Генерирует моря по методу горных озёр
    """
    chunk_size = len(processed_map)//len(managing_map)
    for managing_line in range(len(managing_map)):
        for managing_tile in range(len(managing_map[managing_line])):
            if managing_map[managing_line][managing_tile] == 5:
                if random.randrange(10)//5 > 0:
                    mountain_gen(processed_map, managing_line*chunk_size + chunk_size//3, managing_tile*chunk_size + chunk_size//3,
                             random.randrange(chunk_size//2, chunk_size), random.randrange(1, 3), random.randrange(1, 3), '~', ('.'))
                else:
                    lake_gen(processed_map, managing_line*chunk_size + chunk_size//3, managing_tile*chunk_size + chunk_size//3,
                             random.randrange(2, 5), '~', ('.'))
            if managing_map[managing_line][managing_tile] == 4:
                mountain_gen(processed_map, managing_line*chunk_size + chunk_size//3, managing_tile*chunk_size + chunk_size//3,
                             random.randrange(chunk_size//2, chunk_size), random.randrange(1, 3), random.randrange(1, 3), 'C', ('.'))

def big_structures_writer(processed_map, managing_map):
    """
        Отрисовывает моря и каньоны на карте локаций
    """
    chunk_size = len(managing_map)//len(processed_map)
    for number_line in range(len(managing_map)):
        for number_tile in range(len(managing_map[number_line])):
            if managing_map[number_line][number_tile] == '~':
                processed_map[number_line//chunk_size][number_tile//chunk_size] = ['~', 'sea', ['~'], ['.', 's', 'o'], 50, [12.0, 18.0]]

            if managing_map[number_line][number_tile] == 'C':
                processed_map[number_line//chunk_size][number_tile//chunk_size] = ['C', 'big canyons', ['C'], ['.', 'o', '▲'], 20, [20.0,35.0]]


def lake_gen(processed_map, position_y, position_x, size, add_icon, filling_icon):
    """
        Новый генератор озёр

    """
    lake_dict = {
                    2: [2, 4, 6, 6, 4, 2],
                    3: [3, 7, 9, 9, 11, 11, 11, 9, 9, 7, 3],
                    4: [4, 10, 14, 16, 18, 18, 20, 20, 20, 22, 22, 22, 22, 20, 20, 20, 18, 18, 16, 14, 10, 4],
                }
    
    size_lake = len(lake_dict[size])
    for step in range(size_lake):
        if random.randrange(5)//4 > 0:
            position_x += random.randrange(-1, 2)
        offset_x = (size_lake - lake_dict[size][step])//2
        for step_print in range(lake_dict[size][step]):
            if 1 < position_y < len(processed_map) - 2 and 1 < position_x + offset_x + step_print < len(processed_map) - 2:
                if processed_map[position_y][position_x + offset_x + step_print - 1] != add_icon:
                    processed_map[position_y][position_x + offset_x + step_print - 1] = random.choice(filling_icon)
                if processed_map[position_y][position_x + offset_x + step_print + 1] != add_icon:
                    processed_map[position_y][position_x + offset_x + step_print + 1] = random.choice(filling_icon)
                if processed_map[position_y - 1][position_x + offset_x + step_print] != add_icon:
                    processed_map[position_y - 1][position_x + offset_x + step_print] = random.choice(filling_icon)
                if processed_map[position_y + 1][position_x + offset_x + step_print] != add_icon:
                    processed_map[position_y + 1][position_x + offset_x + step_print] = random.choice(filling_icon)
                processed_map[position_y][position_x + offset_x + step_print] = add_icon
        position_y += 1
        
                
def mountain_gen(processed_map, position_y, position_x, size, add_position_y_to_step, start_quantity_step, add_icon, filling_icon):
    """
        Генерация гор и водоёмов
    """
    quantity_step = start_quantity_step
    type_generate = 'evenly'
    direction = random.randrange(2)
    for step in range(size):
        if len(processed_map) - 2 > position_y >= 1:
            if 2 < position_x < len(processed_map[0]):
                processed_map[position_y][position_x - 1] = random.choice(filling_icon)
                processed_map[position_y][position_x - 2] = random.choice(filling_icon)
                if add_position_y_to_step == 2:
                    processed_map[position_y + 1][position_x - 1] = random.choice(filling_icon)
                    processed_map[position_y + 1][position_x - 2] = random.choice(filling_icon)
            for i in range(quantity_step + 1):
                if 1 < position_x + i + 2 < len(processed_map[0]) - 2 - i:
                    processed_map[position_y][position_x + i] = add_icon
                    processed_map[position_y][position_x + i + 1] = random.choice(filling_icon)
                    processed_map[position_y][position_x + i + 2] = random.choice(filling_icon)
                    if type_generate == 'left' and random.randrange(10)//9 > 0:
                        position_x -= 1
                    if type_generate == 'right' and random.randrange(10)//9 > 0:
                        position_x += 1
                    if add_position_y_to_step == 2:
                        processed_map[position_y + 1][position_x + i] = add_icon
                        processed_map[position_y + 1][position_x + i + 1] = random.choice(filling_icon)
                        processed_map[position_y + 1][position_x + i + 2] = random.choice(filling_icon)
                    if step == 0:
                        processed_map[position_y - 1][position_x + i] = random.choice(filling_icon)
                    if step == size - 1:
                        processed_map[position_y + 1][position_x + i] = random.choice(filling_icon)

        if direction == 0:
            if random.randrange(20)//15 > 0:
                type_generate = 'left'
            elif random.randrange(20)//15 > 0:
                type_generate = 'right'
            elif random.randrange(20)//15 > 0:
                type_generate = 'evenly'
        elif direction == 1:
            if random.randrange(20)//15 > 0:
                type_generate = 'right'
            elif random.randrange(20)//15 > 0:
                type_generate = 'left'
            elif random.randrange(20)//15 > 0:
                type_generate = 'evenly'
                
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

def mountains_generate(all_tiles_map, chunks_map):
    """
        Генерация гор и озёр по методу горных озёр
    """
    chunk_size = len(all_tiles_map)//len(chunks_map)
    for number_line in range(len(chunks_map)):
        for number_tile in range(len(chunks_map[number_line])):
            if chunks_map[number_line][number_tile][0] == '▲':
                mountain_gen(all_tiles_map, number_line*chunk_size + random.randrange(chunk_size//2),
                             number_tile*chunk_size + random.randrange(chunk_size//2), random.randrange(10, 25), 2, 0, '▲', ('o', '.', ','))
            elif chunks_map[number_line][number_tile][0] == 'A':
                mountain_gen(all_tiles_map, number_line*chunk_size + random.randrange(chunk_size//2),
                             number_tile*chunk_size + random.randrange(chunk_size//2), random.randrange(5, 10), 2, 0, '▲', ('o', '.', ','))

            elif chunks_map[number_line][number_tile][0] in ('A', '.', 'S') and random.randrange(20)//18 > 0:
                mountain_gen(all_tiles_map, number_line*chunk_size + random.randrange(chunk_size//2),
                             number_tile*chunk_size + random.randrange(chunk_size//2), random.randrange(2, 6), 2, 0, 'i', ('i'))
                
            #elif chunks_map[number_line][number_tile][0] == 'P' and random.randrange(20)//10 > 0:
            #    mountain_gen(all_tiles_map, number_line*chunk_size + random.randrange(chunk_size//2),
            #                 number_tile*chunk_size + random.randrange(chunk_size//2), random.randrange(10, 20), 1, 2, '~', ('u'))

            elif chunks_map[number_line][number_tile][0] == 'P' and random.randrange(20)//15 > 0:
                lake_gen(all_tiles_map, number_line*chunk_size + random.randrange(chunk_size//2),
                         number_tile*chunk_size + random.randrange(chunk_size//2), random.randrange(2, 5), '~', ('u'))

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ГЕНЕРАЦИЯ ОСНОВЫ КАРТЫ
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
    
@timeit
def global_region_generate(global_grid):
    """
        Генерирует карту глобальных регионов

        Типы глобальных регионов:   0 - пустынный
                                    1 - горный
                                    2 - зелёный
                                    3 - солёный
                                    4 - каньонный
                                    5 - водяной
                                    6 - пустыня
    """
    global_region_map = []
    for i in range(global_grid):
        global_region_map.append([random.randrange(7) for x in range(global_grid)])
    return global_region_map

@timeit
def region_generate(global_region_map, global_region_grid, region_grid):
    """
        На основании карты глобальных регионов, генерирует карту регионов содержащих зёрна возможных локаций
    """
    seed_dict = {  
                    0: [['j', '.', 'S', 'F']],      # Пустынный
                    1: [['A', '▲']],                # Горный
                    2: [['„', ',', 'P']],           # Живой
                    3: [[';', '.']],                # Солёный
                    4: [['A', '.']],                # Каньонный
                    5: [['S', '▲']],                # Водяной
                    6: [['j', '.']],                # Пустыня
                }

    raw_region_map = all_map_master_generate(global_region_map, region_grid, True, seed_dict, 0, False)
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
                    'A': ['A',  'cliff semi-desert',   ['A', '.', ','],       ['▲', 'o', 'i'],    7,        [35.0,50.0]],
                    'S': ['S',  'snake semi-desert',   ['A', '.', ','],       ['▲','o', 'i'],     7,        [35.0,50.0]],
                    '▲': ['▲',  'hills',               ['o', ','],            ['▲', '„', ','],   20,        [20.0,35.0]],
                    'B': ['▲',  'big hills',           ['▲', 'o'],            ['o'],             20,        [20.0,35.0]],
                    'C': ['C',  'canyons',             ['C', '.', ','],       ['.'],             20,        [20.0,35.0]],
                    'R': ['R',  'big canyons',         ['C'],                 ['.', 'o', '▲'],   20,        [20.0,35.0]],
                    '„': ['„',  'field',               ['u', '„', ','],       ['ü', 'o'],         5,        [20.0,35.0]],
                    ',': [',',  'dried field',         ['„', ','],            ['o', 'u'],         2,        [30.0,40.0]],
                    'P': ['P',  'forest',              ['P', '„'],            ['F', ','],         0,        [15.0,30.0]],
                    '~': ['~',  'salty lake',          ['~'],                 ['„', '.'],        20,        [25.0,40.0]],
                    ';': [';',  'saline land',         [':'],                 [':'],             15,        [40.0,50.0]],
                    'F': ['F',  'dried forest',        ['F', ','],            ['P', 'o'],        10,        [25.0,40.0]],
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
                    ':': ':',
                    'S': 'S',
                    'o': 'o',
                    'F': 'F',
                    'P': 'P',
                    '~': '~',
                    '`': '`',
                    'u': 'u',
                    's': 'u',
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

    banned_list = ['~', '▲', '`']
    
    for number_seed_line in range(len(chunks_map)):
        for number_seed in range(len(chunks_map[number_seed_line])):
            for number_line in range((number_seed_line)*chunk_size, (number_seed_line)*chunk_size + chunk_size):
                for number_tile in range((number_seed)*chunk_size, (number_seed)*chunk_size + chunk_size):
                    if random.randrange(10)//9 and not(processed_map[number_line][number_tile] in banned_list):
                        add_tile = random.choice(chunks_map[number_seed_line][number_seed][3])
                        if add_tile != ';' or (add_tile == ';' and processed_map[number_line][number_tile] == ':'):
                            processed_map[number_line][number_tile] = add_tile
                        elif add_tile == ';' and processed_map[number_line][number_tile] != ':':
                            processed_map[number_line][number_tile] = ':'

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

        field_tiles_tuple кортеж тайлов, по которым производится рассчёт

        not_the_first_layer - False если слой первый и единственный. True если слой расчитывается на предыдущем слое.

        random_pass - При включении случайным образом пропускается повышение уровня тайлов
    """
    minus_level_list = ['~', 'C', '`']
    plus_level_list = ['▲']
    stairs_list = ['O', 'A', 'P', 'B', 'Q', 'C', 'R', 'D']
    white_stairs_list = ['C']

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

                if tile.type in stairs_list and tile.icon in white_stairs_list:
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
            new_global_location = Location(seed[1], random.uniform(min(seed[5][0], seed[5][1]), max(seed[5][0], seed[5][1])), [], seed[0], seed[4], [len(global_map) - 1, len(new_global_line) - 1])
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
        add_descripion_2 = random.choice(description_two[2])
        if add_descripion_2 != '~':
            description_one[2].append(add_descripion_2)
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
                test_print += str(printing_map[number_line][number_tile].icon) + str(abs(printing_map[number_line][number_tile].level))
            test_print += '\n'
        print(test_print)
    else:
        test_print = ''
        for number_line in range(len(printing_map)):
            for number_tile in range(len(printing_map[number_line])):
                test_print += str(printing_map[number_line][number_tile]) + ' '
            test_print += '\n'
        print(test_print)

def minimap_create(global_map):
    """
        Создание миникарты на основе глобальной карты
    """
    minimap = []
    for number_line, line in enumerate(global_map):
        minimap_line = []
        for number_tile, tile in enumerate(line):
            minimap_line.append(Tile_minimap(tile.icon, tile.name, tile.price_move, tile.temperature))
        minimap.append(minimap_line)
        
    levelness_calculation(minimap, ('~', '▲', 'C', ';', 'o', ',', '„', 'S'), False, False)
    levelness_calculation(minimap, ('~', 'C', '`'), True, False)

    return minimap


"""
=========================================================================================================================================================
"""
if __name__ == '__main__':
    """
        Запуск генератора отдельно от игры
    """
    pygame.init()

    dispay_size = [1200, 750]
    screen = pygame.display.set_mode(dispay_size, FULLSCREEN | DOUBLEBUF)
    pygame.display.set_caption("My Game")

    #                                global_region_grid | region_grid | chunks_grid | mini_region_grid | tile_field_grid
    global_map = master_map_generate(       2,                2,            2,            5,                 5,    screen)
    sys.exit()

