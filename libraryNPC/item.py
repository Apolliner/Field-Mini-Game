from libraryNPC.bases import Bases


class Item:
    """ Предмет """
    def __init__(self, name, type, weight, **kwargs):
        self.id = bases_gen_random_id(kwargs["ids_list"])
        self.name = name
        self.type = type
        self.weight = weight

    def use(self, **kwargs):
        """ Использовать предмет """
        self.kill()


class ItemEquipment(Item):
    """ Предмет, который можно надеть """
    def __init__(self, *args, use_slot=None, add_slots=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_slots = add_slots
        self.use_slot = use_slot
        self.use = False

    def use(self, **kwargs):
        """ Использовать предмет """
        pass

class ItemStack(Item):
    """ Предмет, содержащий множество предметов """
    def __init__(self, *args, count=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = count

    def use(self, **kwargs):
        """ Использовать предмет """
        if self.count <= 1:
            self.kill()
        else:
            self.count -= 1


class ItemWeapon(ItemEquipment):
    """ Предмет оружия """
    def __init__(self, *args, cartridge_type=None, cartridges_loaded=0, cartridges_in_the_magazine=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.cartridge_type = cartridge_type
        self.cartridges_loaded = cartridges_loaded
        self.cartridges_in_the_magazine = cartridges_in_the_magazine

