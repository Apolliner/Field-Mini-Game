"""
    Проработать вопросы:
                        - Групповых действий
                        - Инвентарь
                        - Оружие
"""

class GoalSettingNPC:
    """
        Самостоятельное целеполагание.
        Проверка до выполнения действия из стека, на необходимость выполнения посторонних действий.
        В каждом случае возвращается список
    """
    def goal_setting_check_enemies(self) -> List:
        """ Проверка округи на наличие противников"""
        return []

    def goal_setting_get_danger_memory(self) -> List:
        """ Получение открытых элементов памяти об текущих опасностях """
        return []

    def goal_setting_check_need(self) -> List:
        """ Проверка потребности в лечении, еде, воде, отдыхе или уходе за оружием """

        needs_tuple = ("health", "hanger", "thirst", "fatigue")
        need_list = list()
        for need in needs_tuple:
            if getattr(self, need) < 25:
                need_list.append(need)
        
        return need_list

    def goal_setting_master(self):
        """ Место для основной логики проверки текущего состояния. Здесь проверяется состояние и назначаются задачи """
        enemies = self.goal_setting_check_enemies()
        if enemies is not None:
            pass
        danger_memories = self.goal_setting_get_danger_memory()
        if danger_memories is not None:
            pass
        if not (self.alarm and self.stealth and self.alertness):
            needs = self.goal_setting_check_need()
            if needs is not None:
                for need in needs:
                    if need == "fatigue":
                        target = self.memory.add_memories("action", "campfire")
                        self.action_stack.add_stack_element(name="action", element=self._action_stack_router,
                                                            target=target)
                    else:
                        target = self.memory.add_memories("test action", need)
                        self.action_stack.add_stack_element(name="test action", element=self._action_stack_router,
                                                            target=target)
                    return True
        return False
