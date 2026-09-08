from pydantic import BaseModel, Field
from typing import List, Optional

class ContextMessage(BaseModel):
    id: int
    timestamp: str
    sender: str
    message: str

class SearchResultItem(BaseModel):
    message_id: int
    sender: str
    message: str
    timestamp: str
    score: float
    context_before: List[ContextMessage] = []
    context_after: List[ContextMessage] = []

class SearchResponse(BaseModel):
    query: str
    query_type: str
    answer: str
    results: List[SearchResultItem]

class SingleMessageResponse(BaseModel):
    message_id: int
    sender: str
    message: str
    timestamp: str
    context_before: List[ContextMessage] = []
    context_after: List[ContextMessage] = []

class StatsResponse(BaseModel):
    total_messages: int
    participants_count: int
    participants: List[str]
    date_range: str
    embedding_model: str
    vector_search: str
    evaluation_summary: Optional[dict] = None

class EvaluationQueryItem(BaseModel):
    query: str
    correct_message_id: int
    type: str
    retrieved_top1_id: Optional[int] = None
    rank: Optional[int] = None
    found_in_top1: bool = False
    found_in_top3: bool = False
    found_in_top5: bool = False
    reciprocal_rank: float = 0.0

class EvaluationResponse(BaseModel):
    total_queries: int
    top1_accuracy: float
    top3_accuracy: float
    top5_accuracy: float
    mrr: float
    queries: List[EvaluationQueryItem] = []
