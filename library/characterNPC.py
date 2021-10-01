import random
import logging
from library.characterBase import Character, CharacterAction
from library.characterPath import Path


class ActionNPC:
    """
        Содержит описание сложных, многоэтапных действий
    """
    pass


class ActionStep:
    """
        Содержит этап из которого список этапов действия
    """
    pass


class NPC(Character, Path):
    """
        Умные противники, обрабатываемые в каждый момент времени

        РЕАЛИЗОВАТЬ:
        1) Память о прошлых совершаемых и прерванных действиях. Возможно нужен универсальный класс дейсвий и
        поле, отвечающее за хранение списка с прерванными действиями


        Логика всего перемещения:

        if я просто иду?:
            if моя текущая цель это туда? and есть вейпоинты?:
                если да, то иду
            else:
                считаю вейпоинты
                и иду

        elif я преследую?:
            if моя текущая цель это та? and есть вейпоинты? and если цель не далеко ушла:
                иду по старым вейпоинтам
            else:
                считаю вейпоинты
                и иду

        elif я убегаю?
            if есть вейпоинты?
                бегу
            else:
                считаю вейпоинты
                и иду

        elif я ищу следы?
            if я нашел след?
                if а вейпоинты к нему есть?
                    иду по вейпоинтам
                else
                    считаю вейпоинты
                    и иду
            else
                ищу след
                шщу путь к нему
                иду

        elif я совершаю действие?
            if я совершаю все то же действие? and if я всё на том же этапе? qnd
                if я иду?
                    if у меня есть вейпоинты?
                        иду по вейпоинтам
                    else:
                        считаю вейпоинты
                        и иду
                else:
                    я стою

    """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc):
        super().__init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc)

        # ЖИЗНЕННЫЕ ПОКАЗАТЕЛИ:
        self.health = 100  # Здоровье                                   int
        self.hunger = 100  # Голод                                      int
        self.thirst = 100  # Жажда                                      int
        self.fatigue = 100  # Усталость                                 int

        # ЭКИПИРОВКА:
        self.inventory = []  # Инвентарь                                list
        self.equipment = []  # Экипировка                               list

        # ПОВЕДЕНИЕ:
        self.alarm = False  # Атака, ожидание атаки.                    bool
        self.stealth = False  # Скрытность                              bool
        self.alertness = False  # Настороженность                       bool
        self.determination = 100  # Решительность (качество персонажа)  int

        # ОБРАБОТКА
        self.status = []  # Список текущего состояния             list

    def npc_master_calculation(self, step, activity_list):
        """
            Обработка действий персонажа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position()  # Родительский метод
        self.character_reset_at_the_beginning()  # Родительский метод
        self.npc_new_step_check_status()

        # Рассчёт действий
        action = self.npc_checking_the_situation()

        # Совершение действий
        if action.type == 'move':
            self.npc_move_calculations(action)

        elif action.type == 'activity':
            self.npc_activity_calculations(action)

        elif action.type == 'attack':
            self.npc_attack_calculations(action)

        elif action.type == 'getting_damaged':
            self.npc_getting_damaged_calculations(action)

        elif action.type == 'extra':
            self.npc_extra_action_calculations(action)

        else:
            pass

        # Рассчёт последствий
        self.npc_consequences_calculation()

    def npc_new_step_check_status(self):
        """
            Проверяет состояние персонажа на начало хода.
        """
        self.status = []
        if self.health < 50:
            self.status.append('injury')
        elif self.hunger < 50:
            self.status.append('hunger')
        elif self.thirst < 50:
            self.status.append('thirst')
        elif self.fatigue < 50:
            self.status.append('fatigue')

    def npc_checking_the_situation(self):
        """
            Проверяет обстановку для решения дальнейших действий

            Проверяет наличие опасности, наличие путевых точек, наличие неудовлетворённых потребностей.
            Возвращат тип действия, совершаемого на данном шаге.
        """

        if self.alarm:
            if 'injury' in self.status and 100 // self.determination > 0:
                # тут указание преследователя для убегания от него
                return CharacterAction('move', 'escape')
            else:
                return CharacterAction('attack', 'target')

        elif 'injury' in self.status or 'hunger' in self.status or 'thirst' in self.status or \
                'fatigue' in self.status:
            if self.alertness:
                return CharacterAction('activity', 'slow')
            else:
                return CharacterAction('activity', 'fast')
        else:
            return CharacterAction('move', 'details')

    def npc_move_calculations(self, action, activity_list, step, global_map, vertices_graph):
        """
            Передвижение персонажа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        if self.escape:
            self.npc_escape_move()
        if self.follow:
            self.npc_follow_move()
        elif self.activity:
            self.npc_activity_move()
        else:
            self.npc_move(global_map, vertices_graph)

        self.path_local_move(global_map)

    def npc_move(self, global_map, vertices_graph):
        """ Рассчёт перемещения в конкретную точку """
        self.path_calculate(self, global_map, vertices_graph)

        self.path_local_move(global_map)

    def npc_escape_move(self):
        """ Рассчёт бегства """
        pass

    def npc_follow_move(self, global_map, vertices_map):
        """ Рассчёт преследования некоторого персонажа """
        if self.vertices == self.follow.vertices:
            if self.path_length(self.follow.world_position, self.local_waypoints[-1]) > 3:
                self.local_waypoints = self._path_world_tiles_a_star_algorithm(global_map,
                                                                               self.world_position, self.target)
        elif self.follow.vertices != self.global_waypoints:
            self.global_waypoints = self._path_world_vertices_a_star_algorithm(vertices_map,
                                                                               self.vertices, self.follow.vertices)
            self.local_waypionts = self.path_local_waypoints_calculate(self.world_position, global_map)

        # передвижение
        self.path_local_move(self, global_map)

    def npc_random_move(self):
        """ Случайное перемещение или пропуск хода """
        pass

    def npc_activity_move(self):
        """ Перемещение всвязи с выполнением активности """
        pass

    def npc_activity_calculations(self, action):
        """
            Выполнение и оставление активностей на карте, связанных с удовлетворением потребностей или
            праздным времяпрепровожденим.
        """
        pass

    def npc_attack_calculations(self, action):
        """ Действия при атаке """
        pass

    def npc_getting_damaged_calculations(self, action):
        """ Получение повреждений """
        pass

    def npc_extra_action_calculations(self, action):
        """ Особенные действия NPC """
        pass

    def npc_consequences_calculation(self):
        """ Рассчёт последствий действий персонажа """
        pass

