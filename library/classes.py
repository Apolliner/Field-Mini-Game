import pickle
import copy


class World:
    """ Содержит в себе описание текущего состояния игрового мира """

    def __init__(self):
        self.npc_path_calculation = False  # Считал ли какой-либо NPC глобальный или локальный путь на этом шаге


class Person:
    """
        Содержит в себе глобальное местоположение персонажа, расположение в пределах загруженного
        участка карты и координаты используемых чанков
    """
    __slots__ = (
    'name', 'assemblage_point', 'dynamic', 'chunks_use_map', 'pointer', 'gun', 'global_position', 'number_chunk',
    'environment_temperature', 'person_temperature', 'person_pass_step', 'enemy_pass_step',
    'speed', 'test_visible', 'level', 'vertices', 'local_position', 'direction', 'pass_draw_move',
    'recalculating_the_display', 'type',
    'icon', 'pointer_step', 'zone_relationships', 'activating_spawn', 'world_position')

    def __init__(self, assemblage_point: list, dynamic: list, chunks_use_map: list, pointer: list, gun: list):
        self.name = 'person'
        self.assemblage_point = assemblage_point
        self.dynamic = dynamic
        self.chunks_use_map = chunks_use_map
        self.pointer = pointer
        self.gun = gun
        self.global_position = assemblage_point
        self.number_chunk = 0
        self.environment_temperature = 36.6
        self.person_temperature = 36.6
        self.person_pass_step = 0
        self.enemy_pass_step = 0
        self.speed = 1
        self.test_visible = False
        self.level = 0
        self.vertices = 0
        self.local_position = dynamic
        self.direction = 'center'
        self.pass_draw_move = 0
        self.recalculating_the_display = True  # Перессчёт игрового экрана
        self.type = '0'
        self.icon = '☺'
        self.pointer_step = False
        self.zone_relationships = []
        self.activating_spawn = False
        self.world_position = [0, 0]  # общемировое тайловое положение

    def world_position_calculate(self, chunk_size):
        """ Рассчитывает глобальные координаты от центра мира """
        self.world_position = [self.local_position[0] + (self.global_position[0]) * (chunk_size),
                               self.local_position[1] + (self.global_position[1]) * (chunk_size)]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["assemblage_point"] = self.assemblage_point
        state["dynamic"] = self.dynamic
        state["chunks_use_map"] = self.chunks_use_map
        state["pointer"] = self.pointer
        state["gun"] = self.gun
        state["global_position"] = self.global_position
        state["number_chunk"] = self.number_chunk
        state["environment_temperature"] = self.environment_temperature
        state["person_temperature"] = self.person_temperature
        state["person_pass_step"] = self.person_pass_step
        state["enemy_pass_step"] = self.enemy_pass_step
        state["speed"] = self.speed
        state["test_visible"] = self.test_visible
        state["level"] = self.level
        state["vertices"] = self.vertices
        state["local_position"] = self.local_position
        state["direction"] = self.direction
        state["pass_draw_move"] = self.pass_draw_move
        state["recalculating_the_display"] = self.recalculating_the_display
        state["type"] = self.type
        state["icon"] = self.icon
        state["pointer_step"] = self.pointer_step
        state["zone_relationships"] = self.zone_relationships
        state["activating_spawn"] = self.activating_spawn
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.assemblage_point = state["assemblage_point"]
        self.dynamic = state["dynamic"]
        self.chunks_use_map = state["chunks_use_map"]
        self.pointer = state["pointer"]
        self.gun = state["gun"]
        self.global_position = state["global_position"]
        self.number_chunk = state["number_chunk"]
        self.environment_temperature = state["environment_temperature"]
        self.person_temperature = state["person_temperature"]
        self.person_pass_step = state["person_pass_step"]
        self.enemy_pass_step = state["enemy_pass_step"]
        self.speed = state["speed"]
        self.test_visible = state["test_visible"]
        self.level = state["level"]
        self.vertices = state["vertices"]
        self.local_position = state["local_position"]
        self.direction = state["direction"]
        self.pass_draw_move = state["pass_draw_move"]
        self.recalculating_the_display = state["recalculating_the_display"]
        self.type = state["type"]
        self.icon = state["icon"]
        self.pointer_step = state["pointer_step"]
        self.zone_relationships = state["zone_relationships"]
        self.activating_spawn = state["activating_spawn"]

    def check_local_position(self):
        local_position = []
        if self.dynamic[0] > len(self.chunks_use_map) // 2 - 1:
            local_position.append(self.dynamic[0] - len(self.chunks_use_map) // 2)
        else:
            local_position.append(self.dynamic[0])

        if self.dynamic[1] > len(self.chunks_use_map) // 2 - 1:
            local_position.append(self.dynamic[1] - len(self.chunks_use_map) // 2)
        else:
            local_position.append(self.dynamic[1])
        self.local_position = local_position

    def global_position_calculation(self, chank_size):
        """
            Рассчитывает глобальное положение по положению динамического чанка и положению внутри его
            Выдаёт глобальные координаты и номер чанка, в котором сейчас находится игрок
            Номера чанков выглядят так: 0 1
                                        2 3
        """

        if self.dynamic[0] < chank_size > self.dynamic[1]:
            self.global_position = self.assemblage_point
            self.number_chunk = 0
        elif self.dynamic[0] < chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0], self.assemblage_point[1] + 1]
            self.number_chunk = 1
        elif self.dynamic[0] >= chank_size > self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1]]
            self.number_chunk = 2
        elif self.dynamic[0] >= chank_size <= self.dynamic[1]:
            self.global_position = [self.assemblage_point[0] + 1, self.assemblage_point[1] + 1]
            self.number_chunk = 3


class Interfase:
    """ Содержит элементы для последующего вывода на экран """

    def __init__(self, game_field, biom_map, minimap_on):
        self.game_field = game_field
        self.biom_map = biom_map
        self.minimap_on = minimap_on
        self.point_to_draw = [0, 0]


class Location:
    """ Содержит описание локации """
    __slots__ = ('name', 'temperature', 'chunk', 'icon', 'price_move', 'vertices', 'position')
    def __init__(self, name:str, temperature:float, chunk:list, icon:str, price_move:int, position):
        self.name = name
        self.temperature = temperature
        self.chunk = chunk
        self.icon = icon
        self.price_move = price_move
        self.vertices = []
        self.position = position
    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["temperature"] = self.temperature
        state["chunk"] = pickle.dumps(self.chunk)
        state["icon"] = self.icon
        state["price_move"] = self.price_move
        state["vertices"] = self.vertices
        state["position"] = self.position
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.temperature = state["temperature"]
        self.chunk = pickle.loads(state["chunk"])
        self.icon = state["icon"]
        self.price_move = state["price_move"]
        self.vertices = state["vertices"]
        self.position = state["position"]


class Tile:
    """ Содержит изображение, описание, особое содержание тайла, стоимость передвижения, тип, высоту и лестницу """
    __slots__ = (
    'icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices', 'world_vertices')

    def __init__(self, icon):
        self.icon = icon
        self.description = self.getting_attributes(icon, 0)
        self.list_of_features = []
        self.price_move = self.getting_attributes(icon, 1)
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1
        self.world_vertices = -2

    def getting_attributes(self, icon, number):
        ground_dict = {
            'j': ['бархан',             1],
            's': ['ракушка',            1],
            '.': ['горячий песок',      1],
            ',': ['жухлая трава',       1],
            'o': ['валун',              15],
            'A': ['холм',               15],
            '▲': ['скала',              20],
            'i': ['кактус',             1],
            ':': ['солончак',           1],
            ';': ['солончак',           1],
            '„': ['трава',              1],
            'u': ['высокая трава',      1],
            'ü': ['колючая трава',      10],
            'F': ['чахлое дерево',      1],
            'P': ['раскидистое дерево', 1],
            '~': ['вода',               20],
            '`': ['солёная вода',       20],
            'f': ['брод',               7],
            'C': ['каньон',             7],
            '??': ['ничего',            10],
        }
        return ground_dict[icon][number]

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["icon"] = self.icon
        state["description"] = self.description
        state["list_of_features"] = self.list_of_features
        state["price_move"] = self.price_move
        state["type"] = self.type
        state["level"] = self.level
        state["stairs"] = self.stairs
        state["vertices"] = self.vertices
        state["world_vertices"] = self.world_vertices
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.icon = state["icon"]
        self.description = state["description"]
        self.list_of_features = state["list_of_features"]
        self.price_move = state["price_move"]
        self.type = state["type"]
        self.level = state["level"]
        self.stairs = state["stairs"]
        self.vertices = state["vertices"]
        self.world_vertices = state["world_vertices"]


class Tile_minimap:
    """ Содержит изображение, описание, особое содержание тайла миникарты"""
    __slots__ = (
    'icon', 'description', 'list_of_features', 'price_move', 'type', 'level', 'stairs', 'vertices', 'temperature')

    def __init__(self, icon, name, price_move, temperature):
        self.icon = icon
        self.description = name
        self.list_of_features = []
        self.price_move = price_move
        self.temperature = temperature
        self.type = '0'
        self.level = 0
        self.stairs = False
        self.vertices = -1

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["icon"] = self.icon
        state["description"] = self.description
        state["list_of_features"] = self.list_of_features
        state["price_move"] = self.price_move
        state["temperature"] = self.temperature
        state["type"] = self.type
        state["level"] = self.level
        state["stairs"] = self.stairs
        state["vertices"] = self.vertices

        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.icon = state["icon"]
        self.description = state["description"]
        self.list_of_features = state["list_of_features"]
        self.price_move = state["price_move"]
        self.temperature = state["temperature"]
        self.type = state["type"]
        self.level = state["level"]
        self.stairs = state["stairs"]
        self.vertices = state["vertices"]


class Global_interact:
    """ Описание глобального события """
    def __init__(self, name, description, global_position, local_position):
        self.name = name
        self.description = description
        self.global_position = global_position
        self.local_position = local_position
        self.step = 0


class Action_in_map:
    """ Содержит в себе описание активности и срок её жизни """
    __slots__ = ('name', 'icon', 'description', 'lifetime', 'birth', 'global_position', 'local_position', 'caused',
                 'lifetime_description', 'visible', 'type', 'level')

    def __init__(self, name, birth, position_npc, local_position, chunk_size, caused):
        self.name = name
        self.icon = self.action_dict(0)
        self.lifetime = self.action_dict(2)
        self.birth = birth
        self.global_position = copy.deepcopy(position_npc)
        self.local_position = local_position  # [dynamic_position[0]%chunk_size, dynamic_position[1]%chunk_size]
        self.caused = caused
        self.lifetime_description = ''
        self.description = f'{self.action_dict(1)} похоже на {self.caused}'
        self.visible = self.action_dict(3)
        self.type = '0'
        self.level = 0

    def __getstate__(self) -> dict:
        """ Сохранение класса """
        state = {}
        state["name"] = self.name
        state["icon"] = self.icon
        state["lifetime"] = self.lifetime
        state["birth"] = self.birth
        state["global_position"] = self.global_position
        state["local_position"] = self.local_position
        state["global_position"] = self.global_position
        state["caused"] = self.caused
        state["lifetime_description"] = self.lifetime_description
        state["description"] = self.description
        state["visible"] = self.visible
        state["type"] = self.type
        state["level"] = self.level
        return state

    def __setstate__(self, state: dict):
        """ Восстановление класса """
        self.name = state["name"]
        self.icon = state["icon"]
        self.lifetime = state["lifetime"]
        self.birth = state["birth"]
        self.global_position = state["global_position"]
        self.local_position = state["local_position"]
        self.global_position = state["global_position"]
        self.caused = state["caused"]
        self.lifetime_description = state["lifetime_description"]
        self.description = state["description"]
        self.visible = state["visible"]
        self.type = state["type"]
        self.level = state["level"]

    def all_description(self):
        self.description = f'{self.lifetime_description} {self.action_dict(1)} похоже на {self.caused}'

    def action_dict(self, number):
        """ Принимает название активности, возвращает её иконку, описание и срок жизни"""

        action_dict = {
            'camp': ['/', 'следы лагеря', 150, True],
            'bonfire': ['+', 'следы костра', 150, True],
            'rest_stop': ['№', 'следы остановки человека', 150, True],
            'horse_tracks': ['%', 'следы лошади', 150, True],
            'human_tracks': ['8', 'следы человека', 150, True],
            'animal_traces': ['@', 'следы зверя', 150, True],
            'gnawed bones': ['#', 'обглоданные зверем кости', 500, True],
            'defecate': ['&', 'справленная нужда', 150, True],
            'animal_rest_stop': ['$', 'следы животной лежанки', 150, True],
            'dead_man': ['D', 'мёртвый человек', 1000, True],
            'test_beacon': ['B', 'маяк для теста', 1000, True],
            'unknown': ['?', 'неизвестно', 150, True],
            'faint_footprints': ['=', 'слабые следы', 50, False],
            'waypoint': ['w', 'вейпоинт', 50, False],
            'explosion': ['e', 'взрыв', 1, True],
            'dust': ['d', 'пыль', 10, True],
        }
        if self.name in action_dict:
            return action_dict[self.name][number]
        else:
            return action_dict['unknown'][number]

    def lifetime_description_calculation(self, step):
        if step < (self.birth + self.lifetime // 3):
            self.lifetime_description = f'свежие [{self.birth + self.lifetime - step}]'
        elif step > (self.birth + (self.lifetime // 3) * 2):
            self.lifetime_description = f'старые [{self.birth + self.lifetime - step}]'
        else:
            self.lifetime_description = f'[{self.birth + self.lifetime - step}]'