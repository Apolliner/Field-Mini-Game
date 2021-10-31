import pygame
import random
import copy
import sys
from library.utils import gluing_location
from library.classes import Action_in_map
from library.gameEvents import return_npc, return_creature
from library.gameEvents import world_position_recalculation
from library.characterNPC import NPC


"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ПОЛЬЗОВАТЕЛЬСКИЙ ВВОД И ЕГО ОБРАБОТКА

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


def master_player_action(global_map, person, chunk_size, go_to_print, mode_action, interaction, activity_list, step,
                         enemy_list, mouse_position):
    person.level = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].level  # Определение высоты персонажа
    person.vertices = person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].vertices
    pressed_button = ''
    person.check_local_position()
    person.direction = 'center'
    person.global_position_calculation(chunk_size)
    person.activating_spawn = False

    mode_action, pressed_button, mouse_position = request_press_button(global_map, person, chunk_size, go_to_print,
                                                                       mode_action,
                                                                       interaction, mouse_position)

    if pressed_button != 'none':
        if mode_action == 'move':
            activity_list.append(
                Action_in_map('faint_footprints', step, person.global_position, person.local_position, chunk_size,
                              person.name, person))
            if random.randrange(21) // 18 > 0:  # Оставление персонажем следов
                if not global_map[person.global_position[0]][person.global_position[1]].chunk[person.local_position[0]][
                           person.local_position[1]].icon in ('f', '~'):
                    activity_list.append(
                        Action_in_map('human_tracks', step, person.global_position, person.local_position, chunk_size,
                                      person.name, person))
            if random.randrange(40) // 38 > 0:  # Активация спавнов существ
                person.activating_spawn = True
            request_move(global_map, person, chunk_size, go_to_print, pressed_button)

        elif mode_action == 'test_move':
            test_request_move(global_map, person, chunk_size, go_to_print, pressed_button, interaction, activity_list,
                              step, enemy_list, mouse_position)

        elif mode_action == 'pointer':
            request_pointer(person, chunk_size, go_to_print, pressed_button)
        elif mode_action == 'gun':
            request_gun(global_map, person, chunk_size, go_to_print, pressed_button)
        if pressed_button == 'button_map':
            go_to_print.minimap_on = (go_to_print.minimap_on == False)
        request_processing(pressed_button)

    person.global_position_calculation(chunk_size)
    person.check_local_position()
    person.world_position_calculate(chunk_size)

    return mode_action, mouse_position


def wait_keyboard(person, mouse_position):
    """
        Ждёт нажатия клавиши или изменения положения указателя мыши
    """
    pygame.key.set_repeat(1, 2)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                mouse_position = event.pos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    return 'a', mouse_position
                if event.key == pygame.K_RIGHT:
                    return 'd', mouse_position
                if event.key == pygame.K_UP:
                    return 'w', mouse_position
                if event.key == pygame.K_DOWN:
                    return 's', mouse_position
                if event.key == pygame.K_ESCAPE:
                    return 'escape', mouse_position
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return 'space', mouse_position
                if event.key == pygame.K_w:
                    return 'w', mouse_position
                if event.key == pygame.K_a:
                    return 'a', mouse_position
                if event.key == pygame.K_s:
                    return 's', mouse_position
                if event.key == pygame.K_d:
                    return 'd', mouse_position
                if event.key == pygame.K_t:
                    return 't', mouse_position
                if event.key == pygame.K_p:
                    return 'p', mouse_position
                if event.key == pygame.K_v:
                    return 'v', mouse_position
                if event.key == pygame.K_c:
                    return 'c', mouse_position
                if event.key == pygame.K_h:
                    return 'h', mouse_position
                if event.key == pygame.K_o:
                    return 'o', mouse_position
                if event.key == pygame.K_e:
                    return 'e', mouse_position
                if event.key == pygame.K_z:
                    return 'z', mouse_position
                if event.key == pygame.K_f:
                    return 'f', mouse_position
            if event.type == pygame.MOUSEMOTION:
                person.pointer_step = True
                return 'none', event.pos


def request_press_button(global_map, person, chunk_size, go_to_print, mode_action, interaction, mouse_position):
    """
        Спрашивает ввод, возвращает тип активности и нажимаемую кнопку

    """
    pygame.event.clear()
    key, mouse_position = wait_keyboard(person, mouse_position)

    if key == 'w' or key == 'up' or key == 'ц':
        return (mode_action, 'up', mouse_position)
    elif key == 'a' or key == 'left' or key == 'ф':
        return (mode_action, 'left', mouse_position)
    elif key == 's' or key == 'down' or key == 'ы':
        return (mode_action, 'down', mouse_position)
    elif key == 'd' or key == 'right' or key == 'в':
        return (mode_action, 'right', mouse_position)
    elif key == 'space':
        return (mode_action, 'space', mouse_position)
    elif key == 'escape':
        return ('in_game_menu', 'escape', mouse_position)
    elif key == 'k' or key == 'л':
        if mode_action == 'move':
            person.pointer = [chunk_size // 2, chunk_size // 2]
            return ('pointer', 'button_pointer', mouse_position)
        elif mode_action == 'pointer':
            person.pointer = [chunk_size // 2, chunk_size // 2]
            return ('move', 'button_pointer', mouse_position)
        else:
            person.pointer = [chunk_size // 2, chunk_size // 2]
            person.gun = [chunk_size // 2, chunk_size // 2]
            return ('move', 'button_pointer', mouse_position)
    elif key == 'g' or key == 'п':
        if mode_action == 'move':
            person.gun = [chunk_size // 2, chunk_size // 2]
            return ('gun', 'button_gun', mouse_position)
        elif mode_action == 'gun':
            person.gun = [chunk_size // 2, chunk_size // 2]
            return ('move', 'button_gun', mouse_position)
        else:
            person.pointer = [chunk_size // 2, chunk_size // 2]
            person.gun = [chunk_size // 2, chunk_size // 2]
            return ('move', 'button_gun', mouse_position)
    elif key == 'm' or key == 'ь':
        return (mode_action, 'button_map', mouse_position)
    elif key == 't' or key == 'е':
        if mode_action == 'test_move':
            return ('move', 'button_test', mouse_position)
        else:
            return ('test_move', 'button_test', mouse_position)
    elif key == 'p' or key == 'з':
        if mode_action == 'test_move':
            return ('test_move', 'button_purpose_task', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'v' or key == 'м':
        if mode_action == 'test_move':
            return ('test_move', 'button_test_visible', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'o' or key == 'щ':
        if mode_action == 'test_move':
            return ('test_move', 'view_waypoints', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'e' or key == 'у':
        if mode_action == 'test_move':
            return ('test_move', 'escape_me', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'b' or key == 'и':
        if mode_action == 'test_move':
            return ('test_move', 'button_add_beacon', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'c' or key == 'с':
        if mode_action == 'test_move':
            return ('test_move', 'add_coyot', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'z' or key == 'я':
        if mode_action == 'test_move':
            return ('test_move', 'add_snake', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'f' or key == 'а':
        if mode_action == 'test_move':
            return ('test_move', 'follow_me', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    elif key == 'h' or key == 'р':
        if mode_action == 'test_move':
            return ('test_move', 'add_hunter', mouse_position)
        else:
            return (mode_action, 'none', mouse_position)
    else:
        return (mode_action, 'none', mouse_position)


def request_move(global_map: list, person, chunk_size: int, go_to_print, pressed_button):
    """
        Меняет динамическое местоположение персонажа


        Сначала происходит проверка не является ли следующий по пути тайл скалой, затем проверяется не находится ли он на другом уровне
        или лестницей или персонаж сейчас стоит на лестнице.
    """
    if pressed_button == 'up':

        if person.chunks_use_map[person.dynamic[0] - 1][person.dynamic[1]].icon != '▲' and (
                person.level == person.chunks_use_map[
            person.dynamic[0] - 1][person.dynamic[1]].level or person.chunks_use_map[person.dynamic[0] - 1][
                    person.dynamic[1]].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[0] >= chunk_size // 2 and person.assemblage_point[0] > 0:
                person.dynamic[0] -= 1
                person.direction = 'up'
                person.type = 'u3'

    elif pressed_button == 'left':

        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] - 1].icon != '▲' and (
                person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] - 1].level or person.chunks_use_map[person.dynamic[0]][
                    person.dynamic[1] - 1].stairs or person.chunks_use_map[person.dynamic[0]][
                    person.dynamic[1]].stairs):
            if person.dynamic[1] >= chunk_size // 2 and person.assemblage_point[1] > 0:
                person.dynamic[1] -= 1
                person.direction = 'left'
                person.type = 'l3'

    elif pressed_button == 'down':

        if person.chunks_use_map[person.dynamic[0] + 1][person.dynamic[1]].icon != '▲' and (
                person.level == person.chunks_use_map[
            person.dynamic[0] + 1][person.dynamic[1]].level or person.chunks_use_map[person.dynamic[0] + 1][
                    person.dynamic[1]].stairs or person.chunks_use_map[person.dynamic[0]][person.dynamic[1]].stairs):
            if person.dynamic[0] <= (chunk_size + chunk_size // 2) and person.assemblage_point[0] != (
                    len(global_map) - 2):
                person.dynamic[0] += 1
                person.direction = 'down'
                person.type = 'd3'

    elif pressed_button == 'right':

        if person.chunks_use_map[person.dynamic[0]][person.dynamic[1] + 1].icon != '▲' and (
                person.level == person.chunks_use_map[
            person.dynamic[0]][person.dynamic[1] + 1].level or person.chunks_use_map[person.dynamic[0]][
                    person.dynamic[1] + 1].stairs or person.chunks_use_map[person.dynamic[0]][
                    person.dynamic[1]].stairs):
            if person.dynamic[1] <= (chunk_size + chunk_size // 2) and person.assemblage_point[1] != (
                    len(global_map) - 2):
                person.dynamic[1] += 1
                person.direction = 'right'
                person.type = 'r3'

    person.global_position_calculation(chunk_size)  # Рассчитывает глобальное положение и номер чанка через метод


def test_request_move(global_map: list, person, chunk_size: int, go_to_print, pressed_button, interaction,
                      activity_list, step, enemy_list, mouse_position):  # тестовый быстрый режим перемещения
    """
        Меняет динамическое местоположение персонажа в тестовом режиме, без ограничений. По полчанка за раз.
        При нажатии на 'p' назначает всем NPC точку следования.
    """
    if pressed_button == 'up':
        if person.dynamic[0] >= chunk_size // 2 and person.assemblage_point[0] > 0:
            person.dynamic[0] -= chunk_size // 2
            person.recalculating_the_display = True

    elif pressed_button == 'left':
        if person.dynamic[1] >= chunk_size // 2 and person.assemblage_point[1] > 0:
            person.dynamic[1] -= chunk_size // 2
            person.recalculating_the_display = True

    elif pressed_button == 'down':
        if person.dynamic[0] <= (chunk_size + chunk_size // 2) and person.assemblage_point[0] != (len(global_map) - 2):
            person.dynamic[0] += chunk_size // 2
            person.recalculating_the_display = True

    elif pressed_button == 'right':
        if person.dynamic[1] <= (chunk_size + chunk_size // 2) and person.assemblage_point[1] != (len(global_map) - 2):
            person.dynamic[1] += chunk_size // 2
            person.recalculating_the_display = True

    elif pressed_button == 'button_purpose_task':

        mouse_screen_coords = [mouse_position[1]//30, mouse_position[0]//30]
        person_world_position = copy.deepcopy(person.world_position)
        mouse_world_position = [person_world_position[0] - chunk_size//2 + mouse_screen_coords[0],
                                person_world_position[1] - chunk_size//2 + mouse_screen_coords[1]]

        mouse_global_position, mouse_local_position = world_position_recalculation(mouse_world_position, chunk_size)

        mouse_vertices = global_map[mouse_global_position[0]][mouse_global_position[1]].chunk[mouse_local_position[0]][
                                                                                    mouse_local_position[1]].vertices
        interaction.append(['task_point_all_enemies', [mouse_global_position, mouse_vertices, mouse_local_position],
                                                                                               mouse_world_position])
        activity_list.append(Action_in_map('test_beacon', step, mouse_global_position, mouse_local_position,
                                                                                            chunk_size, '', person))

    elif pressed_button == 'follow_me':
        mouse_screen_coords = [mouse_position[1] // 30, mouse_position[0] // 30]
        person_world_position = copy.deepcopy(person.world_position)
        mouse_world_position = [person_world_position[0] - chunk_size // 2 + mouse_screen_coords[0],
                                person_world_position[1] - chunk_size // 2 + mouse_screen_coords[1]]
        mouse_enemy = None
        for enemy in enemy_list:
            if hasattr(enemy, 'memory') and enemy.world_position == mouse_world_position:
                mouse_enemy = enemy
                break
        if mouse_enemy is not None:
            interaction.append(['follow_me_all_enemies', [mouse_enemy, 'follow', 3]])
        else:
            interaction.append(['follow_me_all_enemies', [person, 'follow', 3]])

    elif pressed_button == 'escape_me':
        interaction.append(['escape_me_all_enemies', [person, 'escape', 3]])

    elif pressed_button == 'button_add_beacon':
        activity_list.append(
            Action_in_map('test_beacon', step, person.global_position, person.local_position, chunk_size,
                          f'\n оставлен вами в локальной точке - {[person.dynamic[0] % chunk_size, person.dynamic[1] % chunk_size]}| динамической - {person.dynamic}| глобальной - {person.global_position}', person))

    elif pressed_button == 'button_test_visible':
        person.test_visible = not person.test_visible

    elif pressed_button == 'view_waypoints':
        interaction.append(['view_waypoints'])

    elif pressed_button == 'explosion':
        interaction.append(['add_global_interaction', 'explosion', person.global_position, person.local_position])

    elif pressed_button == 'add_hunter':
        mouse_screen_coords = [mouse_position[1] // 30, mouse_position[0] // 30]
        person_world_position = copy.deepcopy(person.world_position)
        mouse_world_position = [person_world_position[0] - chunk_size // 2 + mouse_screen_coords[0],
                                person_world_position[1] - chunk_size // 2 + mouse_screen_coords[1]]

        mouse_global_position, mouse_local_position = world_position_recalculation(mouse_world_position, chunk_size)

        enemy_list.append(NPC(mouse_global_position, mouse_local_position, 'new_riffleman', 'new_riffleman', '☻',
                                                                            'd0', 'Тестовый NPC', 'new_riffleman'))

    elif pressed_button == 'add_coyot':
        global_position = copy.deepcopy(person.global_position)
        local_position = copy.deepcopy(person.local_position)
        if local_position[0] >= chunk_size:
            global_position[0] += 1
            local_position[0] = 0
        elif local_position[1] >= chunk_size:
            global_position[1] += 1
            local_position[1] = 0
        enemy_list.append(return_npc(global_position, local_position, 'coyot'))
    elif pressed_button == 'add_snake':
        global_position = copy.deepcopy(person.global_position)
        local_position = copy.deepcopy(person.local_position)
        if local_position[0] >= chunk_size:
            global_position[0] += 1
            local_position[0] = 0
        elif local_position[1] >= chunk_size:
            global_position[1] += 1
            local_position[1] = 0
        enemy_list.append(return_creature(global_position, local_position, 'snake'))

    person.global_position_calculation(chunk_size)  # Рассчитывает глобальное положение и номер чанка через метод


def request_pointer(person, chunk_size: int, go_to_print, pressed_button):
    """
        Меняет местоположение указателя
    """
    if pressed_button == 'up' and person.pointer[0] > 0:
        person.pointer[0] -= 1
    elif pressed_button == 'left' and person.pointer[1] > 0:
        person.pointer[1] -= 1
    elif pressed_button == 'down' and person.pointer[0] < chunk_size - 1:
        person.pointer[0] += 1
    elif pressed_button == 'right' and person.pointer[1] < chunk_size - 1:
        person.pointer[1] += 1


def request_gun(global_map: list, person, chunk_size: int, go_to_print, pressed_button):
    """
        Меняет местоположение указателя оружия
    """
    if pressed_button == 'up' and person.gun[0] > chunk_size // 2 - 5:
        person.gun[0] -= 1

    elif pressed_button == 'left' and person.gun[1] > chunk_size // 2 - 5:
        person.gun[1] -= 1

    elif pressed_button == 'down' and person.gun[0] < chunk_size // 2 + 5:
        person.gun[0] += 1

    elif pressed_button == 'right' and person.gun[1] < chunk_size // 2 + 5:
        person.gun[1] += 1


def calculation_assemblage_point(global_map: list, person, chunk_size: int):
    """
        Перерассчитывает положение точки сборки, динамические координаты, перерассчитывает динамический чанк.
    """

    if person.dynamic[0] > (chunk_size // 2 + chunk_size - 1):
        person.assemblage_point[0] += 1
        person.dynamic[0] -= chunk_size
    elif person.dynamic[0] < chunk_size // 2:
        person.assemblage_point[0] -= 1
        person.dynamic[0] += chunk_size

    if person.dynamic[1] > (chunk_size // 2 + chunk_size - 1):
        person.assemblage_point[1] += 1
        person.dynamic[1] -= chunk_size
    elif person.dynamic[1] < chunk_size // 2:
        person.assemblage_point[1] -= 1
        person.dynamic[1] += chunk_size

    assemblage_chunk = []

    line_slice = global_map[person.assemblage_point[0]:(person.assemblage_point[0] + 2)]

    for line in line_slice:
        line = line[person.assemblage_point[1]:(person.assemblage_point[1] + 2)]
        assemblage_chunk.append(line)
        person.zone_relationships = []
    for number_line in range(len(assemblage_chunk)):
        for chunk in range(len(assemblage_chunk)):
            person.zone_relationships.append(assemblage_chunk[number_line][chunk].vertices)
            assemblage_chunk[number_line][chunk] = assemblage_chunk[number_line][chunk].chunk

    person.chunks_use_map = gluing_location(assemblage_chunk, 2, chunk_size)


def request_processing(pressed_button):
    """
        Обрабатывает пользовательский запрос
    """
    pass


