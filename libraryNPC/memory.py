import random
from libraryNPC.stackBase import BaseStack
from libraryNPC.bases import Bases


class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие должно быть закрыто. Закрытые события обобщаются для экономии места.

        Задачи так же являются элементами памяти
    """
    def __init__(self, id, type, name, status, step, master, target=None, entity=None, connection=None, position=None):
        self.id = id
        self.type = type
        self.name = name
        self.status = status
        self.step = step            # Шаг обновляется при каждом изменении элемента памяти
        self.birth = step           # Создание элемента остаётся постоянным
        self.master = master        # Объект персонажа, к которому относится элемент памяти
        self.payload = list()
        self.target = target
        self.entity = entity        # Объект персонажа
        self.connections = dict()
        if connection is not None:
            self.connections[connection.id] = connection
        self.positions = list()
        if position is not None:
            self.positions.append(position)

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
            return list(self.positions[-1])
        return None

class Memory(Bases):
    """
        Содержит в себе граф памяти
        Память хранит события, обобщенные события и их связи

        master содержит объект персонажа, чья память обрабатывается
        _graph содержит связи между элементами памяти
        _types содержит объекты элементов памяти, отсортированные по типам

        Нужно как то передавать информацию о том, что выполняется та же задача, что и на прошлом шаге.
    """
    def __init__(self, master):
        self.master = master        # Объект персонажа, чья память обрабатывается
        self._graph = dict()
        self._types = dict()
        self.event_stack = BaseStack()  # FIXME система задач 1

    def add_standard_memories(self, player):
        """ Заполняет память стандартными знаниями """
        self._all_add_new_memories(MemoryNode(self._id_generate(), "area", "base_area", "opened", 0, self.master))
        self._all_add_new_memories(MemoryNode(self._id_generate(), "character", "ordered character", "opened", 0,
                                                                                    self.master, entity=player))

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

    def generalization_of_experience(self):
        """ Обобщает множество одинаковых закрытых записей в одну """
        for key in self._types:
            closed_memories = list()
            for element in self._types[key]:
                if element.status == "closed":
                    closed_memories.append(element)
            if len(closed_memories) > 5:
                summarized = MemoryNode(self._id_generate(), key, '', "summarized", None)
                self._all_add_new_memories(summarized)
                for closed_memory in closed_memories:
                    closed_id = closed_memory.id
                    for connect in closed_memory.connections:
                        if summarized is not connect.connections:
                            connect.connections[summarized.id] = summarized
                        connect.connections.pop(closed_id, False)
                    self._graph.pop(closed_id, False)
                    self._types[closed_memory.type].pop(closed_id)

    def get_position(self):  # FIXME система задач 1
        """ Получение последней позиции последнего элемента из _event_stack """
        element = self.event_stack.get_stack_element()
        if element and element.positions:
            return element.positions[-1]
        return None

    def get_vertices(self, global_map):  # FIXME система задач 1
        """ Получение зоны доступности тайла на последней позиции последнего элемента из _event_stack """
        world_position = self.get_position()
        if world_position is None:
            return None
        return self.bases_world_tile(global_map, world_position).vertices

    def check_old_target(self, **kwargs):  # FIXME система задач 1
        """ Возвращает - продолжается ли старое задание (True) или выполняется новое (False). None говорит об ошибке """
        element = self.event_stack.get_stack_element()
        if element and "step" in kwargs:
            if element.step == kwargs["step"]:
                return False
            else:
                return True
        return None

