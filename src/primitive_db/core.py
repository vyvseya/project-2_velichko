from primitive_db.utils import load_table_data

VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """создает таблицу с проверокой столбцов
    и добавляет айди"""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not table_name.isidentifier():
        print(f"Некорректное имя таблицы: {table_name}. Попробуйте снова.")
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


def insert(metadata, table_name, values):
    """добавляет запись в таблицу с проверкой типов и генерацией ID"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name][1:]

    if len(values) != len(columns):
        print("Некорректное количество значений. Попробуйте снова.")
        return None

    valid_types = {"int": int, "str": str, "bool": bool}
    record = {}

    for column, value in zip(columns, values):
        name, data_type = column.split(":")
        expected_type = valid_types[data_type]

        if type(value) is not expected_type:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return None

        if data_type == "str" and not value.strip():
            print("Некорректное значение: пустая строка. Попробуйте снова.")
            return None

        record[name] = value

    table_data = load_table_data(table_name)

    new_id = max((row["ID"] for row in table_data), default=0) + 1
    record = {"ID": new_id, **record}

    table_data.append(record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


def select(table_data, where_clause=None):
    """возвращает все записи таблицы или записи, подходящие под условие"""
    if where_clause is None:
        return table_data

    return [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


def update(table_data, set_clause, where_clause):
    """обновляет поля записей, соответствующих заданному условию"""
    for row in select(table_data, where_clause):
        row.update(set_clause)

    return table_data


def delete(table_data, where_clause):
    """удаляет записи, соответствующие заданному условию"""
    if not where_clause:
        return table_data

    for row in select(table_data, where_clause):
        table_data.remove(row)

    return table_data
