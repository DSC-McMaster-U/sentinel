"""HTTP endpoints for pull request reviews."""

from fastapi import APIRouter

from app.schemas import PullRequestInput
from app.schemas.review_report import ReviewReport
from app.services.review_service import build_mock_review_report

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewReport)
def review_pull_request(request: PullRequestInput) -> ReviewReport:
    """Return a mock review report for the submitted PR's head commit."""
    return build_mock_review_report(request)
