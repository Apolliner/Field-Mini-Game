

class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие должно быть закрыто. Закрытые события обобщаются для экономии места.
    """
    def __init__(self, id, type, name, status, entity, connection=None):
        self.id = id
        self.type = type
        self.name = name
        self.status = status
        self.entity = entity
        self.connections = list()
        if connection:
            self.connections.append(connection)

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
        self._types = dict()
        self._event_stack = list()

    def add_standard_memories(self):
        """ Заполняет память стандартными знаниями """
        self._nodes.extend([
                MemoryNode(len(self._nodes), "area", "base_area", "opened", None),  # Запись обо всём мире
                MemoryNode(len(self._nodes + 1), "character", "ordered character", "opened",
                                                                                        "<Объект персонажа игрока>")])

    def generalization_of_experience(self):
        """ Обобщает множество одинаковых закрытых записей в одну """

        for key in self._types:
            closed_memories = list()
            for element in self._types[key]:
                if element.status == "closed":
                    closed_memories.append(element)
            if len(closed_memories) > 5:
                summarized = MemoryNode(len(self._nodes), key, '', "summarized", None)
                for closed_memory in closed_memories:
                    closed_number = closed_memory.id

