# Tests for analytics (FR-11 / ARCHITECTURE §9)
from app.services.analytics import AnalyticsService

def test_analytics_metrics_computed():
    svc = AnalyticsService(db=None)
    metrics = svc.compute_metrics(exam_id=1, role_filter="faculty")
    assert "avg_score" in metrics
    assert "completion_rate" in metrics
    assert "question_trends" in metrics

def test_overview_with_filters():
    svc = AnalyticsService(db=None)
    res = svc.overview(exam_id=10, subject_filter="Math")
    assert res["filters_applied"]["exam_id"] == 10
    assert res["filters_applied"]["subject"] == "Math"
