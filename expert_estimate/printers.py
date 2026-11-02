# -*- coding: utf-8 -*-
"""
Модуль форматированного академического вывода результатов экспертного оценивания.
Обеспечивает аккуратное табличное оформление, визуальное разделение этапов,
содержательные математические пояснения и автоматическую итоговую интерпретацию.
"""

from typing import Dict, List, Optional, Tuple
from .named_matrix import NamedMatrix
from .stats import assign_places, format_places_order, get_sorted_by_rank


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
    print(f"\n{text}")


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
    print_note("Ранг `1` присвоен наилучшей альтернативе, `5` ранг — наихудшей.")


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
    order_str = format_places_order(places)
    print(f"\nРезультирующий порядок проектов по методу средних арифметических рангов: {order_str}.")
    print_note(f"{lead_obj} получила минимальный средний балл ({lead_val:.2f}). Чем меньше r̄, тем выше приоритет.")


def print_ranking_by_median(ranks_median: Dict[str, float]) -> None:
    """Метод медианных рангов."""
    places = assign_places(get_sorted_by_rank(ranks_median))
    print_header("3. МЕТОД МЕДИАННЫХ РАНГОВ", "(квантиль порядка 0.5)")
    print_ranking("Итоговое ранжирование по медиане", places, "медианный ранг")
    order_str = format_places_order(places)
    print(f"\nРезультирующий порядок проектов по методу медианных рангов: {order_str}.")


# =========================================================================
# 3. ВЕКТОРЫ ПРЕДПОЧТЕНИЙ И МАТРИЦА ПОТЕРЬ
# =========================================================================

def print_preference_vectors(preference_vectors: Dict[int, Dict[str, int]], objects: List[str]) -> None:
    """Матрица векторов предпочтений π^(k)."""
    print_header("5. ВЕКТОРЫ ПРЕДПОЧТЕНИЙ π^(k)", "π_i^(k) указывает количество альтернатив, которые эксперт k счёл строго лучше a_i")
    columns = ["Эксперт"] + objects
    rows = []
    for num in sorted(preference_vectors.keys()):
        pv = preference_vectors[num]
        rows.append([f"Э{num}"] + [pv.get(obj, 0) for obj in objects])

    print(format_box_table(columns, rows, ["center"] * len(columns)))
    print_note("Значение π_i всегда равно (r_i - 1). Лучший объект имеет π = 0.")
    print_note("Для каждой экспертной ранжировки строится вектор предпочтений, координата которого показывает количество объектов, расположенных выше соответствующего объекта в ранжировке. Поскольку ранг первого места равен 1, координаты вектора предпочтений определяются вычитанием единицы из исходной матрицы рангов.")


# =========================================================================
# 4. БИНАРНЫЕ ОТНОШЕНИЯ И РАССТОЯНИЯ КЕМЕНИ
# =========================================================================

def print_binary_relations(relations: Dict[int, NamedMatrix]) -> None:
    """Печать квадратных матриц бинарных отношений A_k."""
    print_header("4. БИНАРНЫЕ ОТНОШЕНИЯ И РАССТОЯНИЯ КЕМЕНИ", "Отношение нестрогого доминирования: x_ij = 1, если r_i >= r_j; иначе 0")
    print_note("Диагональ всегда равна 1 (x_ii = 1). Элемент x_ij = 0 означает, что объект a_i строго лучше объекта a_j.")
    for expert, m in sorted(relations.items()):
        print(f"\n┌── Эксперт Э{expert} ───────────────────────────────────────┐")
        cols = m.cols
        matrix_rows = [[r] + [m[r, c] for c in cols] for r in m.rows]
        print(format_box_table([" "] + cols, matrix_rows, ["center"] * (len(cols) + 1)))



def print_distance_matrix(distances: NamedMatrix) -> None:
    """Матрица попарных расстояний Кемени между экспертами."""
    print_note("Была рассчитана матрица попарных расстояний D размера 5 × 5. Для каждого эксперта вычислена сумма расстояний")
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
        marker = "★ Минимум" if is_best else ""
        rows.append([f"Эксперт Э{expert}", s, marker])

    print(format_box_table(["Эксперт", "Сумма по строке S_k", "Статус"], rows, ["center", "right", "center"]))

    if len(medians) == 1:
        m = medians[0]
        ranks = transformed[int(m)]
        order = " ≻ ".join([obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])])
        print(f"\nМинимальная сумма расстояний составила Smin = {best} (эксперт Э{m}). Результирующий порядок проектов: {order}.")
    else:
        exp_list = ", ".join([f"Э{m}" for m in medians])
        print(f"\nМинимальная сумма расстояний составила Smin = {best} (эксперты: {exp_list}).")
        for m in medians:
            ranks = transformed[int(m)]
            order = " ≻ ".join([obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])])
            print(f"  • Эксперт Э{m}: {order} (S = {best})")


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

    for idx, order in enumerate(orders, start=1):
        suffix = f" (решение #{idx})" if len(orders) > 1 else ""
        print(f"\nОптимальная матрица назначений X_ij{suffix}:")
        obj_to_place = {obj: place for place, obj in enumerate(order, start=1)}
        x_rows = []
        for r in loss.rows:
            row = [r] + [1 if int(c) == obj_to_place[r] else 0 for c in cols]
            x_rows.append(row)
        print(format_box_table(headers, x_rows, ["center"] * len(headers)))

    print(f"\n- Минимальная сумма позиционных потерь: Φ_Assign = {total}")
    print(f"- Количество оптимальных решений: {len(orders)}")
    print("\nОптимальные распределения альтернатив по местам:")
    for i, order in enumerate(orders, start=1):
        terms = [f"r^{obj.replace('a', '')}{j}" for j, obj in enumerate(order, start=1)]
        vals = [str(loss[obj, str(j)]) for j, obj in enumerate(order, start=1)]
        calc_str = f"Φ = {' + '.join(terms)} = {' + '.join(vals)} = {total}"
        print(f"  {i}. {' ≻ '.join(order)}   ({calc_str})")

    if len(orders) == 1:
        print(f"\nМинимум позиционных потерь равен {total}, найдено одно решение. Результирующий порядок проектов: {' ≻ '.join(orders[0])}.")
    else:
        print(f"\nМинимум позиционных потерь равен {total}, найдено решений: {len(orders)}.")
        for i, order in enumerate(orders, start=1):
            print(f"  Результирующий порядок проектов #{i}: {' ≻ '.join(order)}.")

    print_note(
        f"Значение {total} относится к позиционной L1-функции штрафа задачи о назначениях. "
        "Оно не является расстоянием Кемени и оптимизирует другой критерий."
    )


def print_kemeny_bruteforce(orders: List[List[str]], total: int, num_checked: int = 120) -> None:
    """Вывод результатов полного перебора Кемени."""
    print_header(
        "7. ИСТИННАЯ МЕДИАНА КЕМЕНИ (ПОЛНЫЙ ПЕРЕБОР ПЕРЕСТАНОВОК)",
        f"Глобальная минимизация истинного расстояния Кемени Φ_Kemeny(R) = ∑d(R, R_k) на всех {num_checked} перестановках"
    )
    print(f"- Проверено всех строгих перестановок: {num_checked}")
    print(f"- Минимальная сумма попарных расстояний Кемени: Φ_Kemeny = {total}")
    print(f"- Найдено глобальных оптимумов Кемени: {len(orders)}")
    print("\nГлобальные медианы Кемени:")
    for i, order in enumerate(orders, start=1):
        print(f"  {i}. {' ≻ '.join(order)}   (истинное расстояние Кемени Σd = {total})")

    if len(orders) == 1:
        print(f"\nМинимальное истинное расстояние Кемени равно {total}, число глобальных оптимумов — {len(orders)}. Результирующий порядок проектов: {' ≻ '.join(orders[0])}.")
    else:
        print(f"\nМинимальное истинное расстояние Кемени равно {total}, число глобальных оптимумов — {len(orders)}.")
        for i, order in enumerate(orders, start=1):
            print(f"  Результирующий порядок проектов #{i}: {' ≻ '.join(order)}.")

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

    headers = ["Метод агрегирования", "Оптимизируемый критерий", "Значение критерия", "Результирующий порядок", "Расстояние Кемени"]
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
    distances: Optional[NamedMatrix] = None,
    medians_experts: Optional[List[str]] = None,
) -> None:
    """Формирует и выводит итоговую аналитическую интерпретацию результатов."""
    import math
    from .kemeny import get_kemeny_medians_by_experts, kemeny_total_distance
    from .relations import build_distance_matrix
    from .stats import format_places_order, get_ranking_by_average, get_ranking_by_median

    if distances is None:
        distances = build_distance_matrix(relations)
    if medians_experts is None:
        medians_experts = get_kemeny_medians_by_experts(distances)

    print_header("9. ИТОГОВАЯ АНАЛИТИЧЕСКАЯ ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ", "Сравнение методов агрегирования экспертных оценок")

    # 1. Результаты агрегирования экспертных оценок
    avg_ranking = get_ranking_by_average(table)
    med_ranking = get_ranking_by_median(table)
    avg_order_str = format_places_order(avg_ranking)
    med_order_str = format_places_order(med_ranking)

    avg_leaders = [item[1] for item in avg_ranking if item[0] == 1]
    avg_leader_str = ", ".join(avg_leaders)
    avg_rank_val = avg_ranking[0][2]

    med_leaders = [item[1] for item in med_ranking if item[0] == 1]
    med_leader_str = ", ".join(med_leaders)
    med_rank_val = med_ranking[0][2]

    sums = {row: sum(distances[row].values()) for row in distances.rows}
    s_min = sums[medians_experts[0]]
    if len(medians_experts) == 1:
        expert_label = f"эксперт Э{medians_experts[0]}"
    else:
        expert_label = f"эксперты {', '.join(f'Э{m}' for m in medians_experts)}"

    expert_ranks = table[int(medians_experts[0])]
    expert_order = [obj for obj, _ in sorted(expert_ranks.items(), key=lambda x: x[1])]
    expert_order_str = " ≻ ".join(expert_order)

    print("\n1. РЕЗУЛЬТАТЫ АГРЕГИРОВАНИЯ ЭКСПЕРТНЫХ ОЦЕНОК")
    print(f"\n  • Метод средних арифметических рангов:\n    {avg_order_str}.")
    print(f"    Лидер — {avg_leader_str} со средним рангом {avg_rank_val:.2f}.")

    print(f"\n  • Метод медианных рангов:\n    {med_order_str}.")
    print(f"    Лидер — {med_leader_str} с медианным рангом {med_rank_val:.2f}.")

    print("\n  • Медиана среди исходных экспертных ранжировок:")
    print(f"    минимальная сумма расстояний Кемени S_min = {s_min}.")
    print(f"    Наилучшее согласование с остальными экспертами показывает {expert_label}:")
    print(f"    {expert_order_str}.")

    # 2. Сравнение оптимизационных методов
    print("\n2. СРАВНЕНИЕ ОПТИМИЗАЦИОННЫХ МЕТОДОВ")
    first_as = assignment_orders[0]
    first_km = bruteforce_orders[0]
    as_order_str = " ≻ ".join(first_as)
    km_order_str = " ≻ ".join(first_km)

    print("\n  • Задача о назначениях:")
    print(f"    оптимальный порядок — {as_order_str};")
    print(f"    минимальная сумма позиционных потерь Φ_Assign = {assignment_total}.")

    print("\n  • Истинная медиана Кемени:")
    print(f"    оптимальный порядок — {km_order_str};")
    print(f"    минимальная сумма расстояний Φ_Kemeny = {bruteforce_total}.")

    d_as = kemeny_total_distance(first_as, relations, objects)

    assign_set = {tuple(o) for o in assignment_orders}
    kemeny_set = {tuple(o) for o in bruteforce_orders}
    common = assign_set.intersection(kemeny_set)

    if not common:
        diff_objs = [obj for i, obj in enumerate(first_km) if first_km[i] != first_as[i]]
        diff_unique = sorted(list(set(diff_objs)))
        if len(diff_unique) == 2:
            diff_text = f"перестановкой проектов {diff_unique[0]} и {diff_unique[1]}"
        else:
            diff_text = f"порядком альтернатив {', '.join(diff_unique)}"

        print(f"\n  • Полученные ранжировки различаются {diff_text}.")
        print("    При этом сумма расстояний Кемени для решения задачи о назначениях")
        print(f"    равна {d_as}, что превышает глобальный минимум {bruteforce_total}.")
    else:
        print("\n  • Решение задачи о назначениях совпало с истинной медианой Кемени.")
        print(f"    Сумма расстояний Кемени для данного порядка равна {d_as}.")

    print("\n  ВЫВОД: задача о назначениях и поиск медианы Кемени оптимизируют")
    print("  разные целевые функции. Минимизация позиционных потерь не гарантирует")
    print("  нахождения глобальной медианы Кемени.")

    # 3. Итоговое решение задачи коллективного выбора
    n = len(objects)
    num_checked = math.factorial(n)

    print("\n3. ИТОГОВОЕ РЕШЕНИЕ ЗАДАЧИ КОЛЛЕКТИВНОГО ВЫБОРА\n")
    print(f"  • Проверено {n}! = {num_checked} возможных ранжировок.")
    if len(bruteforce_orders) == 1:
        print("  • Найдена единственная глобальная медиана Кемени.")
    else:
        print(f"  • Найдено {len(bruteforce_orders)} глобальных медиан Кемени.")
    print(f"  • Минимальное значение критерия Кемени — {bruteforce_total}.")
    print(f"  • Итоговое ранжирование:\n    {km_order_str}.")

    leader_obj = first_km[0]
    last_obj = first_km[-1]

    print("\n  ОБЩИЙ ВЫВОД:")
    print("  По результатам полного перебора установлено, что глобально оптимальное")
    print(f"  коллективное ранжирование — {km_order_str}.")
    print(f"  Альтернатива {leader_obj} занимает первое место, а {last_obj} — последнее.")
    print("  Результаты демонстрируют, что выбор метода агрегирования влияет")
    print("  на итоговый порядок альтернатив, поэтому для определения глобально")
    print("  оптимального ранжирования по критерию Кемени необходимо минимизировать")
    print("  именно сумму расстояний Кемени.")
    print("═" * 76)
