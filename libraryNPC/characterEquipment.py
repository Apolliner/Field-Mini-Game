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

    def equipment_get_slots(self) -> dict:
        """ Возвращает словарь со списками доступных и занятых полей исходя из имеющегося снаряжения """
        ...

    def equipment_put_on(self, slot: str, item: ItemEquipment):
        """ Надеть элемент в указанный слот """
        if hasattr(self, F"_equipment{slot}"):
            setattr(self, F"_equipment{slot}", item)

    def equipment_take_off(self, slot: str):
        """ Снять элемент из указанного слота """
        ...