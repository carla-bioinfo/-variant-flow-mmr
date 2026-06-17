"""
Unit tests for data models

Tests the CoverageMetrics, QCFlag, and other models
"""

import pytest
from vflow.core.models import (
    CoverageMetrics, QCFlag, SeverityLevel, 
    GeneAnalysisResult, PMS2AssessmentResult
)


class TestCoverageMetrics:
    """Test CoverageMetrics dataclass"""
    
    def test_create_coverage_metrics(self):
        """Test creating a CoverageMetrics object"""
        metrics = CoverageMetrics(
            gene="MLH1",
            mean_depth=95.5,
            min_depth=18,
            max_depth=220,
            median_depth=98,
            bases_ge_20x=0.956,
            bases_ge_50x=0.892,
            bases_ge_100x=0.745,
            breadth=0.956,
            uniformity=0.89
        )
        
        assert metrics.gene == "MLH1"
        assert metrics.mean_depth == 95.5
        assert metrics.bases_ge_20x == 0.956
    
    def test_acceptable_coverage(self):
        """Test is_acceptable() method"""
        # Acceptable coverage
        metrics_good = CoverageMetrics(
            gene="MLH1", mean_depth=100, min_depth=50,
            max_depth=200, median_depth=100,
            bases_ge_20x=0.96, bases_ge_50x=0.90, bases_ge_100x=0.80,
            breadth=0.96, uniformity=0.90
        )
        assert metrics_good.is_acceptable() is True
        
        # Poor coverage
        metrics_bad = CoverageMetrics(
            gene="MLH1", mean_depth=15, min_depth=5,
            max_depth=50, median_depth=15,
            bases_ge_20x=0.60, bases_ge_50x=0.20, bases_ge_100x=0.0,
            breadth=0.60, uniformity=0.60
        )
        assert metrics_bad.is_acceptable() is False


class TestQCFlag:
    """Test QCFlag dataclass"""
    
    def test_create_qc_flag(self):
        """Test creating a QCFlag"""
        flag = QCFlag(
            severity=SeverityLevel.HIGH,
            category="COVERAGE",
            message="Low coverage detected",
            recommendation="Review"
        )
        
        assert flag.severity == SeverityLevel.HIGH
        assert flag.category == "COVERAGE"
    
    def test_severity_levels(self):
        """Test all severity levels"""
        levels = [
            SeverityLevel.LOW,
            SeverityLevel.MEDIUM,
            SeverityLevel.HIGH,
            SeverityLevel.CRITICAL
        ]
        assert len(levels) == 4


class TestGeneAnalysisResult:
    """Test GeneAnalysisResult"""
    
    def test_analysis_summary(self):
        """Test summary generation"""
        metrics = CoverageMetrics(
            gene="MSH2", mean_depth=85.0, min_depth=20,
            max_depth=180, median_depth=87,
            bases_ge_20x=0.93, bases_ge_50x=0.85, bases_ge_100x=0.70,
            breadth=0.93, uniformity=0.88
        )
        
        result = GeneAnalysisResult(
            gene="MSH2",
            metrics=metrics,
            flags=[],
            overall_quality=SeverityLevel.MEDIUM
        )
        
        summary = result.summary()
        assert "MSH2" in summary
        assert "85.0x" in summary
        assert "93.0%" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
