# -*- coding: utf-8 -*-
"""
Главный модуль консольного интерфейса (CLI) лабораторной работы №1:
«Исследование сложных систем методом экспертных оценок».

Обеспечивает интерактивное академическое взаимодействие, пошаговое выполнение этапов,
интерактивный ввод суждений с валидацией, детальные пояснения и аналитическую интерпретацию.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_INPUT
from .io import read_data
from .transform import transform_data, get_objects
from .stats import (
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
    get_all_assignment_medians,
    get_all_kemeny_medians_bruteforce,
)
from .printers import (
    print_raw_data,
    print_transformed_data,
    print_ranking_by_average,
    print_ranking_by_median,
    print_preference_vectors,
    print_binary_relations,
    print_distance_matrix,
    print_diff_relations_matrixes,
    print_kemeny_median_by_experts,
    print_kemeny_assignment,
    print_kemeny_bruteforce,
    print_kemeny_comparison,
    print_analytical_interpretation,
)


class Context:
    """Контекст сессии: хранит активные данные и кеширует промежуточные результаты."""

    def __init__(self, filepath: str = DEFAULT_INPUT) -> None:
        self.source_label = filepath
        self.filepath = filepath
        self.raw: Dict[int, List[str]] = {}
        self.transformed: Dict[int, Dict[str, int]] = {}
        self.objects: List[str] = []
        self.preferences: Dict[int, Dict[str, int]] = {}
        self.relations: Dict[int, object] = {}
        self.distances = None
        self.diffs = {}
        self.sums: Dict[str, int] = {}
        self.medians_experts: List[str] = []
        self.assignment = None
        self.bruteforce = None

    def reset_cache(self) -> None:
        """Сбрасывает кеш вычислений при изменении входных данных."""
        self.preferences = {}
        self.relations = {}
        self.distances = None
        self.diffs = {}
        self.sums = {}
        self.medians_experts = []
        self.assignment = None
        self.bruteforce = None

    def load(self, filepath: Optional[str] = None) -> None:
        """Загружает данные из файла."""
        target_path = filepath or self.filepath
        self.raw = read_data(target_path)
        self.filepath = target_path
        self.source_label = target_path
        self.transformed = transform_data(self.raw)
        self.objects = get_objects(self.transformed)
        self.reset_cache()

    def set_data(self, raw_table: Dict[int, List[str]], label: str = "Ввод с клавиатуры") -> None:
        """Устанавливает данные, введённые пользователем вручную."""
        self.raw = raw_table
        self.source_label = label
        self.transformed = transform_data(self.raw)
        self.objects = get_objects(self.transformed)
        self.reset_cache()


# =========================================================================
# ВЫПОЛНЕНИЕ ЭТАПОВ
# =========================================================================

def run_stage(code: str, ctx: Context) -> None:
    """Выполняет выбранный этап анализа с ленивым расчётом зависимостей."""

    if code == "1":
        # Протоколы и матрица рангов
        print_raw_data(ctx.raw)
        print_transformed_data(ctx.transformed, ctx.objects)

    elif code == "2":
        # Средние ранги
        print_ranking_by_average(
            {obj: r for _, obj, r in get_ranking_by_average(ctx.transformed)}
        )

    elif code == "3":
        # Медианные ранги
        print_ranking_by_median(
            {obj: r for _, obj, r in get_ranking_by_median(ctx.transformed)}
        )

    elif code == "4":
        # Бинарные отношения и расстояния Кемени
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.distances is None:
            ctx.distances = build_distance_matrix(ctx.relations)
        if not ctx.sums:
            ctx.sums = get_row_sums(ctx.distances)
        if not ctx.medians_experts:
            ctx.medians_experts = get_kemeny_medians_by_experts(ctx.distances)

        print_binary_relations(ctx.relations)
        print_distance_matrix(ctx.distances)
        print_kemeny_median_by_experts(
            ctx.distances, ctx.transformed, ctx.medians_experts, ctx.sums
        )

    elif code == "5":
        # Векторы предпочтений и матрица потерь
        if not ctx.preferences:
            ctx.preferences = get_preference_vectors(ctx.transformed, ctx.objects)
        print_preference_vectors(ctx.preferences, ctx.objects)

    elif code == "6":
        # Задача о назначениях
        orders, total, loss = get_all_assignment_medians(ctx.transformed, ctx.objects)
        ctx.assignment = (orders, total, loss)
        print_kemeny_assignment(orders, total, loss)

    elif code == "7":
        # Истинная медиана Кемени (полный перебор)
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        orders, total = get_all_kemeny_medians_bruteforce(ctx.relations, ctx.objects)
        ctx.bruteforce = (orders, total)
        print_kemeny_bruteforce(orders, total, num_checked=120 if len(ctx.objects) == 5 else len(orders))

    elif code == "8":
        # Сводное сопоставление подходов
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.distances is None:
            ctx.distances = build_distance_matrix(ctx.relations)
        if not ctx.medians_experts:
            ctx.medians_experts = get_kemeny_medians_by_experts(ctx.distances)

        if ctx.assignment is None:
            ctx.assignment = get_all_assignment_medians(ctx.transformed, ctx.objects)
        if ctx.bruteforce is None:
            ctx.bruteforce = get_all_kemeny_medians_bruteforce(ctx.relations, ctx.objects)

        assign_orders, assign_total, _ = ctx.assignment
        kemeny_orders, kemeny_total = ctx.bruteforce

        print_kemeny_comparison(
            relations=ctx.relations,
            objects=ctx.objects,
            transformed=ctx.transformed,
            distances=ctx.distances,
            medians_experts=ctx.medians_experts,
            assignment_orders=assign_orders,
            assignment_total=assign_total,
            bruteforce_orders=kemeny_orders,
            bruteforce_total=kemeny_total,
        )

    elif code == "9":
        # Итоговая аналитическая интерпретация
        if not ctx.relations:
            ctx.relations = get_binary_relations(ctx.transformed, ctx.objects)
        if ctx.assignment is None:
            ctx.assignment = get_all_assignment_medians(ctx.transformed, ctx.objects)
        if ctx.bruteforce is None:
            ctx.bruteforce = get_all_kemeny_medians_bruteforce(ctx.relations, ctx.objects)

        assign_orders, assign_total, _ = ctx.assignment
        kemeny_orders, kemeny_total = ctx.bruteforce

        print_analytical_interpretation(
            table=ctx.transformed,
            objects=ctx.objects,
            relations=ctx.relations,
            assignment_orders=assign_orders,
            assignment_total=assign_total,
            bruteforce_orders=kemeny_orders,
            bruteforce_total=kemeny_total,
        )


# =========================================================================
# ИНТЕРАКТИВНЫЙ ВВОД ДАННЫХ С КЛАВИАТУРЫ
# =========================================================================

def input_custom_rankings(ctx: Context) -> None:
    """Обеспечивает дружественный пошаговый ввод данных экспертов с валидацией."""
    print("\n" + "═" * 76)
    print("  ИНТЕРАКТИВНЫЙ ВВОД СУЖДЕНИЙ ЭКСПЕРТОВ")
    print("═" * 76)
    print("Вы можете ввести собственные экспертные оценки для анализа.")

    # 1. Запрос объектов
    default_objs_str = " ".join(ctx.objects) if ctx.objects else "a1 a2 a3 a4 a5"
    print(f"\nВведите список исследуемых альтернатив через пробел.")
    print(f"[Нажмите Enter для использования по умолчанию: {default_objs_str}]")
    try:
        user_objs = input("Альтернативы: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nВвод отменён.")
        return

    if user_objs:
        target_objects = user_objs.split()
    else:
        target_objects = default_objs_str.split()

    target_set = set(target_objects)
    n = len(target_objects)

    # 2. Количество экспертов
    print(f"\nВведите количество экспертов в комиссии (например, 5):")
    while True:
        try:
            m_input = input("Количество экспертов: ").strip()
            m = int(m_input)
            if m < 2:
                print("⚠ В комиссии должно быть как минимум 2 эксперта. Попробуйте снова.")
                continue
            break
        except ValueError:
            print("⚠ Пожалуйста, введите целое положительное число.")
        except (EOFError, KeyboardInterrupt):
            print("\nВвод отменён.")
            return

    # 3. Ввод суждений для каждого эксперта
    print("\n────────────────────────────────────────────────────────────────────────────")
    print(f"Введите ранжирование для каждого эксперта.")
    print(f"Порядок ввода: от наиболее предпочтительной альтернативы к наименее.")
    print(f"Допустимые обозначения проектов: {' '.join(target_objects)}")
    print("────────────────────────────────────────────────────────────────────────────")

    new_table: Dict[int, List[str]] = {}

    for k in range(1, m + 1):
        while True:
            try:
                print(f"\nЭксперт Э{k}:")
                line = input(f"Ранжирование Э{k} > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nВвод прерван.")
                return

            if not line:
                print("⚠ Строка не может быть пустой. Попробуйте снова.")
                continue

            tokens = line.split()

            if len(tokens) != n:
                print(f"⚠ Неверное число проектов ({len(tokens)} вместо {n}).")
                print(f"   Каждый из {n} проектов должен присутствовать ровно один раз.")
                continue

            tokens_set = set(tokens)
            missing = target_set - tokens_set
            unknown = tokens_set - target_set

            if unknown:
                print(f"⚠ Обнаружены неизвестные обозначения: {', '.join(unknown)}.")
                print(f"   Ожидались только: {' '.join(target_objects)}.")
                continue

            if missing:
                print(f"⚠ Пропущены обязательные проекты: {', '.join(missing)}.")
                continue

            # Успешный ввод
            new_table[k] = tokens
            print(f"✓ Ранжирование эксперта Э{k} принято: {' ≻ '.join(tokens)}")
            break

    # 4. Вопрос о сохранении в файл
    print("\n✓ Все суждения экспертов успешно приняты!")
    try:
        save_choice = input("Сохранить эти данные в файл input.txt? (y/n, по умолчанию n): ").strip().lower()
        if save_choice in ("y", "yes", "д", "да"):
            with open("input.txt", "w", encoding="utf-8") as f:
                for k in sorted(new_table.keys()):
                    f.write(" ".join(new_table[k]) + "\n")
            print("✓ Данные сохранены в файл input.txt.")
            ctx.set_data(new_table, label="input.txt (обновлён)")
        else:
            ctx.set_data(new_table, label="Пользовательский ввод (в памяти)")
    except Exception as e:
        print(f"⚠ Не удалось сохранить в файл: {e}")
        ctx.set_data(new_table, label="Пользовательский ввод (в памяти)")

    print("✓ Текущий контекст обновлён. Теперь вы можете запустить анализ.")


# =========================================================================
# ГЛАВНОЕ МЕНЮ И ЦИКЛ ВЗАИМОДЕЙСТВИЯ (REPL)
# =========================================================================

def print_menu(ctx: Context) -> None:
    """Выводит стилизованное главное меню программы."""
    m_exp = len(ctx.raw)
    n_obj = len(ctx.objects)

    print()
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║        ИССЛЕДОВАНИЕ СЛОЖНЫХ СИСТЕМ МЕТОДОМ ЭКСПЕРТНЫХ ОЦЕНОК (ММАСС)         ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"  Источник данных: {ctx.source_label}  |  Экспертов: {m_exp}  |  Альтернатив: {n_obj}")
    print("────────────────────────────────────────────────────────────────────────────────")
    print("  1. Исходные суждения экспертов и матрица рангов")
    print("  2. Метод средних арифметических рангов")
    print("  3. Метод медианных рангов (робастная статистика)")
    print("  4. Бинарные отношения и расстояния Кемени (матрица D, суммы S_k)")
    print("  5. Векторы предпочтений π^(k) и матрица позиционных потерь")
    print("  6. Задача о назначениях (минимизация позиционных потерь Φ_Assign)")
    print("  7. Истинная медиана Кемени (полный перебор всех n! перестановок)")
    print("  8. Сводное сопоставление результатов всех методов")
    print("  9. Итоговая аналитическая интерпретация группового выбора")
    print("────────────────────────────────────────────────────────────────────────────────")
    print("  a. Выполнить полный расчёт (все этапы с аналитикой)")
    print("  i. Ввести новые данные экспертов с клавиатуры")
    print("  f. Загрузить данные из другого файла")
    print("  0. Завершить работу программы")
    print("────────────────────────────────────────────────────────────────────────────────")


def parse_user_choice(choice_str: str) -> List[str]:
    """Разбирает выбор пользователя в упорядоченный список этапов."""
    choice = choice_str.strip().lower()
    if choice in ("a", "all", "все"):
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    valid_stages = []
    # Поддерживаем ввод через пробел, запятую или подряд: "1 2 3" или "2, 3"
    tokens = choice.replace(",", " ").split()
    for tok in tokens:
        if tok in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            valid_stages.append(tok)

    return valid_stages


def repl(ctx: Context) -> None:
    """Главный интерактивный цикл управления."""
    while True:
        print_menu(ctx)
        try:
            choice = input("Выберите пункт меню > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\nРабота программы завершена. До свидания!")
            return

        if not choice:
            continue

        if choice in ("0", "q", "quit", "exit", "вых", "выход"):
            print("\nРабота программы успешно завершена. Спасибо за использование системы экспертных оценок!")
            return

        if choice == "i":
            input_custom_rankings(ctx)
            continue

        if choice == "f":
            try:
                new_path = input("\nВведите путь к файлу с данными: ").strip()
                if not new_path:
                    print("⚠ Путь не указан.")
                    continue
                ctx.load(new_path)
                print(f"✓ Успешно загружен файл: {new_path}")
            except FileNotFoundError:
                print(f"⚠ Ошибка: файл не найден по пути '{new_path}'.")
            except Exception as e:
                print(f"⚠ Ошибка чтения файла: {e}")
            continue

        stages = parse_user_choice(choice)
        if not stages:
            print("⚠ Неизвестный пункт меню. Пожалуйста, укажите номер от 1 до 9, 'a', 'i', 'f' или '0'.")
            continue

        for stage_code in stages:
            try:
                run_stage(stage_code, ctx)
            except Exception as err:
                print(f"⚠ Ошибка при выполнении этапа {stage_code}: {err}")

        # Удобная пауза для изучения результатов перед обновлением меню
        print("\n" + "─" * 76)
        try:
            input("Нажмите Enter для возврата в главное меню (или 0 для выхода)... ")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота программы завершена.")
            return


# =========================================================================
# ТОЧКА ВХОДА CLI
# =========================================================================

def main() -> None:
    """Точка входа консольного приложения."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    target_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    ctx = Context(target_file)

    try:
        ctx.load()
    except FileNotFoundError:
        print(f"⚠ Файл '{target_file}' не найден. Создаём сессию по умолчанию.")
        ctx = Context(DEFAULT_INPUT)

    repl(ctx)


if __name__ == "__main__":
    main()
