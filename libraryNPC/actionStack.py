
class ActionStack:
    """ Cтек действий"""
    def __init__(self):
        self._stack = list()

    def add_stack_element(self, element, name, type_action):
        """
            Положить элемент

            name - Имя элемента
            element - функция действия
            type_element - Тип элемента, базовый или промежуточный. Промежуточные удаляются до первого базового.
        """
        self._stack.append({"name": name, "body": element, "type": type_action})

    def get_stack_element(self):
        """ Получить элемент """
        len_stack = self.get_len_stack()
        if len_stack > 0:
            return self.stack[-1]
        else:
            return None

    def pop_stack_element(self):
        """ Удалить и вернуть элемент """
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

    def _get_type_element(self):
        """ Возвращает тип последнего элемента """
        len_stack = self.get_len_stack()
        if len_stack > 0:
            return self.stack[-1]["type"]
        else:
            return None


    def clear_stack(self):
        """ Экстренное удаление всех элементов стека кроме первого"""
        self._stack = list()

    def clear_intermediate_action(self):
        """ Удаление промежуточных действий до первого базового """

        while True:
            if len(self._stack) == 0:
                break
            else:
                type_element = self._get_type_element()
                if type_element is None or type_element == "base":
                    break
                self.pop_stack_element(self)

