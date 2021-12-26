import math

class Bases:
    """ Базовые методы, нужные везде """

    def bases_world_position_calculate(self, global_position, local_position):
        """
            Рассчитывает мировые координаты от центра мира
        """
        return [local_position[0] + (global_position[0] + 1) * self.chunk_size,
                local_position[1] + (global_position[1] + 1) * self.chunk_size]

    def bases_world_position_recalculation(self, world_position):
        """
            Принимает мировые координаты и размер чанка, возвращает глобальные и локальные координаты.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_position, local_position

    def bases_world_tile(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает тайл.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]

    def bases_world_location(self, global_map, world_position):
        """
            Принимает мировые координаты, глобальную карту и размер чанка, возвращает локацию.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        return global_map[global_position[0]][global_position[1]]

    def bases_hypotenuse(self, cathet_y, cathet_x):
        """ Считает гипотенузу по двум катетам """
        hypotenuse = math.sqrt(cathet_y**2 + cathet_x**2)
        return hypotenuse

    class BaseStack:
        """ Базовая реализация стека """
        def __init__(self):
            self._stack = list()

        def add_stack_element(self, element, name):
            """ Положить элемент """
            self._stack.append({"name": name, "body": element})

        def get_stack_element(self):
            """ Получить элемент """
            len_stack = self.get_len_stack()
            if len_stack > 0:
                return self.stack.pop[len_stack - 1]
            else:
                return None

        def pop_stack_element(self):
            """ Извлечь элемент """
            len_stack = self.get_len_stack()
            if len_stack > 0:
                return self.stack.pop(len_stack - 1)
            else:
                return None

        def get_len_stack(self):
            """ Размер стека """
            return len(self._stack)

        def get_names(self):
            """ Возвращает список имён элементов """
            names = list()
            for element in self._stack:
                names.append(element["name"])
            return names