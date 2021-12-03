import pygame
import random
import time
from library.classes import Tile

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ФОРМИРОВАНИЕ БЛОКОВ ДЛЯ ВЫВОДА НА ЭКРАН ЧЕРЕЗ PYGAME ДЛЯ МУЛЬТИПЛЕЕРНОЙ ВЕРСИИ ИГРЫ


+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


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

    all_color_dict = add_color_dict(5000)

    def __init__(self, x, y, size_tile, number):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(number))
        self.image.set_alpha(60)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def color_dict(self, number):
        if number in self.all_color_dict:
            return self.all_color_dict[number]
        else:
            return (random.randrange(256), random.randrange(256), random.randrange(256))


class Minimap_temperature(pygame.sprite.Sprite):
    """ Содержит спрайты температуры """

    def __init__(self, x, y, size_tile, temperature):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill(self.color_dict(temperature))
        self.image.set_alpha(95)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def color_dict(self, temperature):
        color_dict = {
            0: (0, 0, 0),
            1: (0, 0, 255),
            2: (100, 100, 200),
            3: (100, 200, 100),
            4: (200, 255, 100),
            5: (255, 255, 0),
            6: (255, 225, 0),
            7: (255, 200, 0),
            8: (255, 165, 0),
            9: (255, 130, 0),
            10: (255, 100, 0),
            11: (255, 70, 0),
            12: (255, 40, 0),
            13: (255, 0, 0),
            14: (225, 0, 0),
            15: (200, 0, 0),
            16: (150, 0, 0),
            17: (100, 0, 0),
            18: (0, 0, 0),
        }
        key = 0
        if temperature <= 0:
            key = 1
        elif 0 < temperature <= 5:
            key = 2
        elif 5 < temperature <= 10:
            key = 3
        elif 10 < temperature <= 15:
            key = 4
        elif 15 < temperature <= 20:
            key = 5
        elif 20 < temperature <= 25:
            key = 6
        elif 25 < temperature <= 30:
            key = 7
        elif 30 < temperature <= 35:
            key = 8
        elif 35 < temperature <= 40:
            key = 9
        elif 40 < temperature <= 45:
            key = 10
        elif 45 < temperature <= 50:
            key = 11
        elif temperature > 50:
            key = 15
        return color_dict[key]


def landscape_layer_calculations(person, chunk_size, go_to_print):
    """
        Формирует изображение ландшафта на печать
    """
    half_views = (chunk_size // 2)
    start_stop = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views),
                  (person.dynamic[0] + half_views + 1), (person.dynamic[1] + half_views + 1)]
    line_views = person.chunks_use_map[start_stop[0]:start_stop[2]]

    go_to_print.point_to_draw = [(person.dynamic[0] - half_views), (person.dynamic[1] - half_views)]

    landscape_layer = []
    for line in line_views:
        new_line = []
        line = line[start_stop[1]:start_stop[3]]
        for tile in line:
            new_line.append(tile)
        landscape_layer.append(new_line)
    return landscape_layer


def entities_layer_calculations(person, chunk_size: int, go_to_print, entities_list):
    """
        Отрисовывает слой активностей или слой персонажей
    """
    start_stop = [(person.dynamic[0] - chunk_size // 2), (person.dynamic[1] - chunk_size // 2),
                  (person.dynamic[0] + chunk_size // 2 + 1), (person.dynamic[1] + chunk_size // 2 + 1)]
    go_draw_entities = []
    #print()
    #print(F"person.assemblage_point - {person.assemblage_point}, local_position - {person.local_position}, global_position - {person.global_position}")
    for entity in entities_list:
        if entity.visible or person.test_visible:
            if entity.global_position[0] == person.assemblage_point[0] and entity.global_position[1] == \
                    person.assemblage_point[1]:
                #print(F"true 1 local_position - {entity.local_position}, global_position - {entity.global_position}, name - {entity.name}")
                go_draw_entities.append([entity.local_position[0], entity.local_position[1], entity])

            elif entity.global_position[0] == person.assemblage_point[0] and entity.global_position[1] == \
                    person.assemblage_point[1] + 1:
                #print(F"true 2 local_position - {entity.local_position}, global_position - {entity.global_position}, name - {entity.name}")
                go_draw_entities.append([entity.local_position[0], entity.local_position[1] + chunk_size, entity])

            elif entity.global_position[0] == person.assemblage_point[0] + 1 and entity.global_position[1] == \
                    person.assemblage_point[1]:
                #print(F"true 3 local_position - {entity.local_position}, global_position - {entity.global_position}, name - {entity.name}")
                go_draw_entities.append([entity.local_position[0] + chunk_size, entity.local_position[1], entity])

            elif entity.global_position[0] == person.assemblage_point[0] + 1 and entity.global_position[1] == \
                    person.assemblage_point[1] + 1:
                #print(F"true 5 local_position - {entity.local_position}, global_position - {entity.global_position}, name - {entity.name}")
                go_draw_entities.append(
                    [entity.local_position[0] + chunk_size, entity.local_position[1] + chunk_size, entity])
    #print(F"\b\bgo_draw_entities - {go_draw_entities}\n")
    entities_layer = []
    for number_line in range(start_stop[0], start_stop[2]):
        new_line = []
        for number_tile in range(start_stop[1], start_stop[3]):
            no_changes = True
            for entity in go_draw_entities:    # FIXME СУПЕР НЕ ЭФФЕКТИВНО
                if number_line == entity[0] and number_tile == entity[1]:
                    #print(F"true")
                    new_line.append(entity[2])
                    no_changes = False
                    break
            if no_changes:
                new_line.append(Tile('0'))
        entities_layer.append(new_line)

    return entities_layer


def sky_layer_calculations(chunk_size):
    """
        Отрисовывает сущности на небе. Пока что создаёт карту-пустышку.
    """
    sky_layer = []
    for number_line in range(chunk_size):
        new_line = []
        for number_tile in range(chunk_size):
            new_line.append(Tile('0'))
        sky_layer.append(new_line)
    return sky_layer


class Level_tiles(pygame.sprite.Sprite):
    """ Содержит спрайты миникарты """

    def __init__(self, x, y, size_tile, level):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size_tile, size_tile))
        self.image.fill((239, 228, 176), special_flags=pygame.BLEND_RGB_ADD)
        self.image.set_alpha(25 * level)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def load_tile_table(filename, width, height):
    """
        Режет большой тайлсет на спрайты тайлов
    """
    image = pygame.image.load(filename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, image_width / width):
        line = []
        tile_table.append(line)
        for tile_y in range(0, image_height / height):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tile_table


def print_minimap(global_map, person, go_to_print, enemy_list):
    """
        Печатает упрощенную схему глобальной карты по биомам
    """

    minimap = []
    for number_line in range(len(global_map)):
        print_line = ''
        for biom in range(len(global_map[number_line])):
            enemy_here = '--'
            for enemy in range(len(enemy_list)):
                if number_line == enemy_list[enemy].global_position[0] and biom == enemy_list[enemy].global_position[1]:
                    enemy_here = enemy_list[enemy].icon
            if number_line == person.global_position[0] and biom == person.global_position[1]:
                go_to_print.text2 = global_map[number_line][biom].name
                go_to_print.text3 = [global_map[number_line][biom].temperature, 36.6]
                print_line += '☺'
            elif enemy_here != '--':
                print_line += enemy_here
            else:
                print_line += global_map[number_line][biom].icon + ''
        minimap.append((print_line))
    go_to_print.biom_map = minimap


class Offset_sprites:
    """ Передаёт в следующий ход смещение выводимых на экран спрайтов """

    def __init__(self):
        self.all = [0, 0]


def person_walk_draw(entity, person, settings_for_intermediate_steps):
    """
        Меняет кадры анимации персонажа во время промежуточных кадров
    """
    #print()
    #print(F"entity before type = {entity.type}")
    direction_dict = {
        'left': {0: 'l0',
                 1: 'l1',
                 2: 'l2',
                 3: 'l3'},
        'right': {0: 'r0',
                  1: 'r1',
                  2: 'r2',
                  3: 'r3'},
        'up': {0: 'u0',
               1: 'u1',
               2: 'u2',
               3: 'u3'},
        'down': {0: 'd0',
                 1: 'd1',
                 2: 'd2',
                 3: 'd3'}
    }

    intermediate_steps_dict = {
        2: [0, 1],
        3: [0, 1, 2],
        5: [0, 1, 1, 2, 3],
        6: [0, 1, 1, 2, 2, 3],
        10: [0, 0, 1, 1, 1, 2, 2, 2, 3, 3],
        15: [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3],
        30: [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
    }

    entity.type = direction_dict[entity.direction][
        intermediate_steps_dict[settings_for_intermediate_steps[0]][person.pass_draw_move - 1]]
    print(F"entity.name = {entity.name}entity after type = {entity.type}")


def new_npc_walk_draw(entity, person, settings_for_intermediate_steps):
    """
            Меняет кадры анимации персонажа во время промежуточных кадров
    """
    intermediate_steps_dict = {
        2: [0, 1],
        3: [0, 1, 2],
        5: [0, 1, 1, 2, 3],
        6: [0, 1, 1, 2, 2, 3],
        10: [0, 0, 1, 1, 1, 2, 2, 2, 3, 3],
        15: [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3],
        30: [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
    }
    # Если нет движения то за направление принимается старое движение
    if entity.direction == "center":
        animation = "pf"
        direction = entity.old_direction[0]
    # Если движение есть, то устанавливается новое направление
    else:
        entity.old_direction = entity.direction
        direction = entity.direction[0]
        animation = "p"
    intermediate_step = intermediate_steps_dict[settings_for_intermediate_steps[0]][person.pass_draw_move - 1]

    entity.type = F"{direction}{animation}{intermediate_step}"


class Draw_open_image(pygame.sprite.Sprite):
    """ Отрисовывает полученное изображение """

    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Draw_rect(pygame.sprite.Sprite):
    """ Отрисовывает любую поверхность """

    def __init__(self, x, y, x_size, y_size, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x_size, y_size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.speed = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def master_pygame_draw(person, chunk_size, go_to_print, global_map, mode_action, enemy_list, activity_list, screen,
                       minimap_surface, minimap_dict, sprites_dict, offset_sprites, landscape_layer, activity_layer,
                       entities_layer, finishing_surface, settings_for_intermediate_steps, mouse_position, raw_minimap):
    """
        Работает с классом Interfaсe, содержащимся в go_to_print

        Формирует 4 слоя итогового изображения:
            1) Ландшафт
            2) Следы активностей
            3) Персонажи
            4) Небо (опционально)

        Отрисовывает в следующем порядке:
            1) Ландшафт
            2) Следы активностей
            3) Персонажи
            4) Персонаж игрока
            5) Небо (опционально)

        РЕАЛИЗОВАТЬ:
        1) Изменение смещения и количества промежуточных шагов в зависимости от времени, потраченного на основной кадр

    """

    time_1 = time.time()  # проверка времени выполнения

    size_tile = 30  # Настройка размера тайлов игрового окна
    size_tile_minimap = 15  # Настройка размера тайлов миникарты

    number_intermediate_steps = settings_for_intermediate_steps[0]  # Количество промежуточных шагов
    step_direction = settings_for_intermediate_steps[1]  # Смещение промежуточного шага

    if not person.pointer_step:  # Если не шаг указателя
        if person.pass_draw_move:  # Промежуточный кадр
            # Рассчет кадра движения персонажа
            if person.direction in ('left', 'right', 'down', 'up'):
                person_walk_draw(person, person, settings_for_intermediate_steps)

            working_minimap_surface = pygame.Surface.copy(minimap_surface)  # Копирование поверхности миникарты

            blit_coordinates = (0, 0)

            if person.direction == 'up':
                offset_sprites.all[0] += step_direction
                blit_coordinates = (0, step_direction)
            elif person.direction == 'down':
                offset_sprites.all[0] -= step_direction
                blit_coordinates = (0, 0 - step_direction)
            elif person.direction == 'left':
                offset_sprites.all[1] += step_direction
                blit_coordinates = (step_direction, 0)
            elif person.direction == 'right':
                offset_sprites.all[1] -= step_direction
                blit_coordinates = (0 - step_direction, 0)

            working_surface = pygame.Surface.copy(finishing_surface)
            finishing_surface.blit(working_surface, blit_coordinates)

            screen.blit(finishing_surface, (0, 0))

            # Отрисовка активностей
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if activity_layer[number_line][number_tile].icon != '0':
                        print_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][
                            activity_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line * size_tile + offset_sprites.all[0]
                        print_sprite.rect.left = number_tile * size_tile + offset_sprites.all[1]
                        print_sprite.draw(screen)

            # Отрисовка НПЦ
            entities_layer = entities_layer_calculations(person, chunk_size, go_to_print, enemy_list)
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if entities_layer[number_line][number_tile].icon != '0':
                        if entities_layer[number_line][number_tile].name == 'riffleman' or \
                                            hasattr(entities_layer[number_line][number_tile], 'memory'):  # FIXME

                            if hasattr(entities_layer[number_line][number_tile], 'memory'):
                                new_npc_walk_draw(entities_layer[number_line][number_tile], person,
                                                  settings_for_intermediate_steps)
                            elif entities_layer[number_line][number_tile].direction in ('left', 'right', 'down', 'up'):
                                person_walk_draw(entities_layer[number_line][number_tile], person,
                                                 settings_for_intermediate_steps)

                        offset_enemy = entities_layer[number_line][number_tile].offset
                        #print()
                        #print(F"true 1 enemy.direction - {entities_layer[number_line][number_tile].direction}")
                        if entities_layer[number_line][number_tile].direction == 'left':
                            #print(F"true 2")
                            offset_enemy[1] -= step_direction
                        elif entities_layer[number_line][number_tile].direction == 'right':
                            #print(F"true 3")
                            offset_enemy[1] += step_direction
                        elif entities_layer[number_line][number_tile].direction == 'up':
                            #print(F"true 4")
                            offset_enemy[0] -= step_direction
                        elif entities_layer[number_line][number_tile].direction == 'down':
                            #print(F"true 5")
                            offset_enemy[0] += step_direction
                        else:
                            #print(F"true 6")
                            offset_enemy = [0, 0]
                        #print(F"\nenemy.name - {entities_layer[number_line][number_tile].name} offset_enemy - {offset_enemy}")
                        print_sprite = sprites_dict[entities_layer[number_line][number_tile].icon][
                            entities_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line * size_tile + offset_sprites.all[0] + offset_enemy[0]
                        print_sprite.rect.left = number_tile * size_tile + offset_sprites.all[1] + offset_enemy[1]
                        print_sprite.draw(screen)

            person.pass_draw_move -= 1

        else:  # Основной кадр

            screen.fill((255, 255, 255))
            # Перерисовка миникарты
            working_minimap_surface = pygame.Surface.copy(minimap_surface)
            # Количество промежуточных кадров
            person.pass_draw_move = number_intermediate_steps
            # Определение смещения
            offset_y = 0
            offset_x = 0
            if person.direction == 'left':
                offset_x -= size_tile
            elif person.direction == 'right':
                offset_x += size_tile
            elif person.direction == 'up':
                offset_y -= size_tile
            elif person.direction == 'down':
                offset_y += size_tile

            offset_sprites.all = [offset_y, offset_x]

            # minimap_sprite = pygame.sprite.Group()
            landscape_layer = landscape_layer_calculations(person, chunk_size, go_to_print)
            activity_layer = entities_layer_calculations(person, chunk_size, go_to_print, activity_list)
            # sky_layer = sky_layer_calculations(chunk_size)

            if person.recalculating_the_display:  # Если нужно перерисовывать весь экран
                # Отрисовка ландшафта
                for number_line in range(chunk_size):
                    for number_tile in range(chunk_size):
                        print_sprite = sprites_dict[landscape_layer[number_line][number_tile].icon][
                            landscape_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line * size_tile + offset_y
                        print_sprite.rect.left = number_tile * size_tile + offset_x
                        print_sprite.draw(finishing_surface)

                        if landscape_layer[number_line][number_tile].level > 1:
                            Level_tiles(number_tile * size_tile + offset_x, number_line * size_tile + offset_y,
                                        size_tile,
                                        landscape_layer[number_line][number_tile].level - 1).draw(finishing_surface)

                screen.blit(finishing_surface, (0, 0))  # Отрисовка финишной поверхности

                # Отрисовка активностей
                for number_line in range(chunk_size):
                    for number_tile in range(chunk_size):
                        if activity_layer[number_line][number_tile].icon != '0':
                            activity_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][
                                activity_layer[number_line][number_tile].type]
                            activity_sprite.rect.top = number_line * size_tile + offset_y
                            activity_sprite.rect.left = number_tile * size_tile + offset_x
                            activity_sprite.draw(screen)

            else:  # Если нужно перерисовывать только линии или столбцы
                working_surface = pygame.Surface.copy(finishing_surface)
                number_line = 0
                number_tile = 0
                if person.direction == 'left':
                    number_line = 0
                    number_tile = chunk_size
                elif person.direction == 'right':
                    number_line = 0
                    number_tile = chunk_size - 1
                elif person.direction == 'up':
                    number_line = chunk_size
                    number_tile = 0
                elif person.direction == 'down':
                    number_line = chunk_size - 1
                    number_tile = 0

                finishing_surface.blit(working_surface, (number_line, number_tile))
                for number_len in range(len(landscape_layer)):
                    number_line = 0
                    number_tile = 0
                    if person.direction == 'left':
                        number_line = number_len
                        number_tile = 0
                    elif person.direction == 'right':
                        number_line = number_len
                        number_tile = chunk_size - 1
                    elif person.direction == 'up':
                        number_line = 0
                        number_tile = number_len
                    elif person.direction == 'down':
                        number_line = chunk_size - 1
                        number_tile = number_len

                    # Отрисовка рассчитаных линий и столбцов
                    print_sprite = sprites_dict[landscape_layer[number_line][number_tile].icon][
                        landscape_layer[number_line][number_tile].type]
                    print_sprite.rect.top = number_line * size_tile
                    print_sprite.rect.left = number_tile * size_tile
                    print_sprite.draw(finishing_surface)

                    if landscape_layer[number_line][number_tile].level > 1:
                        Level_tiles(number_tile * size_tile + offset_x, number_line * size_tile + offset_y, size_tile,
                                    landscape_layer[number_line][number_tile].level - 1).draw(finishing_surface)
                    if activity_layer[number_line][number_tile].icon != '0':
                        print_sprite = sprites_dict[activity_layer[number_line][number_tile].icon][
                            activity_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line * size_tile
                        print_sprite.rect.left = number_tile * size_tile
                        print_sprite.draw(finishing_surface)
                        # Отрисовка НПЦ
            entities_layer = entities_layer_calculations(person, chunk_size, go_to_print,
                                                         enemy_list)  # Использование функции для отображения активностей

            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    if entities_layer[number_line][number_tile].icon != '0':
                        enemy_offset_x = 0
                        enemy_offset_y = 0
                        if entities_layer[number_line][number_tile].direction == 'left':
                            enemy_offset_x = size_tile

                        elif entities_layer[number_line][number_tile].direction == 'right':
                            enemy_offset_x = 0 - size_tile

                        elif entities_layer[number_line][number_tile].direction == 'up':
                            enemy_offset_y = size_tile

                        elif entities_layer[number_line][number_tile].direction == 'down':
                            enemy_offset_y = 0 - size_tile

                        entities_layer[number_line][number_tile].offset = [enemy_offset_y, enemy_offset_x]
                        print_sprite = sprites_dict[entities_layer[number_line][number_tile].icon][
                            entities_layer[number_line][number_tile].type]
                        print_sprite.rect.top = number_line * size_tile + offset_sprites.all[0] + enemy_offset_y
                        print_sprite.rect.left = number_tile * size_tile + offset_sprites.all[1] + enemy_offset_x
                        print_sprite.draw(screen)

        # Отрисовка зон доступности
        if person.test_visible:
            for number_line in range(chunk_size):
                for number_tile in range(chunk_size):
                    Island_friends(number_tile * size_tile + offset_sprites.all[1],
                                   number_line * size_tile + offset_sprites.all[0], size_tile,
                                   landscape_layer[number_line][number_tile].vertices).draw(screen)
                    if landscape_layer[number_line][number_tile].stairs:
                        print_sprite = sprites_dict['stairs']['0']
                        print_sprite.rect.top = number_line * size_tile + offset_sprites.all[0]
                        print_sprite.rect.left = number_tile * size_tile + offset_sprites.all[1]
                        print_sprite.draw(screen)

            if person.zone_relationships:
                person_offset = [0, 0]
                if person.direction == 'left':
                    person_offset = [0, 1]
                elif person.direction == 'right':
                    person_offset = [0, -1]
                elif person.direction == 'up':
                    person_offset = [1, 0]
                elif person.direction == 'down':
                    person_offset = [-1, 0]
                for number_vertices, vertices in enumerate(person.zone_relationships):
                    if person.number_chunk == number_vertices:
                        for vertice in vertices:
                            if vertice.connections:
                                for connect in vertice.connections:
                                    for tile in connect.tiles:
                                        if (person.local_position[0] - chunk_size // 2) < tile[0] < (
                                                person.local_position[0] + chunk_size // 2) and (
                                                person.local_position[1] - chunk_size // 2) < tile[1] < (
                                                person.local_position[1] + chunk_size // 2):
                                            offset = [tile[0] - person.local_position[0],
                                                      tile[1] - person.local_position[1]]
                                            Island_friends(
                                                (chunk_size // 2 + offset[1] + person_offset[1]) * size_tile +
                                                offset_sprites.all[1] + 10,
                                                (chunk_size // 2 + offset[0] + person_offset[0]) * size_tile +
                                                offset_sprites.all[0] + 10,
                                                10, connect.number).draw(screen)

        # Отрисовка персонажа
        person_sprite = sprites_dict[person.icon][person.type]
        person_sprite.rect.top = chunk_size // 2 * size_tile
        person_sprite.rect.left = chunk_size // 2 * size_tile
        person_sprite.draw(screen)

        # Рисование белой рамки, закрывающей смещение
        for number_line in range(chunk_size + 1):
            for number_tile in range(chunk_size + 1):
                if 0 == number_line or number_line == chunk_size:
                    Draw_rect(number_line * size_tile, number_tile * size_tile, size_tile, size_tile,
                              (255, 255, 255)).draw(screen)
                if 0 == number_tile or number_tile == chunk_size:
                    Draw_rect(number_line * size_tile, number_tile * size_tile, size_tile, size_tile,
                              (255, 255, 255)).draw(screen)

        # Печать персонажей на миникарту
        person_sprite = minimap_dict[person.icon][person.type]
        person_sprite.rect.top = person.global_position[0] * size_tile_minimap
        person_sprite.rect.left = person.global_position[1] * size_tile_minimap
        person_sprite.draw(working_minimap_surface)

        for enemy in enemy_list:
            if not hasattr(enemy, 'memory'):
                enemy_sprite = minimap_dict[enemy.icon][enemy.type]
                enemy_sprite.rect.top = enemy.global_position[0] * size_tile_minimap
                enemy_sprite.rect.left = enemy.global_position[1] * size_tile_minimap
                enemy_sprite.draw(working_minimap_surface)

        screen.blit(working_minimap_surface, ((len(global_map) - 1) * size_tile, 0))

        # Отрисовка температуры на миникарте
        if person.test_visible:
            for number_minimap_line, minimap_line in enumerate(raw_minimap):
                for number_minimap_tile, minimap_tile in enumerate(minimap_line):
                    Minimap_temperature(number_minimap_tile * size_tile_minimap + (26 * size_tile),
                                        number_minimap_line * size_tile_minimap,
                                        size_tile_minimap, minimap_tile.temperature).draw(screen)

    time_2 = time.time()  # проверка времени выполнения

    # Рассчёт количества промежуточных шагов в зависимости от скорости вывода основного шага
    if not person.pointer_step:
        settings_for_intermediate_steps = frames_per_cycle_and_delays(person, time_1, time_2,
                                                                      settings_for_intermediate_steps)

    end = time.time()  # проверка времени выполнения

    Draw_rect(30 * 26, 30 * 14, 1000, 500, (255, 255, 255)).draw(screen)  # заливает белым область надписей

    print_time = f"{person.world_position} - person.world_position, {settings_for_intermediate_steps} - скорость шага, {mouse_position} - mouse_position"  # {round(time_2 - time_1, 4)} - отрисовка"

    fontObj = pygame.font.Font('freesansbold.ttf', 10)
    textSurfaceObj = fontObj.render(print_time, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30 * 34, 15 * 30)
    screen.blit(textSurfaceObj, textRectObj)

    print_pointer = F"Под ногами {pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position, 'ground', raw_minimap)}"

    textSurfaceObj = fontObj.render(print_pointer, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30 * 34, 16 * 31)
    screen.blit(textSurfaceObj, textRectObj)

    print_pointer = F"Вы видите {pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position, 'pointer', raw_minimap)}"

    textSurfaceObj = fontObj.render(print_pointer, True, (0, 0, 0), (255, 255, 255))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (30 * 34, 17 * 31)
    screen.blit(textSurfaceObj, textRectObj)

    pygame.display.flip()

    return screen, landscape_layer, activity_layer, entities_layer, offset_sprites, finishing_surface, settings_for_intermediate_steps


def pointer_description(landscape_layer, activity_layer, entities_layer, chunk_size, size_tile, mouse_position,
                        type_descrption, raw_minimap):
    """
        Собирает описание того что под ногами и того, куда указывает указатель
        coords - [x, y]
    """

    def coords_description(coords, area, chunk_size):
        """
            Принимает координаты и карту, возвращает описание.
        """
        if coords[0] < chunk_size and coords[1] < chunk_size:
            return area[coords[1]][coords[0]].description
        else:
            return ''

    person_coords = [chunk_size // 2, chunk_size // 2]
    mouse_coords = []
    for axis_position in mouse_position:
        mouse_coords.append(axis_position // size_tile)
    ground_description = ''
    pointer_description = ''
    if mouse_coords[0] < chunk_size and mouse_coords[1] < chunk_size:
        pointer_description += 'vertices = ' + str(
            landscape_layer[mouse_coords[1]][mouse_coords[0]].vertices) + ' тут ' + str(
            landscape_layer[mouse_coords[1]][mouse_coords[0]].list_of_features) + ' '

    for area in (landscape_layer, activity_layer, entities_layer):
        ground_description += coords_description(person_coords, area, chunk_size)
        pointer_description += coords_description(mouse_coords, area, chunk_size)
    if mouse_coords[0] > chunk_size:
        minimap_coords = []
        axis_position_x, axis_position_y = mouse_position
        minimap_coords.append((axis_position_x - (chunk_size + 1) * size_tile) // 15)
        minimap_coords.append(axis_position_y // 15)
        pointer_description += coords_description(minimap_coords, raw_minimap, len(raw_minimap))
        if minimap_coords[0] < len(raw_minimap) and minimap_coords[1] < len(raw_minimap):
            pointer_description += f" | T = {int(raw_minimap[minimap_coords[1]][minimap_coords[0]].temperature)} градусов"

    if type_descrption == 'ground':
        return ground_description
    else:
        return pointer_description

def frames_per_cycle_and_delays(person, time_1, time_2, settings_for_intermediate_steps):
    """
        Рассчёт количества промежуточных шагов в зависимости от скорости вывода основного шага и
        установка задержек на промежуточные кадры для плавности перемещения
    """
    if not person.person_pass_step and not person.enemy_pass_step:
        if (time_2 - time_1) >= 0.075:
            settings_for_intermediate_steps = [2, 15]
        elif 0.075 > (time_2 - time_1) >= 0.05:
            settings_for_intermediate_steps = [3, 10]
        elif 0.05 > (time_2 - time_1) >= 0.03:
            settings_for_intermediate_steps = [5, 6]
        elif 0.03 > (time_2 - time_1) >= 0.025:
            settings_for_intermediate_steps = [6, 5]
        elif 0.025 > (time_2 - time_1) >= 0.015:
            settings_for_intermediate_steps = [10, 3]
        elif 0.015 > (time_2 - time_1) >= 0.01:
            settings_for_intermediate_steps = [15, 2]
        elif 0.01 > (time_2 - time_1):
            settings_for_intermediate_steps = [30, 1]
        person.pass_draw_move = settings_for_intermediate_steps[0]

    elif person.person_pass_step and person.enemy_pass_step: #Установка задержек на промежуточные кадры для плавности перемещения
        if settings_for_intermediate_steps == [2, 15] and (time_2 - time_1) < 0.1:
            time.sleep(0.1 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [3, 10] and (time_2 - time_1) < 0.08:
            time.sleep(0.08 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [5, 6] and (time_2 - time_1) < 0.03:
            time.sleep(0.03 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [6, 5] and (time_2 - time_1) < 0.025:
            time.sleep(0.025 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [10, 3] and (time_2 - time_1) < 0.015:
            time.sleep(0.015 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [15, 2] and (time_2 - time_1) < 0.01:
            time.sleep(0.01 - (time_2 - time_1))
        elif settings_for_intermediate_steps == [30, 1] and (time_2 - time_1) < 0.005:
            time.sleep(0.005 - (time_2 - time_1))
    return settings_for_intermediate_steps