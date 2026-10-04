from typing import Callable, Dict, List, Optional

from .config import object_sort_key


def transform_data(table: Dict[int, List[str]]) -> Dict[int, Dict[str, int]]:
    """
    {эксперт: [объекты в порядке предпочтения]} →
    {эксперт: {объект: ранг}}
    """
    return {
        expert: {obj: pos for pos, obj in enumerate(evaluations, start=1)}
        for expert, evaluations in table.items()
    }

def get_objects(table: Dict[int, Dict[str, int]], sort_func: Optional[Callable[[str], object]] = None) -> List[str]:
    """
    Собирает все уникальные объекты из всех экспертов и сортирует их.
    По умолчанию — по числовому суффиксу: a1 < a2 < a10.
    """
    objects = {obj for ranks in table.values() for obj in ranks}
    if sort_func is None:
        sort_func = object_sort_key
    return sorted(objects, key=sort_func)
