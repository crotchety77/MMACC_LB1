import sys

from .config import DEFAULT_INPUT, STAGES
from .io import read_data
from .transform import transform_data, get_objects
from .stats import (
    get_ranks_sum,
    get_ranks_average,
    get_ranks_median,
    get_ranking_by_average,
    get_ranking_by_median,
)
from .relations import (
    get_binary_relations,
    build_distance_matrix,
    get_diff_relations_matrixes,
)
from .kemeny import (
    get_row_sums,
    get_preference_vectors,
    get_kemeny_medians_by_experts,
    get_kemeny_median_assignment,
    get_all_assignment_medians,
    get_all_kemeny_medians_bruteforce,
)
from .printers import (
    print_raw_data,
    print_transformed_data,
    print_ranking,
    print_preference_vectors,
    print_binary_relations,
    print_distance_matrix,
    print_diff_relations_matrixes,
    print_kemeny_median_by_experts,
    print_kemeny_assignment,
    print_kemeny_comparison,
)

# Названия этапов для меню
STAGE_TITLES = {
    "raw":               "Исходные данные",
    "transformed":       "Матрица Эксперт × Объект",
    "average":           "Ранжирование по среднему",
    "median":            "Ранжирование по медиане",
    "preferences":       "Векторы предпочтений π^(k)",
    "relations":         "Матрицы бинарных отношений",
    "distances":         "Матрица расстояний Кемени",
    "diffs":             "Матрицы разностей |A − B|",
    "kemeny_experts":    "Медиана Кемени (среди экспертов)",
    "kemeny_assignment": "Медиана Кемени (задача о назначениях)",
    "kemeny_bruteforce": "Медиана Кемени (полный перебор)",
    "kemeny_compare":    "Сравнение подходов к медиане",
}

class Context:
    """Хранит промежуточные результаты, чтобы не считать их дважды."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.raw = {}
        self.transformed = {}
        self.objects = []
        self.preferences = {}
        self.relations = {}
        self.distances = None
        self.diffs = {}
        self.sums = {}
        self.medians_experts = []
        self.assignment = None
        self.bruteforce = None

    def load(self) -> None:
        self.raw = read_data(self.filepath)
        self.transformed = transform_data(self.raw)
        self.objects = get_objects(self.transformed)

def run_stage(stage: str, ctx: Context) -> None:
    """Выполняет один этап (с ленивым расчётом зависимостей)."""

    if stage == "raw":
        print_raw_data(ctx.raw)

    elif stage == "transformed":
        print_transformed_data(ctx.transformed, ctx.objects)

    elif stage == "average":
        print_ranking(
            "Итоговое ранжирование по среднему",
            get_ranking_by_average(ctx.transformed),
            "средний ранг",
        )

    elif stage == "median":
        print_ranking(
            "Итоговое ранжирование по медиане",
            get_ranking_by_median(ctx.transformed),
            "медиана",
        )

    elif stage == "preferences":
        if not ctx.preferences:
            ctx.preferences = get_preference_vectors(ctx.transformed, ctx.objects)
        print_preference_vectors(ctx.preferences, ctx.objects)

    elif stage == "relations":
        ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        print_binary_relations(ctx.relations)

    elif stage == "distances":
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        ctx.distances = build_distance_matrix(ctx.relations)
        print_distance_matrix(ctx.distances)

    elif stage == "diffs":
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.distances is None:
            ctx.distances = build_distance_matrix(ctx.relations)
        ctx.diffs = get_diff_relations_matrixes(ctx.relations)
        print_diff_relations_matrixes(ctx.diffs, ctx.distances)

    elif stage == "kemeny_experts":
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.distances is None:
            ctx.distances = build_distance_matrix(ctx.relations)
        ctx.sums = get_row_sums(ctx.distances)
        ctx.medians_experts = get_kemeny_medians_by_experts(ctx.distances)
        print_kemeny_median_by_experts(
            ctx.distances, ctx.transformed, ctx.medians_experts, ctx.sums
        )

    elif stage == "kemeny_assignment":
        orders, total, loss = get_all_assignment_medians(
            ctx.transformed,
            ctx.objects,
        )

        ctx.assignment = (orders, total, loss)

        print_kemeny_assignment(
            orders,
            total,
            loss,
        )

    elif stage == "kemeny_bruteforce":
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        orders, total = get_all_kemeny_medians_bruteforce(
            ctx.relations, ctx.objects
        )
        ctx.bruteforce = (orders, total)
        print(f"\nПроверка (полный перебор), все оптимумы (Σ = {total}):")
        for o in orders:
            print(f"   {' > '.join(o)}")
    
    elif stage == "kemeny_compare":
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.distances is None:
            ctx.distances = build_distance_matrix(ctx.relations)
        if not ctx.sums:
            ctx.sums = get_row_sums(ctx.distances)
        if not ctx.medians_experts:
            ctx.medians_experts = get_kemeny_medians_by_experts(ctx.distances)

        if ctx.assignment is None:
            ctx.assignment = get_all_assignment_medians(
                ctx.transformed,
                ctx.objects,
            )

        if ctx.bruteforce is None:
            ctx.bruteforce = get_all_kemeny_medians_bruteforce(
                ctx.relations,
                ctx.objects,
            )

        assignment_orders, assignment_total, _ = ctx.assignment
        bruteforce_orders, bruteforce_total = ctx.bruteforce

        print_kemeny_comparison(
            relations=ctx.relations,
            objects=ctx.objects,
            transformed=ctx.transformed,
            distances=ctx.distances,
            medians_experts=ctx.medians_experts,
            assignment_orders=assignment_orders,
            assignment_total=assignment_total,
            bruteforce_orders=bruteforce_orders,
            bruteforce_total=bruteforce_total,
        )

# ---------- меню ----------

def print_menu(ctx: Context) -> None:
    print()
    print(f"Файл: {ctx.filepath}   (экспертов: {len(ctx.raw)}, объектов: {len(ctx.objects)})")
    print("-" * 50)
    for i, stage in enumerate(STAGES, start=1):
        print(f"  {i:>2}. {STAGE_TITLES.get(stage, stage)}")
    print("   0. Выход")
    print("   a. Все этапы")
    print("   f. Сменить файл")

def parse_choice(choice: str) -> list[str]:
    """Разбирает ввод пользователя в список этапов."""
    choice = choice.strip().lower()

    if choice == "a":
        return list(STAGES)

    stages = []
    for token in choice.replace(",", " ").split():
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(STAGES):
                stages.append(STAGES[idx])
    return stages

def repl(ctx: Context) -> None:
    print("=== Выбор вывода ===")

    while True:
        print_menu(ctx)
        try:
            choice = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            return

        if choice in ("0", "q", "quit", "exit"):
            print("Выход.")
            return

        if choice == "f":
            path = input("Путь к файлу: ").strip()
            if not path:
                continue
            try:
                ctx.filepath = path
                ctx.load()
                print(f"Загружено: {ctx.filepath}")
            except FileNotFoundError:
                print(f"Файл не найден: {path}")
            continue

        stages = parse_choice(choice)
        if not stages:
            continue

        for stage in stages:
            print()
            run_stage(stage, ctx)

        # ----- пауза после выполнения -----
        print()
        try:
            again = input("Enter или 0: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            return

        if again in ("0", "q", "quit", "exit"):
            print("Выход.")
            return

# ---------- main ----------

def main() -> None:
    filepath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT

    ctx = Context(filepath)
    try:
        ctx.load()
    except FileNotFoundError:
        print(f"Файл не найден: {filepath}")
        # Всё равно даём шанс ввести другой файл в интерактиве
        ctx = Context(DEFAULT_INPUT)

    repl(ctx)

if __name__ == "__main__":
    main()
