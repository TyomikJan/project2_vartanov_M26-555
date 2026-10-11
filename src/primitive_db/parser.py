import re

from .constants import FALSE_LITERAL, QUOTE_CHARS, TRUE_LITERAL

_TOKEN = re.compile(r'"[^"]*"|\'[^\']*\'|[^,\s][^,]*?(?=\s*(?:,|$))')


def parse_value(raw):
    """Convert a literal into int/bool/str. Strings must be quoted."""
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in QUOTE_CHARS:
        return raw[1:-1]
    if raw.lower() in (TRUE_LITERAL, FALSE_LITERAL):
        return raw.lower() == TRUE_LITERAL
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    raise ValueError(f"Некорректное значение: {raw}. Строки должны быть в кавычках.")


def split_commas(text):
    """Split by commas that are outside of quotes."""
    parts, buf, quote = [], "", None
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
            buf += ch
        elif ch in QUOTE_CHARS:
            quote = ch
            buf += ch
        elif ch == ",":
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    if quote:
        raise ValueError("Незакрытая кавычка.")
    parts.append(buf)
    return [p.strip() for p in parts]


def parse_values(text):
    """'"a", 1, true' -> ['a', 1, True]"""
    return [parse_value(p) for p in split_commas(text)]


def parse_clause(text):
    """'age = 28' or 'a = 1, b = "x"' -> {'age': 28} / {'a': 1, 'b': 'x'}"""
    result = {}
    for part in split_commas(text):
        name, sep, value = part.partition("=")
        name = name.strip()
        if not sep or not name or not value.strip():
            raise ValueError(f"Некорректное значение: {part}.")
        result[name] = parse_value(value)
    return result
