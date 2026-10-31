import time
from functools import wraps


def handle_db_errors(func):
    """Перехватывает ошибки базы данных и выводит понятные сообщения."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Вызывает функцию и обрабатывает возможные исключения."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")

        return None

    return wrapper


def confirm_action(action_name):
    """создаёт декоратор для подтверждения опасных операций"""

    def decorator(func):
        """оборачивает функцию запросом подтверждения"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            """выполняет операцию только после подтверждения"""
            answer = (
                input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
                .strip()
                .lower()
            )

            if answer != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """измеряет и выводит время выполнения функции"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Вызывает функцию и измеряет время её работы."""
        start_time = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.monotonic()
            elapsed_time = end_time - start_time

            print(f"Функция {func.__name__} выполнилась за {elapsed_time:.3f} секунд")

    return wrapper


def create_cacher():
    """создаёт кэш с помощью замыкания"""
    cache = {}

    def cache_result(key, value_func):
        """возвращает результат из кэша и сохраняет его"""
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result
