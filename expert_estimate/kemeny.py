from itertools import permutations
from typing import Dict, List, Optional, Tuple

from .named_matrix import NamedMatrix
from .relations import kemeny_distance_matrices


# ---------- среди экспертов ----------

def get_row_sums(distances: NamedMatrix) -> Dict[str, int]:
    """Суммы расстояний по строкам матрицы D."""
    return {row: sum(distances[row].values()) for row in distances.rows}

def get_kemeny_medians_by_experts(distances: NamedMatrix) -> List[str]:
    """Все эксперты, дающие минимум суммы расстояний (могут быть ничьи)."""
    sums = get_row_sums(distances)
    best = min(sums.values())
    return [k for k, s in sums.items() if s == best]

# ---------- через задачу о назначениях ----------

def get_preference_vector(ranks: Dict[str, int], objects: List[str]) -> Dict[str, int]:
    """π_i = сколько альтернатив ЛУЧШЕ, чем a_i."""
    return {
        obj: sum(1 for other in objects if ranks[other] < ranks[obj])
        for obj in objects
    }

def get_preference_vectors(table: Dict[int, Dict[str, int]], objects: List[str]) -> Dict[int, Dict[str, int]]:
    """{эксперт: {объект: π}}"""
    return {
        expert: get_preference_vector(ranks, objects)
        for expert, ranks in table.items()
    }

def build_loss_matrix(preference_vectors: Dict[int, Dict[str, int]], objects: List[str]) -> NamedMatrix:
    """
    r_ij = Σ_k |(j-1) − π_i^(k)|.
    Строки — объекты, столбцы — места (1..N).
    """
    n = len(objects)
    places = [str(j) for j in range(1, n + 1)]

    loss = NamedMatrix(rows=objects, cols=places, default=0)

    for obj in objects:
        for j in range(1, n + 1):
            pi_candidate = j - 1
            loss[obj, str(j)] = sum(
                abs(pi_candidate - pv[obj])
                for pv in preference_vectors.values()
            )

    return loss

def solve_assignment(loss: NamedMatrix, objects: List[str]) -> Tuple[Dict[str, int], int]:
    """
    Задача о назначениях перебором.
    :return: ({объект: место}, минимальные суммарные потери)
    """
    n = len(objects)
    best_order: Optional[List[str]] = None
    best_total = float("inf")

    for perm in permutations(objects):
        total = sum(loss[perm[j], str(j + 1)] for j in range(n))
        if total < best_total:
            best_total = total
            best_order = list(perm)

    return {obj: pos + 1 for pos, obj in enumerate(best_order)}, int(best_total)

def get_all_assignment_optima(
    loss: NamedMatrix,
    objects: List[str],
) -> Tuple[List[List[str]], int]:
    """
    Все оптимальные решения задачи о назначениях перебором.

    :return: (все оптимальные ранжирования, минимальные суммарные потери)
    """
    n = len(objects)
    best_total = float("inf")
    best_orders: List[List[str]] = []

    for perm in permutations(objects):
        total = sum(loss[perm[j], str(j + 1)] for j in range(n))
        if total < best_total:
            best_total = total
            best_orders = [list(perm)]
        elif total == best_total:
            best_orders.append(list(perm))

    return best_orders, int(best_total)


def get_all_assignment_medians(table: Dict[int, Dict[str, int]], objects: List[str]) -> Tuple[List[List[str]], int, NamedMatrix]:
    """
    Все оптимальные ранжирования по методу задачи о назначениях.

    :return: (все оптимальные ранжирования, минимум целевой функции, матрица потерь)
    """
    pv = get_preference_vectors(table, objects)
    loss = build_loss_matrix(pv, objects)
    orders, total = get_all_assignment_optima(loss, objects)
    return orders, total, loss


def get_kemeny_median_assignment(table: Dict[int, Dict[str, int]], objects: List[str]) -> Tuple[List[str], int, NamedMatrix, NamedMatrix]:
    """
    Полный цикл метода через задачу о назначениях.
    :return: (ранжирование, сумма потерь, матрица потерь r_ij, матрица назначений X)
    """
    pv = get_preference_vectors(table, objects)
    loss = build_loss_matrix(pv, objects)
    places, total = solve_assignment(loss, objects)
    order = [obj for obj, _ in sorted(places.items(), key=lambda x: x[1])]

    n = len(objects)
    X = NamedMatrix(rows=objects, cols=[str(j) for j in range(1, n + 1)], default=0)
    for obj, place in places.items():
        X[obj, str(place)] = 1

    return order, total, loss, X

# ---------- полный перебор (для проверки) ----------

def ranking_to_matrix(order: List[str], objects: List[str]) -> NamedMatrix:
    """Строит матрицу бинарных отношений по ранжированию.
    Строки/столбцы — в порядке objects."""
    ranks = {obj: pos + 1 for pos, obj in enumerate(order)}
    m = NamedMatrix(rows=objects, cols=objects, default=0)
    for a in objects:
        for b in objects:
            m[a, b] = 1 if ranks[a] >= ranks[b] else 0
    return m

def get_kemeny_median_bruteforce(relations: Dict[int, NamedMatrix], objects: List[str]) -> Tuple[List[str], int]:
    """Истинная медиана Кемени перебором всех N! перестановок."""
    best_order: Optional[List[str]] = None
    best_total = float("inf")

    for perm in permutations(objects):
        candidate = list(perm)
        candidate_matrix = ranking_to_matrix(candidate, objects)
        total = sum(
            kemeny_distance_matrices(candidate_matrix, m)
            for m in relations.values()
        )
        if total < best_total:
            best_total = total
            best_order = candidate

    return best_order, int(best_total)

def get_all_kemeny_medians_bruteforce(relations: Dict[int, NamedMatrix], objects: List[str]) -> Tuple[List[List[str]], int]:
    """
    Все ранжирования, минимизирующие Σ_k d(R, R_k).
    :return: (список ранжирований, минимальная сумма)
    """
    best_total = float("inf")
    best_orders: List[List[str]] = []

    for perm in permutations(objects):
        candidate = list(perm)
        candidate_matrix = ranking_to_matrix(candidate, objects)
        total = sum(
            kemeny_distance_matrices(candidate_matrix, m)
            for m in relations.values()
        )
        if total < best_total:
            best_total = total
            best_orders = [candidate]
        elif total == best_total:
            best_orders.append(candidate)

    return best_orders, int(best_total)

def kemeny_total_distance(order: List[str], relations: Dict[int, NamedMatrix], objects: List[str]) -> int:
    """Σ_k d(R, R_k) для конкретного ранжирования."""
    candidate_matrix = ranking_to_matrix(order, objects)
    return sum(
        kemeny_distance_matrices(candidate_matrix, m)
        for m in relations.values()
    )
