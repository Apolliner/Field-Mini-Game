from libraryNPC.stackBase import BaseStack
from library.decorators import trace


class ActionStack(BaseStack):
    @trace
    def add_stack_element(self, **kwargs):
        """
            Положить элемент

            name - Имя элемента
            element - функция действия
            target - Хранит задачу этого элемента.
        """
        self._stack.append({"name": kwargs["name"], "element": kwargs["element"], "target": kwargs["target"]})

    @trace
    def get_names(self):
        """ Возвращает список имён элементов """
        names = list()
        for element in self._stack:
            names.append(element["name"])
        return names

    @trace
    def _get_type_element(self):
        """ Возвращает тип последнего элемента """
        len_stack = self.get_len_stack()
        if len_stack > 0:
            return self._stack[-1]["type"]
        else:
            return None

    @trace
    def clear_intermediate_action(self):
        """ Удаление промежуточных действий до первого базового """
        while True:
            if len(self._stack) == 0:
                break
            else:
                type_element = self._get_type_element()
                if type_element is None or type_element == "base":
                    break
                else:
                    self.pop_stack_element()

    @trace
    def get_target(self):
        element = self.get_stack_element()
        if element and "target" in element:
            return element["target"]
        return None

