from libraryNPC.bases import Bases


class PathBase():
    """ Базовый класс передвижения, чтобы не пересекались методы разных типов передвижения """

    def _path_base_local_move(self, **kwargs):
        """ Реализует перемещение персонажа по локальным вейпоинтам """
        # FIXME пока всё очень просто
        if self.local_waypoints:
            waypoint = self.local_waypoints.pop(0)
            print(F"self.target.get_position() - {self.target.get_position()}\n"
                  F"waypoint - {waypoint}, self.world_position - {self.world_position}\n"
                  F"self.global_waypoints - {self.global_waypoints}\n"
                  F"self.local_waypoints - {self.local_waypoints}")
            if len(self.local_waypoints) == 0 and self.global_waypoints:
                self.global_waypoints.pop(0) # Удаление реализованного вейпоинта
            self.direction, self.animations = self._path_base_direction_calculation(self.world_position, waypoint)
            self.world_position = waypoint
            self.global_position, self.local_position = self.bases_world_position_recalculation(self.world_position)
            tile = self.bases_world_tile(kwargs["global_map"], self.world_position)
            self.vertices = tile.vertices
            self.level = tile.level

    def _path_base_direction_calculation(self, start, finish):
        """ Определяет направление движения """
        if [start[0] - 1, start[1]] == finish:
            return 'up', 'u'
        elif [start[0] + 1, start[1]] == finish:
            return 'down', 'd'
        elif [start[0], start[1] - 1] == finish:
            return 'left', 'l'
        elif [start[0], start[1] + 1] == finish:
            return 'right', 'r'
        return "center", 'd'

    def _path_base_global_direction_calculation(self, start_vertices, finish_vertices, vertices_dict):
        """ Определяет направление глобального движения """
        #print(F"start_vertices - {start_vertices}")
        start = vertices_dict[start_vertices].position
        finish = vertices_dict[finish_vertices].position
        if [start[0] - 1, start[1]] == finish:
            return 'up'
        elif [start[0] + 1, start[1]] == finish:
            return 'down'
        elif [start[0], start[1] - 1] == finish:
            return 'left'
        elif [start[0], start[1] + 1] == finish:
            return 'right'
        return None

    def _path_base_line_waypoints_calculation(self, start_point, finish_point, limiter=False):
        """
            Cчитает прямой путь до координат цели, останавливая рассчёт в тот момент, когда достигнет
            другой зоны доступности. Возвращает последний рассчитаный тайл в мировых координатах
            Возвращает список мировых вейпоинтов.
        """

        start_global_position, _ = self.bases_world_position_recalculation(start_point)

        axis_y = finish_point[0] - start_point[0]  # длинна стороны и количество шагов
        axis_x = finish_point[1] - start_point[1]  # длинна стороны и количество шагов
        if abs(axis_y) > abs(axis_x):
            if axis_x != 0:
                length_step = abs(axis_y) // abs(axis_x)  # на один X столько то Y
            else:
                length_step = abs(axis_y)
            long_side = 'y'
        else:
            if axis_y != 0:
                length_step = abs(axis_x) // abs(axis_y)  # на один Y столько то X
            else:
                length_step = abs(axis_x)
            long_side = 'x'

        waypoints = [start_point]

        for step in range((abs(axis_y) + abs(axis_x))):
            if limiter:
                global_position, _ = self.bases_world_position_recalculation(waypoints[-1])
                # Если другая глобальная позиция, то сменить положение
                if global_position != start_global_position:
                   break
            if (step + 1) % (length_step + 1) == 0:
                if long_side == 'y':
                    if axis_y >= 0 and axis_x >= 0 or axis_y < 0 and axis_x >= 0:
                        waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                    else:
                        waypoints.append([waypoints[step][0], waypoints[step][1] - 1])
                elif long_side == 'x':
                    if axis_x >= 0 and axis_y >= 0 or axis_x < 0 and axis_y >= 0:
                        waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                    else:
                        waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
            else:
                if long_side == 'y':
                    if axis_y >= 0 and axis_x >= 0 or axis_y >= 0 and axis_x < 0:
                        waypoints.append([waypoints[step][0] + 1, waypoints[step][1]])
                    else:
                        waypoints.append([waypoints[step][0] - 1, waypoints[step][1]])
                elif long_side == 'x':
                    if axis_x >= 0 and axis_y >= 0 or axis_x >= 0 and axis_y < 0:
                        waypoints.append([waypoints[step][0], waypoints[step][1] + 1])
                    else:
                        waypoints.append([waypoints[step][0], waypoints[step][1] - 1])

        return waypoints[-1]