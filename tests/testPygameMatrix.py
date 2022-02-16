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
        #self.color = color
        #self.alpha = alpha
        pygame.sprite.Sprite.__init__(self)
        self.img = image_tile
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface((size_tile, size_tile))
        #self.image.fill(self.color)
        #self.image.set_alpha(self.alpha)
        #self.rect = self.image.get_rect()
        self.rect.left = zero_x + number_x*size_tile
        self.rect.top = zero_y + number_y*size_tile
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
        #self.image = pygame.Surface((size_tile, size_tile))
        #self.image.fill(self.color)
        #self.image.set_alpha(self.alpha)

        if multi_matrix is not None:
            position = np.matrix(((self.number_x, self.number_y, 1)))
            result_position = position * multi_matrix

            position_x = zero_x + result_position[(0, 2)] * self.old_size_tile
            position_y = zero_y + result_position[(0, 1)] * self.old_size_tile
            #position_x = zero_x + self.number_x * size_tile
            #position_y = zero_y + self.number_y * size_tile
            #print(F"\nresult_position - {result_position}\n({position_x, (position_y)})\n")
        else:
            #position_x = zero_x + self.number_x * size_tile
            #position_y = zero_y + self.number_y * size_tile
            position_x = self.rect.left
            position_y = self.rect.top

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
size_tile = 30

x_plus = 0
y_plus = 0
# Цикл игры
running = True
MOUSEBUTTONDOWN = False
step = 0
color_alpha_tile = ColorTile(200, 300, 50, RED, 100)

def get_transfer_matrix(t_x, t_y):
    #matrix = ((1, 0, t_x),
    #          (0, 1, t_y),
    #          (0, 0, 1))
    matrix = np.matrix(((t_x, t_y, 1),
                        (0, 1, 0),
                        (1, 0, 0)))
    return matrix

def get_scale_matrix(s_x, s_y):
    matrix = np.matrix(((0, 0, 1),
                        (0, s_y, 0),
                        (s_x, 0, 1)))
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

while running:
    multi_matrix = None
    pos = None
    scale = None
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
                scale = 1.2
                size_tile = round(size_tile * scale, 0)
            elif event.button == 5:
                if size_tile > 5:
                    pos = event.pos
                    scale = 0.9
                    size_tile = round(size_tile * scale, 0)
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
    # Рендеринг
    screen.fill(BLUE)
    len_x, len_y = size = screen.get_width(), screen.get_height()
    center_x = len_x / 2
    center_y = len_y / 2
    len_fields = len(fields)
    zero_x = center_x - len_fields*size_tile // 2 + x_plus
    zero_y = center_y - len_fields*size_tile // 2 + y_plus

    if pos is not None:
        transfer_x = pos[0] - center_x
        transfer_y = pos[1] - center_y
        start_transfer_matrix = get_transfer_matrix(transfer_x, transfer_y)
        scale_matrix = get_scale_matrix(scale, scale)
        finish_transfer_matrix = get_transfer_matrix(0 - transfer_x, 0 - transfer_y)
        multi_matrix = scale_matrix#matrix_multiplication(start_transfer_matrix, scale_matrix, finish_transfer_matrix)


    if step%10 == 9999999999:
        len_fields = len(fields)
        for i in range(len_fields):
            group.add(Tile(zero_x, zero_y, i, len_fields - 1, size_tile, random.choice([stones, grass])))
        group.update(zero_x, zero_y, size_tile, multi_matrix, up=True,)

    else:
        group.update(zero_x, zero_y, size_tile, multi_matrix)

    group.draw(screen)
    #color_alpha_tile.draw(screen)
    screen.blit(update_fps(), (10, 0))
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()