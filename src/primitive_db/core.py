VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """создает таблицу с проверокой столбцов
    и добавляет айди"""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not columns:
        print("Некорректное значение: отсутствуют столбцы. Попробуйте снова.")
        return metadata

    new_columns = ["ID:int"]
    column_names = set()

    for column in columns:
        name, separator, data_type = column.partition(":")

        if not name or separator != ":" or data_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        if name in column_names or (name == "ID" and data_type != "int"):
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_names.add(name)

        if name != "ID":
            new_columns.append(column)

    metadata[table_name] = new_columns

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(new_columns)}'
    )

    return metadata


def drop_table(metadata, table_name):
    """удаляет таблицу из мет, если онаа сущ"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata
