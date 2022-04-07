from libraryNPC.bases import Bases
from libraryNPC.item import Item


class CharacterEquipment(Bases):
    """ Экипировка персонажа """
    def __init__(self, head=None, face=None, body=None, right_hand=None, left_hand=None, legs=None, feet=None):
        self._equipment_head: Item = head
        self._equipment_face: Item = face
        self._equipment_body: Item = body
        self._equipment_right_hand: Item = right_hand
        self._equipment_left_hand: Item = left_hand
        self._equipment_legs: Item = legs
        self._equipment_feet: Item = feet

    def equipment_get_slots(self) -> dict:
        """ Возвращает словарь со списками доступных и занятых полей исходя из имеющегося снаряжения """
        ...

    def equipment_put_on(self, slot: str):
        """ Надеть элемент в указанный слот """
        ...

    def equipment_take_off(self, slot: str):
        """ Снять элемент из указанного слота """
        ...