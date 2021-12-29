from library.bases import Bases


class SearchFootprints(Bases):

    def _search_footprints(self, **kwargs):
        """
            Повторяет в цикле следующие действия:
            Поиск в округе нужных следов -> если найдены, то идти к ним -> новый поиск
                                         -> если не найдены, то искать в радиусе
        """

        return False

    def _search_for_traces(self, **kwargs):
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
                    if check_position in step_activity_dict and list(check_position) not in pass_positions and \
                            kwargs["step_activity_dict"][check_position].entity.name_npc == self.investigation.name_npc \
                            and kwargs["step_activity_dict"][check_position].visible:
                        if (activity and activity.birth < step_activity_dict[check_position].birth) or not activity:
                            if self.target.type == 'investigation' or self.target.type == 'radius_investigation':
                                if self.target.kwargs['activity'].birth < kwargs["step_activity_dict"][check_position].birth:
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
            self.path_calculate(kwargs["global_map"], kwargs["vertices_graph"], kwargs["vertices_dict"],
                                                                                                kwargs["enemy_list"])
        elif self.target.type == 'investigation':
            self.npc_radius_search_for_traces(kwargs["global_map"], kwargs["step"])

    def _radius_search_for_traces(self, **kwargs):
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
                if self.path_world_tile(kwargs["global_map"], new_position).vertices != -1:
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

