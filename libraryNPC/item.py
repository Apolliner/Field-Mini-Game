from libraryNPC.bases import Bases


class Item(Bases):
    """ Предмет """
    def __init__(self, name, type, weight, **kwargs):
        self.id = bases_gen_random_id(kwargs["ids_list"])
        self.name = name
        self.type = type
        self.weight = weight

    def use(self):
        """ Использовать предмет """
        self.kill()