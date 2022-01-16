
class BaseStack:
    """ Базовая реализация стека """
    def __init__(self):
        self._stack = list()

    def add_stack_element(self, **kwargs):
        """
            Положить элемент
            element - элемент стека
        """
        self._stack.append({"element": kwargs["element"]})

    def get_stack_element(self):
        """ Получить элемент """
        len_stack = self.get_len_stack()
        if len_stack > 0:
            return self._stack[-1]
        else:
            return None

    def pop_stack_element(self):
        """ Удалить и вернуть элемент """
        len_stack = self.get_len_stack()
        if len_stack > 0:
            return self._stack.pop(len_stack - 1)
        else:
            return None

    def get_len_stack(self):
        """ Размер стека """
        return len(self._stack)

    def clear_stack(self):
        """ Экстренное удаление всех элементов стека"""
        self._stack = list()


