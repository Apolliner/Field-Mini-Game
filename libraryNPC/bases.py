import math
import random
from library.decorators import trace


class Bases:
    """ Базовые методы, нужные везде """

    inf = float("inf")

    @trace
    def bases_path_length(self, start_point, finish_point):
        """
            Вычисляет примерное расстояния до финиша, для рассчётов стоимости перемещения
        """
        return math.sqrt((start_point[0] - finish_point[0]) ** 2 + (start_point[1] - finish_point[1]) ** 2)

    @trace
    def bases_world_position_calculate(self, global_position, local_position):
        """
            Рассчитывает мировые координаты от центра мира
        """
        return [local_position[0] + (global_position[0] + 1) * self.chunk_size,
                local_position[1] + (global_position[1] + 1) * self.chunk_size]

    @trace
    def bases_world_position_recalculation(self, world_position):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_position, local_position

    @trace
    def bases_world_tile(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

    @trace
    def bases_world_location(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает локацию.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        return global_map[global_position[0]][global_position[1]]

    @trace
    def bases_hypotenuse(self, cathet_y, cathet_x):
        """ Считает гипотенузу по двум катетам """
        hypotenuse = math.sqrt(cathet_y**2 + cathet_x**2)
        return hypotenuse

    @trace
    def bases_router(self, stack, **kwargs):
        """
            Маршрутизатор, выполняющий функции из стека, так же проверяет стек на наличие бесконечной
            рекурсии. FIXME None нужно заменить, так как его значение в остальной обработке означает необработанную
                            ситуацию
                            /\ Теперь это inf - infinity
        """
        names_count = dict()
        for name in stack.get_names():
            if name not in names_count:
                names_count[name] = 0
            names_count[name] += 1
        for key in names_count:
            if names_count[key] > 10:
                # Если одинаковых элементов больше десяти, то возможно началась бесконечная рекурсия
                # и надо очистить стек. Базовый первый элемент берётся из описания самого персонажа.
                stack.clear_stack()

        while True:
            action = stack.get_stack_element()
            answer = action["element"](**kwargs)
            self.target = action["target"]
            if answer is True:
                stack.pop_stack_element()
                break
            elif answer is False:
                break
            elif answer is self.inf:
                continue

    @trace
    def bases_del_all_waypoints(self, **kwargs):
        """ Удаляет все вейпоинты """
        self.global_waypoints = list()
        self.local_waypoints = list()

    @trace
    def bases_gen_random_id(self, ids_list):
        while True:
            new_id = random.randrange(999999)
            if new_id not in ids_list:
                ids_list.append(new_id)
                return new_id

    @trace
    def bases_check_vertices(self, vertices, vertices_dict):
        """
            Когда нужен объект зоны доступности, а бывает приходит её номер, то этот метод проверяет
            и возвращает объект
        """
        if type(vertices) is int:
            return vertices_dict[vertices]
        return vertices

    def bases_return_circle(self):
        return ['00000...00000',
                '000.......000',
                '00.........00',
                '0...........0',
                '0...........0',
                '.............',
                '.............',
                '.............',
                '0...........0',
                '0...........0',
                '00.........00',
                '000.......000',
                '00000...00000']
