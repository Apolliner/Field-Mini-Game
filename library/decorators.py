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
