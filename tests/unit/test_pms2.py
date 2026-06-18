"""
Unit tests for PMS2 Assessment Module
"""

import pytest
from src.vflow.core.pms2_assessment import PMS2Assessor
from src.vflow.core.models import PMS2AssessmentResult, SeverityLevel


class TestPMS2Assessor:
    """Test PMS2Assessor functionality"""
    
    def setup_method(self):
        """Initialize assessor before each test"""
        self.assessor = PMS2Assessor()
    
    def test_critical_region_detection(self):
        """Test detection of critical regions"""
        assert self.assessor.is_in_critical_region(21000) is True
        assert self.assessor.is_in_critical_region(50000) is False
    
    def test_critical_snv_assessment(self):
        """Test SNV in critical region returns CRITICAL risk"""
        result = self.assessor.assess_variant("PMS2", position=21000, variant_type="SNV")
        
        assert isinstance(result, PMS2AssessmentResult)
        assert result.pseudogene_risk == SeverityLevel.CRITICAL
        assert result.requires_orthogonal_confirmation is True
    
    def test_low_risk_snv(self):
        """Test SNV outside critical regions returns LOW risk"""
        result = self.assessor.assess_variant("PMS2", position=50000, variant_type="SNV")
        
        assert result.pseudogene_risk == SeverityLevel.LOW
        assert result.requires_orthogonal_confirmation is False
    
    def test_deletion_high_risk(self):
        """Test structural variants get higher risk"""
        result = self.assessor.assess_variant("PMS2", position=36000, variant_type="deletion")
        
        assert result.pseudogene_risk == SeverityLevel.CRITICAL
        assert "CNV analysis" in str(result.recommendations)
    
    def test_recommendations_generated(self):
        """Test that recommendations are always provided"""
        result = self.assessor.assess_variant("PMS2", position=21000, variant_type="SNV")
        
        assert len(result.recommendations) > 0
        assert all(isinstance(r, str) for r in result.recommendations)
    
    def test_wrong_gene_raises_error(self):
        """Test that non-PMS2 genes raise ValueError"""
        with pytest.raises(ValueError):
            self.assessor.assess_variant("MLH1", position=10000)
    
    def test_summary_generation(self):
        """Test that gene field is correct"""
        result = self.assessor.assess_variant("PMS2", position=21000)
        
        assert result.gene == "PMS2"
        assert result.pseudogene_risk == SeverityLevel.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
