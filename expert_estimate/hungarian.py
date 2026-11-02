"""
Венгерский метод (алгоритм Куна — Манкреса) для решения задачи о назначениях.
Сложность: O(n^3).
Реализация на чистом Python без внешних зависимостей.
"""
from typing import List, Tuple, Union


def hungarian_algorithm(
    cost_matrix: List[List[Union[int, float]]]
) -> Tuple[List[int], Union[int, float]]:
    """
    Решает задачу о назначениях на минимум (Linear Sum Assignment Problem)
    венгерским методом (алгоритм Куна — Манкреса с модификацией потенциалов) за O(n^3).

    :param cost_matrix: квадратная матрица стоимостей (потерь) размера n x n.
    :return: (assignment, min_cost)
        - assignment: список длины n, где assignment[i] = j означает,
          что объект (строка) i назначен на позицию (столбец) j (0-based индексация).
        - min_cost: точная минимальная сумма стоимостей назначений.
    """
    n = len(cost_matrix)
    if n == 0:
        return [], 0

    for i, row in enumerate(cost_matrix):
        if len(row) != n:
            raise ValueError(f"Строка {i} имеет длину {len(row)}, ожидалось {n} (матрица должна быть n x n)")

    # Проверка целочисленности для точного приведения типов
    all_ints = all(isinstance(val, int) for row in cost_matrix for val in row)

    # Массивы для потенциалов и пути (1-based индексация с фиктивным элементом 0)
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)

        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0

            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost_matrix[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [-1] * n
    for j in range(1, n + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1

    total_cost = sum(cost_matrix[i][assignment[i]] for i in range(n))
    if all_ints:
        total_cost = int(round(total_cost))

    return assignment, total_cost

