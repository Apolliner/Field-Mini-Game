

class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие должно быть закрыто. Закрытые события обобщаются для экономии места.
    """
    def __init__(self, number, type, name, status, entity, connection=None):
        self.number = number
        self.type = type
        self.name = name
        self.status = status
        self.entity = entity
        self.connections = list()
        if connection:
            self.connections.append(connection)


class Memory:
    """
        Содержит в себе граф памяти
        Память хранит события, обобщенные события и их связи

        _nodes содержит элементы памяти
        _graph содержит связи между элементами памяти
    """
    def __init__(self):
        self._nodes = list()
        self._graph = dict()
        self._event_stack = list()

    def add_standard_memories(self):
        """ Заполняет память стандартными знаниями """
        self._nodes.extend([
                MemoryNode(len(self._nodes), "area", "base_area", "opened", None),  # Запись обо всём мире
                MemoryNode(len(self._nodes + 1), "character", "target", "opened", "<Объект персонажа игрока>")])
