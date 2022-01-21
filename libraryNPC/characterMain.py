import random
from libraryNPC.characterBase import Character
from libraryNPC.characterPath import Path
from libraryNPC.characterPathMove import PathMove
from libraryNPC.bases import Bases
from libraryNPC.characterNPCSearchFootprints import SearchFootprints
from libraryNPC.characterMove import CharacterMove
from libraryNPC.memory import Memory, MemoryNode
from libraryNPC.stackBase import BaseStack
from libraryNPC.stackAction import ActionStack
from libraryNPC.temporaryOld import TemporaryOld

"""
    Вообще всё взаимодействие NPC с миром посредством стека, хранящем функции.
    
    Поиск -> перемещение в точку -> совершение активностей -> прерывания на опасность
    Атака -> выстрел -> занятие позиции -> перезарядка 
"""


class NewNPC(Character, CharacterMove, TemporaryOld):  #, SearchFootprints, CharacterMove, PathMove):
    """ Ещё одна попытка сделать расширяемых NPC на базе стека """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc, **kwargs):
        super().__init__(global_position, local_position, name, name_npc, icon, type, description, type_npc, **kwargs)

        # ЖИЗНЕННЫЕ ПОКАЗАТЕЛИ:
        self.health = 100                               # Здоровье                                  int
        self.hunger = 100                               # Голод                                     int
        self.thirst = 100                               # Жажда                                     int
        self.fatigue = 100                              # Усталость                                 int

        # ЭКИПИРОВКА:
        self.inventory = list()                         # Инвентарь                                 list
        self.equipment = list()                         # Экипировка                                list

        # ПОВЕДЕНИЕ:
        self.alarm = False                              # Атака, ожидание атаки.                    bool
        self.stealth = False                            # Скрытность                                bool
        self.alertness = False                          # Настороженность                           bool
        self.determination = 100                        # Решительность (качество персонажа)        int
        self.action_stack = ActionStack()

        # ОБРАБОТКА
        self.status = list()                            # Список текущего состояния                 list
        self.memory = Memory(self)                      # Граф памяти персонажа                     Memory
        self.friends = list()                           # Список друзей персонажа                   list
        self.enemies = list()                           # Список врагов персонажа                   list

        self._init_new_npc(**kwargs)

    def npc_master_calculation(self, **kwargs):
        """
            Обработка действий персонажа на текущем шаге
        """
        # Подготовка
        self.character_reset_at_the_beginning()
        self.check_achieving_the_target()

        # Расчёт срочных действий
        self.npc_checking_the_situation(**kwargs)

        # Совершение действий, находящихся в стеке
        self.bases_router(self.action_stack, **kwargs)

        # Расчёт последствий
        self.past_target = self.target
        self.character_check_all_position(**kwargs)

    def npc_checking_the_situation(self, **kwargs):
        """
            Проверка ситуации. Проверка стека на адекватность. Выкидывание элементов из стека при необходимости
            или добавление новых.
        """
        pass

    def _init_new_npc(self, **kwargs):
        """ Инициализирует нового NPC """
        self.memory.add_standard_memories(kwargs["player"])
        target = self.memory.add_memories("target", "global_move", **kwargs)
        self.action_stack.add_stack_element(name="global_move", element=self._move_search_person, target=target)

    def check_achieving_the_target(self):
        pass

