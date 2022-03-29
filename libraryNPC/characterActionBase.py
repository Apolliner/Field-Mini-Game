from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
from library.decorators import trace
"""
    Необходимые для всех типов активности действия
"""
class CharacterActionBase(Bases):
    @trace
    def action_base_activity_update(self, activity_positions, new_icon=None, new_type=None, new_description=None,
                                                                                            lifetime=None, **kwargs):
        """ Обновляет находящуюся в указанных координатах активность """
        global_position, local_position = self.bases_world_position_recalculation(activity_positions)

        activity_list = kwargs["activity_list"]
        for activity in activity_list:
            if activity.global_position == global_position and activity.local_position == local_position:
                if new_icon:
                    activity.icon = new_icon
                if new_type:
                    activity.type = new_type
                if new_description:
                    activity.description = new_description
                if lifetime:
                    activity.lifetime = lifetime
                return True

        return False

    @trace
    def action_base_animate_router(self, **kwargs):
        """ Отыгрывает указанную анимацию указанное количество шагов """
        animation_dict = {"look around":   "la",
                          "squat":         "sq",
                          "to stand":      "s",
                          "pistol":        "p",
                          "pistol fire":   "pf",
                          "stand create":  "sc",
                          "squat create":  "sqc",
                          }
        def _generator_action_base_animate(count_step, animations):
            for i in range(count_step):
                self.animation = animations
                yield False
            return True

        if not self.target.generator and (not self.target.payload or "animations" not in self.target.payload or
                                          not self.target.payload["animations"]):
            return self.inf_true
        print(F'self.target.payload["animations"] - {self.target.payload["animations"]}')

        if self.target.generator is None:
            animation_item = self.target.payload["animations"].pop(0)
            animation = animation_dict[animation_item["name"]]
            count_steps = animation_item["steps"]
            self.target.generator = _generator_action_base_animate(count_steps, animation)
            answer = next(self.target.generator, True)
        else:
            answer = next(self.target.generator, True)
        if answer == True:
            self.target.generator = None
            if self.target.payload["animations"]:
                answer = False
            else:
                return self.inf_true
        return answer

    def action_base_go_position(self, go_position, **kwargs):
        """ Передвижение в указанную позицию """
        target = self.memory.add_memories("target", "action_move", positions=[go_position], **kwargs)
        self.action_stack.add_stack_element(name="action_move", element=self.path_move, target=target)

    def action_base_set_animation(self, name_animation, steps_animation, **kwargs):
        """ Устанавливает указанную анимацию """
        payload = {"animations": [{"name": name_animation, "steps": steps_animation}]}
        target = self.memory.add_memories("target", "animation", payload=payload, **kwargs)
        self.action_stack.add_stack_element(name="animation", element=self.action_base_animate_router,
                                            target=target)
    @staticmethod
    def action_base_generator(func):
        """
        Декоратор генератора активности
        """
        def inner(self, *args, **kwargs):
            if self.target.generator is None:
                self.target.generator = func(self, *args, **kwargs)
            return self._action_base_use_generator(self)
        return inner

    def _action_base_use_generator(self):
        x = self.target.generator
        print(F"x - {x}")
        y = next(x, True)
        print(F"y - {y}")
        return y

