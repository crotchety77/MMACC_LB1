export interface MatrixData {
  name: string;
  description?: string;
  rows: string[];
  cols: string[];
  data: number[][];
}

export interface RankingItem {
  place: number;
  object: string;
  value: number;
}

export interface KemenyMedianSolution {
  order: string[];
  order_str: string;
  total_distance: number;
  loss_value?: number;
  expert_id?: string;
}

export interface KemenyMethodResult {
  title: string;
  criterion_name: string;
  criterion_value: number;
  solutions: KemenyMedianSolution[];
}

export interface KemenyComparisonSummary {
  intersection_experts_bruteforce: number;
  intersection_assignment_bruteforce: number;
  assignment_is_subset_of_bruteforce: boolean;
  all_methods_agree: boolean;
}

export interface ExpertGraphNode {
  id: string;
  label: string;
  ranking: string[];
  ranking_str: string;
  sum_distance: number;
  is_median: boolean;
}

export interface ExpertGraphEdge {
  source: string;
  target: string;
  distance: number;
  similarity: number;
}

export interface ExpertGraphData {
  nodes: ExpertGraphNode[];
  edges: ExpertGraphEdge[];
}

export interface AnalysisSummary {
  num_experts: number;
  num_objects: number;
  unique_rankings_count: number;
  best_kemeny_orders: string[][];
  best_kemeny_distance: number;
  is_consensus_perfect: boolean;
}

export interface RankingsData {
  average: RankingItem[];
  median: RankingItem[];
}

export interface AnalyzeResponse {
  experts: string[];
  objects: string[];
  raw_rankings: Record<string, string[]>;
  summary: AnalysisSummary;
  rankings: RankingsData;
  matrices: {
    transformed: MatrixData;
    preferences: MatrixData;
    distance: MatrixData;
    loss: MatrixData;
    assignment: MatrixData;
  };
  binary_relations: Record<string, MatrixData>;
  diff_matrices: Record<string, MatrixData>;
  kemeny: {
    expert_method: KemenyMethodResult;
    assignment_method: KemenyMethodResult;
    bruteforce_method: KemenyMethodResult;
  };
  comparison: KemenyComparisonSummary;
  graph: ExpertGraphData;
}

export interface ExampleVariant {
  title: string;
  content: string;
}

export interface ExamplesResponse {
  examples: Record<string, ExampleVariant>;
}
