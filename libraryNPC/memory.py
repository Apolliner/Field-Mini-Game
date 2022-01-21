import random
from libraryNPC.stackBase import BaseStack
from libraryNPC.bases import Bases
from libraryNPC.classes import PushingList


class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие должно быть закрыто. Закрытые события обобщаются для экономии места.

        Задачи так же являются элементами памяти
    """
    def __init__(self, id, type, name, master, step=0, target=None, entity=None, connection=None, positions=None, **kwargs):
        self.id = id
        self.type = type
        self.name = name
        self.status = "opened"
        self.step = step            # Шаг обновляется при каждом изменении элемента памяти
        self.birth = step           # Создание элемента остаётся постоянным
        self.master = master        # Объект персонажа, к которому относится элемент памяти
        self.payload = list()
        self.target = target
        self.entity = entity        # Объект персонажа
        self.connections = dict()
        if connection is not None:
            self.connections[connection.id] = connection
        self.positions = PushingList()
        if positions is not None:
            self.positions.extend(positions)

    def _update_position(self, position=None):
        """
            Доступно только элементу памяти о конкретном персонаже. Можно как получать из объекта персонажа, так и
            устанавливать вручную (например при нахождении следов)
        """
        if position is not None:
            self.positions.append(position)
            return True
        else:
            if self.entity:  # FIXME Нужна проверка на возможность обновить положение существа
                self.positions.append(self.entity.world_position)
                return True
        return None

    def _check_target_type(self):
        """ Автоматически определяет степень важности цели """
        types_dict = {
            "kill": "base",
            "action": "operative"
        }
        if self.name in types_dict:
            return types_dict[self.name]
        return "base"

    def get_position(self):
        """ Возвращает позицию из цели """
        if self.target:
            return list(self.entity.world_position)
        if self.positions:
            print(F"positions - {self.positions}")
            return self.positions[-1]
        return None

    def get_tile(self, global_map, chunk_size):
        """ Возвращает тайл, на позицию которого указывает цель """
        world_position = self.get_position()
        if world_position is not None:
            global_position = [world_position[0] // chunk_size, world_position[1] // chunk_size]
            local_position = [world_position[0] % chunk_size, world_position[1] % chunk_size]
            return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]]
        return None

    def get_vertices(self, global_map, chunk_size):
        """ Возвращает зону доступности цели """
        tile = self.get_tile(global_map, chunk_size)
        if tile is not None:
            return tile.vertices
        return None


class Memory(Bases):
    """
        Содержит в себе граф памяти
        Память хранит события, обобщенные события и их связи

        master содержит объект персонажа, чья память обрабатывается
        _graph содержит связи между элементами памяти
        _types содержит объекты элементов памяти, отсортированные по типам

        Нужно как то передавать информацию о том, что выполняется та же задача, что и на прошлом шаге.
        FIXME Можно так же, как и раньше, только target это элемент памяти
    """
    def __init__(self, master):
        self.master = master        # Объект персонажа, чья память обрабатывается
        self._graph = dict()
        self._types = dict()

    def add_standard_memories(self, player):
        """ Заполняет память стандартными знаниями """
        self._all_add_new_memories(MemoryNode(self._id_generate(), "area", "base_area", self.master))
        self._all_add_new_memories(MemoryNode(self._id_generate(), "character", "ordered character",
                                                                                    self.master, entity=player))

    def add_memories(self, type, name, **kwargs):
        """ Метод для создания новой записи и автоматического её добавления в граф. Возвращает созданный элемент """
        new_memory = MemoryNode(self._id_generate(), type, name, self.master, **kwargs)
        self._all_add_new_memories(new_memory)
        return new_memory

    def _all_add_new_memories(self, memories):
        """ Добавление объекта элемента памяти как в граф, так и в словарь по типам """
        self._graph[memories.id] = memories
        if memories.type not in self._types:
            self._types[memories.type] = list()
        self._types[memories.type].append(memories)

    def _id_generate(self):
        """ Генерация случайного id, которого ещё нет в графе """
        while True:
            gen_id = random.randrange(9999999)
            if gen_id not in self._graph:
                break
        return gen_id

    def generalization_of_experience(self, **kwargs):
        """ Обобщает множество одинаковых закрытых записей в одну """
        for key in self._types:
            closed_memories = list()
            for element in self._types[key]:
                if element.status == "closed":
                    closed_memories.append(element)
            if len(closed_memories) > 5:
                positions = PushingList()
                for closed_memory in closed_memories:
                    positions.extend(closed_memory.positions)
                summarized = MemoryNode(self._id_generate(), key, '', "summarized", kwargs["step"], positions=positions)
                self._all_add_new_memories(summarized)
                for closed_memory in closed_memories:
                    closed_id = closed_memory.id
                    for connect in closed_memory.connections:
                        if summarized is not connect.connections:
                            connect.connections[summarized.id] = summarized
                        connect.connections.pop(closed_id, False)
                    self._graph.pop(closed_id, False)
                    self._types[closed_memory.type].pop(closed_id)


