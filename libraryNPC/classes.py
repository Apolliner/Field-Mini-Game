class PushingList(list):
    """ При переполнении выталкивает первый элемент. Стандартная максимальная длинна 10 элементов. """
    max_len = 10

    def append(self, item):
        super(PushingList, self).append(item)
        if self.__len__() > self.max_len:
            self.pop(0)
