from libraryNPC.bases import Bases
"""
    Логика действий персонажей
"""

class CharacterAction(Bases):
    def action_return_action(self):
        actions_dict = {
            "campfire": {
                "name": "campfire",
                "description": "",
                "stages": {
                    "search for a place": self._action_search_for_a_place,
                    "collect firewood": self._action_collect_firewood,
                    "arrange a fire pit": self._action_arrange_a_fire_pit,
                    "kindle campfire": self._action_kindle_campfire
                }
            }
        }

    def _action_func(self, **kwargs):
        pass

    def _action_search_for_a_place(self, **kwargs):
        """ Ищет подходящее место для костра """
        ...

    def _action_collect_firewood(self, **kwargs):
        """ 3 раза ищет дрова или ветки. Собирает их и приносит в одну точку """
        ...

    def _action_arrange_a_fire_pit(self, **kwargs):
        """ 3 раза ходит от дров до места установки костра. Каждый раз проводит действие над костром. """
        ...

    def _action_kindle_campfire(self, **kwargs):
        """ Проводит некоторое время производя действие над костром. Время определяется случайно """
        ...