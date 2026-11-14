"""Pydantic models for knowledge graph entities."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class KnowledgeChunk(BaseModel):
    id: str
    content: str
    source_type: str  # email | document | task | calendar
    source_id: str
    source_title: str
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""
    tags: list[str] = Field(default_factory=list)
    relevance_score: float = 0.0


class Connection(BaseModel):
    id: str
    source_id: str
    source_type: str
    source_label: str
    target_id: str
    target_type: str
    target_label: str
    relationship: str  # "related_to" | "references" | "follows_up" | "blocks" | "mentions"
    strength: float = 0.5  # 0-1
    description: str = ""


class KnowledgeNode(BaseModel):
    id: str
    label: str
    type: str  # email | document | task | person | topic | company
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    connections: list[str] = Field(default_factory=list)  # list of Connection IDs
    importance_score: float = 0.5
    color: str = "#6366f1"
    size: int = 20


class KnowledgeGraph(BaseModel):
    nodes: list[KnowledgeNode] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
    last_updated: str = ""

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.connections)
