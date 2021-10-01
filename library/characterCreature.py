import random
import logging
from library.characterBase import Character, CharacterAction
from library.characterPath import Path

class Creature(Character, Path):
    """
    Мелкие, необсчитываемые за кадром существа и противники

    РЕАЛИЗОВАТЬ:
    1) Изменение режима передвижения с полёта, на хождение по земле.
    2) Изменение высоты полёта птиц, их иконки и тени под ними
    """

    def __init__(self, global_position, local_position, name, name_npc, icon, type, activity_map,
                 person_description, speed, deactivation_tiles, fly, description, type_npc):
        super().__init__(self, global_position, local_position, name, name_npc, icon, type, description, type_npc)

        self.fly = fly  # Полёт                                 bool
        self.steps_to_despawn = 30  # Шагов до удаления                     int
        self.deactivation_tiles = deactivation_tiles  # Тайлы удаления                        tuple

    def master_character_calculation(self):
        """
            Обработка действий существа на текущем шаге
        """
        # Подготовка
        self.character_check_all_position()  # Родительский метод
        self.character_reset_at_the_beginning()  # Родительский метод

        # Рассчёт действий
        action = self.creature_checking_the_situation()

        # Совершение действий
        if action.type == 'move':
            self.creature_move_calculations(action)

        elif action.type == 'activity':
            self.creature_activity_calculations(action)

        elif action.type == 'attack':
            self.creature_attack_calculations(action)

        elif action.type == 'getting_damaged':
            self.creature_getting_damaged_calculations(action)

        elif action.type == 'extra':
            self.creature_extra_action_calculations(action)

        else:
            pass

        # Рассчёт последствий
        self.creature_consequences_calculation()

    def creature_checking_the_situation(self):
        """
            Оценивает ситуацию для существа
        """
        return CharacterAction('move', 'escape')

    def creature_move_calculations(self, action, activity_list, step):
        """
            Передвижение существа   ----- Можно заполнить уже готовой логикой из старой версии -----
        """
        pass

    def creature_activity_calculations(self, action):
        """
            Выполнение и оставление активностей на карте, связанных с удовлетворением потребностей
            или праздным времяпрепровожденим.
        """
        pass

    def creature_attack_calculations(self, action):
        """ Действия существа при атаке """
        pass

    def creature_getting_damaged_calculations(self, action):
        """ Получение повреждений существом """
        pass

    def creature_extra_action_calculations(self, action):
        """ Особенные действия существа """
        pass

    def creature_consequences_calculation(self):
        """ Рассчёт последствий действий существа """
        pass

    def if_deactivation_tiles(self, global_map):
        """
            Проверяет находится ли существо на тайле деактивации и выбрасывает шанс на диактивацию
        """
        if global_map[self.global_position[0]][self.global_position[1]].chunk[self.local_position[0]][
            self.local_position[1]].icon in self.deactivation_tiles:
            if random.randrange(20) // 18 > 0:
                self.delete = True

    def in_dynamic_chunk(self, person):
        """
            Рассчитывает находится ли существо на динамическом чанке
        """
        if self.global_position in (
        person.assemblage_point, [person.assemblage_point[0] + 1, person.assemblage_point[1]],
        [person.assemblage_point[0], person.assemblage_point[1] + 1],
        [person.assemblage_point[0] + 1, person.assemblage_point[1] + 1]):
            self.steps_to_despawn = 30
        else:
            self.steps_to_despawn -= 1
        if self.steps_to_despawn <= 0:
            self.delete = True
        logging.debug(f"self.name_npc - {self.name_npc}, self.steps_to_despawn - {self.steps_to_despawn}, "
                      f"self.delete - {self.delete}")

    def simple_move(self, chunk_size, global_map):
        """
            Хаотичное рандомное движение с учётом препятствий
        """
        global_position_y = self.global_position[0]
        global_position_x = self.global_position[1]
        tile = global_map[global_position_y][global_position_x].chunk[self.local_position[0]][self.local_position[1]]
        if random.randrange(2) == 0:
            axis_y = random.randrange(-1, 2)
            axis_x = 0
        else:
            axis_y = 0
            axis_x = random.randrange(-1, 2)
        local_position_y = self.local_position[0] + axis_y
        if local_position_y > chunk_size - 1:
            global_position_y += 1
            local_position_y = 0
        elif local_position_y < 0:
            global_position_y -= 1
            local_position_y = chunk_size - 1

        local_position_x = self.local_position[1] + axis_x
        if local_position_x > chunk_size - 1:
            global_position_x += 1
            local_position_x = 0
        elif local_position_x < 0:
            global_position_x -= 1
            local_position_x = chunk_size - 1

        if 0 > global_position_y < chunk_size - 1:
            global_position_y = 0
            self.delete = True
        if 0 > global_position_x < chunk_size - 1:
            global_position_x = 0
            self.delete = True

        go_tile = global_map[global_position_y][global_position_x].chunk[local_position_y][local_position_x]

        if (tile.level == go_tile.level or tile.stairs or go_tile.stairs) and not go_tile.icon in ('~', '▲'):
            if axis_y == -1:
                self.direction = 'up'
            elif axis_y == 1:
                self.direction = 'down'
            elif axis_x == -1:
                self.direction = 'left'
            elif axis_x == 1:
                self.direction = 'right'
            self.global_position = [global_position_y, global_position_x]
            self.local_position = [local_position_y, local_position_x]

    def fly_simple_move(self, chunk_size):
        """
            Хаотичное рандомное движение без учёта препятствий
        """
        global_position_y = self.global_position[0]
        global_position_x = self.global_position[1]
        if random.randrange(2) == 0:
            axis_y = random.randrange(-1, 2)
            axis_x = 0
        else:
            axis_y = 0
            axis_x = random.randrange(-1, 2)
        local_position_y = self.local_position[0] + axis_y
        if local_position_y > chunk_size - 1:
            global_position_y += 1
            local_position_y = 0
        elif local_position_y < 0:
            global_position_y -= 1
            local_position_y = chunk_size - 1

        local_position_x = self.local_position[1] + axis_x
        if local_position_x > chunk_size - 1:
            global_position_x += 1
            local_position_x = 0
        elif local_position_x < 0:
            global_position_x -= 1
            local_position_x = chunk_size - 1

        if 0 > global_position_y < chunk_size - 1:
            global_position_y = 0
            self.delete = True
        if 0 > global_position_x < chunk_size - 1:
            global_position_x = 0
            self.delete = True

        if axis_y == -1:
            self.direction = 'up'
        elif axis_y == 1:
            self.direction = 'down'
        elif axis_x == -1:
            self.direction = 'left'
        elif axis_x == 1:
            self.direction = 'right'

        self.global_position = [global_position_y, global_position_x]
        self.local_position = [local_position_y, local_position_x]