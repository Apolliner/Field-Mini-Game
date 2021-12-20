import copy
import random
import logging
from library.characterBase import Character, CharacterAction, Target
from library.characterPath import Path
from library.bases import Bases

"""
    ОПИСАНИЕ ПОИСКА ШАГОВ
    
    Для персонажа есть "свои" NPC и все остальные - "посторонние"
    Периодически персонаж проверяет округу на наличие посторонних следов. Следами считаются следы ног и следы активностей.
    При нахождении следов, выбирается самый свежий и оставивший её персонаж помещается в investigation.
    Устанавливается цель на найденные следы.
    При перемещении к следам, происходит следующий поиск самых свежих следов.
    При их отсутствии, происходит установка точки поиска, затем случайно, в определённом радиусе от этой точки 
    выбираются несколько точек, в которых произойдут дополнительные поиски следов.
    Если след потерян, но следы были свежими, то надолго остаётся режим опасности. Если следы старые, то ненадолго.
    Персонаж возвращяется к своим обычным делам
    
    
    ТРЕБУЕТСЯ ОПИСАНИЕ ГЛОБАЛЬНОГО ПОИСКА
    Так как NPC противники являются охотниками за головами, у них должна быть логика перемещения по игровой карте. 
    
    ТРЕБУЕТСЯ ПРОРАБОТАТЬ РАБОТУ ПАМЯТИ ПЕРСОНАЖА
    Требуется запоминать прошлые совершённые действия и положения. Возможно стоит реализовать их запись в memory.
    
    Память представляет из себя словарь, с типами событий, содержащими списки классов Memory
    
"""

class Memory:
    """
        Содержит память NPC противников

        Память может быть следующих типов:
        activity
        target
        follow
        escape
        investigation

        Статус может быть

        passed
        failed
        interrupted
        continued

        Если статус interrupted, то можно достать действие из памяти и повторить, или закончить.

    """
    def __init__(self, step, world_position, description, status, entity=None, content=None):
        self.step = step
        self.world_position = world_position
        self.description = description
        self.status = status
        self.entity = entity
        self.content = content


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


class NPC(Character, Path, Bases):
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
        self.memory = {'investigation':[],
                       'activity':[],
                       'move':[]}  # Память о действиях и событиях      dict
        self.friends = list()  # Список друзей персонажа                list
        self.enemies = list()  # Список врагов персонажа                list

    def npc_master_calculation(self, step, activity_list, global_map, vertices_graph, vertices_dict, enemy_list,
                               step_activity_dict):
        """
            Обработка действий персонажа на текущем шаге
        """
        #print(F"\n\n\nstep -            {step}")
        # Подготовка
        self.character_check_all_position(global_map)  # Родительский метод
        self.character_reset_at_the_beginning()  # Родительский метод
        self.npc_new_step_check_status()
        self.check_achieving_the_target()

        # Рассчёт действий
        action = self.npc_checking_the_situation(vertices_graph, vertices_dict, enemy_list, step_activity_dict, step)

        # Совершение действий
        if action.type == 'move':
            self.npc_move_calculations(action, activity_list, step, global_map, vertices_graph,
                                                                    vertices_dict, enemy_list)

        elif action.type == 'activity':
            self.npc_activity_calculations(action)

        elif action.type == 'attack':
            self.npc_attack_calculations(action)

        elif action.type == 'getting_damaged':
            self.npc_getting_damaged_calculations(action)

        elif action.type == 'extra':
            self.npc_extra_action_calculations(action, global_map, enemy_list, step_activity_dict, vertices_graph,
                                               vertices_dict, step)
        else:
            pass

        # Рассчёт последствий
        self.npc_consequences_calculation()
        self.past_target = self.target

    def check_achieving_the_target(self):
        """
            Проверяет достижение цели или достижение глобального вейпоинта
        """
        if self.global_waypoints and self.vertices == self.global_waypoints[0]:
            self.global_waypoints.pop(0)
        if self.target and self.global_position == self.target.position:
            self.target = None

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

        if self.forced_pass > 3:
            self.global_waypoints = list()
            self.local_waypoints = list()
            self.forced_pass = 0

    def npc_checking_the_situation(self, vertices_graph, vertices_dict, enemy_list, step_activity_dict, step):
        """
            Проверяет обстановку для решения дальнейших действий

            Проверяет наличие опасности, наличие путевых точек, наличие неудовлетворённых потребностей.
            Возвращает тип действия, совершаемого на данном шаге.
        """
        if not self.investigation and random.randrange(10)//9 > 0:
            self.checking_for_noticeable_traces(step_activity_dict)

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
        elif self.escape:  # Назначение побега
            if self.past_target.entity != self.escape:
                self.global_waypoints = list()
                self.local_waypoints = list()
                self.target = Target(type='escape', entity=self.escape, position=self.escape.world_position,
                                     create_step=0, lifetime=1000)
            else:
                self.target = self.past_target
                self.target.entity = self.escape
            return CharacterAction('move', 'escape')

        elif self.follow:  # Назначение преследования
            if self.past_target.entity != self.follow:
                self.global_waypoints = list()
                self.local_waypoints = list()
                self.target = Target(type='follow', entity=self.follow, position=self.follow.world_position,
                                 create_step=0, lifetime=1000)
            else:
                self.target = self.past_target
                self.target.entity = self.follow
            return CharacterAction('move', 'follow')  # Если есть цель преследования, то преследование
        elif self.investigation:  # Если были обнаружены следы
            if self.past_target.entity != self.investigation:
                #print(F"\ntrue 1\n"
                #      F"self.past_target.entity - {self.past_target.entity}\n"
                #      F"self.investigation - {self.investigation}")
                self.global_waypoints = list()
                self.local_waypoints = list()
                #print(F"self.target.entity - {self.target.entity}\n")
            else:
                #print(F"true 2")
                self.target = self.past_target
                self.target.entity = self.follow
            return CharacterAction('extra', 'investigation')

        elif self.target:                                # Если есть цель

            # Если тип цели равен None, то проверяется содержимое памяти
            if self.target.type is None:
                self.npc_check_memory(step)

            if self.target != self.past_target:
                self.global_waypoints = list()
                self.local_waypoints = list()
            return CharacterAction('move', 'details')    # FIXME Пока все цели только на перемещение
        else:  # Если нет цели

            self.target = self.npc_calculation_random_target(vertices_graph, vertices_dict)
            return CharacterAction('move', 'details')
        return CharacterAction('pass', 'details')

    def checking_for_noticeable_traces(self, step_activity_dict):
        """ Проверяет наличие заметных шагов рядом с персонажем """
        pathfinder_dict = {
            1: ['0.0', '...', '0.0'],
            2: ['00.00', '0...0', '.....', '0...0', '00.00'],
            3: ['000.000', '00...00', '0.....0', '.......', '0.....0', '00...00', '000.000'],
            4: ['0000.0000', '00.....00', '0.......0', '0.......0', '.........', '0.......0', '0.......0', '00.....00',
                '0000.0000'],
            5: ['0000...0000', '000.....000', '00.......00', '0.........0', '...........', '...........', '...........',
                '0.........0', '00.......00', '000.....000', '0000...0000'],
            6: ['00000...00000', '000.......000', '00.........00', '0...........0', '0...........0', '.............',
                '.............', '.............', '0...........0', '0...........0', '00.........00', '000.......000',
                '00000...00000'],
        }
        null_position = [self.world_position[0] - self.pathfinder, self.world_position[1] - self.pathfinder]
        pattern = pathfinder_dict[self.pathfinder]
        activity_position = None
        activity = None
        for number_line, line in enumerate(pattern):
            for number_tile, tile in enumerate(line):
                if tile == '.':
                    check_position = (null_position[0] + number_line, null_position[1] + number_tile)
                    if check_position in step_activity_dict and step_activity_dict[check_position].entity.name_npc == 'person': #step_activity_dict[check_position].caused != self.name_npc:
                        #print(F"Найдена активность в - {check_position}")
                        if activity is None or (activity and activity.birth == step_activity_dict[check_position].birth):
                            activity = step_activity_dict[check_position]
                            activity_position = check_position
        if activity:
            self.investigation = activity.entity
            self.target = Target(type='investigation', entity=None, position=activity_position, create_step=0, lifetime=1000, activity=activity)

    def npc_calculation_random_target(self, vertices_graph, vertices_dict):
        """ Считает случайную цель """
        number_vertices = self.vertices
        for step in range(10):
            vertices = random.choice(vertices_dict[number_vertices].connections)
            number_vertices = vertices.number

        vertices_global_position = vertices_dict[number_vertices].position
        vertices_local_position = random.choice(random.choice(vertices_dict[number_vertices].connections).tiles)
        world_position = self.character_world_position_calculate(vertices_global_position, vertices_local_position)
        return Target(type='move', entity=None, position=world_position, create_step=0, lifetime=1000)


    def npc_move_calculations(self, action, activity_list, step, global_map, vertices_graph, vertices_dict, enemy_list):
        """
            Передвижение персонажа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        if action.details == 'escape':
            self.npc_escape_move(global_map, vertices_graph, vertices_dict, enemy_list)
        elif action.details == 'follow':
            self.npc_follow_move(global_map, vertices_graph, vertices_dict, enemy_list)
        elif self.activity:
            self.npc_activity_move(global_map, vertices_graph, vertices_dict, enemy_list)
        else:
            self.npc_move(global_map, vertices_graph, vertices_dict, enemy_list)
        #self.path_local_move(global_map, enemy_list)

    def npc_move(self, global_map, vertices_graph, vertices_dict, enemy_list):
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
            self.path_local_move(global_map, enemy_list)
        else:
            self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)

    def npc_escape_move(self, global_map, vertices_graph, vertices_dict, enemy_list):
        """
            Рассчёт бегства

            elif я убегаю?
                if я всё так же убегаю? and есть вейпоинты?
                    бегу
                else:
                    считаю вейпоинты
                    и иду
        """
        if self.target == self.past_target and self.local_waypoints and self.npc_escape_check(global_map):
            self.path_local_move(global_map, enemy_list)
        else:
            self.path_escape_calculate(global_map, vertices_graph, vertices_dict, enemy_list)

    def npc_escape_check(self, global_map):
        """ Проверяет актуальность посчитанных вейпоинтов побега """
        if self.path_length(self.world_position, self.target.get_position()) < 10:
            return False
        return True

    def npc_follow_move(self, global_map, vertices_graph, vertices_dict, enemy_list):
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
            if self.path_length(self.target.get_position(), self.world_position) > 2:
                self.path_local_move(global_map, enemy_list)
        else:
            self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)

    def npc_follow_check(self, global_map):
        """
            Проверяет актуальны ли глобальные и локальные координаты преследуемой цели
        """
        if self.vertices == self.target.get_vertices(global_map) and self.local_waypoints:
            if self.path_length(self.target.get_position(), self.local_waypoints[-1]) > 3:
                return False
            return True
        elif self.global_waypoints and self.target.get_vertices(global_map) == self.global_waypoints[-1]:
            return True
        return False

    def npc_random_move(self):
        """ Случайное перемещение или пропуск хода """
        pass

    def npc_activity_move(self, global_map, vertices_graph, enemy_list):
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
        # FIXME Логика не отсюда, но пускай пока лежит.
        if self.target == self.past_target:
            if self.target.type == 'investigation':
                if self.local_waypoints:
                    self.path_local_move(global_map, enemy_list)
                else:
                    self.path_calculate(self, global_map, vertices_graph, enemy_list)

    def npc_activity_calculations(self):
        """ Первоначальные рассчёты совершения активности """
        pass

    def npc_attack_calculations(self, action, global_map, vertices_graph, vertices_dict, enemy_list):
        """
            Действия при атаке

            elif я атакую?
            if я атакую ту же цель?
                if дальний бой?
                    pass
                elif ближний бой?
                    pass
        """
        if self.target == self.past_target:
            if self.attack.type == 'close_combat':
                pass
            elif self.attack == "ranged_combat":
                # FIXME тут нужна проверка на тип оружия, соответственно на сколько шагов надо подойти для выстрела.
                if self.path_length(self.world_position, self.target.get_position()) < 10:
                    pass
                else:
                    self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)

    def npc_getting_damaged_calculations(self, action):
        """ Получение повреждений """
        pass

    def npc_extra_action_calculations(self, action, global_map, enemy_list, step_activity_dict, vertices_graph,
                                      vertices_dict, step):
        """ Особенные действия NPC """
        if action.details == 'investigation':
            # Если установлена цель поиска по радиусу и текущее местоположение равно указанной цели, то производится
            # поиск следов
            if self.target.type == 'radius_investigation' and self.world_position == self.target.get_position():
                self.npc_search_for_traces(step_activity_dict, global_map, vertices_graph, vertices_dict, enemy_list,
                                                                                                                step)
                # Если после поиска следов цель не меняется на следование к следующим следам, то рассчитывается путь до
                # следующей точки в радиусе
                if self.target.type != 'investigation':
                    self.npc_radius_search_for_traces(global_map, step)
            # Если установлена цель поиска в радиусе но текущее положение не равно цели, то передвижение
            elif self.target.type == 'radius_investigation' and self.world_position != self.target.get_position():
                self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)

            # Если текущая цель следование к следующим следам и цель ещё не достигнута
            elif self.target and self.target.type == 'investigation' and self.world_position != self.target.get_position():
                self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)
            # Если текущая цель следование к следующим вейпоинтам, и цель достигнута, то производится новый поиск в радиусе
            else:
                self.memory['investigation'].append(Memory(step, self.world_position, None, 'passed'))
                self.npc_search_for_traces(step_activity_dict, global_map, vertices_graph, vertices_dict, enemy_list, step)

    def npc_consequences_calculation(self):
        """ Рассчёт последствий действий персонажа """
        pass

    def world_position_calculate(self, _):
        """ Затычка для подключения к старой системе"""
        pass

    def npc_search_for_traces(self, step_activity_dict, global_map, vertices_graph, vertices_dict, enemy_list, step):
        """
            Проверяет есть ли посчитанные вейпоинты поиска пути.
            Проверяет зону вокруг персонажа на наличие следов или лёгких следов
            Зона рассчитывается по предрассчитанным шаблонам

            Возможно стоит реализовать алгоритм Дийкстры, вместо шаблонов, а может шаблоны будут быстрее

            Персонаж замечает видимые следы и начинает искать невидимые следы, идёт по ним.
        """
        pathfinder_dict = {
            1: ['0.0', '...', '0.0'],
            2: ['00.00', '0...0', '.....', '0...0', '00.00'],
            3: ['000.000', '00...00', '0.....0', '.......', '0.....0', '00...00', '000.000'],
            4: ['0000.0000', '00.....00', '0.......0', '0.......0', '.........', '0.......0', '0.......0', '00.....00',
                '0000.0000'],
            5: ['0000...0000', '000.....000', '00.......00', '0.........0', '...........', '...........', '...........',
                '0.........0', '00.......00', '000.....000', '0000...0000'],
            6: ['00000...00000', '000.......000', '00.........00', '0...........0', '0...........0', '.............',
                '.............', '.............', '0...........0', '0...........0', '00.........00', '000.......000',
                '00000...00000'],
        }
        pass_positions = list()
        # Запрет возвращаться к текущему следу
        #if self.target and self.target.type == 'investigation' and self.target.get_position() != self.world_position:
        pass_positions.append(self.target.get_position())
        memory_list = self.npc_get_memory('investigation')
        # Запрет возвращаться к уже проверенным следам
        if memory_list:
            for memory in memory_list:
                pass_positions.append(memory.world_position)

        null_position = [self.world_position[0] - self.pathfinder, self.world_position[1] - self.pathfinder]
        pattern = pathfinder_dict[self.pathfinder]
        activity_position = None
        activity = None
        for number_line, line in enumerate(pattern):
            for number_tile, tile in enumerate(line):
                if tile == '.':
                    check_position = (null_position[0] + number_line, null_position[1] + number_tile)
                    if check_position in step_activity_dict and list(check_position) not in pass_positions and step_activity_dict[
                                                check_position].entity.name_npc == self.investigation.name_npc and \
                                                step_activity_dict[check_position].visible:
                        if (activity and activity.birth < step_activity_dict[check_position].birth) or not activity:
                            if self.target.type == 'investigation' or self.target.type == 'radius_investigation':
                                if self.target.kwargs['activity'].birth < step_activity_dict[check_position].birth:
                                    activity = step_activity_dict[check_position]
                                    activity_position = list(check_position)
                            else:
                                activity = step_activity_dict[check_position]
                                activity_position = list(check_position)
        if activity:
            self.memory['investigation'].append(Memory(step, self.target.get_position(), None, 'passed',
                                                                entity=self.target.entity, content=None))
            self.target = Target(type='investigation', entity=None, position=activity_position, create_step=0,
                                                                                    lifetime=1000, activity=activity)
            self.path_calculate(global_map, vertices_graph, vertices_dict, enemy_list)
        elif self.target.type == 'investigation':
            self.npc_radius_search_for_traces(global_map, step)

    def npc_get_memory(self, type):
        """
            Возвращает последние 3 записи указанного типа
        """
        if type in self.memory:
            memory = self.memory[type]
            memory = list(reversed(memory))
            if memory:
                if len(memory) >= 10:
                    return memory[::10]
                else:
                    return memory
        return None

    def npc_check_memory(self, step):
        """
            Проверяет содержимое памяти

            Если находит подходящую запись для продолжения, то отмечает её продолженной

        """
        type_tuple = ('activity', 'move', 'follow')
        for type in type_tuple:
            memory_list = self.npc_get_memory(self, type)
            if memory_list is not None:
                for memory in memory_list:
                    if memory.status == 'interrupted':
                        self.target = Target(type=memory.type, entity=memory.entity,
                                    position=memory.world_position, create_step=step, lifetime=1000)
                        memory.status = "continued"
                        if memory.type in ('follow', 'escape', 'investigation') and memory.entity:
                            setattr(self, memory.type, memory.entity)
                        break
            else:
                continue

    def npc_radius_search_for_traces(self, global_map, step):
        """
            Выставляет точку, определяет радиус, и проверяет 4 точки по сторонам, в каждой точке ищет следы.
            Если не находит, то бросает это занятие
        """
        def edge_detection(direction, radius, world_position):
            """ Доходит до максимально доступной точки на границе радиуса """
            for step in range(radius):
                if direction == 'left':
                    new_position = [world_position[0], world_position[1] - 1]
                elif direction == 'up':
                    new_position = [world_position[0] - 1, world_position[1]]
                elif direction == 'right':
                    new_position = [world_position[0], world_position[1] + 1]
                else:  # direction == 'down':
                    new_position = [world_position[0] + 1, world_position[1]]
                if self.path_world_tile(global_map, new_position).vertices != -1:
                    world_position = new_position
                else:
                    return world_position
            return world_position
        radius_investigation_dict = {1: 'left', 2: 'up', 3: 'right', 4: 'down'}  # FIXME для начала просто по сторонам
        # Если поиск по радиусу ещё не проводился
        if self.target.type == 'radius_investigation' and self.target.kwargs['step_radius'] <= 4:
            finish_point = edge_detection(radius_investigation_dict[self.target.kwargs['step_radius']], self.pathfinder,
                                                                                           self.target.kwargs["center"])
            self.target = Target(type='radius_investigation', entity=None, position=finish_point,
                                 create_step=step, lifetime=1000, step_radius=(self.target.kwargs['step_radius'] + 1),
                                 center=self.target.kwargs["center"], activity=self.target.kwargs['activity'])
        elif self.target.type == 'radius_investigation' and self.target.kwargs['step_radius'] > 4:
            # Сброс поиска
            self.target = Target(type='move', entity=None, position=self.world_position,
                                 create_step=step, lifetime=1000)
        else:
            finish_point = edge_detection(radius_investigation_dict[1], self.pathfinder, self.world_position)

            self.target = Target(type='radius_investigation', entity=None, position=finish_point,
                                        create_step=step, lifetime=1000, step_radius=1, center=self.world_position,
                                        activity=self.target.kwargs['activity'])

