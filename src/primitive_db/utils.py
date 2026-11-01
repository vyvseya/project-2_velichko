import json

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """загружает метаданные из json
    или возврощает пустой словарь"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """сохраняет метаданные базы данных в json-файл"""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """загружает записи таблицы или возвращает пустой список"""
    filepath = DATA_DIR / f"{table_name}.json"

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """сохраняет записи таблицы в отдельный json-файл"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    filepath = DATA_DIR / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """удаляет json-файл с записями таблицы, если он сущ"""
    filepath = DATA_DIR / f"{table_name}.json"
    filepath.unlink(missing_ok=True)
