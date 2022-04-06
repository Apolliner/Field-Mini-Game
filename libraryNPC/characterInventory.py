from libraryNPC.bases import Bases
from libraryNPC.item import Item

class CharacterInventory(Bases):
    """ Инвентарь персонажа """
    _inventory = {"other": [], "meal": []}

    def inventory_get_item(self, type, count=1):
        if type in self._inventory and self._inventory[type]:
            items = self._inventory[type]