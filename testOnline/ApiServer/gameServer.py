"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется сервер игры.
"""
import copy
import time
import json
import pickle
import random
from init import db
from Models.base import Base
from Models.player import Player as PlayerModel
from Models.playerRequest import PlayerRequest


def load_map():
    """
        Загрузка игровой карты через pickle
    """
    with open("save/saved_map.pkl", "rb") as fp:
        all_load = pickle.load(fp)
    #      global_map, raw_minimap, vertices_graph, vertices_dict
    return all_load[0], all_load[1], all_load[2], all_load[3]

class World:
    """ Содержит техническую информацию """
    chunk_size = 25

class Player:
    def __init__(self, id, name, icon, global_position, local_position, world_position):
        self.id = id
        self.name = name
        self.name_npc = 'player'
        self.type = '0'
        self.icon = icon
        self.assemblage_point = None
        self.dynamic_position = None
        self.chunks_use_map = []
        self.global_position = global_position
        self.local_position = local_position
        self.world_position = world_position  # общемировое тайловое положение
        self.number_chunk = 0
        self.level = 0
        self.vertices = 0
        self.direction = 'center'
        self.speed = 1

    def player_position_calculation(self, chunk_size):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        self.global_position = [self.world_position[0] // chunk_size, self.world_position[1] // chunk_size]
        self.local_position = [self.world_position[0] % chunk_size, self.world_position[1] % chunk_size]

    def calculation_dynamic_chunk(self, global_map, chunk_size):
        """ Рассчитывает динамический чанк, динамические координаты и точку сборки """
        assemblage_point = copy.deepcopy(self.global_position)
        dynamic_position = copy.deepcopy(self.local_position)
        if chunk_size//2 > self.local_position[0]:
            assemblage_point[0] -= 1
            dynamic_position[0] += chunk_size
        if chunk_size//2 > self.local_position[1]:
            assemblage_point[1] -= 1
            dynamic_position[1] += chunk_size

        lines = global_map[assemblage_point[0]:(assemblage_point[0] + 2)]
        assemblage_chunk = list()
        for line in lines:
            assemblage_chunk.append(line[assemblage_point[1]:(assemblage_point[1] + 2)])
        for number_line in range(len(assemblage_chunk)):
            for chunk in range(len(assemblage_chunk)):
                assemblage_chunk[number_line][chunk] = assemblage_chunk[number_line][chunk].chunk

        assemblage_chunk = self.gluing_location(assemblage_chunk, 2, chunk_size)

        final_chunk = list()
        for number_line, line in enumerate(assemblage_chunk):
            final_chunk_line = list()
            for number_tile, tile in enumerate(line):
                final_chunk_line.append(tile.icon + tile.type)
            final_chunk.append(final_chunk_line)

        #print_chunk = ''
        #for line in final_chunk:
        #    print_line = ''
        #    for tile in line:
        #        print_line += tile
        #    print_chunk + print_line + "\n"
        #print(F"\n\n{print_chunk}\n\n")

        self.chunks_use_map = final_chunk
        self.assemblage_point = assemblage_point
        self.dynamic_position = dynamic_position

    def gluing_location(self, raw_gluing_map, grid, count_block):
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
                        gluing_index = (number_region_line + number_location_line) + (
                                count_location // (grid * (count_block ** 2)) * (count_block - 1))  # определяет индекс
                        gluing_map[gluing_index].append(
                            raw_gluing_map[number_region_line][number_region][number_location_line][number_location])
                        count_location += 1
        return gluing_map


def get_tile_world(global_map, world_position, chunk_size):
    """
        Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
    """
    global_position = [world_position[0] // chunk_size, world_position[1] // chunk_size]
    local_position = [world_position[0] % chunk_size, world_position[1] % chunk_size]
    return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

def get_level_and_vertices(global_map, world_position, chunk_size):
    """
        Принимает мировые координаты, глобальную карту и размер чанка, возвращает высоту и зону доступности.
    """
    tile = get_tile_world(global_map, world_position, chunk_size)
    return tile.level, tile.vertices

def master_player_action(global_map, player, player_request, world):
    """ Рассчитывает передвижение персонажа """
    player.level, player.vertices = get_level_and_vertices(global_map, player.world_position, world.chunk_size)
    player.direction = 'center'
    player.activating_spawn = False

    if player_request is not None and player_request.description != 'none':
        if player_request.type == 'move':
            request_move(global_map, player, player_request, world.chunk_size)

    player.calculation_dynamic_chunk(global_map, world.chunk_size)
    return player


def request_move(global_map, player, player_request, chunk_size):
    """
        Меняет мировое местоположение персонажа
        Сначала происходит проверка не является ли следующий по пути тайл скалой, затем проверяется не находится ли он
        на другом уровне или лестницей или персонаж сейчас стоит на лестнице.
    """
    player_tile = get_tile_world(global_map, player.world_position, chunk_size)
    if player_request.description == 'up':
        up_tile = get_tile_world(global_map, [player.world_position[0] - 1, player.world_position[1]], chunk_size)
        if up_tile.icon != '▲' and (player_tile.level == up_tile.level or up_tile.stairs or player_tile.stairs):
            player.world_position[0] -= 1
            player.direction = 'up'
            player.type = 'u3'
    elif player_request.description == 'left':
        left_tile = get_tile_world(global_map, [player.world_position[0], player.world_position[1] - 1], chunk_size)
        if left_tile.icon != '▲' and (player_tile.level == left_tile.level or left_tile.stairs or player_tile.stairs):
            player.world_position[1] -= 1
            player.direction = 'left'
            player.type = 'l3'
    elif player_request.description == 'down':
        down_tile = get_tile_world(global_map, [player.world_position[0] + 1, player.world_position[1]], chunk_size)
        if down_tile.icon != '▲' and (player_tile.level == down_tile.level or down_tile.stairs or player_tile.stairs):
            player.world_position[0] += 1
            player.direction = 'down'
            player.type = 'd3'

    elif player_request.description == 'right':
        right_tile = get_tile_world(global_map, [player.world_position[0], player.world_position[1] + 1], chunk_size)
        if right_tile.icon != '▲' and (player_tile.level == right_tile.level or right_tile.stairs or player_tile.stairs):
            player.world_position[1] += 1
            player.direction = 'right'
            player.type = 'r3'

    player.player_position_calculation(chunk_size)  # Рассчитывает глобальное положение и номер чанка через метод


def player_model_update(player, player_model):
    """ Обновляет модель игрока """
    player_model.icon = player.icon
    player_model.name = player.name
    player_model.type = player.type
    player_model.x_dynamic = player.dynamic_position[1]
    player_model.y_dynamic = player.dynamic_position[0]
    player_model.x_world = player.world_position[1]
    player_model.y_world = player.world_position[0]
    player_model.chunk = json.dumps(player.chunks_use_map)
    player_model.level = player.level
    player_model.vertices = player.vertices
    player_model.assemblage_point_x = player.assemblage_point[1]
    player_model.assemblage_point_y = player.assemblage_point[0]
    player_model.direction = player.direction
    return player_model


def test_player_move(enemy, step, chunk_size):
    """ Тестовый персонаж, ходящий по кругу. """
    autopilot_list = [
    'down',
    'down',
    'down',
    'down',
    'down',
    'right',
    'right',
    'right',
    'right',
    'right',
    'up',
    'up',
    'up',
    'up',
    'up',
    'left',
    'left',
    'left',
    'left',
    'left',
    ]

    enemy.direction = autopilot_list[step%20]
    if enemy.direction = 'up':
        enemy.world_position[0] -= 1
    elif enemy.direction = 'down':
        enemy.world_position[0] += 1
    elif enemy.direction = 'left':
        enemy.world_position[1] -= 1
    elif enemy.direction = 'right':
        enemy.world_position[1] += 1

    enemy.player_position_calculation(chunk_size)


def main_loop():
    """

    СТРУКТУРА GAME_LOOP:
        загрузка игровой карты
        набирает пулл игроков
        запускает цикл
            запрашивает пулл игроков
            проходит циклом по пулу игроков.
                Получает запрос пользователя и удаляет его
                обрабатывает запрос пользователя
                записывает в БД результат рассчётов

    ИСПОЛЬЗУЕМЫЕ МОДЕЛИ:
        Player
            id
            x_dynamic
            y_dynamic
            x_global
            y_global
            x_local
            y_local
            chunk
            requests    ?

        PlayerRequest
            id
            player_id
            time
            type
            description

    """
    global_map, raw_minimap, vertices_graph, vertices_dict = load_map()
    step = 0
    world = World()
    players_dict = dict()
    names = ('Малыш Билли', 'Буффало Билл', 'Маленькая Верная Рука Энни Окли', 'Дикий Билл Хикок', 'Бедовая Джейн',
             'Бутч Кэссиди', 'Сандэнс Кид', 'Черный Барт')
    icons = ("☺", "☻")
    while True:
        players_model = PlayerModel.query.all()
        if players_model is not None:
            for player_model in players_model:
                if player_model.id not in players_dict:
                    players_dict[player_model.id] = Player(player_model.id, random.choice(names), random.choice(icons),
                                                           [2, 2], [2, 2], [40, 40])
                player = players_dict[player_model.id]
                player_request = PlayerRequest.query.filter_by(player_id=player.id).first()
                player = master_player_action(global_map, player, player_request, world)
                player_model = player_model_update(player, player_model)
                db.session.add(player_model)
                if player_request is not None:
                    db.session.delete(player_request)
                db.session.commit()
            step += 1

main_loop()