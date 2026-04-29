from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    status: str
    mock_mode: bool
    db_exists: bool
    chroma_ready: bool

class QueryRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    question: str = Field(..., min_length=1, max_length=500)

class QueryResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    question: str
    sql: str
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    chart_config: Dict[str, Any]
    data: List[Dict[str, Any]]
    execution_time_ms: float
    ai_summary: str

class MiningSourceResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: str
    name: str
    description: str
    icon: str

class MiningDiscoverRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    source: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Node(BaseModel):
    id: str
    label: str
    frequency: int
    type: str

class Edge(BaseModel):
    id: str
    source: str
    target: str
    frequency: int
    label: str

class ProcessGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class Conformance(BaseModel):
    fitness: float
    precision: float

class Performance(BaseModel):
    avg_duration_hours: float
    median_duration_hours: float
    bottleneck_activity: str
    bottleneck_avg_wait_hours: float

class MiningDiscoverResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    graph: ProcessGraph
    conformance: Conformance
    performance: Performance
    case_count: int
    task_id: str

class TaskStatusResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DashboardGenerateRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    prompt: str

class KpiData(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: str
    name: str
    module: str
    value: float
    unit: str
    trend: List[float]
    status: str
    threshold_amber: float
    threshold_red: float
    description: str
    higher_is_better: bool

class KpiModulesResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    FI: List[KpiData]
    SD: List[KpiData]
    MM: List[KpiData]
    PP: List[KpiData]

class Cause(BaseModel):
    title: str
    description: str
    severity: str
    affected_records: int
    recommendation: str

class RcaEvent(BaseModel):
    date: str
    event: str
    impact: str

class RcaData(BaseModel):
    summary: str
    causes: List[Cause]
    timeline: List[RcaEvent]

class RcaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    kpi_id: str
    rca: RcaData
