import os
import pygame
import random
import numpy as np
from math import sin, cos
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
fields = ["..........",
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
WIDTH = 600
HEIGHT = 600
FPS = 30
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


grass = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_grass_0.png')).convert()
stones = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_stone_0.png')).convert()
bonfire = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_bonfire_2.png')).convert_alpha()
enemy = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_enemy_riffleman_down_squat_1.png')).convert_alpha()


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
        self.position_x = zero_x + number_x*size_tile
        self.position_y = zero_y + number_y*size_tile
        self.start_position_x = number_x*size_tile
        self.start_position_y = number_y*size_tile
        self.rect.left = self.position_x
        self.rect.top = self.position_y
        self.speed = 0

    def draw(self, surface):
        pass
        #if self.rect.top > 150 and self.rect.left > 150:
        #    surface.blit(self.image, self.rect)

    def update(self, zero_x, zero_y, size_tile, multi_matrix, up=False):
        if up:
            if self.number_y == 0:
                self.kill()
            self.number_y -= 1

        position = np.matrix(((self.start_position_x, self.start_position_y, 1)))
        #position = np.matrix(((self.rect.left, self.rect.top, 1)))
        result_position = position * multi_matrix

        position_x = result_position[(0, 0)]
        position_y = result_position[(0, 1)]

        if self.old_size_tile != size_tile:
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
        self.rect.left = position_x
        self.rect.top = position_y
        self.old_size_tile = size_tile
        #else:
            #print(F"position_x - {position_x}, position_y - {position_y}")
            #self.rect = pygame.Surface((size_tile, size_tile)).fill(RED)#.get_rect()



len_x, len_y = size = screen.get_width(), screen.get_height()
center_x = len_x/2
center_y = len_y/2
len_fields = len(fields)
zero_x = center_x - len_fields//2
zero_y = center_y - len_fields//2
size_tile = 30

group = pygame.sprite.Group()

for number_line, line in enumerate(fields):
    for number_tile, tile in enumerate(line):
        if tile == "x":
            group.add(Tile(zero_x, zero_y, number_tile, number_line, size_tile, stones))
        else:
            group.add(Tile(zero_x, zero_y, number_tile, number_line, size_tile, grass))

font = pygame.font.SysFont("Arial", 18)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text

x = 100
y = 200
start_size_tile = size_tile
size_tile = 30

x_plus = 0
y_plus = 0
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
    #matrix = ((cos(angle), -sin(angle), 0),
    #          (sin(angle), cos(angle), 0),
    #          (0, 0, 1))
    matrix = np.matrix(((0, 0, 1),
                        (-sin(angle), cos(angle), 0),
                        (cos(angle), sin(angle), 0)))
    return matrix

def matrix_multiplication(*args):
    result = None
    for i, matrix in enumerate(args):
        if i == 0:
            result = matrix
        else:
            result *= matrix
    return result

multi_matrix = None
scale = 1
pos = (0, 0)
old_pos = pos
color_tile = ColorTile(0, 0, 5, RED)
color_tile2 = ColorTile(0, 0, 5, GREEN)
null_position = np.matrix(((0, 0, 1)))
while running:
    scales = False
    amendment_pos_x = 0
    amendment_pos_y = 0
    multi_matrix = None
    #scale = 1
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
                scale = size_tile / start_size_tile
                scales = True
            elif event.button == 5:
                if size_tile > 5:
                    pos = event.pos
                    old_size_tile = size_tile
                    _scale = 0.9
                    size_tile = round(size_tile * _scale, 0)
                    scale = size_tile / start_size_tile
                    scales = True
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
                amendment_pos_x += motion_x
                amendment_pos_y += motion_y
    # Рендеринг
    screen.fill(BLUE)
    len_x, len_y = size = screen.get_width(), screen.get_height()
    center_x = len_x / 2
    center_y = len_y / 2
    len_fields = len(fields)
    zero_x = center_x - len_fields*size_tile // 2 + x_plus
    zero_y = center_y - len_fields*size_tile // 2 + y_plus
    empty_matrix = np.matrix(((0, 0, 1),
                              (0, 1, 0),
                              (1, 0, 0)))


        #start_transfer_matrix = get_transfer_matrix(transfer_x, transfer_y)

        #finish_transfer_matrix = get_transfer_matrix(0 - transfer_x, 0 - transfer_y)
        #multi_matrix = matrix_multiplication(zero_transfer_matrix, start_transfer_matrix, scale_matrix, finish_transfer_matrix)

    scale_matrix = get_scale_matrix(scale, scale)
    zero_transfer_matrix = get_transfer_matrix(x_plus, y_plus)
    #if pos is not None:

    reversed_null_transfer = get_transfer_matrix(0 - null_position[(0, 0)], 0 - null_position[(0, 1)])
    transfer_x = -pos[0]# - old_pos[0]
    transfer_y = -pos[1]# - old_pos[1]
    start_transfer_matrix = get_transfer_matrix(transfer_x, transfer_y)
    finish_transfer_matrix = get_transfer_matrix(0 - transfer_x, 0 - transfer_y)

    old_pos_transfer = get_transfer_matrix(-old_pos[0], -old_pos[1])
    old_pos_transfer_reversed = get_transfer_matrix(old_pos[0], old_pos[1])

    multi_matrix = matrix_multiplication(start_transfer_matrix, scale_matrix, finish_transfer_matrix)#, zero_transfer_matrix)

    #if scales:
    #    plus_position = np.matrix(((x_plus, y_plus, 1))) * multi_matrix
    #    x_plus = plus_position[(0, 0)]
    #    y_plus = plus_position[(0, 1)]

    null_position = np.matrix(((0, 0, 1))) * multi_matrix
    color_tile.rect.left = null_position[(0, 0)]
    color_tile.rect.top = null_position[(0, 1)]
    #null_transfer = get_transfer_matrix(null_position[(0, 0)], null_position[(0, 1)])
    #multi_matrix = matrix_multiplication(multi_matrix, null_transfer)


    #else:
    #    multi_matrix = matrix_multiplication(scale_matrix)#, zero_transfer_matrix)
    #print(multi_matrix)
    #if step%10 == 9999999999:
    #    len_fields = len(fields)
    #    for i in range(len_fields):
    #        group.add(Tile(zero_x, zero_y, i, len_fields - 1, size_tile, random.choice([stones, grass])))
    #    group.update(zero_x, zero_y, size_tile, multi_matrix, up=True,)

    #else:
    group.update(zero_x, zero_y, size_tile, multi_matrix)

    group.draw(screen)
    #color_alpha_tile.draw(screen)
    screen.blit(update_fps(), (10, 0))
    color_tile2.rect.left = old_pos[0]
    color_tile2.rect.top = old_pos[1]
    color_tile2.draw(screen)
    color_tile.draw(screen)
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()
    old_pos = pos

pygame.quit()