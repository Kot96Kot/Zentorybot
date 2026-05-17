from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ContentDraftStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ContentBrief(BaseModel):
    marketplace: str
    category: str
    product_name: str
    brand: str
    article: str
    price: float
    main_characteristics: dict[str, Any] = Field(default_factory=dict)
    customer_pains: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    marketplace_restrictions: list[str] = Field(default_factory=list)
    sku: str | None = None


class InfographicTask(BaseModel):
    slide: int
    title: str
    message: str
    visual_direction: str


class PhotoTask(BaseModel):
    shot: int
    title: str
    requirements: str


class VideoTask(BaseModel):
    scene: int
    title: str
    script: str


class ContentCardDraft(BaseModel):
    marketplace: str
    sku: str | None = None
    article: str
    seo_title: str
    description: str
    unique_selling_propositions: list[str]
    benefits: list[str]
    characteristics: dict[str, Any]
    infographic_tasks: list[InfographicTask]
    photo_tasks: list[PhotoTask]
    video_tasks: list[VideoTask]
    keywords: list[str]
    pre_publish_checklist: list[str]
    status: ContentDraftStatus = ContentDraftStatus.DRAFT
    requires_approval: bool = True
    llm_provider: str = "mock"
    mock: bool = True
