import math
import random
import logging

class Path:
    """
        Полный рассчёт пути по мировым координатам, возможно станет частью класса character

        Работает с классами, содержащими поля:
        global_position
        local_position
        world_position
        global_waypoints
        local_waypoints
        target
        direction
        forced_pass
    """

    chunk_size = 25

    def path_length(self, start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)

    def path_world_position_calculate(self, global_position, local_position):
        """
            Рассчитывает мировые координаты от центра мира
        """
        return [local_position[0] + (global_position[0] + 1) * self.chunk_size,
                local_position[1] + (global_position[1] + 1) * self.chunk_size]

    def path_world_position_recalculation(self, world_position):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_position, local_position

    def path_global_direction_calculation(self, start_vertices, finish_vertices, vertices_dict):
        """ Определяет направление глобального движения """
        #print(F"start_vertices - {start_vertices}")
        start = vertices_dict[start_vertices].position
        finish = vertices_dict[finish_vertices].position
        if [start[0] - 1, start[1]] == finish:
            return 'up'
        elif [start[0] + 1, start[1]] == finish:
            return 'down'
        elif [start[0], start[1] - 1] == finish:
            return 'left'
        elif [start[0], start[1] + 1] == finish:
            return 'right'
        return None

    def path_direction_calculation(self, start, finish):
        """ Определяет направление движения """
        if [start[0] - 1, start[1]] == finish:
            return 'up', 'u3'
        elif [start[0] + 1, start[1]] == finish:
            return 'down', 'd3'
        elif [start[0], start[1] - 1] == finish:
            return 'left', 'l3'
        elif [start[0], start[1] + 1] == finish:
            return 'right', 'r3'
        return "center", 'd0'

    def path_world_tile(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

    def path_world_location(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает локацию.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        return global_map[global_position[0]][global_position[1]]

    def path_local_move(self, global_map, enemy_list):
        """ Перемещения к очередному локальному вейпоинту. Проверяет наличие другого NPC на пути. """
        move = True
        for enemy in enemy_list:
            if enemy.world_position == self.local_waypoints[0]:
                self.forced_pass += 1
                move = False
        if move:
            self.forced_pass = 0
            waypoint = self.local_waypoints.pop(0)
            self.direction, self.type = self.path_direction_calculation(self.world_position, waypoint)
            self.global_position, self.local_position = self.path_world_position_recalculation(waypoint)
            self.vertices = self.path_world_tile(global_map, waypoint)

    def path_escape_calculate(self, global_map, vertices_graph, vertices_dict, enemy_list):
        """
            Рассчитывает точку бегства для персонажа и локальные вейпоинты к ней
            Возможно потребуется модифицированный алгоритм A* развёрнутый наоборот
            То есть чем ближе к противнику от которого убегает персонаж, тем дороже стоимость вершины до него.
            Финальной выбирается самая дешёвая точка после 250-300 циклов.
        """
        self.local_waypoints = self._path_escape_world_tiles_a_star_algorithm(global_map, self.world_position,
                                                                              self.target.get_position())
        # Если есть куда двигаться
        if self.local_waypoints:
            self.path_local_move(global_map, enemy_list)

    def path_calculate(self, global_map, vertices_graph, vertices_dict, enemy_list):
        """
            Принимает старт и финиш в виде мировых координат, а так же глобальную карту и граф зон доступности для рассчёта пути.

        """

        # Если нет ни глобальных ни локальных вейпоинтов
        if not self.global_waypoints and not self.local_waypoints:

            # Если совпадают глобальные положения с целью
            if self.vertices == self.path_world_tile(global_map, self.target.get_position()).vertices:
                self.local_waypoints, _ = self._path_world_tiles_a_star_algorithm(global_map,
                                                         self.world_position, self.target.get_position(), self.vertices)
            # Если глобальные положения различаются
            else:
                #print(F"self.vertices - {self.vertices}, self.target.get_vertices(global_map) - {self.target.get_vertices(global_map)}")
                self.global_waypoints, _ = self._path_world_vertices_a_star_algorithm(vertices_dict,
                                    vertices_dict[self.vertices], vertices_dict[self.target.get_vertices(global_map)])


                self.local_waypoints = self.path_local_waypoints_calculate(self.world_position, global_map,
                                                                                    vertices_graph, vertices_dict)

        # Есть глобальные, но нет локальных вейпоинтов
        elif self.global_waypoints and not self.local_waypoints:
            self.local_waypoints = self.path_local_waypoints_calculate(self.world_position, global_map, vertices_graph,
                                                                                                        vertices_dict)

        # Если есть куда двигаться
        if self.local_waypoints:
            self.path_local_move(global_map, enemy_list)

    def approximate_finish_calculation(self, start_point, finish_point):
        """
            Cчитает прямой путь до координат цели, останавливая рассчёт в тот момент, когда достигнет
            другой зоны доступности. Возвращает последний рассчитаный тайл в мировых координатах
        """

        start_global_position, _ = self.path_world_position_recalculation(start_point)

        axis_y = finish_point[0] - start_point[0]  # длинна стороны и количество шагов
        axis_x = finish_point[1] - start_point[1]  # длинна стороны и количество шагов
        if abs(axis_y) > abs(axis_x):
            if axis_x != 0:
                length_step = abs(axis_y) // abs(axis_x)  # на один X столько то Y
            else:
                length_step = abs(axis_y)
            long_side = 'y'
        else:
            if axis_y != 0:
                length_step = abs(axis_x) // abs(axis_y)  # на один Y столько то X
            else:
                length_step = abs(axis_x)
            long_side = 'x'

        waypoints = [start_point]

        for step in range((abs(axis_y) + abs(axis_x))):
            global_position, _ = self.path_world_position_recalculation(waypoints[-1])
            # Если другая глобальная позиция,то сменить положение
            if global_position != start_global_position:
                break
            if (step + 1) % (length_step + 1) == 0:
                if long_side == 'y':
                    if axis_y >= 0 and axis_x >= 0 or axis_y < 0 and axis_x >= 0:
                        waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                    else:
                        waypoints.append([waypoints[step][0], waypoints[step][1] - 1])
                elif long_side == 'x':
                    if axis_x >= 0 and axis_y >= 0 or axis_x < 0 and axis_y >= 0:
                        waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                    else:
                        waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
            else:
                if long_side == 'y':
                    if axis_y >= 0 and axis_x >= 0 or axis_y >= 0 and axis_x < 0:
                        waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                    else:
                        waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
                elif long_side == 'x':
                    if axis_x >= 0 and axis_y >= 0 or axis_x >= 0 and axis_y < 0:
                        waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                    else:
                        waypoints.append([waypoints[step][0], waypoints[step][1] - 1])

        return waypoints[-1]

    def path_local_waypoints_calculate(self, start_point, global_map, vertices_graph, vertices_dict):
        """
            Рассчитывает локальные вейпоинты для передвижения

            На основании приблизительного центра зон доступности, а так же поправок этого центра в зависимости от
            направления следующего вейпоинта, рассчитывает прямой путь до этого приблизительного центра,
            останавливаясь на границе локаций, и определяет ближайшую точку перехода к последней точке прямого пути.
        """
        direction = self.path_global_direction_calculation(self.vertices, self.global_waypoints[0], vertices_dict)
        finish_point = []

        for vertices in self.path_world_location(global_map, start_point).vertices:
            if vertices.number == self.vertices:
                for connect in vertices.connections:
                    if connect.number == self.global_waypoints[0]:
                        if self.target.get_vertices(global_map) == self.global_waypoints[0]:
                            _, approximate_position = self.path_world_position_recalculation(self.target.get_position())
                        else:
                            approximate_position = connect.approximate_position

                            if len(self.global_waypoints) > 1:
                                second_direction = self.path_global_direction_calculation(self.global_waypoints[0],
                                                                self.global_waypoints[1], vertices_dict)
                                if second_direction == 'up':
                                    approximate_position = [approximate_position[0] - connect.y_amendment,
                                                            approximate_position[1]]
                                elif second_direction == 'down':
                                    approximate_position = [approximate_position[0] + connect.y_amendment,
                                                            approximate_position[1]]
                                elif second_direction == 'left':
                                    approximate_position = [approximate_position[0], approximate_position[1] -
                                                            connect.x_amendment]
                                elif second_direction == 'right':
                                    approximate_position = [approximate_position[0], approximate_position[1] +
                                                            connect.x_amendment]
                        _, local_start = self.path_world_position_recalculation(start_point)
                        world_approximate_finish = self.approximate_finish_calculation(local_start, approximate_position)
                        _, approximate_finish = self.path_world_position_recalculation(world_approximate_finish)
                        #print(F"approximate_position -  {approximate_position}")
                        #print(F"local_start -           {local_start}")
                        #print(F"approximate_finish -    {approximate_finish}")
                        min_len = 99999
                        min_number = None
                        for number_tile, tile in enumerate(connect.tiles):
                            length = self.path_length(approximate_finish, tile)
                            if length < min_len:
                                min_len = length
                                min_number = number_tile
                        if min_number is None:
                            return []
                        finish = connect.tiles[min_number]
                        #print(F"finish -                {finish}")
                        raw_finish_point = self.path_world_position_calculate(vertices.position, finish)  # Преобразование в мировые координаты
                        if direction == 'up':
                            finish_point = [raw_finish_point[0] - 1, raw_finish_point[1]]
                        elif direction == 'down':
                            finish_point = [raw_finish_point[0] + 1, raw_finish_point[1]]
                        elif direction == 'left':
                            finish_point = [raw_finish_point[0], raw_finish_point[1] - 1]
                        elif direction == 'right':
                            finish_point = [raw_finish_point[0], raw_finish_point[1] + 1]
                        break

        local_waypoints, success = self._path_world_tiles_a_star_algorithm(global_map, start_point, finish_point,
                                                                                        self.global_waypoints[0])
        return local_waypoints

    def _path_world_vertices_a_star_algorithm(self, vertices_dict, start_vertices, finish_vertices):
        """
            Рассчитывает поиск пути, алгоритмом A* с использованием исключительно полей доступности.

            Вообще, если бы не желание запихнуть в одну функцию обработку глобальных и локальных координат,
            то надо было сразу перевести глобальный рассчёт на чистые Global_vertices,
            ведь они уже и так содержат всю необходимую информацию.

            ЗАДАЧИ:
            Возможно, можно порезать код на отдельные функции, что бы повторно использовать код.

            ОСОБЕННОСТИ:
            Есть путаница с number глобальных Global_vertices и локальных Node_vertices

            Сюда приходит:
            Список вершин - vertices_map;
            Cтартовая вершина - start_vertices - class Global_vertices;
            Финишная вершина - finish_vertices - class Global_vertices;

            return список вершин - вейпоинтов

        """

        class Node_vertices:
            """Содержит узлы графа для работы с зонами доступности"""
            __slots__ = ('number', 'vertices', 'position', 'price', 'direction', 'ready')

            def __init__(self, number, vertices, position, price, direction):
                self.number = number
                self.vertices = vertices
                self.position = position
                self.price = price
                self.direction = direction  # Хранит номер вершины из которой вышла
                self.ready = True  # Проверена ли точка

        def node_connections(vertices_dict, graph, processed_node, finish_vertices, verified_vertices):
            """
                Определяет связи вершины и добавляет их в граф при расчёте по глобальной карте
            """
            processed_node.ready = False
            # Находим указанную зону доступности
            vertices = vertices_dict[processed_node.vertices]
            # Проверяем, есть ли у неё связи
            if vertices.connections:
                for connect in vertices.connections:
                    if not connect.number in verified_vertices:
                        verified_vertices.append(connect.number)
                        graph.append(Node_vertices(len(graph), connect.number, connect.position,
                                                   self.path_length(connect.position,
                                                               finish_vertices.position),
                                                   processed_node.number))

        graph = []  # Список, содержащий все вершины
        verified_vertices = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_vertices.number, start_vertices.position,
                                   self.path_length(start_vertices.position, finish_vertices.position), 0))
        verified_vertices.append(start_vertices.number)

        node_connections(vertices_dict, graph, graph[0], finish_vertices, verified_vertices)

        general_loop = True  # Параметр останавливающий цикл
        step_count = 0  # Шаг цикла
        number_finish_node = 0  # Хранит номер финишной точки
        reversed_waypoints = []  # Обращенный список вейпоинтов
        success = True  # Передаёт информацию об успехе и не успехе
        while general_loop:
            min_price = 99999
            node = graph[-1]
            for number_node in range(len(graph)):
                if graph[number_node].ready:
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        node = graph[number_node]
            if min_price == 99999:
                number_finish_node = len(graph) - 1
                success = False
                general_loop = False

                self.target = None

            node_connections(vertices_dict, graph, node, finish_vertices, verified_vertices)

            if node.vertices == finish_vertices.number:
                number_finish_node = node.number
                general_loop = False

            step_count += 1
            if step_count == 300:
                last_check_success = False
                for last_check in verified_vertices:
                    if last_check == finish_vertices.number:
                        for node in graph:
                            if node.vertices == last_check:
                                number_finish_node = node.number
                                last_check_success = True
                                general_loop = False
                if not last_check_success:
                    min_price = 99999
                    node = graph[-1]
                    for number_node in range(len(graph)):
                        if graph[number_node].price < min_price:
                            min_price = graph[number_node].price
                            number_finish_node = number_node

                    self.target = None
                    success = False
                    general_loop = False

        check_node = graph[number_finish_node]

        ran_while = True
        while ran_while:
            reversed_waypoints.append(check_node.vertices)
            if check_node.direction == 0:
                ran_while = False
            check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой
        return list(reversed(reversed_waypoints)), success

    def _path_world_tiles_a_star_algorithm(self, global_map, start_point, finish_point, global_waypoint):
        """
            Рассчитывает поиск пути, алгоритмом A* на основании глобальных зон доступности и мировых координат тайлов.

            Сюда приходит:
            Обрабатываемая карта - global_map;
            Cтартовые кординаты - start_point:[world_y, world_x];
            Финишная точка - finish_point:[world_y, world_x];

        """
        len_map = len(global_map) * self.chunk_size

        class Node_vertices:
            """Содержит узлы графа для работы с зонами доступности"""
            __slots__ = ('number', 'vertices', 'position', 'price', 'direction', 'ready')

            def __init__(self, number, vertices, position, price, direction):
                self.number = number
                self.vertices = vertices
                self.position = position
                self.price = price
                self.direction = direction  # Хранит номер вершины из которой вышла
                self.ready = True  # Проверена ли точка

        def node_friends_calculation(global_map, graph, node, finish_point, verified_position, global_waypoint):
            """
                Вычисляет соседние узлы графа при расчёте по локальной карте

                То же самое, что было раньше, только с проверкой на высоту и лестницы
            """
            node.ready = False
            node_tile = self.path_world_tile(global_map, node.position)
            tiles_positions = list()

            tiles_positions.append([node.position[0] + 1, node.position[1]])

            tiles_positions.append([node.position[0] - 1, node.position[1]])

            tiles_positions.append([node.position[0], node.position[1] + 1])

            tiles_positions.append([node.position[0], node.position[1] - 1])
            if tiles_positions:
                for tile_position in tiles_positions:
                    tile = self.path_world_tile(global_map, tile_position)
                    if tile.vertices == node_tile.vertices or tile.vertices == global_waypoint and \
                                                    tile.level == node_tile.level or node_tile.stairs or tile.stairs:
                        if tile_position not in verified_position:
                            verified_position.append(tile_position)
                            graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                       tile.price_move + self.path_length(tile_position, finish_point),
                                                       node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number}
                            # и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

        start_tile = self.path_world_tile(global_map, start_point)

        graph = []  # Список, содержащий все вершины
        verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_tile.vertices, start_point, self.path_length(start_point, finish_point), 0))
        verified_position.append(start_point)
        node_friends_calculation(global_map, graph, graph[0], finish_point, verified_position, global_waypoint)

        general_loop = True  # Параметр останавливающий цикл
        step_count = 0  # Шаг цикла
        number_finish_node = 0  # Хранит номер финишной точки
        reversed_waypoints = []  # Обращенный список вейпоинтов
        success = True  # Передаёт информацию об успехе и не успехе
        while general_loop:
            min_price = 99999
            node = graph[-1]
            for number_node in range(len(graph)):
                if graph[number_node].ready:
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        node = graph[number_node]
            if min_price == 99999:
                number_finish_node = len(graph) - 1
                success = False
                general_loop = False
            node_friends_calculation(global_map, graph, node, finish_point, verified_position, global_waypoint)
            if node.position == finish_point:
                number_finish_node = node.number
                general_loop = False
            step_count += 1
            if step_count == 300:
                last_check_success = False
                for last_check in verified_position:
                    if last_check == finish_point:
                        for node in graph:
                            if node.position == last_check:
                                number_finish_node = node.number
                                last_check_success = True
                                general_loop = False
                if not last_check_success:
                    min_price = 99999
                    node = graph[-1]
                    for number_node in range(len(graph)):
                        if graph[number_node].price < min_price:
                            min_price = graph[number_node].price
                            number_finish_node = number_node
                    success = False
                    general_loop = False
        # Определение пути по сохранённым направлениям
        check_node = graph[number_finish_node]
        ran_while = True
        while ran_while:
            reversed_waypoints.append(check_node.position)
            if check_node.direction == 0:
                ran_while = False
            check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой

        return list(reversed(reversed_waypoints)), success


    def _path_escape_world_tiles_a_star_algorithm(self, global_map, start_point, escape_point):
        """
            Рассчитывает поиск пути для побега, алгоритмом A* на основании глобальных зон доступности и
            мировых координат тайлов.

            Сюда приходит:
            Обрабатываемая карта - global_map;
            Стартовые координаты - start_point:[world_y, world_x];
            Точка побега - escape_point:[world_y, world_x];

            Устанавливает стартовую цену равную 100 и при рассчёте пути добавляет цену при приближении к точке
            побега и уменьшает при удалении от неё
        """
        len_map = len(global_map) * self.chunk_size

        class Node_vertices:
            """Содержит узлы графа для работы с зонами доступности"""
            __slots__ = ('number', 'vertices', 'position', 'price', 'direction', 'ready')

            def __init__(self, number, vertices, position, price, direction):
                self.number = number
                self.vertices = vertices
                self.position = position
                self.price = price
                self.direction = direction  # Хранит номер вершины из которой вышла
                self.ready = True  # Проверена ли точка

        def escape_path_length(start_point, finish_point, start_lenth):
            """
                Вычисляет примерное расстояния до точки побега и рассчитывает цену.
            """
            lenth = math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)
            if lenth > start_lenth:
                return 100 - (lenth - start_lenth)
            elif lenth < start_lenth:
                return 100 + (start_lenth - lenth)*2
            return 100

        def node_friends_calculation(global_map, graph, node, escape_point, verified_position, start_lenth):
            """
                Вычисляет соседние узлы графа при расчёте по локальной карте

                То же самое, что было раньше, только с проверкой на высоту и лестницы
            """
            node.ready = False
            node_tile = self.path_world_tile(global_map, node.position)
            tiles_positions = list()
            tiles_positions.append([node.position[0] + 1, node.position[1]])
            tiles_positions.append([node.position[0] - 1, node.position[1]])
            tiles_positions.append([node.position[0], node.position[1] + 1])
            tiles_positions.append([node.position[0], node.position[1] - 1])
            if tiles_positions:
                for tile_position in tiles_positions:
                    tile = self.path_world_tile(global_map, tile_position)
                    if tile.level == node_tile.level or node_tile.stairs or tile.stairs:
                        if tile_position not in verified_position:
                            verified_position.append(tile_position)
                            graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                    tile.price_move + escape_path_length(tile_position, escape_point,
                                                    start_lenth), node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number}
                            # и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

        start_lenth = self.path_length(start_point, escape_point)

        start_tile = self.path_world_tile(global_map, start_point)

        graph = []  # Список, содержащий все вершины
        verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_tile.vertices, start_point, 100, 0))
        verified_position.append(start_point)
        node_friends_calculation(global_map, graph, graph[0], escape_point, verified_position, start_lenth)

        general_loop = True  # Параметр останавливающий цикл
        step_count = 0  # Шаг цикла
        number_finish_node = 0  # Хранит номер финишной точки
        reversed_waypoints = []  # Обращенный список вейпоинтов
        while general_loop:
            min_price = 99999
            node = graph[-1]
            for number_node in range(len(graph)):
                if graph[number_node].ready:
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        node = graph[number_node]
            if min_price == 99999:
                number_finish_node = len(graph) - 1
                success = False
                general_loop = False
            node_friends_calculation(global_map, graph, node, escape_point, verified_position, start_lenth)
            step_count += 1
            if step_count == 50:
                min_price = 99999
                node = graph[-1]
                for number_node in range(len(graph)):
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        number_finish_node = number_node
                general_loop = False
        # Определение пути по сохранённым направлениям
        check_node = graph[number_finish_node]
        ran_while = True
        while ran_while:
            reversed_waypoints.append(check_node.position)
            if check_node.direction == 0:
                ran_while = False
            check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой

        return list(reversed(reversed_waypoints))
