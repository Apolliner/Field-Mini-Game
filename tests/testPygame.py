import os
import time
import copy
import pygame
import random
import pickle
import numpy as np
from math import sin, cos, pi
from library.mapGenerator import master_map_generate
from library.resources import loading_all_sprites

person_x = 100
person_y = 100

fields = "........................."

WIDTH = 600
HEIGHT = 600
FPS = 60
# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()


def load_tile(filename):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', filename)).convert_alpha()

animations = {
    "standard": {
        '0': load_tile('tile_enemy_riffleman_down_0.png'),
        'l0': load_tile('tile_enemy_riffleman_left_0.png'),
        'l1': load_tile('tile_enemy_riffleman_left_1.png'),
        'l2': load_tile('tile_enemy_riffleman_left_2.png'),
        'l3': load_tile('tile_enemy_riffleman_left_3.png'),
        'r0': load_tile('tile_enemy_riffleman_right_0.png'),
        'r1': load_tile('tile_enemy_riffleman_right_1.png'),
        'r2': load_tile('tile_enemy_riffleman_right_2.png'),
        'r3': load_tile('tile_enemy_riffleman_right_3.png'),
        'd0': load_tile('tile_enemy_riffleman_down_0.png'),
        'd1': load_tile('tile_enemy_riffleman_down_1.png'),
        'd2': load_tile('tile_enemy_riffleman_down_2.png'),
        'd3': load_tile('tile_enemy_riffleman_down_3.png'),
        'u0': load_tile('tile_enemy_riffleman_up_0.png'),
        'u1': load_tile('tile_enemy_riffleman_up_1.png'),
        'u2': load_tile('tile_enemy_riffleman_up_2.png'),
        'u3': load_tile('tile_enemy_riffleman_up_3.png'),
    },
    "ford": {
        '0': load_tile('ford_animation\\tile_enemy_riffleman_down_0_ford.png'),
        'l0': load_tile('ford_animation\\tile_enemy_riffleman_left_0_ford.png'),
        'l1': load_tile('ford_animation\\tile_enemy_riffleman_left_1_ford.png'),
        'l2': load_tile('ford_animation\\tile_enemy_riffleman_left_2_ford.png'),
        'l3': load_tile('ford_animation\\tile_enemy_riffleman_left_3_ford.png'),
        'r0': load_tile('ford_animation\\tile_enemy_riffleman_right_0_ford.png'),
        'r1': load_tile('ford_animation\\tile_enemy_riffleman_right_1_ford.png'),
        'r2': load_tile('ford_animation\\tile_enemy_riffleman_right_2_ford.png'),
        'r3': load_tile('ford_animation\\tile_enemy_riffleman_right_3_ford.png'),
        'd0': load_tile('ford_animation\\tile_enemy_riffleman_down_0_ford.png'),
        'd1': load_tile('ford_animation\\tile_enemy_riffleman_down_1_ford.png'),
        'd2': load_tile('ford_animation\\tile_enemy_riffleman_down_2_ford.png'),
        'd3': load_tile('ford_animation\\tile_enemy_riffleman_down_3_ford.png'),
        'u0': load_tile('ford_animation\\tile_enemy_riffleman_up_0_ford.png'),
        'u1': load_tile('ford_animation\\tile_enemy_riffleman_up_1_ford.png'),
        'u2': load_tile('ford_animation\\tile_enemy_riffleman_up_2_ford.png'),
        'u3': load_tile('ford_animation\\tile_enemy_riffleman_up_3_ford.png'),
    }
}
tree_transparent = pygame.image.load(
    os.path.join(os.path.dirname(__file__), 'resources', 'tile_live_tree_transparent.png')).convert_alpha()
tree_transparent_test = pygame.image.load(
    os.path.join(os.path.dirname(__file__), 'resources', 'tile_live_tree_transparent_test.png')).convert_alpha()
grass = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_grass_0.png')).convert()
stones = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_stone_0.png')).convert()
bonfire = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', 'tile_bonfire_2.png')).convert_alpha()
enemy = pygame.image.load(
    os.path.join(os.path.dirname(__file__), 'resources', 'tile_enemy_riffleman_down_0.png')).convert_alpha()

len_fields = len(fields)


def load_tile(filename):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), 'resources', filename)).convert_alpha()


transparent_up_tiles = {
    "P": {"0": load_tile('tile_live_tree_transparent.png')},
    "F": {
        "0": load_tile('tile_dry_tree_0_transparent.png'),
        "1": load_tile('tile_dry_tree_1_transparent.png'),
        "2": load_tile('tile_dry_tree_2_transparent.png'),
        "3": load_tile('tile_dry_tree_3_transparent.png'),
        "4": load_tile('tile_dry_tree_4_transparent.png'),
        "6": load_tile('tile_dry_tree_6_transparent.png'),
        "7": load_tile('tile_dry_tree_7_transparent.png'),
    },
    "i": {
        "0": load_tile('tile_cactus_0_transparent.png'),
        "1": load_tile('tile_cactus_1_transparent.png'),
        "2": load_tile('tile_cactus_2_transparent.png'),
        "3": load_tile('tile_cactus_3_transparent.png'),
    },
    "u": {
        "0": load_tile('tile_tall_grass_0_transparent.png'),
        "1": load_tile('tile_tall_grass_1_transparent.png'),
    },
    "ü": {"0": load_tile('tile_prickly_grass_transparent.png')},
    ",": {
        '1': load_tile('tile_dry_grass_0_transparent.png'),
        '2': load_tile('tile_dry_grass_2_transparent.png'),
        '3': load_tile('tile_dry_grass_1_transparent.png'),
        '4': load_tile('tile_dry_grass_2_transparent.png'),
        '5': load_tile('tile_dry_grass_2_transparent.png'),
        '6': load_tile('tile_dry_grass_4_transparent.png'),
        '7': load_tile('tile_dry_grass_3_transparent.png'),
        '8': load_tile('tile_dry_grass_2_transparent.png'),
        '9': load_tile('tile_dry_grass_3_transparent.png'),
        'A': load_tile('tile_dry_grass_4_transparent.png'),
        'B': load_tile('tile_dry_grass_4_transparent.png'),
        'D': load_tile('tile_dry_grass_2_transparent.png'),
        'E': load_tile('tile_dry_grass_3_transparent.png'),
        'F': load_tile('tile_dry_grass_4_transparent.png'),
    },
    "„": {
        '1': load_tile('tile_grass_0_transparent.png'),
        '2': load_tile('tile_grass_2_transparent.png'),
        '3': load_tile('tile_grass_3_transparent.png'),
        '5': load_tile('tile_grass_2_transparent.png'),
        '6': load_tile('tile_grass_3_transparent.png'),
        '8': load_tile('tile_grass_2_transparent.png'),
        '9': load_tile('tile_grass_3_transparent.png'),
        'B': load_tile('tile_grass_2_transparent.png'),
        'C': load_tile('tile_grass_3_transparent.png'),
        'E': load_tile('tile_grass_2_transparent.png'),
        'F': load_tile('tile_grass_3_transparent.png'),
    },
}


def load_map():
    """
        Загрузка игровой карты через pickle
    """
    with open("save/saved_map.pkl", "rb") as fp:
        all_load = pickle.load(fp)

    return all_load[0], all_load[1], all_load[2], all_load[3]


# Загрузка тайлов
resources_dict = loading_all_sprites()

# Загрузка карты
global_map, raw_minimap, vertices_graph, vertices_dict = load_map()

chunk_tile = 25


def get_tile_icon_and_type(x, y):
    """ Возвращает текстуры icon и type тайла с указанных мировых координат """
    global_position_x = x // chunk_tile
    global_position_y = y // chunk_tile
    local_position_x = x % chunk_tile
    local_position_y = y % chunk_tile
    tile = global_map[global_position_y][global_position_x].chunk[local_position_y][local_position_x]
    return tile.icon, tile.type


def get_tile_icon(x, y):
    """ Возвращает текстуры icon и type тайла с указанных мировых координат """
    global_position_x = x // chunk_tile
    global_position_y = y // chunk_tile
    local_position_x = x % chunk_tile
    local_position_y = y % chunk_tile
    tile = global_map[global_position_y][global_position_x].chunk[local_position_y][local_position_x]
    return tile.icon


class ColorTile(pygame.sprite.Sprite):
    """ Содержит спрайты зон доступности """

    def __init__(self, x, y, size_tile, color, alpha=255):
        self.color = color
        self.alpha = alpha
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Tile(pygame.sprite.Sprite):
    """ Содержит спрайты зон доступности """

    def __init__(self, zero_x, zero_y, number_x, number_y, size_tile, image_tile, alpha=255):
        self.old_size_tile = size_tile
        self.number_x = number_x
        self.number_y = number_y
        pygame.sprite.Sprite.__init__(self)
        self.img = image_tile
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        self.rect.left = zero_x + number_x * size_tile
        self.rect.top = zero_y + number_y * size_tile
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, zero_x, zero_y, size_tile, start_end, up=False):
        if start_end:
            x_start = round(start_end[0]) - len_fields // 2
            y_start = round(start_end[1]) - len_fields // 2
            x_end = round(start_end[0]) + len_fields // 2
            y_end = round(start_end[1]) + len_fields // 2
            if self.number_x < x_start or self.number_x > x_end or self.number_y < y_start or self.number_y > y_end:
                self.kill()
        position_x = zero_x + self.number_x * size_tile
        position_y = zero_y + self.number_y * size_tile
        if self.old_size_tile != size_tile:
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
        self.rect.left = position_x
        self.rect.top = position_y
        self.old_size_tile = size_tile


class PersonTile(pygame.sprite.Sprite):
    """ Содержит спрайты зон доступности """

    def __init__(self, zero_x, zero_y, number_x, number_y, size_tile, animation, alpha=255):
        self.animation = animation
        self.old_size_tile = size_tile
        self.number_x = number_x
        self.number_y = number_y
        pygame.sprite.Sprite.__init__(self)
        self.direction = "d"
        self.phase = 0
        self.img = animation["standard"][f"{self.direction}{self.phase}"]
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        self.rect.left = zero_x + number_x * size_tile
        self.rect.top = zero_y + number_y * size_tile
        self.speed = 0
        self.time = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, zero_x, zero_y, size_tile, direction, time, move, tile_icon):

        new_phase = False
        update_animation = False
        if not move:
            if self.phase != 0:
                self.phase = 0
                update_animation = True

        elif time - self.time > FPS // 4 / 100:
            self.phase += 1
            if self.phase > 3:
                self.phase = 0
            update_animation = True
        if update_animation:
            self.img = self.animation["standard"][F"{direction}{self.phase}"]
            if tile_icon == "f":
                self.img = self.animation["ford"][F"{direction}{self.phase}"]
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
            new_phase = True
            self.time = time
        position_x = zero_x + self.number_x * size_tile
        position_y = zero_y + self.number_y * size_tile
        if not new_phase and self.old_size_tile != size_tile:
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
        self.rect.left = position_x
        self.rect.top = position_y
        self.old_size_tile = size_tile


len_x, len_y = size = screen.get_width(), screen.get_height()
center_x = len_x / 2
center_y = len_y / 2
len_fields = len(fields)
zero_x = center_x - len_fields // 2
zero_y = center_y - len_fields // 2
size_tile = 30

group = pygame.sprite.Group()
up_group = pygame.sprite.Group()

for number_line, line in enumerate(fields):
    for number_tile, tile in enumerate(line):
        x = person_x - len_fields // 2 + number_tile
        y = person_y - len_fields // 2 + number_line
        icon, type = get_tile_icon_and_type(x, y)
        group.add(Tile(zero_x, zero_y, x, y, size_tile, resources_dict[icon][type]))

person_tile = PersonTile(zero_x, zero_y, 0, 0, size_tile, animations)
# person_tile = Tile(zero_x, zero_y, 1, 1, size_tile, enemy)
font = pygame.font.SysFont("Arial", 18)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text


def print_text(text):
    fps_text = font.render(text, 1, pygame.Color("coral"))
    return fps_text


global_region_grid = 3
region_grid = 3
chunks_grid = 3
mini_region_grid = 5
tile_field_grid = 5

global_position = [5, 5]
local_position = [5, 5]

# global_map, raw_minimap, vertices_graph, vertices_dict = master_map_generate(global_region_grid,
#                                                region_grid, chunks_grid, mini_region_grid, tile_field_grid, screen)


print(dir(pygame))
x = 100
y = 200
size_tile = 30

x_plus = 0
y_plus = 0
# Цикл игры
running = True
MOUSEBUTTONDOWN = False
step = 0
color_alpha_tile = ColorTile(200, 300, 50, RED, 100)
working_surface = pygame.Surface((800, 800))
working_surface_position = (50, 50)
direction = 'd'
len_fields = len(fields)


class KeyboardDown:
    left = False
    right = False
    up = False
    down = False


kb = KeyboardDown()


class StartEnd:
    x_end = round(person_x + len_fields // 2)
    y_end = round(person_y + len_fields // 2)
    x_start = round(person_x - len_fields // 2)
    y_start = round(person_y - len_fields // 2)


start_end = StartEnd()
while running:
    move = False
    time_ = time.time()
    pygame.key.set_repeat(1, 2)
    step += 1
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # print(event)
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                size_tile //= 0.8
            elif event.button == 5:
                if size_tile > 5:
                    size_tile //= 1.1
            elif event.button == 1:
                MOUSEBUTTONDOWN = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                MOUSEBUTTONDOWN = False
        if event.type == pygame.MOUSEMOTION:
            if MOUSEBUTTONDOWN:
                motion_x, motion_y = event.rel
                x_plus += motion_x
                y_plus += motion_y
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                kb.left = True
            if event.key == pygame.K_RIGHT:
                kb.right = True
            if event.key == pygame.K_UP:
                kb.up = True
            if event.key == pygame.K_DOWN:
                kb.down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                kb.left = False
            if event.key == pygame.K_RIGHT:
                kb.right = False
            if event.key == pygame.K_UP:
                kb.up = False
            if event.key == pygame.K_DOWN:
                kb.down = False
        if event.type == pygame.MULTIGESTURE:
            size_tile += round(event.pinched * 100)

    move = True
    if kb.down:
        if get_tile_icon(round(person_x), round(person_y + 0.3)) not in ('▲', '~'):
            if kb.left:
                direction = 'l'
                person_y += 0.03
                person_x -= 0.03
            elif kb.right:
                direction = 'r'
                person_y += 0.03
                person_x += 0.03
            else:
                direction = 'd'
                person_y += 0.04
        else:
            move = False
    elif kb.up:
        if get_tile_icon(round(person_x), round(person_y - 0.3)) not in ('▲', '~'):
            if kb.left:
                direction = 'l'
                person_x -= 0.03
                person_y -= 0.03
            elif kb.right:
                direction = 'r'
                person_x += 0.03
                person_y -= 0.03
            else:
                direction = 'u'
                person_y -= 0.04
        else:
            move = False
    elif kb.left:
        if get_tile_icon(round(person_x - 0.3), round(person_y)) not in ('▲', '~'):
            direction = 'l'
            person_x -= 0.04
        else:
            move = False
    elif kb.right:
        if get_tile_icon(round(person_x + 0.3), round(person_y)) not in ('▲', '~'):
            direction = 'r'
            person_x += 0.04
        else:
            move = False
    else:
        move = False

    local_position_x = round(person_x) % len_fields
    local_position_y = round(person_y) % len_fields

    # print(F"\nperson_x + len_fields//2 = {person_x + len_fields//2}, x_end = {x_end}\n"
    #      F"person_x + len_fields//2 > x_end = {person_x + len_fields//2 > x_end}\n")
    new_x_start = round(person_x - len_fields // 2)
    new_y_start = round(person_y - len_fields // 2)
    new_x_end = round(person_x + len_fields // 2)
    new_y_end = round(person_y + len_fields // 2)
    # print(F"new_x_end - {new_y_end}, start_end.x_end - {start_end.y_end}")

    if new_x_end > start_end.x_end:
        start_end.x_end = new_x_end
        for i in range(len_fields):
            x = start_end.x_end
            y = i - len_fields // 2 + round(person_y)
            icon, type = get_tile_icon_and_type(x, y)
            group.add(Tile(zero_x, zero_y, x, y, size_tile, resources_dict[icon][type]))
            # if icon == 'P':
            #    up_group.add(Tile(zero_x, zero_y, x, y, size_tile, tree_transparent))
    start_end.x_end = new_x_end

    if new_y_end > start_end.y_end:
        start_end.y_end = new_y_end
        for i in range(len_fields):
            x = i - len_fields // 2 + round(person_x)
            y = start_end.y_end
            icon, type = get_tile_icon_and_type(x, y)
            group.add(Tile(zero_x, zero_y, x, y, size_tile, resources_dict[icon][type]))
            # if icon == 'P':
            #    up_group.add(Tile(zero_x, zero_y, x, y, size_tile, tree_transparent))
    start_end.y_end = new_y_end

    if new_x_start < start_end.x_start:
        start_end.x_start = new_x_start
        for i in range(len_fields):
            x = start_end.x_start
            y = i - len_fields // 2 + round(person_y)
            icon, type = get_tile_icon_and_type(x, y)
            group.add(Tile(zero_x, zero_y, x, y, size_tile, resources_dict[icon][type]))
            # if icon == 'P':
            #    up_group.add(Tile(zero_x, zero_y, x, y, size_tile, tree_transparent))
    start_end.x_start = new_x_start

    if new_y_start < start_end.y_start:
        start_end.y_start = new_y_start
        for i in range(len_fields):
            x = i - len_fields // 2 + round(person_x)
            y = start_end.y_start
            icon, type = get_tile_icon_and_type(x, y)
            group.add(Tile(zero_x, zero_y, x, y, size_tile, resources_dict[icon][type]))
            # if icon == 'P':
            #    up_group.add(Tile(zero_x, zero_y, x, y, size_tile, tree_transparent))
    start_end.y_start = new_y_start
    # ++++++++
    """
    1 2 3
    4 5 6
    7 8 9

    """
    up_group = pygame.sprite.Group()

    person_world_x = round(person_x)
    person_world_y = round(person_y)

    icon_1, type_1 = get_tile_icon_and_type(round(person_x) - 1, round(person_y) - 1)
    icon_2, type_2 = get_tile_icon_and_type(round(person_x), round(person_y) - 1)
    icon_3, type_3 = get_tile_icon_and_type(round(person_x) + 1, round(person_y) - 1)
    icon_4, type_4 = get_tile_icon_and_type(round(person_x) - 1, round(person_y))
    icon_5, type_5 = get_tile_icon_and_type(round(person_x), round(person_y))
    icon_6, type_6 = get_tile_icon_and_type(round(person_x) + 1, round(person_y))
    icon_7, type_7 = get_tile_icon_and_type(round(person_x) - 1, round(person_y) + 1)
    icon_8, type_8 = get_tile_icon_and_type(round(person_x), round(person_y) + 1)
    icon_9, type_9 = get_tile_icon_and_type(round(person_x) + 1, round(person_y) + 1)

    up_icons = [
        [(icon_1, type_1), (icon_2, type_2), (icon_3, type_3)],
        [(icon_4, type_4), (icon_5, type_5), (icon_6, type_6)],
        [(icon_7, type_7), (icon_8, type_8), (icon_9, type_9)]]

    for number_line, line in enumerate(up_icons):
        for number_tile, tile in enumerate(line):
            if number_line == 1 and person_y > person_world_y:
                continue
            icon, type = tile
            if number_line != 0 and icon in transparent_up_tiles and type in transparent_up_tiles[icon]:
                up_group.add(Tile(zero_x, zero_y, number_tile - 1 + person_world_x, number_line - 1 + person_world_y,
                                  size_tile, transparent_up_tiles[icon][type]))

    # if person_tile_icon == 'P':
    #    up_group.add(Tile(zero_x, zero_y, round(person_x), round(person_y), size_tile, tree_transparent))
    # ++++++++
    # Рендеринг
    screen.fill(BLUE)
    len_x, len_y = size = screen.get_width(), screen.get_height()
    center_x = len_x / 2
    center_y = len_y / 2

    zero_x = center_x - len_fields * size_tile // 2 + x_plus
    zero_y = center_y - len_fields * size_tile // 2 + y_plus

    group.update(zero_x - person_x * size_tile, zero_y - person_y * size_tile, size_tile, [person_x, person_y])

    working_surface.fill(GREEN)
    group.draw(working_surface)

    person_tile.update(zero_x + 0 * size_tile, zero_y + 0 * size_tile, size_tile, direction, time_, move, icon_5)
    person_tile.draw(working_surface)

    up_group.update(zero_x - person_x * size_tile, zero_y - person_y * size_tile, size_tile, [person_x, person_y])
    up_group.draw(working_surface)

    screen.blit(working_surface, working_surface_position)

    # color_alpha_tile.draw(screen)
    screen.blit(update_fps(), (10, 0))
    screen.blit(print_text(F"person_x: {person_x}"), (10, 15))
    screen.blit(print_text(F"person_y: {person_y}"), (10, 30))
    screen.blit(print_text(F"len group: {len(group) + len(up_group)}"), (100, 0))
    # screen.blit(print_text(F"person_tile: |{person_tile_icon}|"), (200, 0))
    # screen.blit(print_text(F"tile: {fields[round(person_y)][round[person_x]]}"), (10, 30))
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()