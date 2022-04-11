from libraryNPC.item import Item, ItemEquipment


def get_new_npc_equipment():
    """ Возвращает список элементов экипировки """
    clothes_tuple = (("Шляпа", "clothes", 1, "head"),
                     ("Рубаха с кожаным жилетом", "clothes", 1, "body"),
                     ("Штаны", "clothes", 1, "legs"),
                     ("Кожаные сапоги", "clothes", 1, "feet"))
    items_list: list = []
    for cloth in clothes_tuple:
        items_list.append(ItemEquipment(cloth[0], cloth[1], cloth[2], use_slot=cloth[3]))

    return items_list

