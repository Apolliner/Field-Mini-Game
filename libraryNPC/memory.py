import random
from libraryNPC.stackBase import BaseStack


class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие должно быть закрыто. Закрытые события обобщаются для экономии места.
    """
    def __init__(self, id, type, name, status, entity, connection=None, position=None):
        self.id = id
        self.type = type
        self.name = name
        self.status = status
        self.entity = entity
        self.connections = dict()
        if connection is not None:
            self.connections[connection.id] = connection
        self.positions = list()
        if position is not None:
            self.positions.append(position)

    def get_position(self):
        if hasattr(self, "position") and self.position:
            return self.position
        elif self.entity and self.entity.world_position:
            return self.entity.world_position
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


class Memory:
    """
        Содержит в себе граф памяти
        Память хранит события, обобщенные события и их связи

        _graph содержит связи между элементами памяти
        _types содержит объекты элементов памяти, отсортированные по типам
    """
    def __init__(self):
        self._graph = dict()
        self._types = {
            "area": list(),
            "character": list(),
            "footprints": list()
        }
        self._event_stack = BaseStack()

    def add_standard_memories(self):
        """ Заполняет память стандартными знаниями """
        self._all_add_new_memories(MemoryNode(self._id_generate(), "area", "base_area", "opened", None))
        self._all_add_new_memories(MemoryNode(self._id_generate(), "character", "ordered character", "opened",
                                                                                        "<Объект персонажа игрока>"))

    def _all_add_new_memories(self, memories):
        """ Добавление объекта элемента памяти как в граф, так и в словарь по типам """
        self._graph[memories.id] = memories
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

    def get_position(self):
        """ Получение последней позиции последнего элемента из _event_stack """
        if self._event_stack.get_stack_element() and self._event_stack.get_stack_element().positions:
            return self._event_stack.get_stack_element().positions[-1]
        return None

