from pathlib import Path


# ---------- файлы ----------
DEFAULT_INPUT = "input.txt"
DEFAULT_OUTPUT = "output.txt"

# ---------- формат объектов ----------
OBJECT_PREFIX = "a"
INPUT_SEPARATOR = None   # None = split() по любым пробелам

def parse_object(name: str) -> int:
    """a5 -> 5. Используется для сортировки объектов."""
    return int(name[len(OBJECT_PREFIX):])

def object_sort_key(name: str) -> int:
    """Ключ сортировки объектов: a1 < a2 < a10."""
    return parse_object(name)

# ---------- этапы обработки ----------
# Порядок важен: именно в нём они выполняются и показываются в меню.
STAGES = [
    "raw",                 # исходные данные
    "transformed",         # матрица Эксперт × Объект
    "average",             # ранжирование по среднему
    "median",              # ранжирование по медиане
    "preferences",         # векторы предпочтений
    "relations",           # бинарные отношения
    "distances",           # матрица расстояний Кемени
    "diffs",               # матрицы разностей |A − B|
    "kemeny_experts",      # медиана среди экспертов
    "kemeny_assignment",   # медиана через задачу о назначениях
    "kemeny_bruteforce",   # полный перебор (для проверки)
    "kemeny_compare",
]
