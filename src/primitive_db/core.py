from .constants import BOOL_TYPE, ID_COLUMN, INT_TYPE, VALID_TYPES
from .decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
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
        if name == ID_COLUMN:
            continue  # ID создается автоматом
        parsed.append((name, col_type))

    names = [name for name, _ in parsed]
    if len(set(names)) != len(names):
        print("Некорректное значение: повторяющиеся столбцы. Попробуйте снова.")
        return None

    all_columns = [(ID_COLUMN, INT_TYPE), *parsed]
    metadata[table_name] = {"columns": [f"{n}:{t}" for n, t in all_columns]}
    shown = ", ".join(f"{n}:{t}" for n, t in all_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {shown}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Drop a table. Returns updated metadata, or None on error."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Print all table names."""
    if not metadata:
        print("Таблиц нет.")
    for name in metadata:
        print(f"- {name}")


def _schema(metadata, table_name):
    """Return {column: type} for a table."""
    return dict(c.split(":") for c in metadata[table_name]["columns"])


def _check_type(value, col_type):
    """Check that value matches the column type."""
    if col_type == INT_TYPE:
        return isinstance(value, int) and not isinstance(value, bool)
    if col_type == BOOL_TYPE:
        return isinstance(value, bool)
    return isinstance(value, str)


@handle_db_errors
def validate_clause(metadata, table_name, clause):
    """Check column names and value types of a where/set clause."""
    schema = _schema(metadata, table_name)
    for column, value in clause.items():
        if column not in schema:
            print(f"Ошибка: Столбец {column} не существует.")
            return False
        if not _check_type(value, schema[column]):
            col_type = schema[column]
            print(f"Ошибка: Значение {value!r} не подходит для {column}:{col_type}.")
            return False
    return True


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Append a record; returns (table_data, new_id) or None on error."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = [c.split(":") for c in metadata[table_name]["columns"]][1:]
    if len(values) != len(columns):
        print(f"Ошибка: ожидается {len(columns)} значений, получено {len(values)}.")
        return None
    for (name, col_type), value in zip(columns, values):
        if not _check_type(value, col_type):
            print(f"Ошибка: Значение {value!r} не подходит для {name}:{col_type}.")
            return None
    new_id = max((r[ID_COLUMN] for r in table_data), default=0) + 1
    record = {ID_COLUMN: new_id}
    record.update({name: v for (name, _), v in zip(columns, values)})
    return [*table_data, record], new_id


def _matches(record, where_clause):
    return all(record.get(k) == v for k, v in where_clause.items())


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Return all records, or only those matching where_clause."""
    if not where_clause:
        return table_data
    return [r for r in table_data if _matches(r, where_clause)]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Returns (new_data, ids_of_changed_records)."""
    ids = []
    result = []
    for r in table_data:
        if _matches(r, where_clause):
            r = {**r, **set_clause}
            ids.append(r[ID_COLUMN])
        result.append(r)
    return result, ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Returns (new_data, ids_of_deleted_records)."""
    ids = [r[ID_COLUMN] for r in table_data if _matches(r, where_clause)]
    return [r for r in table_data if not _matches(r, where_clause)], ids
