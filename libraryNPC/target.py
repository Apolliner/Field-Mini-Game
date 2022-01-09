
class Target:
    """ Содержит описание задачи, выполняемой персонажем """
    chunk_size = 25
    def __init__(self, type, entity, position, create_step, lifetime, **payload):
        self.type = type
        self.entity = entity
        self.position = position
        self.create_step = create_step
        self.lifetime = lifetime
        self.payload = payload

    def get_position(self):
        """ Возвращает позицию из цели """
        if self.entity is not None and self.entity:
            return list(self.entity.world_position)
        return list(self.position)

    def get_vertices(self, global_map):
        """ Возвращает номер зоны доступности цели """
        if self.entity is not None:
            return self._return_vertices(self.entity.world_position, global_map)
        return self._return_vertices(self.position, global_map)

    def _return_vertices(self, world_position, global_map):
        """
            Принимает мировые координаты и global_map, возвращает номер зоны доступности цели.
        """
        global_position = [world_position[0] // self.chunk_size, world_position[1] // self.chunk_size]
        local_position = [world_position[0] % self.chunk_size, world_position[1] % self.chunk_size]
        return global_map[global_position[0]][global_position[1]].chunk[local_position[0]][local_position[1]].vertices

    @staticmethod
    def get_target():
        """ По запросу возвращает цель """  # FIXME Пока заглушка
        target_dict = {
                'move':{'type': 'move', 'entity': None, 'position': None, 'lifetime': 1000}
        }
        return Target(type=None, entity=None, position=None, create_step=None, lifetime=None)