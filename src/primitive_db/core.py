VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """Create a table; ID:int is prepended automatically.

    Returns updated metadata, or None on error (message is printed).
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    parsed = []
    for column in columns:
        name, sep, col_type = column.partition(":")
        if not sep or not name or col_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        if name == "ID":
            continue  # ID создается автоматом
        parsed.append((name, col_type))

    names = [name for name, _ in parsed]
    if len(set(names)) != len(names):
        print("Некорректное значение: повторяющиеся столбцы. Попробуйте снова.")
        return None

    all_columns = [("ID", "int"), *parsed]
    metadata[table_name] = {"columns": [f"{n}:{t}" for n, t in all_columns]}
    shown = ", ".join(f"{n}:{t}" for n, t in all_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {shown}')
    return metadata


def drop_table(metadata, table_name):
    """Drop a table. Returns updated metadata, or None on error."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Print all table names."""
    if not metadata:
        print("Таблиц нет.")
    for name in metadata:
        print(f"- {name}")
