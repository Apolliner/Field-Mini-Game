import random
from libraryNPC.bases import Bases
from libraryNPC.item import Item

class CharacterInventory(Bases):
    """ Инвентарь персонажа """
    _inventory = {"other": [], "meal": []}

    def inventory_get_item(self, type, name=None, count=1):
        """ Посмотреть указанные предмет из инвентаря """
        if type in self._inventory and self._inventory[type]:
            items = self._inventory[type]
            if name is None:
                return random.choice(items)
            else:
                for item in items:
                    if item.name == name:
                        return item
            return None

    def inventory_add_item(self, item):
        """ Добавить предмет в инвентарь """
        if item.type in self._inventory:
            self._inventory[item.type].append(item)
        else:
            self._inventory[item.type] = [item]

    def inventory_extract_item(self, item):
        """ Извлечь указанный предмет из инвентаря """
        if item.type in self._inventory:
            for number_check_item, check_item in enumerate(self._inventory[item.type]):
                if check_item is item:
                    self._inventory[item.type].pop(number_check_item)
                    return True
        return False
        


