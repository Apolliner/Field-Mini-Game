class PushingList(list):
    """ При переполнении выталкивает первый элемент. Стандартная максимальная длинна 10 элементов. """
    max_len = 10

    def append(self, *args):
        for arg in args:
            super(PushingList, self).append(arg)
            if self.__len__() > self.max_len:
                self.pop(0)

