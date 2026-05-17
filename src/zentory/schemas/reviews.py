from datetime import date

from pydantic import Field

from zentory.schemas.marketplace import SourceStampedModel


class ReviewSnapshot(SourceStampedModel):
    rating: float = 0
    reviews_count: int = 0
    negative_reviews_count: int = 0
    unanswered_reviews_count: int = 0
    latest_reviews: list[str] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None
