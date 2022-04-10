from libraryNPC.bases import Bases
from libraryNPC.item import Item, ItemEquipment


class CharacterEquipment(Bases):
    """ Экипировка персонажа """
    def __init__(self, head=None, face=None, body=None, right_hand=None, left_hand=None, legs=None, feet=None):
        self._equipment_head: ItemEquipment = head
        self._equipment_face: ItemEquipment = face
        self._equipment_body: ItemEquipment = body
        self._equipment_right_hand: ItemEquipment = right_hand
        self._equipment_left_hand: ItemEquipment = left_hand
        self._equipment_legs: ItemEquipment = legs
        self._equipment_feet: ItemEquipment = feet
        self._slots = ["head", "face", "body", "right_hand", "left_hand", "legs", "feet"]

    def equipment_put_on(self, slot: str, item: ItemEquipment):
        """ Надеть элемент в указанный слот """
        if hasattr(self, F"_equipment{slot}"):
            setattr(self, F"_equipment{slot}", item)
            for add_slot in item.add_slots:
                setattr(self, F"_equipment{add_slot}", None)

    def equipment_take_off(self, slot: str):
        """ Снять элемент из указанного слота """
        if hasattr(self, F"_equipment{slot}"):
            item = getattr(self, F"_equipment{slot}")
            for add_slot in item.add_slots:
                self._slots.pop(add_slot)
                slot_item = getattr(self, F"_equipment{add_slot}")
                slot_item.use = False
                delattr(self, F"_equipment{add_slot}")
            setattr(self,  F"_equipment{slot}", None)