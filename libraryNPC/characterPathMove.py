from libraryNPC.characterPathBase import PathBase

class Path(PathBase):
    """
        Реализует перемещение в точку или зону доступности, содержащуюся в задаче.
    """

    def path_move(self, **kwargs):
        """
            Просто вызывается и само всё делает.
            Возвращает False если цель не достигнута и True если достигнута.
        """
        return False

    def _path_move_calculate(self, **kwargs):
        """
            Рассчитывает путь до тайла или до зоны доступности (в зависимости от того, что приходит из задачи)
        """
        ...

    def _path_move_global_waypoints_calculate(self, start_vertices, finish_vertices, **kwargs):
        """ Рассчитывает глобальные вейпоинты """
        ...

    def _path_move_local_waypoints_calculate(self, start_position, finish_position, **kwargs):
        """ Рассчитывает локальные вейпоинты """
        ...


