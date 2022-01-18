import time
import pygame
import sys
import pickle
import logging
from library import mapGenerator
from library.resources import loading_all_sprites, minimap_dict_create
from library.classes import World, Person, Interfaсe
from library.gameEvents import return_npc, master_game_events
from library.gameOutput import master_pygame_draw, Offset_sprites
from library.gameInput import calculation_assemblage_point, master_player_action
from library.gamePassStep import master_pass_step, new_step_calculation
from library.characterNPC import NPC
from libraryNPC.characterMain import NewNPC


garbage = ['░', '▒', '▓', '█', '☺']

"""

    РЕАЛИЗОВАТЬ:

    1)Взрывчатка и разрушения. Добавить тайлам параметры веса и устойчивости. При воздействии, 
    рассчитывать разрушение и/или сползание.
    2)Так как под тайлами фактически не идет просчёт уровней ниже, добавить им описание коренной 
    породы, которая обнажится при разрушении.
    3)Вся работа с координатами через координаты в формате world_position, то есть, в формате мировых координат.
    4)Переписать всё управление персонажами в отдельный модуль, заранее проработав все необходимые им механики.

    СПИСОК ИЗВЕСТНЫХ БАГОВ:
    При оставлении персонажем активности в 0х координатах, активность получает странные координаты и 
    не остаётся под персонажем (в частности, лёгкие шаги). #ИСПРАВЛЕНО

    ТЕМАТИКА:
    Всё, что мне нравится. Персонажи как в хороший плохой злой, вяленое конское мясо и гремучие змеи!

    ОПИСАНИЕ ТИПОВ КООРДИНАТ:

    Существует 4 типа координат:

    Глобальные координаты (global_position) - координаты локации глобальной карты, на которой в 
    данный момент находится персонаж, NPC или существо.

    Динамические координаты (dynamic_position) - координаты персонажа игрока на динамическом чанке. 
    Первичны для персонажа и используются только им.

    Локальные координаты (local_position) - местоположение персонажа, NPC или существа внутри локации.

    Мировые координаты (world_position) - рассчитываются из локальных и глобальных координат для удобства 
    работы с координатами.

    ТРЕБУЮЩИЕСЯ NPC ПЕРСОНАЖАМ МЕХАНИКИ:
    1)Перемещение в любую доступную точку
    2)Преследование
    3)Убегание
    4)Атака ближняя и дальняя
    5)Случайное перемещение для существ
    6)Полёт
    
"""




"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    УПРАВЛЯЮЩИЙ БЛОК
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


def save_map(global_map, minimap, vertices_graph, vertices_dict):
    """
        Сохранение игровой карты через pickle
    """
    all_save = [global_map, minimap, vertices_graph, vertices_dict]

    with open("save/saved_map.pkl", "wb") as fp:
        pickle.dump(all_save, fp)


def load_map():
    """
        Загрузка игровой карты через pickle
    """
    with open("save/saved_map.pkl", "rb") as fp:
        all_load = pickle.load(fp)
    
    return all_load[0], all_load[1], all_load[2], all_load[3]


def save_game(global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step, vertices_graph, 
                                                                                                vertices_dict):
    """
        Сохраняет игровой процесс
    """
    all_save = [global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step, vertices_graph, 
                                                                                                vertices_dict]

    with open("save/save_game.pkl", "wb") as fp:
        pickle.dump(all_save, fp)


def load_game():
    """
        Загружает игровой процесс
    """
    with open("save/save_game.pkl", "rb") as fp:
        all_load = pickle.load(fp)
        
    return all_load[0], all_load[1], all_load[2], all_load[3], all_load[4], all_load[5], all_load[6], all_load[7], \
                                                                                                        all_load[8]


class button_rect(pygame.sprite.Sprite):
    """ Содержит спрайты поверхностей """

    def __init__(self, y, x, size_y, size_x, color, text):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font('freesansbold.ttf', 10)
        self.textSurf = self.font.render(text, 1, (255, 255, 255))
        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.image.blit(self.textSurf, [size_x/2 , size_y/2])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 0
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)


def master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list, fill = True):
    """
        Отрисовывает игровое меню
    """
    if fill:
        screen.fill((255, 255, 255))
    step = 0
    for menu in menu_list:
        if menu == menu_selection:
            if button_selection:
                button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (155, 200, 155), menu).draw(screen)
            else:
                button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (200, 155, 155), menu).draw(screen)
        else:
            button_rect(dispay_size[1]/2 - 200 + step, dispay_size[0]/2, 80, 200, (155, 155, 155), menu).draw(screen)
        step += 100

    pygame.display.flip()


def settings_loop(screen, dispay_size, fast_generation:bool, global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid):
    """
        Здесь происходит переключение настроек
    """
    menu_selection = 'fast_generation'
    button_selection = False
    menu_list = ['fast_generation', 'exit_settings']
    master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
    settings_loop = True
    while settings_loop:
        time.sleep(0.2)
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        if menu_selection == 'exit_settings' and button_selection: #Выход из настроек
            settings_loop = False
        elif menu_selection == 'fast_generation' and button_selection:
            fast_generation = not fast_generation
        master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
        button_selection = False
        
                    
def preparing_a_new_game(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid, chunk_size, 
                         screen, sprites_dict, minimap_dict):
    """
        Производит подготовку к началу новой игры и её запуск
    """
    global_map, raw_minimap, vertices_graph, vertices_dict = mapGenerator.master_map_generate(global_region_grid, 
                                                region_grid, chunks_grid, mini_region_grid, tile_field_grid, screen)
        
    person = Person([2, 2], [2, 2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
    calculation_assemblage_point(global_map, person, chunk_size)
    enemy_list = [
                    return_npc([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 'horseman'),
                    return_npc([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 'riffleman'),
                    return_npc([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 'coyot'),
                    return_npc([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 'unknown'),
                 ]
    world = World() #Описание текущего состояния игрового мира

    game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, True, [],
              sprites_dict, minimap_dict, vertices_graph, vertices_dict)


def in_game_main_loop(screen, global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step, vertices_graph):
    """
        Меню в уже загруженной игре
    """
    menu_selection = 'continue the game'
    button_selection = False
    menu_list = ['continue the game', 'save game', 'game settings', 'end game', 'leave the game']
    screen.fill((255, 255, 255))
    screen.set_alpha(60)
    master_game_menu_draw(screen, [1200, 750], menu_selection, button_selection, menu_list, False)
    in_game_main_loop = True
    game_loop = True
    while in_game_main_loop:
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        master_game_menu_draw(screen, [1200, 750], menu_selection, button_selection, menu_list, False)
        time.sleep(0.2)
        if menu_selection == 'continue the game' and button_selection:
            in_game_main_loop = False
        if menu_selection == 'save game' and button_selection:
            save_game(global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step, vertices_graph)
            in_game_main_loop = False
        if menu_selection == 'end game' and button_selection: #Закрытие игры
            in_game_main_loop = False
            game_loop = False
        if menu_selection == 'leave the game' and button_selection: #Закрытие игры
            sys.exit()
        
        button_selection = False
    return game_loop


def menu_calculation(menu_list, menu_selection, button_selection):
    """
        Обрабатывает перемещение по любому игровому меню
    """
    pygame.event.clear()
    for number_menu, menu in enumerate(menu_list):
        if menu == menu_selection:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if number_menu < len(menu_list) - 1:
                                return menu_list[number_menu + 1], button_selection
                            else:
                                return menu_list[0], button_selection
                            
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            if number_menu > 0:
                                return menu_list[number_menu - 1], button_selection
                            else:
                                return menu_list[-1], button_selection
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            return menu_selection, True
            
    menu_selection, button_selection


def minimap_create(raw_map, minimap_dict, size_tile):
    """
        Создаёт игровую миникарту для постоянного использования
    """
    minimap_surface = pygame.Surface((len(raw_map)*size_tile, len(raw_map)*size_tile))
    for number_line, line in enumerate(raw_map):
        for number_tile, tile in enumerate(line):
            print_sprite = minimap_dict[tile.icon][tile.type]
            print_sprite.rect.top = number_line*size_tile
            print_sprite.rect.left = number_tile*size_tile
            print_sprite.draw(minimap_surface)
    return minimap_surface         


def main_loop():
    """
        Здесь работает игровое меню
        
    """
    logging.basicConfig(filename="save/logging.log", filemode="w", level=logging.DEBUG)
    
    global_region_grid = 3
    region_grid = 3
    chunks_grid = 3
    mini_region_grid = 5
    tile_field_grid = 5

    chunk_size = mini_region_grid * tile_field_grid #Определяет размер одного игрового поля и окна просмотра. Рекоммендуемое значение 25.
    
    pygame.init()

    dispay_size = [1300, 730] #было [1200, 750]
    screen = pygame.display.set_mode(dispay_size)#, FULLSCREEN | DOUBLEBUF)
    pygame.display.set_caption("My Game")

    #Загрузка и создание поверхностей всех спрайтов
    sprites_dict = loading_all_sprites()
    minimap_dict = minimap_dict_create()

    fast_generation = False #Переключение отображения генерации между прогресс-баром и полным выводом на экран генерирующейся карты
    menu_selection = 'new_game'
    button_selection = False
    menu_list = ['new_game', 'load_game', 'load_map', 'settings', 'about', 'exit_game']
    #Предварительная отрисовка игрового меню
    master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

    while main_loop:
        button_selection = False
        time.sleep(0.2)
        menu_selection, button_selection = menu_calculation(menu_list, menu_selection, button_selection)
        master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
        
        if menu_selection == 'new_game' and button_selection: #Подготовка и запуск новой игры
            button_selection = False
            preparing_a_new_game(global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid, chunk_size, screen,
                                 sprites_dict, minimap_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

        if menu_selection == 'load_game' and button_selection:
            menu_selection = 'new_game'
            button_selection = False
            global_map, person, chunk_size, enemy_list, raw_minimap, activity_list, step, vertices_graph, vertices_dict = load_game()
            world = World() #Описание текущего состояния игрового мира\

            game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, False,
                      [activity_list, step], sprites_dict, minimap_dict, vertices_graph, vertices_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)
            
        if menu_selection == 'load_map' and button_selection:
            menu_selection = 'new_game'
            button_selection = False
            global_map, raw_minimap, vertices_graph, vertices_dict = load_map()
                
            person = Person([2, 2], [2, 2], [], [chunk_size//2, chunk_size//2], [chunk_size//2, chunk_size//2])
            calculation_assemblage_point(global_map, person, chunk_size)
            enemy_list = [
                    return_npc([len(global_map)//2, len(global_map)//2], [chunk_size//2, chunk_size//2], 'horseman'),
                    return_npc([len(global_map)//3, len(global_map)//3], [chunk_size//2, chunk_size//2], 'riffleman'),
                    return_npc([len(global_map)//4, len(global_map)//4], [chunk_size//2, chunk_size//2], 'coyot'),
                    return_npc([len(global_map)//5, len(global_map)//5], [chunk_size//2, chunk_size//2], 'unknown'),]
            world = World() #Описание текущего состояния игрового мира

            game_loop(global_map, person, chunk_size, enemy_list, world, screen, raw_minimap, True, [],
                      sprites_dict, minimap_dict, vertices_graph, vertices_dict)
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)

        if menu_selection == 'exit_game' and button_selection: #Закрытие игры
            sys.exit()
        if menu_selection == 'settings' and button_selection:
            settings_loop(screen, dispay_size, fast_generation, global_region_grid, region_grid, chunks_grid, mini_region_grid, tile_field_grid)
            button_selection = False
            master_game_menu_draw(screen, dispay_size, menu_selection, button_selection, menu_list)


def game_loop(global_map:list, person, chunk_size:int, enemy_list:list, world, screen, raw_minimap,
              new_game:bool, load_pack:list, sprites_dict:dict, minimap_dict:dict, vertices_graph, vertices_dict):
    """
        Здесь происходят все игровые события
        
    """
    if new_game:
        activity_list = []
        step = 0
        save_map(global_map, raw_minimap, vertices_graph, vertices_dict) #тестовое сохранение карты
    else:
        activity_list = load_pack[0]
        step = load_pack[1]
        
    go_to_print = Interfaсe([], [], True)
    global changing_step
    mode_action = 'move'
    clock = pygame.time.Clock()#
    game_fps = 100#

    global_interaction = [] #Глобальные происшествия

    pygame.display.flip()

    offset_sprites = Offset_sprites()

    landscape_layer = [[[]]]
    activity_layer = [[[]]]
    entities_layer = [[[]]]
    
    minimap_surface = minimap_create(raw_minimap, minimap_dict, 15)
    finishing_surface = pygame.Surface(((chunk_size + 1)*30, (chunk_size + 1)*30))

    settings_for_intermediate_steps = [5, 6]
    mouse_position = (0, 0)

    #Предварительная отрисовка игрового окна
    screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps = master_pygame_draw(person, chunk_size,
                        go_to_print, global_map, mode_action, enemy_list, activity_list, screen, minimap_surface,
                        minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                        entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap)

    enemy_list.append(NPC([2, 2], [2, 2], 'new_riffleman', 'new_riffleman', '☻', 'd0', 'Тестовый NPC', 'new_riffleman'))
    kwargs = {"ids_list": list(), "player": person}
    enemy_list.append(NewNPC([2, 2], [2, 2], 'super_riffleman', 'super_riffleman', '☺', 'd0', ' Новый тестовый NPC',
                             'super_riffleman', **kwargs))

    print('game_loop запущен')
    game_loop = True
    while game_loop:
        clock.tick(game_fps)
        interaction = []
        person.pointer_step = False #Сбрасывается перехват шага выводом описания указателя
        world.npc_path_calculation = False #Сброс предыдущего состояния поиска пути NPC персонажами
        master_pass_step(person)
        
        if not person.person_pass_step:
            mode_action, mouse_position = master_player_action(global_map, person, chunk_size, go_to_print, mode_action,
                                                        interaction, activity_list, step, enemy_list, mouse_position)
        if mode_action == 'in_game_menu':
            game_loop = in_game_main_loop(screen, global_map, person, chunk_size, enemy_list, raw_minimap,
                                                                                        activity_list, step)
            mode_action = 'move'
            
        step = new_step_calculation(enemy_list, person, step)
            
        start = time.time() #проверка времени выполнения
        calculation_assemblage_point(global_map, person, chunk_size) # Рассчёт динамического чанка
        #all_pass_step_calculations(person, enemy_list, mode_action, interaction)
        if not person.enemy_pass_step and not person.pointer_step:
            master_game_events(global_map, enemy_list, person, go_to_print, step, activity_list, chunk_size,
                               interaction, world, global_interaction, vertices_graph, vertices_dict)
        screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps = master_pygame_draw(
                    person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list, screen,
                    minimap_surface, minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                    entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap)
        

main_loop()
    

