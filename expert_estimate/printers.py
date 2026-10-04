# -*- coding: utf-8 -*-
"""
Модуль форматированного академического вывода результатов экспертного оценивания.
Обеспечивает аккуратное табличное оформление, визуальное разделение этапов,
содержательные математические пояснения и автоматическую итоговую интерпретацию.
"""

from typing import Dict, List, Optional, Tuple
from .named_matrix import NamedMatrix
from .stats import assign_places, get_sorted_by_rank


# =========================================================================
# ВСПОМОГАТЕЛЬНОЕ ОФОРМЛЕНИЕ ТАБЛИЦ И БАННЕРОВ
# =========================================================================

def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """Выводит стилизованный заголовок этапа."""
    width = max(76, len(title) + 6)
    print()
    print("═" * width)
    print(f"  {title.upper()}")
    if subtitle:
        print(f"  {subtitle}")
    print("═" * width)


def print_note(text: str) -> None:
    """Выводит поясняющую подсказку или аналитический комментарий."""
    print(f"\n💡 Пояснение: {text}")


def format_box_table(
    headers: List[str],
    rows: List[List[object]],
    aligns: Optional[List[str]] = None,
) -> str:
    """
    Формирует эстетичную таблицу в рамке Unicode.
    aligns: список выравниваний для каждой колонки ('left', 'center', 'right').
    """
    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]
    num_cols = len(str_headers)

    if aligns is None:
        aligns = ["left"] + ["center"] * (num_cols - 1)

    widths = [len(h) for h in str_headers]
    for row in str_rows:
        for j, cell in enumerate(row):
            if j < num_cols:
                widths[j] = max(widths[j], len(cell))

    # Минимальная ширина ячейки для читаемости
    widths = [max(w, 4) for w in widths]

    def pad_cell(text: str, width: int, align: str) -> str:
        if align == "center":
            return text.center(width)
        elif align == "right":
            return text.rjust(width)
        return text.ljust(width)

    top_border = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    header_sep = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"

    header_line = "│" + "│".join(f" {pad_cell(h, widths[j], 'center')} " for j, h in enumerate(str_headers)) + "│"

    data_lines = []
    for row in str_rows:
        cells_padded = [
            f" {pad_cell(row[j] if j < len(row) else '', widths[j], aligns[j])} "
            for j in range(num_cols)
        ]
        data_lines.append("│" + "│".join(cells_padded) + "│")

    lines = [top_border, header_line, header_sep] + data_lines + [bottom_border]
    return "\n".join(lines)


def print_table(
    rows: List[List],
    columns: List[str],
    aligns: Optional[List[str]] = None,
) -> None:
    """Универсальная печать таблицы (заменяет старый pandas-вывод на аккуратную рамку)."""
    print(format_box_table(columns, rows, aligns))


# =========================================================================
# 1. ИСХОДНЫЕ ДАННЫЕ И МАТРИЦА РАНГОВ
# =========================================================================

def print_raw_data(table: Dict[int, List[str]]) -> None:
    """Выводит исходные протоколы ранжирования экспертов."""
    print_header("1. ИСХОДНЫЕ СУЖДЕНИЯ ЭКСПЕРТОВ", "Суждения экспертов упорядочены от наиболее предпочтительного к наименее")
    rows = []
    for num, ranks in sorted(table.items()):
        order_str = " ≻ ".join(ranks)
        rows.append([f"Эксперт Э{num}", order_str, " ".join(ranks)])

    print(format_box_table(["Эксперт", "Индивидуальный порядок предпочтений", "Вектор"], rows, ["center", "left", "center"]))
    print_note("Символ '≻' означает строгое предпочтение: первая альтернатива в строке признана наилучшей.")


def print_transformed_data(table: Dict[int, Dict[str, int]], objects: List[str]) -> None:
    """Матрица «Эксперт × Объект» с числовыми рангами."""
    print("\n┌── Матрица рангов объектов (Эксперт × Объект) ──────────────────────────────┐")
    columns = ["Эксперт"] + objects
    rows = []
    for num in sorted(table.keys()):
        ranks = table[num]
        rows.append([f"Э{num}"] + [ranks.get(obj, "—") for obj in objects])

    print(format_box_table(columns, rows, ["center"] * len(columns)))
    print_note("Ранг 1 присвоен наилучшей альтернативе, максимальный ранг — наихудшей.")


# =========================================================================
# 2. СРЕДНИЕ И МЕДИАННЫЕ РАНГИ
# =========================================================================

def print_ranking(title: str, places: List[Tuple[int, str, float]], unit: str) -> None:
    """Табличный вывод результатов ранжирования по среднему/медиане."""
    rows = []
    for place, obj, val in places:
        rows.append([f"{place} место", obj, f"{val:.2f}"])

    print(format_box_table(["Позиция", "Альтернатива", f"Значение ({unit})"], rows, ["center", "center", "right"]))


def print_ranking_by_average(ranks_avg: Dict[str, float]) -> None:
    """Метод средних арифметических рангов."""
    places = assign_places(get_sorted_by_rank(ranks_avg))
    print_header("2. МЕТОД СРЕДНИХ АРИФМЕТИЧЕСКИХ РАНГОВ", "Агрегирование мнений на основе статистического усреднения баллов")
    print_ranking("Итоговое ранжирование по среднему баллу", places, "средний ранг")
    lead_obj = places[0][1]
    lead_val = places[0][2]
    print_note(f"Альтернатива {lead_obj} получила минимальный средний балл ({lead_val:.2f}) и заняла 1-е место. Чем меньше r̄, тем выше приоритет.")


def print_ranking_by_median(ranks_median: Dict[str, float]) -> None:
    """Метод медианных рангов."""
    places = assign_places(get_sorted_by_rank(ranks_median))
    print_header("3. МЕТОД МЕДИАННЫХ РАНГОВ", "Робастная порядковая статистика (квантиль порядка 0.5)")
    print_ranking("Итоговое ранжирование по медиане", places, "медианный ранг")
    print_note("Медианный ранг устойчив к единичным выбросам и смещённым суждениям отдельных экспертов комиссии.")


# =========================================================================
# 3. ВЕКТОРЫ ПРЕДПОЧТЕНИЙ И МАТРИЦА ПОТЕРЬ
# =========================================================================

def print_preference_vectors(preference_vectors: Dict[int, Dict[str, int]], objects: List[str]) -> None:
    """Матрица векторов предпочтений π^(k)."""
    print_header("5. ВЕКТОРЫ ПРЕДПОЧТЕНИЙ π^(k)", "π_i^(k) указывает количество альтернатив, которые эксперт k счёл СТРОГО ЛУЧШЕ a_i")
    columns = ["Эксперт"] + objects
    rows = []
    for num in sorted(preference_vectors.keys()):
        pv = preference_vectors[num]
        rows.append([f"Э{num}"] + [pv.get(obj, 0) for obj in objects])

    print(format_box_table(columns, rows, ["center"] * len(columns)))
    print_note("Для строгого упорядочения без связок значение π_i всегда равно (r_i - 1). Лучший объект имеет π = 0.")


# =========================================================================
# 4. БИНАРНЫЕ ОТНОШЕНИЯ И РАССТОЯНИЯ КЕМЕНИ
# =========================================================================

def print_binary_relations(relations: Dict[int, NamedMatrix]) -> None:
    """Печать квадратных матриц бинарных отношений A_k."""
    print_header("4. БИНАРНЫЕ ОТНОШЕНИЯ И РАССТОЯНИЯ КЕМЕНИ", "Отношение нестрогого доминирования: x_ij = 1, если r_i >= r_j; иначе 0")
    for expert, m in sorted(relations.items()):
        print(f"\n┌── Эксперт Э{expert} ───────────────────────────────────────┐")
        cols = m.cols
        matrix_rows = [[r] + [m[r, c] for c in cols] for r in m.rows]
        print(format_box_table([" "] + cols, matrix_rows, ["center"] * (len(cols) + 1)))
    print_note("Диагональ всегда равна 1 (x_ii = 1). Элемент x_ij = 0 означает, что объект a_i строго лучше объекта a_j.")


def print_distance_matrix(distances: NamedMatrix) -> None:
    """Матрица попарных расстояний Кемени между экспертами."""
    print("\n┌── Матрица попарных расстояний Кемени D ────────────────────────────────┐")
    cols = distances.cols
    rows = []
    for r in distances.rows:
        row_sum = sum(distances[r, c] for c in cols)
        rows.append([f"Э{r}"] + [distances[r, c] for c in cols] + [row_sum])

    headers = ["Эксперт"] + [f"Э{c}" for c in cols] + ["Сумма S_k"]
    print(format_box_table(headers, rows, ["center"] * len(headers)))
    print_note("d(A, B) = ∑ |a_ij - b_ij| = 2 · I(A, B), где I — число инверсий. Диагональ равна 0.")


def print_diff_relations_matrixes(diffs: Dict[Tuple[int, int], NamedMatrix], distances: NamedMatrix) -> None:
    """Матрицы попарных модулей разностей |A - B|."""
    print_header("МАТРИЦЫ РАЗНОСТЕЙ |A_k1 - A_k2|", "Показывают ячейки несовпадения суждений между парами экспертов")
    for (k1, k2), diff in sorted(diffs.items()):
        d = distances[str(k1), str(k2)]
        print(f"\n┌── Разность |Э{k1} − Э{k2}|  (расстояние Кемени d = {d}) ────┐")
        cols = diff.cols
        matrix_rows = [[r] + [diff[r, c] for c in cols] for r in diff.rows]
        print(format_box_table([" "] + cols, matrix_rows, ["center"] * (len(cols) + 1)))


def print_kemeny_median_by_experts(
    distances: NamedMatrix,
    transformed: Dict[int, Dict[str, int]],
    medians: List[str],
    sums: Dict[str, int],
) -> None:
    """Медиана Кемени на множестве заданных мнений экспертов."""
    print("\n┌── Медианы Кемени среди мнений экспертов ───────────────────────────────┐")
    best = min(sums.values())
    rows = []
    for expert, s in sorted(sums.items(), key=lambda x: int(x[0])):
        is_best = (s == best)
        marker = "★ МЕДИАНА" if is_best else ""
        rows.append([f"Эксперт Э{expert}", s, marker])

    print(format_box_table(["Эксперт", "Сумма по строке S_k", "Статус"], rows, ["center", "right", "center"]))

    print(f"\nМинимальное суммарное расстояние Кемени: S_min = {best}")
    print("Медианное(-ые) экспертное(-ые) ранжирование(-я):")
    for m in medians:
        ranks = transformed[int(m)]
        order = [obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])]
        print(f"  • Эксперт Э{m}: {' ≻ '.join(order)}  (S = {best})")
    print_note("Данное ранжирование выбрано исключительно из числа предложенных экспертами суждений.")


# =========================================================================
# 5. ЗАДАЧА О НАЗНАЧЕНИЯХ И ПОЛНЫЙ ПЕРЕБОР
# =========================================================================

def print_kemeny_assignment(orders: List[List[str]], total: int, loss: NamedMatrix) -> None:
    """Вывод решения задачи о назначениях."""
    print_header("6. ЗАДАЧА О НАЗНАЧЕНИЯХ (ПОЗИЦИОННАЯ МАТРИЦА ПОТЕРЬ)", "Минимизация суммы позиционных потерь Φ_Assign(X) = ∑ r_ij · X_ij")
    print("\nМатрица позиционных потерь r_ij (строки — объекты, столбцы — места 1..n):")
    cols = loss.cols
    rows = [[r] + [loss[r, c] for c in cols] for r in loss.rows]
    headers = ["Объект"] + [f"Место {c}" for c in cols]
    print(format_box_table(headers, rows, ["center"] * len(headers)))

    print(f"\n✓ Минимальная сумма позиционных потерь: Φ_Assign = {total}")
    print(f"✓ Количество оптимальных решений: {len(orders)}")
    print("\nОптимальные распределения альтернатив по местам:")
    for i, order in enumerate(orders, start=1):
        print(f"  {i}. {' ≻ '.join(order)}   (минимальные потери Φ_Assign = {total})")

    print_note(
        f"Значение {total} относится к позиционной L1-функции штрафа задачи о назначениях. "
        "Оно не является расстоянием Кемени и оптимизирует другой критерий!"
    )


def print_kemeny_bruteforce(orders: List[List[str]], total: int, num_checked: int = 120) -> None:
    """Вывод результатов полного перебора Кемени."""
    print_header(
        "7. ИСТИННАЯ МЕДИАНА КЕМЕНИ (ПОЛНЫЙ ПЕРЕБОР ПЕРЕСТАНОВОК)",
        f"Глобальная минимизация истинного расстояния Кемени Φ_Kemeny(R) = ∑ d(R, R_k) на всех {num_checked} перестановках"
    )
    print(f"✓ Проверено всех строгих перестановок: {num_checked}")
    print(f"✓ Минимальная сумма попарных расстояний Кемени: Φ_Kemeny = {total}")
    print(f"✓ Найдено глобальных оптимумов Кемени: {len(orders)}")
    print("\nГлобальные медианы Кемени:")
    for i, order in enumerate(orders, start=1):
        print(f"  {i}. {' ≻ '.join(order)}   (истинное расстояние Кемени Σ d = {total})")

    print_note("Истинная медиана Кемени строго минимизирует сумму попарных инверсий ко всем экспертам комиссии без приближений.")


# =========================================================================
# 6. СВОДНОЕ СОПОСТАВЛЕНИЕ И ИТОГОВАЯ ИНТЕРПРЕТАЦИЯ
# =========================================================================

def print_kemeny_comparison(
    relations: Dict[int, "NamedMatrix"],
    objects: List[str],
    transformed: Dict[int, Dict[str, int]],
    distances: "NamedMatrix",
    medians_experts: List[str],
    assignment_orders: List[List[str]],
    assignment_total: int,
    bruteforce_orders: List[List[str]],
    bruteforce_total: int,
) -> None:
    """Сравнительный анализ подходов к определению коллективного предпочтения."""
    from .kemeny import kemeny_total_distance

    print_header("8. СВОДНОЕ СОПОСТАВЛЕНИЕ РЕЗУЛЬТАТОВ ВСЕХ МЕТОДОВ", "Сопоставление целевых функций и полученных ранжирований")

    comp_rows = []

    # 1. Экспертные медианы
    sums = {row: sum(distances[row].values()) for row in distances.rows}
    for m in medians_experts:
        ranks = transformed[int(m)]
        order = [obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])]
        d_kemeny = kemeny_total_distance(order, relations, objects)
        comp_rows.append([
            f"Медиана среди экспертов (Э{m})",
            "Сумма по строке D",
            f"S = {sums[m]}",
            " ≻ ".join(order),
            f"Σ d = {d_kemeny}",
        ])

    # 2. Задача о назначениях
    for i, order in enumerate(assignment_orders, start=1):
        d_kemeny = kemeny_total_distance(order, relations, objects)
        lbl = f"Задача назначений (решение {i})" if len(assignment_orders) > 1 else "Задача назначений"
        comp_rows.append([
            lbl,
            "Сумма потерь r_ij",
            f"Φ_Assign = {assignment_total}",
            " ≻ ".join(order),
            f"Σ d = {d_kemeny}",
        ])

    # 3. Полный перебор Кемени
    for i, order in enumerate(bruteforce_orders, start=1):
        lbl = f"Истинная медиана (оптимум {i})" if len(bruteforce_orders) > 1 else "Истинная медиана Кемени"
        comp_rows.append([
            lbl,
            "Сумма расстояний Кемени",
            f"Φ_Kemeny = {bruteforce_total}",
            " ≻ ".join(order),
            f"Σ d = {bruteforce_total}",
        ])

    headers = ["Метод агрегирования", "Оптимизируемый критерий", "Экстремум", "Результирующий порядок", "Расстояние Кемени"]
    print(format_box_table(headers, comp_rows, ["left", "left", "center", "left", "center"]))

    print_note(
        f"Обратите внимание: минимум задачи назначений ({assignment_total}) и минимум Кемени ({bruteforce_total}) — "
        "это значения РАЗНЫХ целевых функций. Их прямое сравнение математически некорректно."
    )


def print_analytical_interpretation(
    table: Dict[int, Dict[str, int]],
    objects: List[str],
    relations: Dict[int, NamedMatrix],
    assignment_orders: List[List[str]],
    assignment_total: int,
    bruteforce_orders: List[List[str]],
    bruteforce_total: int,
) -> None:
    """Формирует и выводит итоговую динамическую интерпретацию группового выбора."""
    from .kemeny import kemeny_total_distance
    from .stats import get_ranking_by_average, get_ranking_by_median

    avg_ranking = get_ranking_by_average(table)
    med_ranking = get_ranking_by_median(table)

    print_header("9. ИТОГОВАЯ АНАЛИТИЧЕСКАЯ ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ", "Синтез коллективного решения на основе всех исследованных методов")

    # 1. Анализ лидеров и аутсайдеров по Кемени
    first_places = [order[0] for order in bruteforce_orders]
    last_places = [order[-1] for order in bruteforce_orders]

    top_objs = sorted(list(set(first_places)))
    bottom_objs = sorted(list(set(last_places)))

    print("\n1. СТРУКТУРА КОЛЛЕКТИВНОГО ПРИОРИТЕТА:")
    if len(top_objs) == 1:
        print(f"   • Абсолютным фаворитом по критерию Кемени признана альтернатива: {top_objs[0]}.")
    else:
        print(f"   • В группу ключевых претендентов на лидерство входят: {', '.join(top_objs)}.")

    if len(bottom_objs) == 1:
        print(f"   • Наименее предпочтительной (замыкающей) альтернативой признана: {bottom_objs[0]}.")
    else:
        print(f"   • Замыкающие позиции делят альтернативы: {', '.join(bottom_objs)}.")

    print(f"   • Лидер по средним арифметическим рангам: {avg_ranking[0][1]} (средний ранг {avg_ranking[0][2]:.2f}).")
    print(f"   • Лидер по медианным рангам: {med_ranking[0][1]} (медианный ранг {med_ranking[0][2]:.2f}).")

    # 2. Сопоставление задачи о назначениях и медианы Кемени
    print("\n2. СООТНОШЕНИЕ ЗАДАЧИ О НАЗНАЧЕНИЯХ И МЕДИАНЫ КЕМЕНИ:")
    assign_set = {tuple(o) for o in assignment_orders}
    kemeny_set = {tuple(o) for o in bruteforce_orders}
    common = assign_set.intersection(kemeny_set)

    if common:
        print(f"   • Решение задачи о назначениях строго совпало с истинной медианой Кемени.")
        print(f"   • Значение функции позиционных потерь: {assignment_total}, истинное расстояние Кемени: {bruteforce_total}.")
    else:
        first_as = assignment_orders[0]
        first_km = bruteforce_orders[0]
        d_as = kemeny_total_distance(first_as, relations, objects)
        print(f"   • Решение задачи о назначениях ({' ≻ '.join(first_as)})")
        print(f"     НЕ совпадает с истинной глобальной медианой Кемени ({' ≻ '.join(first_km)}).")
        print(f"   • По критерию задачи о назначениях минимум потерь составил: {assignment_total}.")
        print(f"     При этом истинное расстояние Кемени для порядка задачи назначений равно {d_as},")
        print(f"     что строго превышает глобальный оптимум Кемени ({bruteforce_total}).")
        print("   • ВЫВОД: Оптимизация задачи о назначениях с позиционной матрицей потерь")
        print("     сглаживает парные циклические доминирования и не гарантирует нахождения медианы Кемени.")

    # 3. Множественность оптимумов
    print("\n3. УСТОЙЧИВОСТЬ ГЛОБАЛЬНОГО ВЫБОРА:")
    if len(bruteforce_orders) == 1:
        print(f"   • Найдено ЕДИНСТВЕННОЕ глобальное медианное ранжирование со значением Кемени {bruteforce_total}:")
        print(f"     {' ≻ '.join(bruteforce_orders[0])}")
        print("   • Коллективное предпочтение экспертной комиссии определено однозначно.")
    else:
        print(f"   • Найдено {len(bruteforce_orders)} РАВНОПРАВНЫХ глобальных оптимумов Кемени со значением {bruteforce_total}.")
        print("   • Это свидетельствует о наличии паритета между несколькими перестановками внутри группы.")
