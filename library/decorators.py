import time


def timeit(func):
    """
    Декоратор. Считает время выполнения функции.
    """
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        if func.__name__ != "standard":
            print(time.time() - start)
        return result

    return inner


def trace(func):
    """
    Выводит вконсоль названия исполняемых функций
    """
    def inner(*args, **kwargs):
        if func.__name__ != "standard":
            print(func.__name__)
        result = func(*args, **kwargs)
        return result

    return inner

def action_base_generator(func):
    """
    Декоратор генератора активности
    """
    def inner(self, *args, **kwargs):
        if self.target.generator is None:
            self.target.generator = func(self, *args, **kwargs)
        return next(self.target.generator, True)
    return inner
