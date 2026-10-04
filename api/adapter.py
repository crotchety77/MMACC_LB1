from typing import Dict, List, Tuple

from expert_estimate.config import INPUT_SEPARATOR
from expert_estimate.kemeny import (
    get_all_assignment_medians,
    get_all_kemeny_medians_bruteforce,
    get_kemeny_medians_by_experts,
    get_kemeny_median_assignment,
    get_preference_vectors,
    get_row_sums,
    kemeny_total_distance,
)
from expert_estimate.named_matrix import NamedMatrix
from expert_estimate.relations import (
    build_distance_matrix,
    get_binary_relations,
    get_diff_relations_matrixes,
)
from expert_estimate.stats import (
    get_ranking_by_average,
    get_ranking_by_median,
)
from expert_estimate.transform import get_objects, transform_data

from .schemas import (
    AnalysisSummary,
    AnalyzeResponse,
    ExpertGraphData,
    ExpertGraphEdge,
    ExpertGraphNode,
    KemenyComparisonSummary,
    KemenyMedianSolution,
    KemenyMethodResult,
    MatrixData,
    RankingItem,
    RankingsData,
)


def parse_raw_text(text: str) -> Dict[int, List[str]]:
    """Парсит сырой текст, в котором каждая строка — ранжирование эксперта."""
    table: Dict[int, List[str]] = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines, start=1):
        table[idx] = line.split(INPUT_SEPARATOR)
    return table


def named_matrix_to_schema(matrix: NamedMatrix, name: str, description: str = "") -> MatrixData:
    """Преобразует существующий NamedMatrix в Pydantic MatrixData без изменения математики."""
    rows = [str(r) for r in matrix.rows]
    cols = [str(c) for c in matrix.cols]
    data: List[List[float]] = []
    for r in matrix.rows:
        row_values: List[float] = []
        for c in matrix.cols:
            val = matrix[r, c]
            row_values.append(float(val) if val is not None else 0.0)
        data.append(row_values)

    return MatrixData(
        name=name,
        description=description,
        rows=rows,
        cols=cols,
        data=data,
    )


def dict_to_matrix_schema(
    data_dict: Dict[int, Dict[str, int]],
    rows: List[str],
    cols: List[str],
    name: str,
    description: str = "",
) -> MatrixData:
    """Преобразует вложенный dict в MatrixData."""
    data: List[List[float]] = []
    for r in rows:
        expert_idx = int(r.replace("Э", "")) if r.startswith("Э") else int(r)
        row_dict = data_dict.get(expert_idx, {})
        data.append([float(row_dict.get(c, 0)) for c in cols])

    return MatrixData(
        name=name,
        description=description,
        rows=rows,
        cols=cols,
        data=data,
    )


def run_full_analysis(raw_table: Dict[int, List[str]]) -> AnalyzeResponse:
    """
    Вызывает функции существующего ядра expert_estimate напрямую
    и упаковывает результат в структуру AnalyzeResponse.
    """
    if not raw_table:
        raise ValueError("Таблица ранжирований пуста")

    # 1. Трансформация данных и сбор объектов
    transformed = transform_data(raw_table)
    objects = get_objects(transformed)
    experts = [f"Э{k}" for k in sorted(raw_table.keys())]

    # 2. Статистические ранжирования
    avg_ranking_raw = get_ranking_by_average(transformed)
    med_ranking_raw = get_ranking_by_median(transformed)

    ranking_average = [
        RankingItem(place=place, object=obj, value=round(val, 4))
        for place, obj, val in avg_ranking_raw
    ]
    ranking_median = [
        RankingItem(place=place, object=obj, value=round(val, 4))
        for place, obj, val in med_ranking_raw
    ]

    # 3. Векторы предпочтений
    preferences = get_preference_vectors(transformed, objects)

    # 4. Бинарные отношения
    relations = get_binary_relations(transformed, objects)

    # 5. Матрица расстояний
    distances = build_distance_matrix(relations)
    row_sums = get_row_sums(distances)

    # 6. Матрицы разностей
    diffs = get_diff_relations_matrixes(relations)

    # 7. Медианы Кемени: среди экспертов
    medians_experts_ids = get_kemeny_medians_by_experts(distances)
    best_expert_distance = min(row_sums.values()) if row_sums else 0

    expert_solutions: List[KemenyMedianSolution] = []
    for m in medians_experts_ids:
        ranks = transformed[int(m)]
        order = [obj for obj, _ in sorted(ranks.items(), key=lambda x: x[1])]
        d_total = kemeny_total_distance(order, relations, objects)
        expert_solutions.append(
            KemenyMedianSolution(
                order=order,
                order_str=" > ".join(order),
                total_distance=d_total,
                expert_id=f"Э{m}",
            )
        )

    # 8. Задача о назначениях
    _, _, loss_matrix, assignment_matrix_x = get_kemeny_median_assignment(transformed, objects)
    assignment_orders, assignment_total, _ = get_all_assignment_medians(transformed, objects)

    assignment_solutions: List[KemenyMedianSolution] = []
    for order in assignment_orders:
        d_total = kemeny_total_distance(order, relations, objects)
        assignment_solutions.append(
            KemenyMedianSolution(
                order=order,
                order_str=" > ".join(order),
                total_distance=d_total,
                loss_value=assignment_total,
            )
        )

    # 9. Полный перебор (Bruteforce)
    bruteforce_orders, bruteforce_total = get_all_kemeny_medians_bruteforce(relations, objects)
    bruteforce_solutions: List[KemenyMedianSolution] = [
        KemenyMedianSolution(
            order=order,
            order_str=" > ".join(order),
            total_distance=bruteforce_total,
        )
        for order in bruteforce_orders
    ]

    # 10. Сравнение методов
    set_experts = {
        tuple(obj for obj, _ in sorted(transformed[int(m)].items(), key=lambda x: x[1]))
        for m in medians_experts_ids
    }
    set_assignment = {tuple(order) for order in assignment_orders}
    set_bruteforce = {tuple(order) for order in bruteforce_orders}

    intersection_exp_bf = len(set_experts & set_bruteforce)
    intersection_as_bf = len(set_assignment & set_bruteforce)
    assignment_is_subset = set_assignment <= set_bruteforce
    all_agree = (set_experts == set_bruteforce) and (set_assignment == set_bruteforce)

    comparison = KemenyComparisonSummary(
        intersection_experts_bruteforce=intersection_exp_bf,
        intersection_assignment_bruteforce=intersection_as_bf,
        assignment_is_subset_of_bruteforce=assignment_is_subset,
        all_methods_agree=all_agree,
    )

    # 11. Матрицы
    matrix_transformed = dict_to_matrix_schema(
        transformed,
        experts,
        objects,
        name="Матрица рангов (Эксперт × Объект)",
        description="Ранг каждого объекта, выставленный экспертом (1 — лучший ранг)",
    )
    matrix_preferences = dict_to_matrix_schema(
        preferences,
        experts,
        objects,
        name="Векторы предпочтений π^(k)",
        description="Количество альтернатив, которые данный эксперт считает строго лучше указанного объекта",
    )
    matrix_distances = named_matrix_to_schema(
        distances,
        name="Матрица расстояний Кемени между экспертами (D)",
        description="Попарные расстояния Кемени между матрицами бинарных отношений экспертов",
    )
    matrix_loss = named_matrix_to_schema(
        loss_matrix,
        name="Матрица потерь r_ij",
        description="Элементы r_ij = Σ_k |(j-1) - π_i^(k)| для задачи о назначениях",
    )
    matrix_assignment = named_matrix_to_schema(
        assignment_matrix_x,
        name="Матрица назначений X",
        description="Бинарная матрица решения задачи о назначениях (1 — объекту присвоен данный ранг)",
    )

    binary_relations_schemas: Dict[str, MatrixData] = {
        f"Э{k}": named_matrix_to_schema(
            m,
            name=f"Бинарное отношение эксперта Э{k}",
            description=f"x(a, b) = 1 если ранг a >= ранг b (объект a не лучше b для Э{k})",
        )
        for k, m in relations.items()
    }

    diff_matrices_schemas: Dict[str, MatrixData] = {
        f"|Э{k1} - Э{k2}|": named_matrix_to_schema(
            m,
            name=f"Разность отношений |Э{k1} - Э{k2}|",
            description=f"Поэлементный модуль разности бинарных матриц экспертов Э{k1} и Э{k2}",
        )
        for (k1, k2), m in diffs.items()
    }

    # 12. Построение графа экспертов
    max_distance = max([int(distances[str(k1), str(k2)]) for k1 in raw_table for k2 in raw_table], default=1)
    if max_distance == 0:
        max_distance = 1

    graph_nodes: List[ExpertGraphNode] = []
    for k in sorted(raw_table.keys()):
        k_str = str(k)
        is_med = k_str in medians_experts_ids
        r_list = raw_table[k]
        graph_nodes.append(
            ExpertGraphNode(
                id=f"Э{k}",
                label=f"Эксперт {k}",
                ranking=r_list,
                ranking_str=" > ".join(r_list),
                sum_distance=row_sums.get(k_str, 0),
                is_median=is_med,
            )
        )

    graph_edges: List[ExpertGraphEdge] = []
    expert_keys = sorted(raw_table.keys())
    for i_idx, k1 in enumerate(expert_keys):
        for k2 in expert_keys[i_idx + 1:]:
            d_val = int(distances[str(k1), str(k2)])
            sim = round(max(0.0, 1.0 - (d_val / max_distance)), 4)
            graph_edges.append(
                ExpertGraphEdge(
                    source=f"Э{k1}",
                    target=f"Э{k2}",
                    distance=d_val,
                    similarity=sim,
                )
            )

    raw_rankings_dict = {f"Э{k}": v for k, v in raw_table.items()}
    unique_rankings = len({tuple(v) for v in raw_table.values()})

    summary = AnalysisSummary(
        num_experts=len(raw_table),
        num_objects=len(objects),
        unique_rankings_count=unique_rankings,
        best_kemeny_orders=bruteforce_orders,
        best_kemeny_distance=bruteforce_total,
        is_consensus_perfect=(bruteforce_total == 0),
    )

    return AnalyzeResponse(
        experts=experts,
        objects=objects,
        raw_rankings=raw_rankings_dict,
        summary=summary,
        rankings=RankingsData(average=ranking_average, median=ranking_median),
        matrices={
            "transformed": matrix_transformed,
            "preferences": matrix_preferences,
            "distance": matrix_distances,
            "loss": matrix_loss,
            "assignment": matrix_assignment,
        },
        binary_relations=binary_relations_schemas,
        diff_matrices=diff_matrices_schemas,
        kemeny={
            "expert_method": KemenyMethodResult(
                title="Медиана Кемени среди экспертов",
                criterion_name="Сумма расстояний по матрице D",
                criterion_value=best_expert_distance,
                solutions=expert_solutions,
            ),
            "assignment_method": KemenyMethodResult(
                title="Медиана через задачу о назначениях",
                criterion_name="Минимум суммарных потерь Σ r_ij",
                criterion_value=assignment_total,
                solutions=assignment_solutions,
            ),
            "bruteforce_method": KemenyMethodResult(
                title="Истинная медиана Кемени (полный перебор)",
                criterion_name="Минимальная сумма расстояний Кемени Σ d(R, R_k)",
                criterion_value=bruteforce_total,
                solutions=bruteforce_solutions,
            ),
        },
        comparison=comparison,
        graph=ExpertGraphData(nodes=graph_nodes, edges=graph_edges),
    )
