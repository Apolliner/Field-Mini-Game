"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    РАСЧЁТ ПРОПУСКА ХОДА

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


class Interaction:
    """ Содержит описание взаимодействия. НЕ ИСПОЛЬЗУЕТСЯ"""

    def __init__(self, perform, whom, type_interaction, description):
        self.perform = perform
        self.whom = whom
        self.type = type_interaction
        self.description = description


def master_pass_step(person):
    """
        Считает пропуски хода для плавного перемещения персонажа
    """
    if person.pass_draw_move:
        person.person_pass_step = True
        person.enemy_pass_step = True
    else:
        person.person_pass_step = False
        person.enemy_pass_step = False


def all_pass_step_calculations(person, enemy_list, mode_action, interaction):
    """
        Рассчитывает пропуск хода персонажа и NPC и кем он осуществляется.
    """
    if mode_action == 'move':
        person.person_pass_step = 0
        person.enemy_pass_step = 0
    if mode_action == 'pointer':
        person.person_pass_step = 0
        person.enemy_pass_step = 1
    if mode_action == 'gun':
        person.person_pass_step = 0
        person.enemy_pass_step = 1


def new_step_calculation(enemy_list, person, step):
    """
        Считает когда начинается новый шаг
    """
    if not person.pointer_step and not person.pass_draw_move:
        step += 1
    return step
