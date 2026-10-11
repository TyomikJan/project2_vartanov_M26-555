# primitive-db

## Управление таблицами

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
