from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from .named_matrix import NamedMatrix
from .stats import assign_places, get_sorted_by_rank


# ---------- общая таблица (pandas) ----------

def print_table(
    rows: List[List],
    columns: List[str],
    aligns: Optional[List[str]] = None,
) -> None:
    if aligns is None:
        aligns = ["center"] + ["left"] * (len(columns) - 1)

    df = pd.DataFrame(rows, columns=columns)

    for col, align in zip(columns, aligns):
        w = max(len(col), df[col].astype(str).str.len().max())
        df[col] = df[col].astype(str).apply(
            lambda s: s.center(w) if align == "center"
            else s.rjust(w) if align == "right"
            else s.ljust(w)
        )
        df.columns = [c.center(w) if c == col else c for c in df.columns]

    print(df.to_string(index=False))

# ---------- исходные данные ----------

def print_raw_data(table: Dict[int, List[str]]) -> None:
    rows = [(num, " ".join(ranks)) for num, ranks in table.items()]
    print_table(rows, ["Номер эксперта", "Мнение эксперта"], ["center", "left"])

def print_transformed_data(table: Dict[int, Dict[str, int]], objects: List[str]) -> None:
    """Матрица «Эксперт × Объект» с рангами."""
    columns = ["Эксперт"] + objects

    rows = [
        [f"Э{num}"] + [str(ranks.get(obj, "—")) for obj in objects]
        for num, ranks in table.items()
    ]

    widths = [
        max(len(col), max(len(r[i]) for r in rows))
        for i, col in enumerate(columns)
    ]

    aligns = ["right"] + ["center"] * len(objects)

    def fmt(cells):
        parts = []
        for cell, w, align in zip(cells, widths, aligns):
            if align == "center":
                parts.append(cell.center(w))
            elif align == "right":
                parts.append(cell.rjust(w))
            else:
                parts.append(cell.ljust(w))
        return "  ".join(parts)

    print()
    print(fmt(columns))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(fmt(row))

# ---------- ранжирования по среднему/медиане ----------

def print_ranking(title: str, places: List[Tuple[int, str, float]], unit: str) -> None:
    print(f"\n{title}:")
    for place, obj, value in places:
        print(f"  {place}. {obj}  ({unit} = {value:.2f})")

def print_ranking_by_average(ranks_avg: Dict[str, float]) -> None:
    places = assign_places(get_sorted_by_rank(ranks_avg))
    print_ranking("Итоговое ранжирование по среднему", places, "средний ранг")

def print_ranking_by_median(ranks_median: Dict[str, float]) -> None:
    places = assign_places(get_sorted_by_rank(ranks_median))
    print_ranking("Итоговое ранжирование по медиане", places, "медиана")

# ---------- матрицы ----------

def print_preference_vectors(preference_vectors: Dict[int, Dict[str, int]], objects: List[str]) -> None:
    """Матрица «Эксперт × Объект» с векторами предпочтений π^(k)."""
    columns = ["Эксперт"] + objects

    rows = [
        [f"Э{num}"] + [str(pv.get(obj, "—")) for obj in objects]
        for num, pv in preference_vectors.items()
    ]

    widths = [
        max(len(col), max(len(r[i]) for r in rows))
        for i, col in enumerate(columns)
    ]

    aligns = ["right"] + ["center"] * len(objects)

    def fmt(cells):
        parts = []
        for cell, w, align in zip(cells, widths, aligns):
            if align == "center":
                parts.append(cell.center(w))
            elif align == "right":
                parts.append(cell.rjust(w))
            else:
                parts.append(cell.ljust(w))
        return "  ".join(parts)

    print("\nВекторы предпочтений π^(k)  (π_i = сколько объектов ЛУЧШЕ, чем a_i):")
    print()
    print(fmt(columns))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(fmt(row))

def print_binary_relations(relations: Dict[int, NamedMatrix]) -> None:
    for expert, m in relations.items():
        print(f"\nЭксперт Э{expert}:")
        print(m)

def print_distance_matrix(distances: NamedMatrix) -> None:
    print("\nМатрица расстояний Кемени между экспертами:")
    print(distances)

def print_diff_relations_matrixes(diffs: Dict[Tuple[int, int], NamedMatrix], distances: NamedMatrix) -> None:
    for (k1, k2), diff in diffs.items():
        d = distances[str(k1), str(k2)]
        print(f"\n|Э{k1} − Э{k2}|  (d = {d}):")
        print(diff)

# ---------- медианы Кемени ----------

def print_kemeny_median_by_experts(distances: NamedMatrix, transformed: Dict[int, Dict[str, int]], medians: List[str], sums: Dict[str, int]) -> None:
    print("\nСуммы расстояний по строкам матрицы D:")
    best = min(sums.values())
    for expert, s in sums.items():
        marker = " ←" if s == best else ""
        print(f"  Э{expert}: S = {s}{marker}")

    if len(medians) == 1:
        print(f"\nМедиана Кемени (среди экспертов): Э{medians[0]}")
    else:
        labels = ", ".join(f"Э{m}" for m in medians)
        print(f"\nМедианы Кемени (среди экспертов, ничья): {labels}")

    print(f"Суммарное расстояние: {best}")

    print("\nРанжирования медиан:")
    for m in medians:
        ranks = transformed[int(m)]
        order = [obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])]
        print(f"  Э{m}: {' > '.join(order)}")

def print_kemeny_assignment(orders: List[List[str]], total: int, loss: NamedMatrix) -> None:
    print("\n=== Задача о назначениях ===")

    print("\nМатрица потерь r_ij:")
    print(loss)

    print(f"\nМинимальное значение целевой функции: {total}")
    print(f"Количество оптимальных назначений: {len(orders)}")

    print("\nВсе оптимальные ранжирования:")
    for i, order in enumerate(orders, start=1):
        print(f"  {i}. {' > '.join(order)}   (Σ r_ij = {total})")

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
    """
    Сравнивает результаты:
    1. медианы среди экспертных ранжирований;
    2. все оптимумы задачи о назначениях;
    3. все оптимумы истинного Кемени полным перебором.
    """
    from .kemeny import kemeny_total_distance

    print("\n" + "=" * 60)
    print("Сравнение подходов к медиане Кемени")
    print("=" * 60)

    # --- 1. Среди экспертов ---
    print("\n1. Медианы среди экспертов:")

    sums = {
        row: sum(distances[row].values())
        for row in distances.rows
    }

    for m in medians_experts:
        ranks = transformed[int(m)]
        order = [
            obj
            for obj, _ in sorted(
                ranks.items(),
                key=lambda x: x[1]
            )
        ]

        d_total = kemeny_total_distance(
            order,
            relations,
            objects,
        )

        print(f"   Э{m}: {' > '.join(order)}")
        print(
            f"        Σ_k d(R, R_k) = {d_total} "
            f"  (S по D = {sums[m]})"
        )

    # --- 2. Задача о назначениях ---
    print("\n2. Задача о назначениях:")
    print(f"   Минимальное значение Σ r_ij = {assignment_total}")
    print(
        f"   Количество оптимальных решений: "
        f"{len(assignment_orders)}"
    )

    for i, order in enumerate(assignment_orders, start=1):
        d_total = kemeny_total_distance(
            order,
            relations,
            objects,
        )

        print(f"   {i}. {' > '.join(order)}")
        print(f"      Σ r_ij         = {assignment_total}")
        print(f"      Σ_k d(R, R_k)  = {d_total}")

    # --- 3. Полный перебор ---
    print(
        f"\n3. Полный перебор "
        f"(все оптимумы, Σ = {bruteforce_total}):"
    )

    print(
        f"   Количество оптимальных решений: "
        f"{len(bruteforce_orders)}"
    )

    for i, order in enumerate(bruteforce_orders, start=1):
        d_total = kemeny_total_distance(
            order,
            relations,
            objects,
        )

        print(
            f"   {i}. {' > '.join(order)} "
            f"(Σ_k d = {d_total})"
        )

    # --- Пересечения ---
    print("\n" + "-" * 60)
    print("Пересечение множеств оптимумов:")

    set_experts = {
        tuple(
            obj
            for obj, _ in sorted(
                transformed[int(m)].items(),
                key=lambda x: x[1],
            )
        )
        for m in medians_experts
    }

    set_assignment = {
        tuple(order)
        for order in assignment_orders
    }

    set_bruteforce = {
        tuple(order)
        for order in bruteforce_orders
    }

    print(
        f"   среди экспертов ∩ полный перебор: "
        f"{len(set_experts & set_bruteforce)}"
    )

    print(
        f"   назначения ∩ полный перебор:       "
        f"{len(set_assignment & set_bruteforce)}"
    )

    print(
        f"   назначения ∈ полный перебор:       "
        f"{set_assignment <= set_bruteforce}"
    )
