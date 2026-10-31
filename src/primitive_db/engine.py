import json
import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"


def print_help():
    """выводит справку по командам управления таблицами и записями"""
    print("\n***База данных***")

    print("\nУправление таблицами:")
    print(
        "create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу"
    )
    print("list_tables - показать список всех таблиц")
    print("drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print(
        "insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - добавить запись"
    )
    print(
        "select from <имя_таблицы> where "
        "<столбец> = <значение> - найти записи по условию"
    )
    print("select from <имя_таблицы> - показать все записи")
    print(
        "update <имя_таблицы> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
    )
    print("delete from <имя_таблицы> where <столбец> = <значение> - удалить записи")
    print("info <имя_таблицы> - информация о таблице")

    print("\nОбщие команды:")
    print("help - справочная информация")
    print("exit - выход из программы")


def run():
    """запускает цикл команд и сохраняет изменения таблиц в json"""
    print_help()

    cache_result = create_cacher()

    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string("\n>>>Введите команду: ")

        try:
            parts = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not parts:
            continue

        command, *args = parts
        old_metadata = metadata.copy()

        match command:
            case "create_table":
                if len(args) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name, *columns = args
                create_table(metadata, table_name, columns)

            case "drop_table":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name = args[0]

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                result = drop_table(metadata, table_name)

                if result is not None:
                    delete_table_data(table_name)

            case "list_tables":
                if args:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            case "insert":
                match_result = re.fullmatch(
                    r"insert\s+into\s+(\S+)\s+values\s*(\(.*\))",
                    user_input.strip(),
                )

                if match_result is None:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name, raw_values = match_result.groups()

                try:
                    values = parse_values(raw_values)
                except ValueError as error:
                    print(f"{error} Попробуйте снова.")
                    continue

                table_data = insert(metadata, table_name, values)

                if table_data is not None:
                    save_table_data(table_name, table_data)

            case "select":
                match_result = re.fullmatch(
                    r"select\s+from\s+(\S+)(?:\s+where\s+(.+))?",
                    user_input.strip(),
                )

                if match_result is None:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name, raw_condition = match_result.groups()

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                where_clause = None

                if raw_condition is not None:
                    try:
                        where_clause = parse_condition(raw_condition)
                    except ValueError as error:
                        print(f"{error} Попробуйте снова.")
                        continue

                    column_name, value = next(iter(where_clause.items()))
                    column_types = {
                        name: data_type
                        for name, data_type in (
                            column.split(":") for column in metadata[table_name]
                        )
                    }

                    expected_types = {"int": int, "str": str, "bool": bool}

                    if (
                        column_name not in column_types
                        or type(value) is not expected_types[column_types[column_name]]
                    ):
                        print(
                            f"Некорректное значение: {raw_condition}. Попробуйте снова."
                        )
                        continue

                table_data = load_table_data(table_name)

                cache_key = (
                    table_name,
                    json.dumps(where_clause, sort_keys=True),
                    json.dumps(table_data, sort_keys=True),
                )

                results = cache_result(
                    cache_key,
                    lambda: select(table_data, where_clause),
                )

                table = PrettyTable()
                table.field_names = [
                    column.split(":")[0] for column in metadata[table_name]
                ]

                for row in results:
                    table.add_row([row[name] for name in table.field_names])

                print(table)

            case "update":
                match_result = re.fullmatch(
                    r"update\s+(\S+)\s+set\s+(.+?)\s+where\s+(.+)",
                    user_input.strip(),
                )

                if match_result is None:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name, raw_set, raw_where = match_result.groups()

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                try:
                    set_clause = parse_condition(raw_set)
                    where_clause = parse_condition(raw_where)
                except ValueError as error:
                    print(f"{error} Попробуйте снова.")
                    continue

                column_types = dict(
                    column.split(":") for column in metadata[table_name]
                )
                valid_types = {"int": int, "str": str, "bool": bool}

                set_column, set_value = next(iter(set_clause.items()))
                where_column, where_value = next(iter(where_clause.items()))

                if (
                    set_column == "ID"
                    or set_column not in column_types
                    or where_column not in column_types
                ):
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                if (
                    type(set_value) is not valid_types[column_types[set_column]]
                    or type(where_value) is not valid_types[column_types[where_column]]
                ):
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_data = load_table_data(table_name)
                matching_rows = select(table_data, where_clause)

                if not matching_rows:
                    print("Записи по указанному условию не найдены.")
                    continue

                updated_ids = [row["ID"] for row in matching_rows]

                update(table_data, set_clause, where_clause)
                save_table_data(table_name, table_data)

                for record_id in updated_ids:
                    print(
                        f"Запись с ID={record_id} в таблице "
                        f'"{table_name}" успешно обновлена.'
                    )

            case "delete":
                match_result = re.fullmatch(
                    r"delete\s+from\s+(\S+)\s+where\s+(.+)",
                    user_input.strip(),
                )

                if match_result is None:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name, raw_where = match_result.groups()

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                try:
                    where_clause = parse_condition(raw_where)
                except ValueError as error:
                    print(f"{error} Попробуйте снова.")
                    continue

                column_types = dict(
                    column.split(":") for column in metadata[table_name]
                )
                valid_types = {"int": int, "str": str, "bool": bool}

                column_name, value = next(iter(where_clause.items()))

                if (
                    column_name not in column_types
                    or type(value) is not valid_types[column_types[column_name]]
                ):
                    print(f"Некорректное значение: {raw_where}. Попробуйте снова.")
                    continue

                table_data = load_table_data(table_name)
                matching_rows = select(table_data, where_clause)

                if not matching_rows:
                    print("Записи по указанному условию не найдены.")
                    continue

                deleted_ids = [row["ID"] for row in matching_rows]

                result = delete(table_data, where_clause)

                if result is None:
                    continue

                save_table_data(table_name, result)

                for record_id in deleted_ids:
                    print(
                        f"Запись с ID={record_id} успешно удалена "
                        f'из таблицы "{table_name}".'
                    )

            case "info":
                if len(args) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                table_name = args[0]

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(table_name)

                print(f"Таблица: {table_name}")
                print(f"Столбцы: {', '.join(metadata[table_name])}")
                print(f"Количество записей: {len(table_data)}")

            case "help":
                if args:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                print_help()

            case "exit":
                if args:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                break

            case _:
                print(f"Функции {command} нет. Попробуйте снова.")

        if metadata != old_metadata:
            save_metadata(METADATA_FILE, metadata)
