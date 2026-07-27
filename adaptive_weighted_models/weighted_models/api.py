from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .rag import RetrievalIndex, ask_with_context, build_index_from_documents, search_index
from .distributed import ContributionManager


app = FastAPI(title="Adaptive Weighted Models API", version="0.1.0")


class DocumentItem(BaseModel):
    source: str = Field(..., description="Document identifier or URL")
    text: str = Field(..., description="Raw document text")


class BuildIndexRequest(BaseModel):
    index_name: str = Field(default="default")
    documents: list[DocumentItem]
    chunk_size: int = Field(default=140, ge=20, le=2000)
    chunk_overlap: int = Field(default=30, ge=0, le=500)


class SearchRequest(BaseModel):
    index_name: str = Field(default="default")
    query: str
    top_k: int = Field(default=5, ge=1, le=50)


class AskRequest(BaseModel):
    index_name: str = Field(default="default")
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    model: str = Field(default="gpt-4o-mini")
    api_key: str | None = Field(default=None)
    base_url: str | None = Field(default=None)
    response_mode: Literal["llm", "context"] = Field(default="llm")


class SearchResultItem(BaseModel):
    rank: int
    score: float
    source: str
    text: str


class BuildIndexResponse(BaseModel):
    index_name: str
    chunks: int
    vocabulary_terms: int


class SearchResponse(BaseModel):
    index_name: str
    query: str
    count: int
    results: list[SearchResultItem]


class AskResponse(BaseModel):
    index_name: str
    query: str
    answer: str
    results: list[SearchResultItem]


_INDEX_STORE: dict[str, RetrievalIndex] = {}
_CONTRIB = ContributionManager()


class ContribSeedRequest(BaseModel):
    task_type: str = Field(default="rpo_match_score")
    payloads: list[dict]


class ContribSeedResponse(BaseModel):
    enqueued: int
    task_ids: list[str]


class ContribNextRequest(BaseModel):
    worker_id: str


class ContribNextResponse(BaseModel):
    has_task: bool
    task_id: str | None = None
    task_type: str | None = None
    payload: dict | None = None


class ContribSubmitRequest(BaseModel):
    worker_id: str
    task_id: str
    result: dict


class ContribSubmitResponse(BaseModel):
    accepted: bool


class ContribStatsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    claimed_tasks: int
    pending_tasks: int
    workers: dict[str, int]
    result_count: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/index/build", response_model=BuildIndexResponse)
def build_index_api(req: BuildIndexRequest) -> BuildIndexResponse:
    if not req.documents:
        raise HTTPException(status_code=400, detail="documents cannot be empty")

    docs = [(d.source, d.text) for d in req.documents]
    index = build_index_from_documents(docs, chunk_size=req.chunk_size, overlap=req.chunk_overlap)
    _INDEX_STORE[req.index_name] = index

    return BuildIndexResponse(
        index_name=req.index_name,
        chunks=len(index.chunks),
        vocabulary_terms=len(index.vocab),
    )


@app.post("/v1/search", response_model=SearchResponse)
def search_api(req: SearchRequest) -> SearchResponse:
    index = _INDEX_STORE.get(req.index_name)
    if index is None:
        raise HTTPException(status_code=404, detail=f"index '{req.index_name}' not found")

    results = search_index(index, query=req.query, top_k=req.top_k)
    payload = [SearchResultItem(**asdict(r)) for r in results]

    return SearchResponse(
        index_name=req.index_name,
        query=req.query,
        count=len(payload),
        results=payload,
    )


@app.post("/v1/ask", response_model=AskResponse)
def ask_api(req: AskRequest) -> AskResponse:
    index = _INDEX_STORE.get(req.index_name)
    if index is None:
        raise HTTPException(status_code=404, detail=f"index '{req.index_name}' not found")

    results = search_index(index, query=req.query, top_k=req.top_k)
    payload = [SearchResultItem(**asdict(r)) for r in results]

    if req.response_mode == "context":
        lines = []
        for item in payload:
            lines.append(f"[rank={item.rank} score={item.score:.4f} source={item.source}]\n{item.text}")
        answer = "\n\n".join(lines) if lines else "No relevant context found in index."
    else:
        answer = ask_with_context(
            query=req.query,
            results=results,
            model=req.model,
            api_key=req.api_key,
            base_url=req.base_url,
        )

    return AskResponse(
        index_name=req.index_name,
        query=req.query,
        answer=answer,
        results=payload,
    )


@app.post("/v1/contrib/tasks/seed", response_model=ContribSeedResponse)
def contrib_seed(req: ContribSeedRequest) -> ContribSeedResponse:
    if not req.payloads:
        raise HTTPException(status_code=400, detail="payloads cannot be empty")
    ids = _CONTRIB.enqueue_tasks(req.task_type, req.payloads)
    return ContribSeedResponse(enqueued=len(ids), task_ids=ids)


@app.post("/v1/contrib/task/next", response_model=ContribNextResponse)
def contrib_next(req: ContribNextRequest) -> ContribNextResponse:
    task = _CONTRIB.next_task(req.worker_id)
    if task is None:
        return ContribNextResponse(has_task=False)
    return ContribNextResponse(
        has_task=True,
        task_id=task.task_id,
        task_type=task.task_type,
        payload=task.payload,
    )


@app.post("/v1/contrib/task/submit", response_model=ContribSubmitResponse)
def contrib_submit(req: ContribSubmitRequest) -> ContribSubmitResponse:
    ok = _CONTRIB.submit_result(req.worker_id, req.task_id, req.result)
    if not ok:
        raise HTTPException(status_code=404, detail="task not found or not submittable")
    return ContribSubmitResponse(accepted=True)


@app.get("/v1/contrib/stats", response_model=ContribStatsResponse)
def contrib_stats() -> ContribStatsResponse:
    return ContribStatsResponse(**_CONTRIB.stats())
