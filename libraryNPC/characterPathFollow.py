from libraryNPC.characterPathMove import PathMove
from libraryNPC.bases import Bases
from library.decorators import trace

class PathFollow(PathMove, Bases):
    """
        Реализует следование персонажа
        При нахождении близко от цели, локальный поиск пути осуществлять игнорируя зоны доступности
        и с малым количеством циклов, так как его нужно регулярно пересчитывать
    """
    @trace
    def path_follow_add_order(self, id, **kwargs):
        """ Принимает id записи памяти и создаёт задачу на следование до цели """
        target = self.memory.get_memory_by_id(id, **kwargs)
        self.target = target
        self.action_stack.add_stack_element(name="follow", element=self._path_follow, target=target)

    @trace
    def _path_follow(self, **kwargs):
        """ Вызывается и само всё делает """
        target_position = self.target.get_position()
        remoteness = self.bases_path_length(self.world_position, target_position)
        if remoteness > 30: # Если цель близко
            new_waypoints_calculate = False
            if self.local_waypoints:
                finish_remoteness = self.bases_path_length(self.local_waypoints[-1], target_position)
                if finish_remoteness > 3:
                    new_waypoints_calculate = True
            else:
                new_waypoints_calculate = True
            if new_waypoints_calculate:
                #self.action_stack.pop_stack_element()
                self.bases_del_all_waypoints()
                self.local_waypoints = self._path_follow_a_star_algorithm(self.world_position, target_position,
                                                                                            cycles=100, **kwargs)
        else: # Если цель далеко, то всё считается по-обычному
            target_vertices = self.bases_world_tile(kwargs["global_map"], target_position)
            if self.global_waypoints and target_vertices != self.global_waypoints[-1]:
                self.global_waypoints = list()
                self.local_waypoints = list()
            self.path_move(**kwargs)

        if remoteness > 3: # Если цель не слишком близко, то надо к ней идти
            self._path_base_local_move(**kwargs)

    @trace
    def _path_follow_a_star_algorithm(self, start_point, finish_point, cycles=300, **kwargs):
        """
            Рассчитывает поиск пути для следования, алгоритмом A* игнорируя зоны доступности и ограничивая
            количество доступных циклов.

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

        def node_friends_calculation(global_map, graph, node, finish_point, verified_position):
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
                    if tile.level == node_tile.level or node_tile.stairs or tile.stairs:
                        if tile_position not in verified_position:
                            verified_position.append(tile_position)
                            graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                       tile.price_move + self.bases_path_length(tile_position,
                                                                                        finish_point), node.number))
                            # print(f'добавлена вершина под номером {len(graph)}, направлением на вершину с номером {node.number}
                            # и координатами {[node.position[0], node.position[1] - 1]}, {node.vertices}')

        global_map = kwargs["global_map"]
        start_tile = self.bases_world_tile(global_map, start_point)

        graph = []  # Список, содержащий все вершины
        verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_tile.vertices, start_point, self.bases_path_length(start_point,
                                                                                                    finish_point), 0))
        verified_position.append(start_point)
        node_friends_calculation(global_map, graph, graph[0], finish_point, verified_position)

        general_loop = True  # Параметр останавливающий цикл
        step_count = 0  # Шаг цикла
        number_finish_node = 0  # Хранит номер финишной точки
        reversed_waypoints = []  # Обращенный список вейпоинтов
        inf = float("inf")
        while general_loop:
            min_price = inf
            node = graph[-1]
            for number_node in range(len(graph)):
                if graph[number_node].ready:
                    if graph[number_node].price < min_price:
                        min_price = graph[number_node].price
                        node = graph[number_node]
            if min_price == inf:
                number_finish_node = len(graph) - 1
                general_loop = False
            node_friends_calculation(global_map, graph, node, finish_point, verified_position)
            if node.position == finish_point:
                number_finish_node = node.number
                general_loop = False
            step_count += 1
            if step_count == cycles:
                min_price = inf
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

        return list(reversed([list(finish_point)] + reversed_waypoints))


