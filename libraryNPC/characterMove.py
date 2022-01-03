import random


class CharacterMove:

    def _move_search_person(self, **kwargs):
        """ Глобальная цель поиска указанного персонажа. Базовая активность охотников за головами """
        finish_vertices = random.randrange(5000)
        # Проверка на возможность достичь точки
        _, success = self._path_world_vertices_a_star_algorithm(kwargs["vertices_dict"], self.vertices, finish_vertices)
        if success:
            self.action_stack.add_stack_element(self._move_global_path, "global_move")
            return False
        return False

    def _move_global_path(self, **kwargs):
        """
            Перемещение к удалённой точке. Во время перемещения постоянно определяет необходимость совершения
            активностей. FIXME Но пока просто ходит. Здесь же проверяет округу на наличие чужих следов.
        """
        result_search = self.investigation_checking_for_noticeable_traces(**kwargs)
        if result_search:
            if self.local_waypoints:
                self.path_local_move(kwargs["global_map"], kwargs["enemy_list"])
            else:
                self.path_calculate(kwargs["global_map"], kwargs["vertices_graph"], kwargs["vertices_dict"],
                                    kwargs["enemy_list"])
            return False
        else:  # result_search is None:
            self.bases_del_all_waypoints(**kwargs)
            self.action_stack.add_stack_element(self._investigation_action_calculations, "investigation")
            return None