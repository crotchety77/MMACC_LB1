import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from api.main import app
from api.adapter import run_full_analysis
from expert_estimate.io import read_data
from expert_estimate.transform import transform_data, get_objects
from expert_estimate.stats import get_ranking_by_average, get_ranking_by_median
from expert_estimate.relations import (
    get_binary_relations,
    build_distance_matrix,
    get_diff_relations_matrixes,
)
from expert_estimate.kemeny import (
    get_preference_vectors,
    get_row_sums,
    get_kemeny_medians_by_experts,
    get_all_assignment_medians,
    get_all_kemeny_medians_bruteforce,
)


class TestApiVsCore(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_example_endpoint(self):
        resp = self.client.get("/api/example")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("examples", data)
        self.assertIn("default", data["examples"])

    def _verify_dataset(self, filename: str):
        filepath = str(self.base_dir / filename)
        raw_table = read_data(filepath)

        # 1. Считаем напрямую через ядро
        transformed = transform_data(raw_table)
        objects = get_objects(transformed)
        core_avg = get_ranking_by_average(transformed)
        core_med = get_ranking_by_median(transformed)
        core_pv = get_preference_vectors(transformed, objects)
        core_rel = get_binary_relations(transformed, objects)
        core_dist = build_distance_matrix(core_rel)
        core_sums = get_row_sums(core_dist)
        core_med_exp = get_kemeny_medians_by_experts(core_dist)
        core_as_orders, core_as_total, core_loss = get_all_assignment_medians(transformed, objects)
        core_bf_orders, core_bf_total = get_all_kemeny_medians_bruteforce(core_rel, objects)

        # 2. Считаем через адаптер API
        api_res = run_full_analysis(raw_table)

        # 3. Сверяем ранжирования
        self.assertEqual(
            [(item.place, item.object, item.value) for item in api_res.rankings.average],
            [(p, o, round(v, 4)) for p, o, v in core_avg],
            f"Несовпадение ранжирования по среднему для {filename}",
        )
        self.assertEqual(
            [(item.place, item.object, item.value) for item in api_res.rankings.median],
            [(p, o, round(v, 4)) for p, o, v in core_med],
            f"Несовпадение ранжирования по медиане для {filename}",
        )

        # 4. Сверяем матрицу расстояний
        for r in core_dist.rows:
            for c in core_dist.cols:
                r_idx = api_res.matrices["distance"].rows.index(str(r))
                c_idx = api_res.matrices["distance"].cols.index(str(c))
                self.assertEqual(
                    api_res.matrices["distance"].data[r_idx][c_idx],
                    float(core_dist[r, c]),
                )

        # 5. Сверяем оптимумы Кемени
        # Медианы среди экспертов
        api_exp_solutions = [s.expert_id.replace("Э", "") for s in api_res.kemeny["expert_method"].solutions]
        self.assertEqual(sorted(api_exp_solutions), sorted(core_med_exp))
        self.assertEqual(api_res.kemeny["expert_method"].criterion_value, min(core_sums.values()))

        # Задача о назначениях
        self.assertEqual(api_res.kemeny["assignment_method"].criterion_value, core_as_total)
        api_as_orders = [s.order for s in api_res.kemeny["assignment_method"].solutions]
        self.assertEqual(sorted(api_as_orders), sorted(core_as_orders))

        # Полный перебор
        self.assertEqual(api_res.kemeny["bruteforce_method"].criterion_value, core_bf_total)
        api_bf_orders = [s.order for s in api_res.kemeny["bruteforce_method"].solutions]
        self.assertEqual(sorted(api_bf_orders), sorted(core_bf_orders))

        # 6. Проверяем HTTP endpoint POST /api/analyze
        resp = self.client.post("/api/analyze", json={"rankings": list(raw_table.values())})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["summary"]["best_kemeny_distance"], core_bf_total)
        self.assertEqual(len(data["summary"]["best_kemeny_orders"]), len(core_bf_orders))

    def test_default_input(self):
        self._verify_dataset("input.txt")

    def test_v2_input(self):
        self._verify_dataset("input_v2.txt")


if __name__ == "__main__":
    unittest.main()
