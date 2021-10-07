import copy
import random
import logging
from library.characterBase import Character, CharacterAction, Target
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

        elif я атакую?
            if я атакую ту же цель?
                if дальний бой?
                    pass
                elif ближний бой?
                    pass

        ДОПОЛНЕНИЯ:
        self.escape и self.follow содержат в себе либо None либо цель

    """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc):
        super().__init__(global_position, local_position, name, name_npc, icon, type, description, type_npc)

        # ЖИЗНЕННЫЕ ПОКАЗАТЕЛИ:
        self.health = 100  # Здоровье                                   int
        self.hunger = 100  # Голод                                      int
        self.thirst = 100  # Жажда                                      int
        self.fatigue = 100  # Усталость                                 int

        # ЭКИПИРОВКА:
        self.inventory = list()  # Инвентарь                            list
        self.equipment = list()  # Экипировка                           list

        # ПОВЕДЕНИЕ:
        self.alarm = False  # Атака, ожидание атаки.                    bool
        self.stealth = False  # Скрытность                              bool
        self.alertness = False  # Настороженность                       bool
        self.determination = 100  # Решительность (качество персонажа)  int

        # ОБРАБОТКА
        self.status = list()  # Список текущего состояния               list
        self.memory = list()

    def npc_master_calculation(self, step, activity_list, global_map, vertices_graph):
        """
            Обработка действий персонажа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position(global_map)  # Родительский метод
        self.character_reset_at_the_beginning()  # Родительский метод
        self.npc_new_step_check_status()

        # Рассчёт действий
        action = self.npc_checking_the_situation(vertices_graph)

        # Совершение действий
        if action.type == 'move':
            self.npc_move_calculations(action, activity_list, step, global_map, vertices_graph)

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

        self.past_target = copy.deepcopy(self.target)

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

    def npc_checking_the_situation(self, vertices_graph):
        """
            Проверяет обстановку для решения дальнейших действий

            Проверяет наличие опасности, наличие путевых точек, наличие неудовлетворённых потребностей.
            Возвращает тип действия, совершаемого на данном шаге.
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


        elif self.target: # Если есть цель
            return CharacterAction('move', 'details')  # FIXME Пока все цели только на перемещение
        else: # Если нет цели
            self.target = self.npc_calculation_random_target(vertices_graph)
            return CharacterAction('move', 'details')
        #else:
        #    return CharacterAction('move', 'details')

    def npc_calculation_random_target(self, vertices_graph):
        """ Считает случайную цель """
        vertices = vertices_graph[self.vertices]
        direction = random.choice(vertices.connections)
        self.global_waypoints = [direction.number]
        return Target(type='move', entity=None, position=direction.position, create_step=0, lifetime=1000)


    def npc_move_calculations(self, action, activity_list, step, global_map, vertices_graph):
        """
            Передвижение персонажа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        if self.escape:
            self.npc_escape_move()
        if self.follow:
            self.npc_follow_move()
        elif self.activity:
            self.npc_activity_move(global_map, vertices_graph)
        else:
            self.npc_move(global_map, vertices_graph)

        self.path_local_move(global_map)

    def npc_move(self, global_map, vertices_graph):
        """
            Рассчёт перемещения в конкретную точку

            if я просто иду?:
                if моя текущая цель это туда? and есть вейпоинты?:
                    если да, то иду
                else:
                    считаю вейпоинты
                    и иду
        """
        if self.target == self.past_target and self.local_waypoints:
            self.path_local_move(global_map)
        else:
            self.path_calculate(global_map, vertices_graph)

    def npc_escape_move(self, global_map, vertices_graph):
        """
            Рассчёт бегства

            elif я убегаю?
                if я всё так же убегаю? and есть вейпоинты?
                    бегу
                else:
                    считаю вейпоинты
                    и иду
        """
        if self.target == self.past_target and self.local_waypoints:
            self.path_local_move(global_map)
        else:
            self.path_escape_calculate(self, global_map, vertices_graph)

    def npc_follow_move(self, global_map, vertices_graph):
        """
            Рассчёт преследования некоторого персонажа

            elif я преследую?:
                if моя текущая цель это та? and есть вейпоинты? and если цель не далеко ушла:
                    иду по старым вейпоинтам
                else:
                    считаю вейпоинты
                    и иду
        """
        if self.target == self.past_target and self.local_waypoints and self.npc_follow_check(global_map):
            self.path_local_move(global_map)
        else:
            self.path_calculate(self, global_map, vertices_graph)

    def npc_follow_check(self, global_map):
        """
            Проверяет актуальны ли глобальные и локальные координаты преследуемой цели
        """
        if self.vertices == self.target.get_vertices():
            if self.path_length(self.target.world_position, self.local_waypoints[-1]) > 3:
                return False
            return True
        elif self.target.get_vertices(global_map) == self.global_waypoints[-1]:
            return True
        return False

    def npc_random_move(self):
        """ Случайное перемещение или пропуск хода """
        pass

    def npc_activity_move(self, global_map, vertices_graph):
        """
            Выполнение и оставление активностей на карте, связанных с удовлетворением потребностей или
            праздным времяпрепровожденим.
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
        if self.target == self.past_target:
            if self.target.type == 'move':
                if self.local_waypoints:
                    self.path_local_move(global_map)
                else:
                    self.path_calculate(self, global_map, vertices_graph)
            else:
                pass

    def npc_activity_calculations(self):
        """ Первоначальные рассчёты совершения активности """
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

