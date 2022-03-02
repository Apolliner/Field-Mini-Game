import os
import time
import copy
import pygame
import random
import numpy as np
from math import sin, cos, pi
fields = ["............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",
          "............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",
          "............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",
          "............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",
          "............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",
          "............................................................",
          ".x.....x....................................................",
          "..x...x.....................................................",
          "...x.x.x....................................................",
          "....x...x...................................................",
          ".....x...x..................................................",
          "......x.....................................................",
          ".xx....x....................................................",
          ".xx.........................................................",
          "......x.....................................................",

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

def load_tile(filename):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', filename)).convert_alpha()

animation = {
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
}

grass = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_grass_0.png')).convert()
stones = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_stone_0.png')).convert()
bonfire = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_bonfire_2.png')).convert_alpha()
enemy = pygame.image.load(os.path.join(os.path.dirname(__file__), './resources', 'tile_enemy_riffleman_down_0.png')).convert_alpha()


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
        self.rect.left = zero_x + number_x*size_tile
        self.rect.top = zero_y + number_y*size_tile
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, zero_x, zero_y, size_tile, up=False):
        if up:
            if self.number_y == 0:
                self.kill()
            self.number_y -= 1
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
        self.img = animation[f"{self.direction}{self.phase}"]
        self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        self.rect.left = zero_x + number_x*size_tile
        self.rect.top = zero_y + number_y*size_tile
        self.speed = 0
        self.time = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, zero_x, zero_y, size_tile, direction, time):
        new_phase = False
        if time - self.time > FPS//4/100:
            self.phase += 1
            if self.phase > 3:
                self.phase = 0
            self.img = self.animation[F"{direction}{self.phase}"]
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

person_tile = PersonTile(zero_x, zero_y, len(fields)//2, len(fields[0])//2, size_tile, animation)
#person_tile = Tile(zero_x, zero_y, 1, 1, size_tile, enemy)
font = pygame.font.SysFont("Arial", 18)

def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text
print(dir(pygame))
x = 100
y = 200
size_tile = 30
person_x = 0
person_y = 0
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
while running:
    time_ = time.time()
    pygame.key.set_repeat(1, 2)
    step += 1
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        #print(event)
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
                direction = 'l'
                person_x -= 0.01
            if event.key == pygame.K_RIGHT:
                direction = 'r'
                person_x += 0.01
            if event.key == pygame.K_UP:
                direction = 'u'
                person_y -= 0.01
            if event.key == pygame.K_DOWN:
                direction = 'd'
                person_y += 0.01
        if event.type == pygame.MULTIGESTURE:
            size_tile += event.pinched * 100
    # Рендеринг
    screen.fill(BLUE)
    len_x, len_y = size = screen.get_width(), screen.get_height()
    center_x = len_x / 2
    center_y = len_y / 2
    len_fields = len(fields)
    zero_x = center_x - len_fields*size_tile // 2 + x_plus
    zero_y = center_y - len_fields*size_tile // 2 + y_plus
    if step%1000000 == 0:
        len_fields = len(fields)
        for i in range(len_fields):
            group.add(Tile(zero_x, zero_y, i, len_fields - 1, size_tile, random.choice([stones, grass])))
        group.update(zero_x, zero_y, size_tile, up=True)
    else:
        group.update(zero_x, zero_y, size_tile)
    working_surface.fill(GREEN)
    group.draw(working_surface)

    person_tile.update(zero_x + person_x * size_tile, zero_y + person_y * size_tile, size_tile, direction, time_)
    person_tile.draw(working_surface)
    screen.blit(working_surface, working_surface_position)
    #color_alpha_tile.draw(screen)
    screen.blit(update_fps(), (10, 0))
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()