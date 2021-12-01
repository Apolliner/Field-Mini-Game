"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется клиент игры, работающий с API.
"""

import os
import json
import pygame
import time
import requests
import asyncio
from pathlib import Path
from flask_restful import Resource
import os
import keyboard
from library.multiplayerOutput import master_pygame_draw, Offset_sprites
from library.classes import Interfaсe
from library.resources import loading_all_sprites, minimap_dict_create
from library.gameInput import request_press_button
from library.gamePassStep import master_pass_step, new_step_calculation


class Player:
    test_visible = False
    person_pass_step = False
    enemy_pass_step = False
    recalculating_the_display = True
    pointer_step = False
    def __init__(self):
        self.name = 'name'
        self.name_npc = 'player'
        self.type = '0'
        self.icon = '☺'
        self.assemblage_point = None
        self.dynamic_position = None
        self.chunks_use_map = []
        self.global_position = [5, 5]
        self.local_position = [5, 5]
        self.world_position = [5, 5]  # общемировое тайловое положение
        self.number_chunk = 0
        self.level = 0
        self.vertices = 0
        self.direction = 'center'
        self.speed = 1

        self.pass_draw_move = False

    def global_and_local_calculate(self, chunk_size):
        """ Принимает размер чанка, рассчитывает свои координаты по мировым координатам """
        self.global_position = [self.world_position[0] // chunk_size, self.world_position[1] // chunk_size]
        self.local_position = [self.world_position[0] % chunk_size, self.world_position[1] % chunk_size]



def new_player_create(base_url, player, headers, chunk_size):
    raw_answer = requests.post(f'{base_url}/player_post', headers=headers)
    data = json.loads(raw_answer.content)
    if "player_id" in data:
        player_id = data["player_id"]
        time.sleep(2)
        player, enemy_list = get_player(base_url, player, headers, player_id, list(), chunk_size)
        return player, enemy_list
    return None

def get_player(base_url, player, headers, player_id, enemy_list, chunk_size):
    """ Запрос к API на получение персонажа игрока и сохранение этих данных """
    raw_player = requests.get(f'{base_url}/player/{player_id}', headers=headers)
    data_player = json.loads(raw_player.content)
    player = player_direction_calculate(player, player.world_position, data_player["world_position"])
    #print(F"\n\ndata_player['enemies'] - {data_player['enemies']}\n\n")
    #print(F"\n\ndata_player - {data_player}\n\n")
    #print(F"data_player - {data_player}")
    player.id = player_id
    player.name = data_player['name']
    player.type = data_player['type']
    player.icon = data_player['icon']
    player.dynamic = data_player['dynamic_position']
    player.chunks_use_map = chunk_recalculate(json.loads(data_player['chunks_use_map']))
    player.world_position = data_player["world_position"]
    player.level = data_player['level']
    player.vertices = data_player['vertices']
    #player.direction = data_player['direction']
    player.assemblage_point = data_player['assemblage_point']
    player.global_and_local_calculate(chunk_size)
    enemy_list = enemy_list_calculations(enemy_list, data_player['enemies'], chunk_size)

    return player, enemy_list


class Enemy:
    """ Обманка для рендера, делающая вид, что другие персонажи это NPC """
    def __init__(self, id, name, icon, type, world_position):
        self.id = id
        self.global_position = [0, 0]
        self.local_position = [0, 0]
        self.pass_step = 0
        self.on_the_screen = False
        self.steps_to_new_step = 1
        self.visible = True
        self.direction = 'center'
        self.offset = [0, 0]
        self.delete = False
        self.world_position = world_position

        self.name = name
        self.name_npc = "Другой игрок"
        self.icon = icon
        self.type = type
        self.person_description = "Другой игрок"
        self.speed = 1
        self.type_npc = 'hunter'
        self.pass_description = ''
        self.description = ''

    def global_and_local_calculate(self, chunk_size):
        """ Принимает размер чанка, рассчитывает свои координаты по мировым координатам """
        self.global_position = [self.world_position[0] // chunk_size, self.world_position[1] // chunk_size]
        self.local_position = [self.world_position[0] % chunk_size, self.world_position[1] % chunk_size]


def enemy_list_calculations(enemy_list, enemies, chunk_size):
    """ Получает старый и новый список противников, добавляет новых, обновляет старых """
    checked_enemy = list()
    for enemy in enemy_list:
        if enemy.id in enemies:
            enemy.name = enemies[enemy.id]['name']
            enemy.icon = enemies[enemy.id]['icon']
            enemy.type = enemies[enemy.id]['type']
            enemy.world_position = enemies[enemy.id]["world_position"]
            enemy.global_and_local_calculate(chunk_size)
            enemy = player_direction_calculate(enemy, enemy.world_position, enemies[enemy.id]['world_position'])
        checked_enemy.append(int(enemy.id))
    #print(F"\n\nchecked_enemy  - {checked_enemy }\n\n")
    #print(F"\n\nenemies - {enemies}\n\n")
    for enemy in enemies:
        #print(F"enemy - {enemy}, if enemy not in checked_enemy - {int(enemy) not in checked_enemy}")
        if int(enemy) not in checked_enemy:
            enemy_data = enemies[enemy]
            new_enemy = Enemy(enemy_data['id'], enemy_data['name'], enemy_data['icon'], enemy_data['type'],
                                                                                        enemy_data['world_position'])
            new_enemy.global_and_local_calculate(chunk_size)
            enemy_list.append(new_enemy)

    #print()
    #for enemy in enemy_list:
    #    print(F"enemy.global_position - {enemy.global_position}, enemy.local_position - {enemy.local_position}"
    #          F"enemy.world_position - {enemy.world_position}")
    return enemy_list


def chunk_recalculate(chunk):
    #print(F"\n\nchunk - {chunk}\n\n")
    class Tile:
        level = 0
        vertices = 0
        list_of_features = 0
        description = 'description'
        def __init__(self, icon, type):
            self.icon = icon
            self.type = type
    ready_chunk = list()
    for line in chunk:
        ready_line = list()
        for tile in line:
            ready_line.append(Tile(tile[0], tile[1]))
        ready_chunk.append(ready_line)
    return ready_chunk

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


def post_player_request(person, request, base_url, headers, player_id):
    """
        Отправка запроса на сервер
    """
    raw_player = requests.post(f'{base_url}/player/{player_id}', data=request, headers=headers)

def player_request(global_map, person, chunk_size, go_to_print, mode_action, interaction, mouse_position, base_url,
                                                                                                            headers):
    """
        Запрашивает действие, отправляет запрос на сервер
    """
    mode_action = 'move'
    mode_action, pressed_button, mouse_position = request_press_button(global_map, person, chunk_size, go_to_print,
                                                                       mode_action, interaction, mouse_position)
    request = {
                "type": mode_action,
                "description": pressed_button
    }
    data_request = json.dumps(request)
    post_player_request(person, data_request, base_url, headers, person.id)

def player_direction_calculate(player, old_world_position, new_world_position):
    """ Рассчитывает направление движения игрока """
    if new_world_position == [old_world_position[0] - 1, old_world_position[1]]:
        player.direction = 'up'
    elif new_world_position == [old_world_position[0] + 1, old_world_position[1]]:
        player.direction = 'down'
    elif new_world_position == [old_world_position[0], old_world_position[1] - 1]:
        player.direction = 'left'
    elif new_world_position == [old_world_position[0], old_world_position[1] + 1]:
        player.direction = 'right'
    elif new_world_position == [old_world_position[0], old_world_position[1]]:
        player.direction = 'center'
    return player

def print_chunk(person):

    print_box = ''
    for line in person.chunks_use_map:
        print_line = ''
        for tile in line:
            print_line += tile.icon + tile.type
        print_box += print_line + '\n'

    print(F"\n\n{print_box}\n\n")


def main_loop():
    pygame.init()
    chunk_size = 25
    base_url = "http://127.0.0.1:5000"
    headers = {'Content-Type': 'application/json'}
    global_map = []
    dispay_size = [1300, 730]  # было [1200, 750]
    screen = pygame.display.set_mode(dispay_size)  # , FULLSCREEN | DOUBLEBUF)
    pygame.display.set_caption("My Game")

    # Загрузка и создание поверхностей всех спрайтов
    sprites_dict = loading_all_sprites()
    minimap_dict = minimap_dict_create()

    clock = pygame.time.Clock()  #
    game_fps = 100  #
    go_to_print = Interfaсe([], [], True)

    activity_list = []
    enemy_list = []
    step = 0

    global_interaction = []  # Глобальные происшествия

    pygame.display.flip()

    offset_sprites = Offset_sprites()

    landscape_layer = [[[]]]
    activity_layer = [[[]]]
    entities_layer = [[[]]]

    raw_minimap = list()

    minimap_surface = minimap_create(raw_minimap, minimap_dict, 15)
    finishing_surface = pygame.Surface(((chunk_size + 1) * 30, (chunk_size + 1) * 30))

    settings_for_intermediate_steps = [5, 6]
    mouse_position = (0, 0)

    mode_action = 'move'

    person = Player()

    person, enemy_list = new_player_create(base_url, person, headers, chunk_size)

    # Предварительная отрисовка игрового окна
    screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, \
                settings_for_intermediate_steps = master_pygame_draw(person, chunk_size,go_to_print, global_map,
                mode_action, enemy_list, activity_list, screen, minimap_surface, minimap_dict, sprites_dict,
                offset_sprites, landscape_layer, activity_layer, entities_layer, finishing_surface,
                settings_for_intermediate_steps, mouse_position, raw_minimap)


    while True:
        clock.tick(game_fps)
        interaction = []
        person.pointer_step = False

        master_pass_step(person)
        #person.direction = "center"
        if not person.person_pass_step:
            player_request(global_map, person, chunk_size, go_to_print, mode_action, list(), mouse_position, base_url,
                                                                                                            headers)
            time.sleep(0.1)
            person, enemy_list = get_player(base_url, person, headers, person.id, enemy_list, chunk_size)
        #print(F"\n\nenemy_list - {enemy_list}\n\n")
        #person.pass_draw_move = 0  # FIXME
        #person.direction = "down"  # FIXME
        #print(F"\nperson.direction - {person.direction}\n")
        #print(F"\nperson.pass_draw_move - {person.pass_draw_move}\n")
        #print()
        #for enemy in enemy_list:
        #    print(F"enemy.global_position - {enemy.global_position}, enemy.local_position - {enemy.local_position}")
        step = new_step_calculation(enemy_list, person, step)
        screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, \
                    settings_for_intermediate_steps = master_pygame_draw(person, chunk_size, go_to_print, global_map,
                    mode_action, enemy_list, activity_list, screen, minimap_surface, minimap_dict, sprites_dict,
                    offset_sprites, landscape_layer, activity_layer, entities_layer, finishing_surface,
                    settings_for_intermediate_steps, mouse_position, raw_minimap)

main_loop()
