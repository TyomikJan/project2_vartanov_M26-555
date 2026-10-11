import re
import shlex

import prompt
from prettytable import PrettyTable

from .constants import (
    CMD_CREATE_TABLE,
    CMD_DROP_TABLE,
    CMD_EXIT,
    CMD_HELP,
    CMD_LIST_TABLES,
    ID_COLUMN,
    META_FILE,
    TABLE_COMMANDS,
)
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
    validate_clause,
)
from .decorators import create_cacher, handle_db_errors
from .parser import parse_clause, parse_values
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_result = create_cacher()


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


FLAGS = re.I | re.S
PATTERNS = {
    "insert": re.compile(r"insert\s+into\s+(\w+)\s+values\s*\((.*)\)$", FLAGS),
    "select": re.compile(r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?$", FLAGS),
    "update": re.compile(r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)$", FLAGS),
    "delete": re.compile(r"delete\s+from\s+(\w+)\s+where\s+(.+)$", FLAGS),
    "info": re.compile(r"info\s+(\w+)$", FLAGS),
}


def bad_input(text):
    """Report an invalid input value."""
    print(f"Некорректное значение: {text}. Попробуйте снова.")


def table_exists(metadata, name):
    """Return True if the table exists, else print an error."""
    if name not in metadata:
        print(f'Ошибка: Таблица "{name}" не существует.')
        return False
    return True


def handle_insert(metadata, name, raw_values):
    """Parse and run the insert command."""
    result = insert(metadata, name, parse_values(raw_values), load_table_data(name))
    if result:
        data, new_id = result
        save_table_data(name, data)
        print(f'Запись с ID={new_id} успешно добавлена в таблицу "{name}".')


def handle_select(metadata, name, raw_where):
    """Parse, run (with caching) and print the select command."""
    where = parse_clause(raw_where) if raw_where else None
    if where and not validate_clause(metadata, name, where):
        return
    key = (name, tuple(sorted(where.items())) if where else None)
    rows = cache_result(key, lambda: select(load_table_data(name), where))
    columns = [c.split(":")[0] for c in metadata[name]["columns"]]
    table = PrettyTable(columns)
    for row in rows:
        table.add_row([row[c] for c in columns])
    print(table)


def handle_update(metadata, name, raw_set, raw_where):
    """Parse and run the update command."""
    set_clause, where = parse_clause(raw_set), parse_clause(raw_where)
    if ID_COLUMN in set_clause:
        print("Ошибка: ID изменять нельзя.")
        return
    if not (
        validate_clause(metadata, name, set_clause)
        and validate_clause(metadata, name, where)
    ):
        return
    data, ids = update(load_table_data(name), set_clause, where)
    if not ids:
        print("Записи не найдены.")
        return
    save_table_data(name, data)
    for record_id in ids:
        print(f'Запись с ID={record_id} в таблице "{name}" успешно обновлена.')


def handle_delete(metadata, name, raw_where):
    """Parse and run the delete command."""
    where = parse_clause(raw_where)
    if not validate_clause(metadata, name, where):
        return
    result = delete(load_table_data(name), where)
    if result is None:
        return
    data, ids = result
    if not ids:
        print("Записи не найдены.")
        return
    save_table_data(name, data)
    for record_id in ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{name}".')


def handle_info(metadata, name):
    """Print table columns and record count."""
    print(f"Таблица: {name}")
    print("Столбцы: " + ", ".join(metadata[name]["columns"]))
    print(f"Количество записей: {len(load_table_data(name))}")


DATA_HANDLERS = {
    "insert": handle_insert,
    "select": handle_select,
    "update": handle_update,
    "delete": handle_delete,
    "info": handle_info,
}


WRITE_COMMANDS = {"insert", "update", "delete"}


@handle_db_errors
def handle_data_command(metadata, command, text):
    """Run insert/select/update/delete/info."""
    match = PATTERNS[command].match(text)
    if not match:
        bad_input(text)
        return
    name = match[1]
    if not table_exists(metadata, name):
        return
    DATA_HANDLERS[command](metadata, name, *match.groups()[1:])
    if command in WRITE_COMMANDS:
        cache_result.clear()


def handle_table_command(metadata, command, params, text):
    """Run create_table/drop_table/list_tables."""
    if command == CMD_LIST_TABLES:
        list_tables(metadata)
    elif command == CMD_CREATE_TABLE and len(params) >= 2:
        result = create_table(metadata, params[0], params[1:])
        if result is not None:
            save_metadata(META_FILE, result)
    elif command == CMD_DROP_TABLE and len(params) == 1:
        result = drop_table(metadata, params[0])
        if result is not None:
            save_metadata(META_FILE, result)
            delete_table_data(params[0])
            cache_result.clear()
    else:
        bad_input(text)


def run():
    print("***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = prompt.string("\n>>>Введите команду: ").strip()
        except EOFError:
            print()
            break
        if not user_input:
            continue

        command = user_input.split()[0].lower()
        if command == CMD_EXIT:
            break
        elif command == CMD_HELP:
            print_help()
        elif command in DATA_HANDLERS:
            handle_data_command(metadata, command, user_input)
        elif command in TABLE_COMMANDS:
            try:
                params = shlex.split(user_input)[1:]
            except ValueError:
                bad_input(user_input)
                continue
            handle_table_command(metadata, command, params, user_input)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
