# primitive-db

## Управление таблицами

Примитивная консольная база данных: таблицы, CRUD-операции, JSON-хранилище.

Установка и запуск:

```bash
uv tool install .   # или: uv sync && uv run database
database
```

Команды:

- `create_table <имя> <столбец:тип> ...` — создать таблицу (типы: `int`, `str`, `bool`; столбец `ID:int` добавляется автоматически)
- `list_tables` — список таблиц
- `drop_table <имя>` — удалить таблицу
- `help` — справка, `exit` — выход

Метаданные хранятся в `db_meta.json`.

Пример:

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```

Аскинема: [![asciicast](https://asciinema.org/a/0bddfHIsYHCWpkNF.svg)](https://asciinema.org/a/0bddfHIsYHCWpkNF)

## CRUD-операции

Данные таблицы `users` хранятся в `data/users.json`. Строки всегда пишутся в кавычках, `bool` — `true`/`false`. Значение `ID` генерируется автоматически (max + 1), в `insert` его указывать не нужно.

- `insert into <таблица> values (<знач1>, <знач2>, ...)` — добавить запись
- `select from <таблица> [where <столбец> = <значение>]` — прочитать записи (вывод через PrettyTable)
- `update <таблица> set <столбец> = <значение>[, ...] where <столбец> = <значение>` — обновить записи
- `delete from <таблица> where <столбец> = <значение>` — удалить записи
- `info <таблица>` — столбцы и количество записей

Пример:

```
>>>Введите команду: insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>>Введите команду: select from users where age = 28
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+
```

Аскинема с демонстрацией CRUD: [![asciicast](https://asciinema.org/a/axrnCVaVPLtbNzNn.svg)](https://asciinema.org/a/axrnCVaVPLtbNzNn)

## Декораторы и замыкания

Модуль `src/primitive_db/decorators.py`:

- `handle_db_errors` — перехватывает `FileNotFoundError`, `KeyError`, `ValueError` и прочие исключения, печатает сообщение вместо падения. Применён ко всем функциям `core` и к обработчику команд данных.
- `confirm_action(action_name)` — запрашивает подтверждение `[y/n]` перед опасной операцией; при любом ответе, кроме `y`, операция отменяется. Применён к `drop_table` и `delete`.
- `log_time` — выводит время выполнения (`Функция select выполнилась за x секунд`). Применён к `select` и `insert`.
- `create_cacher()` — замыкание с кэшем результатов; используется в `select` для одинаковых запросов. Кэш сбрасывается после `insert`, `update`, `delete` и `drop_table`.

Пример:

```
>>>Введите команду: drop_table users
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]: n
Операция отменена.
```

Аскинема декортаоры: [![asciicast](https://asciinema.org/a/FD1BjLuxHGy4FkSf.svg)](https://asciinema.org/a/FD1BjLuxHGy4FkSf)
