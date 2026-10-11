# primitive-db

Примитивная консольная база данных на Python. Поддерживает создание и удаление таблиц, CRUD-операции (`insert`, `select`, `update`, `delete`), фильтрацию по условию `where`, обновление через `set`, подтверждение опасных действий и кэширование запросов `select`. Метаданные и данные хранятся в JSON-файлах.

## Возможности

- управление таблицами: `create_table`, `drop_table`, `list_tables`, `info`;
- типы столбцов: `int`, `str`, `bool`; столбец `ID:int` добавляется автоматически;
- CRUD-операции с валидацией типов и автоматической генерацией `ID`;
- парсер условий `where` и `set` (строки в кавычках, запятые внутри строк, `bool`);
- вывод таблиц через [PrettyTable](https://pypi.org/project/prettytable/);
- декораторы `handle_db_errors`, `confirm_action`, `log_time` и замыкание-кэш `create_cacher`.

## Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — менеджер пакетов и окружений
- зависимости (ставятся автоматически): `prettytable`, `prompt`
- для разработки: `ruff`

## Установка

```bash
git clone https://github.com/TyomikJan/project2_vartanov_M26-555.git
cd project2_vartanov_M26-555
uv sync
```

## Запуск

Через `uv`:

```bash
uv run database
```

Или установить как консольную утилиту и запускать командой `database`:

```bash
uv tool install .
database
```

## Структура проекта

```
src/primitive_db/
├── main.py        # точка входа
├── engine.py      # главный цикл, разбор и диспетчеризация команд
├── core.py        # логика БД: таблицы и CRUD
├── parser.py      # парсинг значений, условий where/set
├── utils.py       # чтение и запись JSON-файлов
├── decorators.py  # декораторы и замыкание-кэш
└── constants.py   # константы (пути, типы, имена команд)
```

Хранилище:

- `db_meta.json` — метаданные таблиц (имена и столбцы);
- `data/<таблица>.json` — записи таблицы.

Оба пути перечислены в `.gitignore` и создаются при работе программы.

## Линтер

```bash
uv run ruff check .
```

## Команды

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | создать таблицу |
| `list_tables` | список таблиц |
| `drop_table <имя>` | удалить таблицу (с подтверждением) |
| `insert into <таблица> values (<знач1>, <знач2>, ...)` | добавить запись |
| `select from <таблица> [where <столбец> = <значение>]` | прочитать записи |
| `update <таблица> set <столбец> = <значение>[, ...] where <столбец> = <значение>` | обновить записи |
| `delete from <таблица> where <столбец> = <значение>` | удалить записи (с подтверждением) |
| `info <таблица>` | столбцы и количество записей |
| `help` | справка |
| `exit` | выход |

Правила записи значений: строки всегда в кавычках (`"Sergei"`), `bool` — `true`/`false`, `int` — целое число. `ID` генерируется автоматически (max + 1), в `insert` его указывать не нужно, изменять его в `update` нельзя.

## Управление таблицами

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

```
>>>Введите команду: insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>>Введите команду: select from users where age = 28
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+

>>>Введите команду: update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.

>>>Введите команду: delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записи"? [y/n]: y
Запись с ID=1 успешно удалена из таблицы "users".
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

Аскинема декораторы: [![asciicast](https://asciinema.org/a/FD1BjLuxHGy4FkSf.svg)](https://asciinema.org/a/FD1BjLuxHGy4FkSf)
