import math

class Bases:
    """ Базовые методы, нужные везде """

    inf = float("inf")

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

    def bases_get_memory(self, type):
        """
            Возвращает последние 3 записи указанного типа
        """
        if type in self.memory:
            memory = self.memory[type]
            memory = list(reversed(memory))
            if memory:
                if len(memory) >= 10:
                    return memory[::10]
                else:
                    return memory
        return None

    def bases_check_memory(self, step):
        """
            Проверяет содержимое памяти

            Если находит подходящую запись для продолжения, то отмечает её продолженной FIXME устарело

        """
        type_tuple = ('activity', 'move', 'follow')
        for type in type_tuple:
            memory_list = self.npc_get_memory(self, type)
            if memory_list is not None:
                for memory in memory_list:
                    if memory.status == 'interrupted':
                        self.target = Target(type=memory.type, entity=memory.entity, position=memory.world_position,
                                                                                    create_step=step, lifetime=1000)
                        memory.status = "continued"
                        if memory.type in ('follow', 'escape', 'investigation') and memory.entity:
                            setattr(self, memory.type, memory.entity)
                        break
            else:
                continue

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
            answer = action(**kwargs)
            if answer is True:
                stack.pop_stack_element()
                break
            elif answer is False:
                break
            elif answer is self.inf:
                continue

    def bases_del_all_waypoints(self, **kwargs):
        """ Удаляет все вейпоинты """
        self.global_waypoints = list()
        self.local_waypoints = list()

