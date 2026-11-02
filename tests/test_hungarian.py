import random
import unittest
from itertools import permutations

from expert_estimate.hungarian import hungarian_algorithm
from expert_estimate.io import read_data
from expert_estimate.kemeny import (
    build_loss_matrix,
    get_all_assignment_optima,
    get_preference_vectors,
    solve_assignment,
    solve_assignment_bruteforce,
    solve_assignment_hungarian,
)
from expert_estimate.named_matrix import NamedMatrix
from expert_estimate.transform import get_objects, transform_data


class TestHungarianAlgorithm(unittest.TestCase):
    def test_variant_6_baseline(self):
        """Проверка исходных данных варианта 6 (input.txt):
        потери должны составить 30, назначение: a1 -> 1, a2 -> 2, a5 -> 3, a3 -> 4, a4 -> 5."""
        raw_table = read_data("input.txt")
        transformed = transform_data(raw_table)
        objects = get_objects(transformed)

        pv = get_preference_vectors(transformed, objects)
        loss = build_loss_matrix(pv, objects)

        # 1. Венгерский метод (основной решатель)
        h_places, h_total, h_order = solve_assignment_hungarian(loss, objects)
        self.assertEqual(h_total, 30, "Потери по венгерскому методу должны быть 30")
        self.assertEqual(
            h_order,
            ["a1", "a2", "a5", "a3", "a4"],
            "Порядок ранжирования венгерского метода должен быть a1 > a2 > a5 > a3 > a4",
        )
        expected_places = {"a1": 1, "a2": 2, "a5": 3, "a3": 4, "a4": 5}
        self.assertEqual(h_places, expected_places)

        # 2. Полный перебор (независимый проверочный механизм)
        bf_orders, bf_total = solve_assignment_bruteforce(loss, objects)
        self.assertEqual(bf_total, 30, "Потери по полному перебору должны быть 30")
        self.assertEqual(bf_orders, [["a1", "a2", "a5", "a3", "a4"]])

        # 3. Фасадные функции
        places, total = solve_assignment(loss, objects)
        self.assertEqual(total, 30)
        self.assertEqual(places, expected_places)

        all_orders, all_total = get_all_assignment_optima(loss, objects)
        self.assertEqual(all_total, 30)
        self.assertEqual(all_orders, [["a1", "a2", "a5", "a3", "a4"]])

    def test_variant_v2(self):
        """Проверка второго датасета input_v2.txt."""
        raw_table = read_data("input_v2.txt")
        transformed = transform_data(raw_table)
        objects = get_objects(transformed)

        pv = get_preference_vectors(transformed, objects)
        loss = build_loss_matrix(pv, objects)

        h_places, h_total, h_order = solve_assignment_hungarian(loss, objects)
        bf_orders, bf_total = solve_assignment_bruteforce(loss, objects)

        self.assertEqual(h_total, 24)
        self.assertEqual(bf_total, 24)
        self.assertIn(h_order, bf_orders)
        self.assertEqual(h_order, ["a2", "a4", "a5", "a3", "a1"])

    def test_multiple_optimal_assignments(self):
        """Проверка матрицы с несколькими оптимальными назначениями (наличие ничьих)."""
        # 3 объекта, 3 места. Объекты a1 и a2 эквивалентны по стоимости для мест 1 и 2.
        # Матрица потерь:
        # a1: [10, 10, 50]
        # a2: [10, 10, 50]
        # a3: [40, 40,  5]
        # Оптимальные назначения:
        # Вариант 1: a1 -> 1, a2 -> 2, a3 -> 3 (стоимость: 10 + 10 + 5 = 25)
        # Вариант 2: a1 -> 2, a2 -> 1, a3 -> 3 (стоимость: 10 + 10 + 5 = 25)
        objects = ["a1", "a2", "a3"]
        loss = NamedMatrix(rows=objects, cols=["1", "2", "3"], default=0)
        loss["a1", "1"] = 10
        loss["a1", "2"] = 10
        loss["a1", "3"] = 50
        loss["a2", "1"] = 10
        loss["a2", "2"] = 10
        loss["a2", "3"] = 50
        loss["a3", "1"] = 40
        loss["a3", "2"] = 40
        loss["a3", "3"] = 5

        h_places, h_total, h_order = solve_assignment_hungarian(loss, objects)
        bf_orders, bf_total = solve_assignment_bruteforce(loss, objects)

        # 1. Минимумы строго совпадают
        self.assertEqual(h_total, 25)
        self.assertEqual(bf_total, 25)

        # 2. Перебор находит ровно два оптимума
        self.assertEqual(len(bf_orders), 2)
        expected_orders = [["a1", "a2", "a3"], ["a2", "a1", "a3"]]
        self.assertEqual(sorted(bf_orders), sorted(expected_orders))

        # 3. Решение венгерского метода гарантированно входит в число оптимумов
        self.assertIn(h_order, bf_orders)

        # 4. get_all_assignment_optima возвращает оба решения, ставя венгерское первым
        all_optima, total_opt = get_all_assignment_optima(loss, objects)
        self.assertEqual(total_opt, 25)
        self.assertEqual(len(all_optima), 2)
        self.assertEqual(all_optima[0], h_order)
        self.assertEqual(set(tuple(o) for o in all_optima), set(tuple(o) for o in expected_orders))

    def test_random_matrices_equivalence(self):
        """Сравнение венгерского метода и полного перебора на 50 случайных матрицах."""
        random.seed(42)
        for _ in range(50):
            n = random.randint(2, 6)
            matrix = [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]

            # Венгерский алгоритм
            assign, h_cost = hungarian_algorithm(matrix)

            # Проверка корректности перестановки
            self.assertEqual(sorted(assign), list(range(n)))
            recomputed_cost = sum(matrix[i][assign[i]] for i in range(n))
            self.assertEqual(h_cost, recomputed_cost)

            # Полный перебор
            bf_min_cost = min(
                sum(matrix[i][perm[i]] for i in range(n))
                for perm in permutations(range(n))
            )

            # Минимум целевой функции обязан быть строго идентичным
            self.assertEqual(h_cost, bf_min_cost)

    def test_edge_cases(self):
        """Проверка граничных случаев."""
        # 1. Матрица 1x1
        mat1 = [[17]]
        assign1, cost1 = hungarian_algorithm(mat1)
        self.assertEqual(assign1, [0])
        self.assertEqual(cost1, 17)

        # 2. Матрица 2x2
        mat2 = [[10, 2], [3, 8]]
        assign2, cost2 = hungarian_algorithm(mat2)
        self.assertEqual(assign2, [1, 0])
        self.assertEqual(cost2, 5)

        # 3. Пустая матрица
        assign0, cost0 = hungarian_algorithm([])
        self.assertEqual(assign0, [])
        self.assertEqual(cost0, 0)

        # 4. Неквадратная матрица должна вызывать исключение
        with self.assertRaises(ValueError):
            hungarian_algorithm([[1, 2, 3], [4, 5, 6]])


if __name__ == "__main__":
    unittest.main()

