from statistics import median
from typing import Dict, List, Tuple

from .transform import get_objects


def get_ranks_sum(table: Dict[int, Dict[str, int]]) -> Dict[str, int]:
    """{объект: сумма рангов по всем экспертам}"""
    ranks_sum: Dict[str, int] = {}
    for ranks in table.values():
        for obj, rank in ranks.items():
            ranks_sum[obj] = ranks_sum.get(obj, 0) + rank
    return ranks_sum

def get_ranks_average(ranks_sum: Dict[str, int], n_experts: int) -> Dict[str, float]:
    """{объект: средний ранг}"""
    return {obj: total / n_experts for obj, total in ranks_sum.items()}

def get_ranks_median(table: Dict[int, Dict[str, int]]) -> Dict[str, float]:
    """{объект: медианный ранг}"""
    ranks_by_object: Dict[str, List[int]] = {}
    for ranks in table.values():
        for obj, rank in ranks.items():
            ranks_by_object.setdefault(obj, []).append(rank)

    return {obj: median(values) for obj, values in ranks_by_object.items()}

def get_sorted_by_rank(
    ranks: Dict[str, float],
    ascending: bool = True,
) -> List[Tuple[str, float]]:
    """Сортирует объекты по значению (лучший — первый при ascending=True)."""
    return sorted(ranks.items(), key=lambda x: x[1], reverse=not ascending)

def assign_places(sorted_ranks: List[Tuple[str, float]]) -> List[Tuple[int, str, float]]:
    """
    Присваивает места с учётом ничьих (олимпийский принцип: 1, 2, 2, 4, 5).
    :return: [(место, объект, значение), ...]
    """
    result = []
    prev_value = None
    place = 0

    for i, (obj, value) in enumerate(sorted_ranks, start=1):
        if value != prev_value:
            place = i
            prev_value = value
        result.append((place, obj, value))

    return result

def get_ranking_by_average(table: Dict[int, Dict[str, int]]) -> List[Tuple[int, str, float]]:
    """Готовое ранжирование по среднему — удобный враппер."""
    ranks_sum = get_ranks_sum(table)
    ranks_avg = get_ranks_average(ranks_sum, len(table))
    return assign_places(get_sorted_by_rank(ranks_avg))

def get_ranking_by_median(table: Dict[int, Dict[str, int]]) -> List[Tuple[int, str, float]]:
    """Готовое ранжирование по медиане."""
    ranks_median = get_ranks_median(table)
    return assign_places(get_sorted_by_rank(ranks_median))
