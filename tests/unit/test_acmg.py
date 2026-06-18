"""
Unit tests for ACMG Evidence Collection Module
"""

import pytest
from src.vflow.core.acmg_evidence import (
    ACMGCriterion, 
    ACMGEvidenceResult, 
    ACMGEvidenceCollector
)


class TestACMGCriterion:
    """Test individual ACMG criteria"""
    
    def test_criterion_creation(self):
        """Test creating an ACMG criterion"""
        criterion = ACMGCriterion(
            code="PVS1",
            category="Pathogenic",
            strength="Very Strong",
            description="Null variant",
            evidence="Frameshift mutation",
            source="Variant Annotation",
            confidence=0.98
        )
        
        assert criterion.code == "PVS1"
        assert criterion.confidence == 0.98
        assert "Null variant" in str(criterion)
    
    def test_criterion_string_representation(self):
        """Test human-readable format"""
        criterion = ACMGCriterion(
            code="PS1",
            category="Pathogenic",
            strength="Strong",
            description="Same variant as pathogenic",
            evidence="ClinVar: Pathogenic",
            source="ClinVar",
            confidence=0.95
        )
        
        output = str(criterion)
        assert "[PS1]" in output
        assert "ClinVar" in output
        assert "95%" in output


class TestACMGEvidenceCollector:
    """Test ACMG evidence collection"""
    
    def setup_method(self):
        """Initialize collector before each test"""
        self.collector = ACMGEvidenceCollector()
    
    def test_frameshift_detection(self):
        """Test that frameshifts trigger PVS1"""
        result = self.collector.collect_evidence(
            gene="PMS2",
            chromosome="chr7",
            position=6012876,
            reference="CG",
            alternate="C",
            variant_type="frameshift"
        )
        
        assert result.gene == "PMS2"
        assert len(result.pathogenic_criteria) > 0
        assert any(c.code == "PVS1" for c in result.pathogenic_criteria)
    
    def test_nonsense_is_very_strong(self):
        """Test that nonsense variants get PVS1 (Very Strong)"""
        result = self.collector.collect_evidence(
            gene="MLH1",
            chromosome="chr3",
            position=36993942,
            reference="G",
            alternate="A",
            variant_type="nonsense"
        )
        
        pvs1_criteria = [c for c in result.pathogenic_criteria if c.code == "PVS1"]
        assert len(pvs1_criteria) > 0
        assert pvs1_criteria[0].strength == "Very Strong"
    
    def test_rare_snv_gets_pm2(self):
        """Test that rare SNVs trigger PM2"""
        result = self.collector.collect_evidence(
            gene="PMS2",
            chromosome="chr7",
            position=6012876,
            reference="C",
            alternate="T",
            variant_type="SNV"
        )
        
        assert any(c.code == "PM2" for c in result.supporting_criteria)
    
    def test_mmr_gene_required(self):
        """Test that non-MMR genes are handled"""
        result = self.collector.collect_evidence(
            gene="TP53",  # Not an MMR gene
            chromosome="chr17",
            position=7577121,
            reference="G",
            alternate="A",
            variant_type="SNV"
        )
        
        # Should still work, but with warning logged
        assert result.gene == "TP53"
        assert result.total_criteria_found >= 0
    
    def test_evidence_result_structure(self):
        """Test that result has correct structure"""
        result = self.collector.collect_evidence(
            gene="PMS2",
            chromosome="chr7",
            position=6012876,
            reference="C",
            alternate="T",
            variant_type="SNV"
        )
        
        assert isinstance(result, ACMGEvidenceResult)
        assert result.variant is not None
        assert result.gene == "PMS2"
        assert isinstance(result.pathogenic_criteria, list)
        assert isinstance(result.benign_criteria, list)
        assert isinstance(result.supporting_criteria, list)
        assert result.total_criteria_found > 0
    
    def test_summary_is_readable(self):
        """Test that summary generates readable output"""
        result = self.collector.collect_evidence(
            gene="MSH2",
            chromosome="chr2",
            position=47641559,
            reference="G",
            alternate="A",
            variant_type="nonsense"
        )
        
        summary = result.summary()
        assert "MSH2" in summary
        assert "EVIDENCE COLLECTION" in summary
        assert "PVS1" in summary or "Pathogenic" in summary.upper()
    
    def test_suggested_interpretation_is_not_classification(self):
        """Test that interpretation includes 'requires review' disclaimer"""
        result = self.collector.collect_evidence(
            gene="PMS2",
            chromosome="chr7",
            position=6012876,
            reference="CG",
            alternate="C",
            variant_type="frameshift"
        )
        
        interpretation = result.suggested_interpretation
        assert "requires" in interpretation.lower() or "uncertain" in interpretation.lower()
        # Should NOT be a hard classification
        assert interpretation not in ["PATHOGENIC", "BENIGN"]
    
    def test_clinical_note_present(self):
        """Test that clinical note is generated"""
        result = self.collector.collect_evidence(
            gene="PMS2",
            chromosome="chr7",
            position=6012876,
            reference="C",
            alternate="T",
            variant_type="SNV"
        )
        
        assert result.clinical_note is not None
        assert "geneticist" in result.clinical_note.lower()
        assert "review" in result.clinical_note.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
