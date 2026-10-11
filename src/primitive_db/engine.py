import shlex

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = input("\n>>>Введите команду: ")
        except EOFError:
            print()
            break

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        if not args:
            continue

        command, params = args[0], args[1:]
        match command:
            case "exit":
                break
            case "help":
                print_help()
            case "list_tables":
                list_tables(metadata)
            case "create_table":
                if len(params) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                result = create_table(metadata, params[0], params[1:])
                if result is not None:
                    save_metadata(META_FILE, result)
            case "drop_table":
                if len(params) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                result = drop_table(metadata, params[0])
                if result is not None:
                    save_metadata(META_FILE, result)
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
