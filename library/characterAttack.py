from library.bases import Bases


class CharacterAttack(Bases):

    def attack_line_waypoints_calculation(self, start_point, finish_point, limiter=False):
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

    def attack_check_firing_line(self, global_map):
        """ Проверяет линию стрельбы на наличие препятствий. Возвращает свободно ли на линии стрельбы"""
        # Получение прямой линии между персонажами
        line_tiles = self.attack_line_waypoints_calculation(self.world_position, self.target.get_position())
        # Проверяет наличие непроходимых тайлов на линии или увеличения высоты между персонажами
        start_tile = self.bases_world_tile(global_map, self.world_position)
        finish_tile = self.bases_world_tile(global_map, self.target.get_position())
        for line_tile in line_tiles:
            tile = self.bases_world_tile(global_map, line_tile)
            # Если есть высота выше высоты персонажа # Если это непреодолимый тайл и он не является водой
            if tile.level > start_tile.level or (tile.vertices == -1 and tile.icon not in ("~", "f")):
                return False
        return True

    def attack_npc_fire_gun(self, global_map):
        """ Стрельба NPC из оружия """
        if self.attack_check_firing_line(self, global_map):
            pass