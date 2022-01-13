from libraryNPC.bases import Bases


class PathBase(Bases):
    """ Базовый класс передвижения, чтобы не пересекались методы разных типов передвижения """

    def _path_base_local_move(self, **kwargs):
        """ Реализует перемещение персонажа по локальным вейпоинтам """
        ...