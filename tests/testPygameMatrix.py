import os
import copy
import pygame
import random
import numpy as np
from math import sin, cos, pi
fields = ["..............................",
          ".x.....x......................",
          "..x...x.......................",
          "...x.x.x......................",
          "....x...x.....................",
          ".....x...x....................",
          "......x.......................",
          ".xx....x......................",
          ".xx...........................",
          "......x.......................",
          "..............................",
          ".x.....x......................",
          "..x...x.......................",
          "...x.x.x......................",
          "....x...x.....................",
          ".....x...x....................",
          "......x.......................",
          ".xx....x......................",
          ".xx...........................",
          "......x.......................",
          "..............................",
          ".x.....x......................",
          "..x...x.......................",
          "...x.x.x......................",
          "....x...x.....................",
          ".....x...x....................",
          "......x.......................",
          ".xx....x......................",
          ".xx...........................",
          "......x.......................",

          ]
fields1 = ["..........",
          ".x.....x..",
          "..x...x...",
          "...x.x.x..",
          "....x...x.",
          "..........",
          ".x.....x..",
          "..x...x...",
          "...x.x.x..",
          "....x...x.",

          ]
#fields = ["."
#          ]
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
DEGREES_IN_RAD = 57.2955

grass = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_grass_0.png')).convert()
stones = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_stone_0.png')).convert()
bonfire = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_bonfire_2.png')).convert_alpha()
enemy = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_enemy_riffleman_down_squat_1.png')).convert_alpha()


class ColorTile(pygame.sprite.Sprite):
    """ Цветные квадраты """

    def __init__(self, x, y, size_tile, color, alpha=255):

        self.color = color
        self.alpha = alpha
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Tile(pygame.sprite.Sprite):
    """ Спрайты """

    def __init__(self, zero_x, zero_y, number_x, number_y, size_tile, image_tile, degrees, alpha=255):

        pygame.sprite.Sprite.__init__(self)
        self.start_size_tile = size_tile
        self.old_size_tile = size_tile
        self.number_x = number_x
        self.number_y = number_y
        self.img = image_tile
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        position = [zero_x + number_x*size_tile, zero_y + number_y*size_tile]
        self.rect.center = position
        self.speed = 0
        self.old_degrees = degrees

    def update(self, size_tile, multi_matrix, degrees, up=False):
        if up:
            if self.number_y == 0:
                self.kill()
            self.number_y -= 1
        position_matrix = np.matrix(((self.number_x * self.start_size_tile, self.number_y * self.start_size_tile, 1)))
        result_position = position_matrix * multi_matrix
        position = [result_position[(0, 0)], result_position[(0, 1)]]
        if self.old_size_tile != size_tile:
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
        self.rect.center = position
        self.old_size_tile = size_tile
        self.old_degrees = degrees

len_x, len_y = size = screen.get_width(), screen.get_height()
center_x = len_x/2
center_y = len_y/2
len_fields = len(fields)
zero_x = center_x - len_fields//2
zero_y = center_y - len_fields//2

size_tile = 30
start_size_tile = size_tile

group = pygame.sprite.Group()

for number_line, line in enumerate(fields):
    for number_tile, tile in enumerate(line):
        if tile == "x":
            group.add(Tile(zero_x, zero_y, number_tile, number_line, size_tile, stones, 0))
        else:
            group.add(Tile(zero_x, zero_y, number_tile, number_line, size_tile, grass, 0))

font = pygame.font.SysFont("Arial", 18)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text

x = 100
y = 200

zero_plus = [0, 0]
zero_plus_old = zero_plus
# Цикл игры
running = True
MOUSEBUTTONDOWN = False
step = 0

def get_transfer_matrix(t_x, t_y):
    matrix = np.matrix(((1.0,      0,      0),
                        (0,      1.0,      0),
                        (t_x,    t_y,    1.0)))
    return matrix

def get_scale_matrix(s_x, s_y):
    matrix = np.matrix(((s_x, 0,   0),
                        (0,   s_y, 0),
                        (0,   0,   1.0)))
    return matrix

def get_rotate_matrix(angle):
    matrix = np.matrix(((cos(angle),  -sin(angle), 0),
                        (sin(angle),  cos(angle),  0),
                        (0,           0,           1.)))
    return matrix

def matrix_multiplication(*args):
    result = None
    for i, matrix in enumerate(args):
        if i == 0:
            result = matrix
        else:
            result *= matrix
    return result
working_surface = pygame.Surface((900, 900))
scale = 1
pos = (0, 0)
old_pos = pos
color_tile = ColorTile(0, 0, 5, RED)
color_tile2 = ColorTile(0, 0, 5, GREEN)
color_tile3 = ColorTile(50, 50, 50, (100, 255, 100))
null_position = np.matrix(((0, 0, 1)))
empty_matrix = np.matrix(((1, 0, 0),
                          (0, 1, 0),
                          (0, 0, 1)))
multi_matrix = empty_matrix
null_position = np.matrix(((0, 0, 1)))
rotate = False
degrees_all = 0
while running:
    degrees = 0.
    update = False
    amendment_pos_x = 0
    amendment_pos_y = 0
    scale = 1
    step += 1
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                pos = event.pos
                old_size_tile = size_tile
                _scale = 1.2
                size_tile = round(size_tile * _scale, 0)
                scale = size_tile / old_size_tile
                update = True
            elif event.button == 5:
                if size_tile > 5:
                    pos = event.pos
                    old_size_tile = size_tile
                    _scale = 0.9
                    size_tile = round(size_tile * _scale, 0)
                    scale = size_tile / old_size_tile
                    update = True
            elif event.button == 1:
                MOUSEBUTTONDOWN = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                MOUSEBUTTONDOWN = False
        if event.type == pygame.MOUSEMOTION:
            if MOUSEBUTTONDOWN:
                motion_x, motion_y = event.rel
                zero_plus[0] += motion_x
                zero_plus[1] += motion_y
                amendment_pos_x += motion_x
                amendment_pos_y += motion_y
                update = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                rotate = not rotate
    # Рендеринг
    screen.fill(BLUE)
    len_x, len_y = size = screen.get_width(), screen.get_height()
    center_x = len_x / 2
    center_y = len_y / 2
    len_fields = len(fields)
    zero_x = center_x - len_fields*size_tile // 2 + zero_plus[0]
    zero_y = center_y - len_fields*size_tile // 2 + zero_plus[1]
    if update:
        operate_matrix = get_scale_matrix(scale, scale)
        plus_transfer_start = get_transfer_matrix(-zero_plus_old[0], -zero_plus_old[1])
        plus_transfer_finish = get_transfer_matrix(zero_plus[0], zero_plus[1])
        transfer = [zero_plus[0] - pos[0], zero_plus[1] - pos[1]]
        start_transfer_matrix = get_transfer_matrix(transfer[0], transfer[1])
        finish_transfer_matrix = get_transfer_matrix(-transfer[0], -transfer[1])
        new_multi_matrix = matrix_multiplication(plus_transfer_start, start_transfer_matrix, operate_matrix,
                                                                        finish_transfer_matrix, plus_transfer_finish)
        multi_matrix = matrix_multiplication(multi_matrix * new_multi_matrix)

    null_position = np.matrix(((0, 0, 1))) * multi_matrix
    color_tile.rect.center = [null_position[(0, 0)], null_position[(0, 1)]]

    if step%100000000 == 0:
        len_fields = len(fields)
        for i in range(len_fields):
            group.add(Tile(zero_x, zero_y, i, len_fields, start_size_tile, random.choice([stones, grass]),
                                                                                                degrees_all + degrees))
        group.update(size_tile, multi_matrix, degrees_all + degrees, up=True)
    elif update:
        group.update(size_tile, multi_matrix, degrees_all + degrees)
    working_surface.fill(GREEN)
    group.draw(working_surface)
    screen.blit(update_fps(), (10, 0))
    color_tile2.rect.center = old_pos
    color_tile2.draw(working_surface)
    color_tile.draw(working_surface)
    # после отрисовки всего, переворачиваем экран
    screen.blit(working_surface, (50, 50))
    pygame.display.flip()
    old_pos = pos
    zero_plus_old = copy.deepcopy(zero_plus)

    degrees_all += degrees
pygame.quit()