from libraryNPC.characterPathBase import PathBase
from library.decorators import trace

class PathMove(PathBase):
    """
        Реализует перемещение в точку или зону доступности, содержащуюся в задаче.
    """
    chunk_size = 25

    @trace
    def path_move(self, **kwargs):
        """
            Просто вызывается и само всё делает.
            Возвращает False если цель не достигнута и True если достигнута.
        """
        if self.target.get_position():
            if not self.local_waypoints:
                finish = self.target.get_position()
                vertices_dict = kwargs["vertices_dict"]
                if type(finish) is int:  # Расчёт пути до зоны доступности
                    finish_vertices = finish
                    vertices = vertices_dict[finish_vertices]
                    finish = self.bases_world_position_calculate(vertices.position, vertices.approximate_position)
                else:  # Расчёт пути до конкретной точки
                    finish_vertices = self.bases_world_tile(kwargs["global_map"], finish).vertices

                if self.world_position == finish:  # Точка достигнута, задача выполнена
                    return True

                self._path_move_calculate(finish_vertices, finish, **kwargs)
            self._path_base_local_move(**kwargs)
        return False

    @trace
    def _path_move_calculate(self, finish_vertices, finish_tile, **kwargs):
        """
            Рассчитывает путь до тайла или до зоны доступности (в зависимости от того, что приходит из задачи)
        """
        if not self.global_waypoints and self.vertices != finish_vertices:
            self._path_move_global_waypoints_calculate(self.vertices, finish_vertices, **kwargs)
        self._path_move_local_waypoints_calculate(self.world_position, finish_tile, **kwargs)

    @trace
    def _path_move_global_waypoints_calculate(self, start_vertices, finish_vertices, **kwargs):
        """ Рассчитывает глобальные вейпоинты """
        vertices_dict = kwargs["vertices_dict"]
        self.global_waypoints, _ = self._path_world_vertices_a_star_algorithm(vertices_dict,
                    vertices_dict[self.vertices], self.target.get_vertices(**kwargs))

    @trace
    def _path_move_local_waypoints_calculate(self, start_point, finish_point, **kwargs):
        """
            Рассчитывает локальные вейпоинты

            На основании приблизительного центра зон доступности, а так же поправок этого центра в зависимости от
            направления следующего вейпоинта, рассчитывает прямой путь до этого приблизительного центра,
            останавливаясь на границе локаций, и определяет ближайшую точку перехода к последней точке прямого пути.
        """
        global_map = kwargs["global_map"]
        vertices_dict = kwargs["vertices_dict"]
        direction = self._path_base_global_direction_calculation(self.vertices, self.global_waypoints[0], vertices_dict)
        finish_point = []

        for vertices in self.bases_world_location(global_map, start_point).vertices:
            if vertices.number == self.vertices:
                for connect in vertices.connections:
                    if connect.number == self.global_waypoints[0]:
                        if self.target.get_vertices(**kwargs) == self.global_waypoints[0]:
                            _, approximate_position = self.bases_world_position_recalculation(self.target.get_position())
                        else:
                            approximate_position = connect.approximate_position

                            if len(self.global_waypoints) > 1:
                                second_direction = self._path_base_global_direction_calculation(self.global_waypoints[0],
                                                                                          self.global_waypoints[1],
                                                                                          vertices_dict)
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
                        _, local_start = self.bases_world_position_recalculation(start_point)
                        world_approximate_finish = self._path_base_line_waypoints_calculation(local_start,
                                                                                approximate_position, limiter=True)
                        _, approximate_finish = self.bases_world_position_recalculation(world_approximate_finish)
                        min_len = float("inf")
                        min_number = None
                        for number_tile, tile in enumerate(connect.tiles):
                            length = self.bases_path_length(approximate_finish, tile)
                            if length < min_len:
                                min_len = length
                                min_number = number_tile
                        if min_number is None:
                            return []
                        finish = connect.tiles[min_number]
                        # print(F"finish -                {finish}")
                        raw_finish_point = self.bases_world_position_calculate(vertices.position,
                                                                        finish)  # Преобразование в мировые координаты
                        if direction == 'up':
                            finish_point = [raw_finish_point[0] - 1, raw_finish_point[1]]
                        elif direction == 'down':
                            finish_point = [raw_finish_point[0] + 1, raw_finish_point[1]]
                        elif direction == 'left':
                            finish_point = [raw_finish_point[0], raw_finish_point[1] - 1]
                        elif direction == 'right':
                            finish_point = [raw_finish_point[0], raw_finish_point[1] + 1]
                        break

        self.local_waypoints, success = self._path_world_tiles_a_star_algorithm(global_map, start_point, finish_point,
                                                                           self.global_waypoints[0])

    @trace
    def _path_world_vertices_a_star_algorithm(self, vertices_dict, start_vertices, finish_vertices):
        """
            Рассчитывает поиск пути, алгоритмом A* с использованием исключительно полей доступности.

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
                                                   self.bases_path_length(connect.position,
                                                               finish_vertices.position),
                                                   processed_node.number))

        start_vertices = self.bases_check_vertices(start_vertices, vertices_dict)
        finish_vertices = self.bases_check_vertices(finish_vertices, vertices_dict)

        graph = []  # Список, содержащий все вершины
        verified_vertices = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.

        graph.append(Node_vertices(0, start_vertices.number, start_vertices.position,
                                   self.bases_path_length(start_vertices.position, finish_vertices.position), 0))
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

    @trace
    def _path_world_tiles_a_star_algorithm(self, global_map, start_point, finish_point, global_waypoint):
        """
            Рассчитывает поиск пути, алгоритмом A* на основании глобальных зон доступности и мировых координат тайлов.

            Сюда приходит:
            Обрабатываемая карта - global_map;
            Cтартовые кординаты - start_point:[world_y, world_x];
            Финишная точка - finish_point:[world_y, world_x];

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

        def node_friends_calculation(global_map, graph, node, finish_point, verified_position, global_waypoint):
            """
                Вычисляет соседние узлы графа при расчёте по локальной карте

                То же самое, что было раньше, только с проверкой на высоту и лестницы
            """
            node.ready = False
            node_tile = self.bases_world_tile(global_map, node.position)
            tiles_positions = list()

            tiles_positions.append([node.position[0] + 1, node.position[1]])

            tiles_positions.append([node.position[0] - 1, node.position[1]])

            tiles_positions.append([node.position[0], node.position[1] + 1])

            tiles_positions.append([node.position[0], node.position[1] - 1])
            if tiles_positions:
                for tile_position in tiles_positions:
                    tile = self.bases_world_tile(global_map, tile_position)
                    if tile.vertices == node_tile.vertices or tile.vertices == global_waypoint and \
                                                    tile.level == node_tile.level or node_tile.stairs or tile.stairs:
                        if tile_position not in verified_position:
                            verified_position.append(tile_position)
                            graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                       tile.price_move + self.bases_path_length(tile_position,
                                                                                        finish_point), node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number}
                            # и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

        start_tile = self.bases_world_tile(global_map, start_point)

        graph = []  # Список, содержащий все вершины
        verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_tile.vertices, start_point, self.bases_path_length(start_point,
                                                                                                    finish_point), 0))
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

        return list(reversed([list(finish_point)] + reversed_waypoints)), success


