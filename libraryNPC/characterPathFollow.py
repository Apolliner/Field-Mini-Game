from libraryNPC.characterPathBase import PathBase
from libraryNPC.bases import Bases


class PathFollow(PathBase, Bases):
    """
        Реализует следование персонажа
        При нахождении близко от цели, локальный поиск пути осуществлять игнорируя зоны доступности
        и с малым количеством циклов, так как его нужно регулярно перессчитывать
    """

    def _path_follow(self, **kwargs):
        """ Вызывается и само всё делает """
        target_position = self.target.get_position()
        remoteness = self.bases_path_length(self.world_position, target_position)
        if self.local_waypoints:
            finish_remoteness = self.bases_path_length(self.local_waypoints[-1], target_position)
            

