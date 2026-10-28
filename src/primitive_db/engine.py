import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """выводит справку по доступным командам базы данных"""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def run():
    """запускает цикл команд и сохраняет изменения таблиц в json."""
    print_help()

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

                drop_table(metadata, args[0])

            case "list_tables":
                if args:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

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
