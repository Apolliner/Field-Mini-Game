

class MemoryNode:
    """
        Вершина графа памяти
        Каждое событие как протокол - должно быть закрыто. Закрытые события обобщаются для экономии места.
    """
    def __init__(self, number, type, connection=None):
        self.number = number
        self.type = type
        self.connections = list()
        if connection:
            self.connections.append(connection)


class Memory:
    """
        Содержит в себе граф памяти
        Память хранит события и обобщенные события

        _nodes содержит элементы памяти
        _graph содержит связи между элементами памяти
    """
    def __init__(self):
        self._nodes = list()
        self._graph = dict()
        self._event_stack = list()
