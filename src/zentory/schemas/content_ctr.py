from enum import StrEnum

from pydantic import BaseModel, Field


class ContentRisk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ContentBriefCTR(BaseModel):
    marketplace: str
    sku: str
    product_name: str
    category: str
    target_audience: str
    buyer_pains: list[str] = Field(default_factory=list)
    key_features: list[str] = Field(default_factory=list)
    competitor_references: list[str] = Field(default_factory=list)
    current_ctr: float
    target_ctr: float
    mock_mode: bool = True


class ContentPhotoHypothesis(BaseModel):
    idea: str
    why_it_may_work: str
    pain_addressed: str
    element_to_test: str
    risk: ContentRisk
    draft_only: bool = True
    mock_mode: bool = True


class GeneratedImagePrompts(BaseModel):
    sora_prompt: str
    gpt_image_prompt: str
    midjourney_prompt: str
    russian_text_blocks: list[str] = Field(default_factory=list)
    language: str = "en"
    draft_only: bool = True
    mock_mode: bool = True


class CTRTestPlan(BaseModel):
    what_we_test: str
    success_metric: str
    test_period: str
    minimum_traffic: int
    winner_criteria: str
    publication_requires_approval: bool = True
    bulk_change_requires_hard_approval: bool = True
    mock_mode: bool = True


class ContentCTRFactoryResult(BaseModel):
    brief: ContentBriefCTR
    hypotheses: list[ContentPhotoHypothesis] = Field(default_factory=list)
    prompts: list[GeneratedImagePrompts] = Field(default_factory=list)
    ctr_test_plan: CTRTestPlan
    safety_notes: list[str] = Field(default_factory=list)
    mock_mode: bool = True
