from pathlib import Path
from typing import Dict, List

from .config import INPUT_SEPARATOR


def read_data(filepath: str) -> Dict[int, List[str]]:
    """
    Читает данные экспертов из файла.
    :return: {номер эксперта: [объекты в порядке предпочтения]}
    """
    table: Dict[int, List[str]] = {}

    with open(Path(filepath), encoding="utf-8") as file:
        for expert_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            table[expert_num] = line.split(INPUT_SEPARATOR)

    return table
