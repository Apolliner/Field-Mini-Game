from libraryNPC.bases import Bases
from library.tilesDicts import dry, firewood, stones, water
from library.decorators import trace
"""
    Необходимые для всех типов активности действия
"""
class CharacterActionBase(Bases):

    def action_base_animate(self, **kwargs):
        """ Отыгрывает указанную анимацию указанное количество шагов """
        # FIXME пока для теста просто приседание на 5 шагов. Потом нужно будет сделать полноценный роутер
        def _generator_action_base_animate():
            for _ in range(5):
                self.animation = 'sq'
                yield False
            self.animation = 'sq'
            return True
        if self.target.generator is None:
            self.target.generator = _generator_action_base_animate()
        return next(self.target.generator, True)