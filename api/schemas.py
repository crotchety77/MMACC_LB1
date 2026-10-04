from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MatrixData(BaseModel):
    name: str
    description: Optional[str] = ""
    rows: List[str]
    cols: List[str]
    data: List[List[float]] = Field(description="2D array of matrix values [row][col]")


class RankingItem(BaseModel):
    place: int
    object: str
    value: float


class KemenyMedianSolution(BaseModel):
    order: List[str]
    order_str: str
    total_distance: int
    loss_value: Optional[int] = None
    expert_id: Optional[str] = None


class KemenyMethodResult(BaseModel):
    title: str
    criterion_name: str
    criterion_value: int
    solutions: List[KemenyMedianSolution]


class KemenyComparisonSummary(BaseModel):
    intersection_experts_bruteforce: int
    intersection_assignment_bruteforce: int
    assignment_is_subset_of_bruteforce: bool
    all_methods_agree: bool


class ExpertGraphNode(BaseModel):
    id: str
    label: str
    ranking: List[str]
    ranking_str: str
    sum_distance: int
    is_median: bool


class ExpertGraphEdge(BaseModel):
    source: str
    target: str
    distance: int
    similarity: float = Field(description="Normalized similarity 0..1 based on distance")


class ExpertGraphData(BaseModel):
    nodes: List[ExpertGraphNode]
    edges: List[ExpertGraphEdge]


class AnalysisSummary(BaseModel):
    num_experts: int
    num_objects: int
    unique_rankings_count: int
    best_kemeny_orders: List[List[str]]
    best_kemeny_distance: int
    is_consensus_perfect: bool


class RankingsData(BaseModel):
    average: List[RankingItem]
    median: List[RankingItem]


class AnalyzeResponse(BaseModel):
    experts: List[str]
    objects: List[str]
    raw_rankings: Dict[str, List[str]]
    summary: AnalysisSummary
    rankings: RankingsData
    matrices: Dict[str, MatrixData]
    binary_relations: Dict[str, MatrixData]
    diff_matrices: Dict[str, MatrixData]
    kemeny: Dict[str, KemenyMethodResult]
    comparison: KemenyComparisonSummary
    graph: ExpertGraphData


class AnalyzeRequest(BaseModel):
    text: Optional[str] = Field(None, description="Raw text of rankings, one line per expert")
    rankings: Optional[List[List[str]]] = Field(None, description="List of lists of object names")
