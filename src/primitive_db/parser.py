import json
import re


def parse_value(value):
    """преобразует текстовое значение в int, str или bool"""
    value = value.strip()

    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        result = value[1:-1]

        if not result:
            raise ValueError("Пустая строка недопустима.")

        return result

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    if re.fullmatch(r"-?\d+", value):
        return int(value)

    raise ValueError(f"Некорректное значение: {value}.")


def parse_condition(expression):
    """разбирает условие вида 'столбец = значение' в словарь"""
    column, separator, value = expression.partition("=")

    column = column.strip()

    if not separator or not column.isidentifier():
        raise ValueError(f"Некорректное условие: {expression}.")

    return {column: parse_value(value)}


def parse_values(expression):
    """преобразует значения команды insert в список"""
    expression = expression.strip()

    if not (expression.startswith("(") and expression.endswith(")")):
        raise ValueError(f"Некорректное значение: {expression}.")

    try:
        values = json.loads(f"[{expression[1:-1]}]")
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректное значение: {expression}.") from error

    for value in values:
        if type(value) not in (str, int, bool):
            raise ValueError(f"Некорректное значение: {value}.")

        if isinstance(value, str) and not value.strip():
            raise ValueError("Некорректное значение: пустая строка.")

    return values
