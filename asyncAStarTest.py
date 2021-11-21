import time
import random
import asyncio
import pickle
import math
import multiprocessing
from multiprocessing import Pool


def load_map():
    """
        Загрузка игровой карты через pickle
    """
    with open("save/saved_map.pkl", "rb") as fp:
        all_load = pickle.load(fp)

    return all_load[0], all_load[1], all_load[2], all_load[3]

class AStar:
    wp = []
    chunk_size = 25

    async def path_world_tile(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

    async def path_length(self, start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)

    async def async_world_tiles_a_star_algorithm(self, global_map, start_point, finish_point, global_waypoint):
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

        async def node_friends_calculation(global_map, graph, node, finish_point, verified_position, global_waypoint):
            """
                Вычисляет соседние узлы графа при расчёте по локальной карте

                То же самое, что было раньше, только с проверкой на высоту и лестницы
            """
            node.ready = False
            node_tile = await self.path_world_tile(global_map, node.position)
            tiles_positions = list()

            tiles_positions.append([node.position[0] + 1, node.position[1]])

            tiles_positions.append([node.position[0] - 1, node.position[1]])

            tiles_positions.append([node.position[0], node.position[1] + 1])

            tiles_positions.append([node.position[0], node.position[1] - 1])
            if tiles_positions:
                for tile_position in tiles_positions:
                    tile = await self.path_world_tile(global_map, tile_position)
                    if tile_position not in verified_position:
                        verified_position.append(tile_position)
                        graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                   tile.price_move + await self.path_length(tile_position, finish_point),
                                                   node.number))

        start_tile = await self.path_world_tile(global_map, start_point)

        graph = []  # Список, содержащий все вершины
        verified_position = []  # Содержит список всех использованных координат, что бы сравнивать с ним при добавлении новой вершины.
        graph.append(Node_vertices(0, start_tile.vertices, start_point, await self.path_length(start_point, finish_point), 0))
        verified_position.append(start_point)
        await node_friends_calculation(global_map, graph, graph[0], finish_point, verified_position, global_waypoint)

        general_loop = True  # Параметр останавливающий цикл
        step_count = 0  # Шаг цикла
        number_finish_node = 0  # Хранит номер финишной точки
        reversed_waypoints = []  # Обращенный список вейпоинтов
        success = True  # Передаёт информацию об успехе и не успехе
        while general_loop:
            #if step_count % 100 == 0:
            #    print(F"step_count - {step_count}")
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
            await node_friends_calculation(global_map, graph, node, finish_point, verified_position, global_waypoint)
            if node.position == finish_point:
                number_finish_node = node.number
                general_loop = False
            step_count += 1

        # Определение пути по сохранённым направлениям
        check_node = graph[number_finish_node]
        ran_while = True
        while ran_while:
            reversed_waypoints.append(check_node.position)
            if check_node.direction == 0:
                ran_while = False
            check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой
        print(F"success - {success}")
        #print(F"len(wp) - {len(reversed_waypoints)}")
        #wp = list(reversed([list(finish_point)] + reversed_waypoints))

    async def main(self, global_map, start_point, finish_point, global_waypoint):

        await self.async_world_tiles_a_star_algorithm(global_map, start_point, finish_point, global_waypoint)
        await self.async_world_tiles_a_star_algorithm(global_map, start_point, finish_point, global_waypoint)


class AStar2:
    wp = []
    chunk_size = 25

    def path_world_tile(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

    def path_length(self, start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)

    def async_world_tiles_a_star_algorithm(self, global_map, start_point, finish_point, global_waypoint, i):
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
                    if tile_position not in verified_position:
                        verified_position.append(tile_position)
                        graph.append(Node_vertices(len(graph), node.vertices, tile_position,
                                                   tile.price_move + self.path_length(tile_position, finish_point),
                                                   node.number))

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
            #if step_count % 100 == 0:
            #    print(F"step_count - {step_count}")
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

        # Определение пути по сохранённым направлениям
        check_node = graph[number_finish_node]
        ran_while = True
        while ran_while:
            reversed_waypoints.append(check_node.position)
            if check_node.direction == 0:
                ran_while = False
            check_node = graph[check_node.direction]  # Предыдущая вершина объявляется проверяемой
        print(F"success {i} - {success}")
        #print(F"len(wp) - {len(reversed_waypoints)}")
        #wp = list(reversed([list(finish_point)] + reversed_waypoints))

    def main(self, global_map, start_point, finish_point, global_waypoint):
        start = time.time()  # проверка времени выполнения
        for i in range(10):
            #p = Pool(5)
            t = multiprocessing.Process(target=self.async_world_tiles_a_star_algorithm(global_map, start_point,
                                                                            finish_point, global_waypoint, i), args=(i,))
            t.start()
        finish = time.time()
        print(F"all time = {finish - start}")
        #self.async_world_tiles_a_star_algorithm(global_map, start_point, finish_point, global_waypoint)
        #self.async_world_tiles_a_star_algorithm(global_map, start_point, finish_point, global_waypoint)

if __name__ == '__main__':
    start_world_position = [40, 40]
    finish_world_position = [640, 640]
    finish_vertices = 12741

    print(F"load map")
    global_map, raw_minimap, vertices_graph, vertices_dict = load_map()
    print(F"load map success")

    a_star = AStar2()

    a_star.main(global_map, start_world_position, finish_world_position, finish_vertices)
    #asyncio.run(a_star.main(global_map, start_world_position, finish_world_position, finish_vertices))
