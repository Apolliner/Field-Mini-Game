import time


def timeit(func):
    """
    Декоратор. Считает время выполнения функции.
    """
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time() - start)
        return result

    return inner


def trace(funk):
    """
    Выводит вконсоль названия исполняемых функций
    """
    def inner(*args, **kwargs):
        print(funk.__name__)
        result = funk(*args, **kwargs)
        return result

    return inner
