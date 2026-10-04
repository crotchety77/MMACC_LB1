from typing import Dict, List, Tuple

from .named_matrix import NamedMatrix


def get_binary_relations(table: Dict[int, Dict[str, int]], objects: List[str]) -> Dict[int, NamedMatrix]:
    """
    x(a, b) = 1, если rank(a) >= rank(b)  (a хуже или равно b).
    """
    result: Dict[int, NamedMatrix] = {}

    for expert, ranks in table.items():
        m = NamedMatrix(rows=objects, cols=objects, default=0)
        for a in objects:
            for b in objects:
                m[a, b] = 1 if ranks[a] >= ranks[b] else 0
        result[expert] = m

    return result

def kemeny_distance_matrices(a: NamedMatrix, b: NamedMatrix) -> int:
    """d(A, B) = Σ_i Σ_j |a(i, j) − b(i, j)|."""
    if set(a.rows) != set(b.rows) or set(a.cols) != set(b.cols):
        raise ValueError("Матрицы должны иметь одинаковые строки и столбцы")

    return sum(abs(a[i, j] - b[i, j]) for i in a.rows for j in a.cols)

def build_distance_matrix(relations: Dict[int, NamedMatrix]) -> NamedMatrix:
    """D[k1][k2] = расстояние Кемени между матрицами экспертов k1 и k2."""
    experts = list(relations.keys())
    labels = [str(k) for k in experts]

    distances = NamedMatrix(rows=labels, cols=labels, default=0)
    for k1 in experts:
        for k2 in experts:
            distances[str(k1), str(k2)] = kemeny_distance_matrices(
                relations[k1], relations[k2]
            )
    return distances

def diff_matrix(a: NamedMatrix, b: NamedMatrix) -> NamedMatrix:
    """|a(i, j) − b(i, j)|."""
    if a.rows != b.rows or a.cols != b.cols:
        raise ValueError("Матрицы должны иметь одинаковые строки и столбцы")

    result = NamedMatrix(a.rows, a.cols, default=0)
    for i in a.rows:
        for j in a.cols:
            result[i, j] = abs(a[i, j] - b[i, j])
    return result

def get_diff_relations_matrixes(relations: Dict[int, NamedMatrix]) -> Dict[Tuple[int, int], NamedMatrix]:
    """{(k1, k2): |A_k1 − A_k2|} для всех пар k1 < k2."""
    experts = list(relations.keys())
    result: Dict[Tuple[int, int], NamedMatrix] = {}

    for idx, k1 in enumerate(experts):
        for k2 in experts[idx + 1:]:
            result[(k1, k2)] = diff_matrix(relations[k1], relations[k2])

    return result
