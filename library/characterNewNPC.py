import copy
import random
import logging
from library.characterBase import Character, CharacterAction, Target
from library.characterPath import Path
from library.bases import Bases

"""
    Вообще всё взаимодействие NPC с миром посредством стека, хранящем функции.
    
    Поиск -> перемещение в точку -> совершение активностей -> прерывания на опасность
    Атака -> выстрел -> занятие позиции -> перезарядка 
"""


class NewNPC(Character, Path, Bases):
    """ Ещё одна попытка сделать расширяемых NPC на базе стека """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc):
        super().__init__(global_position, local_position, name, name_npc, icon, type, description, type_npc)

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
        self.action_stack = self.BaseStack()

        # ОБРАБОТКА
        self.status = list()                            # Список текущего состояния                 list
        self.memory = {'investigation': [],
                       'activity': [],
                       'move': []}                      # Память о действиях и событиях             dict
        self.friends = list()                           # Список друзей персонажа                   list
        self.enemies = list()                           # Список врагов персонажа                   list

    def npc_master_calculation(self, **kwargs):
        """
            Обработка действий персонажа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position(global_map)
        self.character_reset_at_the_beginning()
        self.npc_new_step_check_status()
        self.check_achieving_the_target()

        # Расчёт действий
        self.npc_checking_the_situation(kwargs)

        # Совершение действий, находящихся в стеке
        action = self.action_stack.get_stack_element()
        success = action(kwargs)
        if success:
            self.action_stack.pop_stack_element()

        # Рассчёт последствий
        self.npc_consequences_calculation()
        self.past_target = self.target

    def npc_checking_the_situation(self, kwargs):
        """
            Проверка ситуации. Проверка стека на адекватность. Выкидывание элементов из стека при необходимости
            или добавление новых.
        """
        pass

    def _npc_search_person(self, kwargs):
        """ Глобальная цель поиска указанного персонажа. Базовая активность охотников за головами """
        finish_vertices = random.randrange(5000)
        # Проверка на возможность достичь точки
        _, success = self._path_world_vertices_a_star_algorithm(kwargs["vertices_dict"], self.vertices, finish_vertices)
        if success:
            self.action_stack.add_stack_element(_npc_move_global_path, "global_move")
            return False
        return False

    def _npc_move_global_path(self, kwargs):
        """
            Перемещение к удалённой точке. Во время перемещения постоянно определяет необходимость совершения
            активностей. FIXME Но пока просто ходит
        """
        if self.local_waypoints:
            self.path_local_move(kwargs["global_map"], kwargs["enemy_list"])
        else:
            self.path_calculate(kwargs["global_map"], kwargs["vertices_graph"], kwargs["vertices_dict"],
                                kwargs["enemy_list"])
