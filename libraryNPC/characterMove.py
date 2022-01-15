import random
from libraryNPC.characterPathMove import PathMove


class CharacterMove(PathMove):

    def _move_search_person(self, **kwargs):
        """ Глобальная цель поиска указанного персонажа. Базовая активность охотников за головами """
        finish_vertices = random.randrange(5000)
        # Проверка на возможность достичь точки
        _, success = self._path_world_vertices_a_star_algorithm(kwargs["vertices_dict"], self.vertices, finish_vertices)
        if success:
            target = self.memory.add_memories("target", "move", position=finish_vertices, **kwargs)
            self.action_stack.add_stack_element(self.path_move, "global_move", target)
            return False
        return False

    def _move_global_path(self, **kwargs):
        """
            Перемещение к удалённой точке. Во время перемещения постоянно определяет необходимость совершения
            активностей. FIXME Но пока просто ходит. В данный момент не используется.
        """
        result_search = self.investigation_checking_for_noticeable_traces(**kwargs)
        if result_search:
            target = self.memory.add_memories("target", "move", position=result_search, **kwargs)
            self.action_stack.add_stack_element(self.path_move, "move", target)
            return False
        else:  # result_search is None:
            self.bases_del_all_waypoints(**kwargs)
            self.action_stack.add_stack_element(self._investigation_action_calculations, "investigation")
            return float("inf")
