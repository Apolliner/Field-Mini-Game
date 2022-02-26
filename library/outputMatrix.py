import pygame
import numpy as np
from math import sin, cos
from library.constans import DEGREES_IN_RAD

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


class ImageTile(pygame.sprite.Sprite):
    """ Спрайт с изображением, изменяемый с помошью матрицы """

    def __init__(self, zero_x, zero_y, number_x, number_y, size_tile, image_tile, degrees, alpha=255):

        pygame.sprite.Sprite.__init__(self)
        self.start_size_tile = size_tile
        self.old_size_tile = size_tile
        self.number_x = number_x
        self.number_y = number_y
        self.img = image_tile
        self.image = pygame.transform.scale(self.image, (size_tile, size_tile))
        self.rect = self.image.get_rect()
        position = [zero_x + number_x*size_tile, zero_y + number_y*size_tile]
        self.rect.center = position
        self.speed = 0
        self.old_degrees = degrees

    def update(self, size_tile, multi_matrix, degrees):
        position_matrix = np.matrix(((self.number_x * self.start_size_tile, self.number_y * self.start_size_tile, 1)))
        result_position = position_matrix * multi_matrix
        position = [result_position[(0, 0)], result_position[(0, 1)]]
        if self.old_degrees != degrees or self.old_size_tile != size_tile:
            self.image = pygame.transform.scale(self.img, (size_tile, size_tile))
            self.rect = self.image.get_rect()
        self.rect.center = position
        self.old_size_tile = size_tile
        self.old_degrees = degrees