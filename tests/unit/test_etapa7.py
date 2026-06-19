"""
Tests for ETAPA 7: PMS2 Assessment Profundo + Métricas QC Clínicas

Tests:
1. HomologyAnalyzer - Detecção de pseudogene
2. PseudogeneRiskDetector - Score de risco
3. BreadthAnalyzer - Breadth de cobertura
4. UniformityAnalyzer - Fold-80 uniformidade
5. SeverityClassifier - Classificação clínica
"""

import pytest
from src.vflow.core.pms2_assessment import HomologyAnalyzer, PseudogeneRiskDetector
from src.vflow.core.coverage import BreadthAnalyzer, UniformityAnalyzer
from src.vflow.validators.quality_gates import SeverityClassifier


# ============================================================================
# TESTS: HomologyAnalyzer
# ============================================================================

class TestHomologyAnalyzer:
    """Tests for HomologyAnalyzer class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = HomologyAnalyzer()
    
    def test_homology_analyzer_init(self):
        """Test HomologyAnalyzer initialization"""
        assert self.analyzer.regions is not None
        assert len(self.analyzer.regions) == 3
        assert "exon_11" in self.analyzer.regions
    
    def test_analyze_position_in_exon_11(self):
        """Test detection of position in exon_11 (CRITICAL)"""
        result = self.analyzer.analyze_position(33560500)
        
        assert result["in_homology_region"] is True
        assert result["region_name"] == "exon_11"
        assert result["homology_pct"] == 95.2
        assert result["risk_level"] == "CRITICAL"
    
    def test_analyze_position_in_exon_15(self):
        """Test detection of position in exon_15 (HIGH)"""
        result = self.analyzer.analyze_position(33573500)
        
        assert result["in_homology_region"] is True
        assert result["region_name"] == "exon_15"
        assert result["risk_level"] == "HIGH"
    
    def test_analyze_position_outside_regions(self):
        """Test position outside homology regions"""
        result = self.analyzer.analyze_position(33400000)
        
        assert result["in_homology_region"] is False
    
    def test_get_risk_from_homology_critical(self):
        """Test risk classification for high homology"""
        risk = self.analyzer.get_risk_from_homology(95.0)
        assert risk == "CRITICAL"
    
    def test_get_risk_from_homology_high(self):
        """Test risk classification for moderate homology"""
        risk = self.analyzer.get_risk_from_homology(87.0)
        assert risk == "HIGH"
    
    def test_get_risk_from_homology_medium(self):
        """Test risk classification for low-moderate homology"""
        risk = self.analyzer.get_risk_from_homology(82.0)
        assert risk == "MEDIUM"
    
    def test_recommend_validation_critical(self):
        """Test validation recommendation for critical scenario"""
        rec = self.analyzer.recommend_validation(95.2, 30)
        assert "Sanger + long-read" in rec
        assert "CRITICAL" in rec
    
    def test_recommend_validation_low(self):
        """Test validation recommendation for low-risk scenario"""
        rec = self.analyzer.recommend_validation(40, 150)
        assert "Standard NGS" in rec
        assert "LOW" in rec


# ============================================================================
# TESTS: PseudogeneRiskDetector
# ============================================================================

class TestPseudogeneRiskDetector:
    """Tests for PseudogeneRiskDetector class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.detector = PseudogeneRiskDetector()
    
    def test_pseudogene_detector_init(self):
        """Test PseudogeneRiskDetector initialization"""
        assert self.detector.WEIGHTS is not None
        assert self.detector.RISK_THRESHOLDS is not None
        assert abs(sum(self.detector.WEIGHTS.values()) - 1.0) < 0.01
    
    def test_calculate_risk_score_critical(self):
        """Test risk score for critical scenario"""
        result = self.detector.calculate_risk_score(
            homology_pct=95.2,
            coverage_depth=30,
            mapeability=0.45,
            variant_type="SNV"
        )
        
        assert result["risk_level"] == "CRITICAL"
        assert result["risk_score"] >= 75
        assert result["confidence_pct"] < 30
    
    def test_calculate_risk_score_low(self):
        """Test risk score for low-risk scenario"""
        result = self.detector.calculate_risk_score(
            homology_pct=40,
            coverage_depth=120,
            mapeability=0.85,
            variant_type="SNV"
        )
        
        assert result["risk_level"] in ["LOW", "MEDIUM"]
        assert result["risk_score"] < 50
        assert result["confidence_pct"] > 50
    
    def test_risk_score_indel_higher_than_snv(self):
        """Test that indels have higher risk than SNVs"""
        result_snv = self.detector.calculate_risk_score(95.2, 50, 0.5, "SNV")
        result_indel = self.detector.calculate_risk_score(95.2, 50, 0.5, "INDEL")
        
        assert result_indel["risk_score"] > result_snv["risk_score"]
    
    def test_risk_score_components(self):
        """Test that component scores are calculated"""
        result = self.detector.calculate_risk_score(95.2, 50, 0.5, "SNV")
        
        assert "components" in result
        assert "homology_score" in result["components"]
        assert "coverage_score" in result["components"]
        assert "mapeability_score" in result["components"]
        assert "variant_score" in result["components"]
    
    def test_interpret_result_critical(self):
        """Test interpretation of critical risk"""
        result = self.detector.calculate_risk_score(95.2, 30, 0.45, "SNV")
        interpretation = self.detector.interpret_result(result)
        
        assert "CRITICAL" in interpretation
        assert "Resequencing" in interpretation


# ============================================================================
# TESTS: BreadthAnalyzer
# ============================================================================

class TestBreadthAnalyzer:
    """Tests for BreadthAnalyzer class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = BreadthAnalyzer()
    
    def test_breadth_analyzer_init(self):
        """Test BreadthAnalyzer initialization"""
        assert self.analyzer.BREADTH_THRESHOLDS is not None
        assert self.analyzer.BREADTH_THRESHOLDS["ge_20x"] == 0.95
    
    def test_calculate_breadth_excellent(self):
        """Test breadth calculation for excellent coverage"""
        depth = [50] * 95 + [15] * 5
        result = self.analyzer.calculate_breadth(depth)
        
        assert result["bases_ge_20x"] == 0.95
        assert result["status"] == "PASS"
    
    def test_calculate_breadth_poor(self):
        """Test breadth calculation for poor coverage"""
        depth = [10] * 60 + [50] * 40
        result = self.analyzer.calculate_breadth(depth)
        
        assert result["bases_ge_20x"] == 0.4
        assert result["status"] == "FAIL"
    
    def test_calculate_breadth_multiple_thresholds(self):
        """Test breadth at multiple thresholds"""
        depth = [100] * 50 + [60] * 30 + [30] * 15 + [10] * 5
        result = self.analyzer.calculate_breadth(depth)
        
        # CORRECTED: More bases meet lower thresholds
        assert result["bases_ge_100x"] <= result["bases_ge_50x"]
        assert result["bases_ge_50x"] <= result["bases_ge_20x"]
    
    def test_calculate_breadth_empty_array(self):
        """Test breadth calculation with empty array"""
        result = self.analyzer.calculate_breadth([])
        
        assert result["bases_ge_20x"] == 0.0
        assert result["status"] == "FAIL"
    
    def test_breadth_status_warning(self):
        """Test WARNING status for near-threshold breadth"""
        depth = [50] * 92 + [10] * 8
        result = self.analyzer.calculate_breadth(depth)
        
        assert result["status"] == "WARNING"


# ============================================================================
# TESTS: UniformityAnalyzer
# ============================================================================

class TestUniformityAnalyzer:
    """Tests for UniformityAnalyzer class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = UniformityAnalyzer()
    
    def test_uniformity_analyzer_init(self):
        """Test UniformityAnalyzer initialization"""
        assert self.analyzer.fold_80_threshold == 2.0
    
    def test_calculate_fold_80_perfect(self):
        """Test fold-80 for perfectly uniform coverage"""
        depth = [50] * 100
        result = self.analyzer.calculate_fold_80(depth)
        
        assert result["fold_80"] == 1.0
        assert result["status"] == "EXCELLENT"
    
    def test_calculate_fold_80_good(self):
        """Test fold-80 for good uniformity"""
        depth = [45] * 80 + [60] * 20
        result = self.analyzer.calculate_fold_80(depth)
        
        assert 1.0 <= result["fold_80"] <= 2.0
        assert result["status"] in ["EXCELLENT", "GOOD"]
    
    def test_calculate_fold_80_poor(self):
        """Test fold-80 for poor uniformity"""
        depth = [10] * 80 + [100] * 20
        result = self.analyzer.calculate_fold_80(depth)
        
        assert result["fold_80"] > 3.0
        assert result["status"] == "POOR"
    
    def test_calculate_fold_80_empty_array(self):
        """Test fold-80 calculation with empty array"""
        result = self.analyzer.calculate_fold_80([])
        
        assert result["fold_80"] is None
        assert result["status"] == "FAIL"
    
    def test_calculate_fold_80_single_element(self):
        """Test fold-80 calculation with single element"""
        result = self.analyzer.calculate_fold_80([50])
        
        assert result["status"] == "FAIL"


# ============================================================================
# TESTS: SeverityClassifier
# ============================================================================

class TestSeverityClassifier:
    """Tests for SeverityClassifier class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.classifier = SeverityClassifier()
    
    def test_severity_classifier_init(self):
        """Test SeverityClassifier initialization"""
        assert self.classifier.SEVERITY_MAP is not None
        assert len(self.classifier.SEVERITY_MAP) == 4
        assert "LOW" in self.classifier.SEVERITY_MAP
    
    def test_classify_breadth_excellent(self):
        """Test breadth classification for excellent"""
        result = self.classifier.classify_coverage_breadth(0.96)
        
        assert result["severity"] == "LOW"
        assert "Excellent" in result["message"]
    
    def test_classify_breadth_poor(self):
        """Test breadth classification for poor"""
        result = self.classifier.classify_coverage_breadth(0.70)
        
        assert result["severity"] == "CRITICAL"
        assert "resequencing" in result["message"]
    
    def test_classify_uniformity_excellent(self):
        """Test uniformity classification for excellent"""
        result = self.classifier.classify_coverage_uniformity(1.2)
        
        assert result["severity"] == "LOW"
    
    def test_classify_uniformity_poor(self):
        """Test uniformity classification for poor"""
        result = self.classifier.classify_coverage_uniformity(5.0)
        
        assert result["severity"] == "CRITICAL"
    
    def test_classify_pseudogene_risk_low(self):
        """Test pseudogene risk classification for low"""
        result = self.classifier.classify_pseudogene_risk(20, 80)
        
        assert result["severity"] == "LOW"
    
    def test_classify_pseudogene_risk_critical(self):
        """Test pseudogene risk classification for critical"""
        result = self.classifier.classify_pseudogene_risk(85, 15)
        
        assert result["severity"] == "CRITICAL"
        assert "resequencing" in result["message"]
    
    def test_aggregate_flags_empty(self):
        """Test aggregation of empty flags"""
        result = self.classifier.aggregate_flags([])
        
        assert result["overall_severity"] == "LOW"
        assert result["flag_count"] == 0
    
    def test_aggregate_flags_mixed(self):
        """Test aggregation of mixed severity flags"""
        flags = [
            self.classifier.classify_coverage_breadth(0.92),
            self.classifier.classify_coverage_uniformity(1.2),
            self.classifier.classify_pseudogene_risk(55, 65)
        ]
        
        result = self.classifier.aggregate_flags(flags)
        
        assert result["overall_severity"] in ["MEDIUM", "HIGH"]
        assert result["flag_count"] == 3
    
    def test_generate_qc_summary(self):
        """Test complete QC summary generation"""
        metrics = {
            "breadth_ge_20x": 0.92,
            "fold_80": 2.1,
            "pseudogene_risk_score": 55,
            "pseudogene_confidence": 65
        }
        
        summary = self.classifier.generate_qc_summary(metrics)
        
        assert "individual_flags" in summary
        assert "aggregated_result" in summary
        assert "clinical_interpretation" in summary
        assert len(summary["individual_flags"]) == 3


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestETAPA7Integration:
    """Integration tests combining multiple components"""
    
    def test_full_qc_workflow_critical_scenario(self):
        """Test complete QC workflow for critical scenario"""
        homology_analyzer = HomologyAnalyzer()
        risk_detector = PseudogeneRiskDetector()
        breadth = BreadthAnalyzer()
        classifier = SeverityClassifier()
        
        homology = homology_analyzer.analyze_position(33560500)
        risk_result = risk_detector.calculate_risk_score(
            homology["homology_pct"],
            coverage_depth=30,
            mapeability=homology["mapeability"],
            variant_type="SNV"
        )
        
        depth = [20] * 70 + [100] * 30
        breadth_result = breadth.calculate_breadth(depth)
        
        summary = classifier.generate_qc_summary({
            "breadth_ge_20x": breadth_result["bases_ge_20x"],
            "fold_80": 2.5,
            "pseudogene_risk_score": risk_result["risk_score"],
            "pseudogene_confidence": risk_result["confidence_pct"]
        })
        
        assert summary["aggregated_result"]["overall_severity"] in ["HIGH", "CRITICAL"]
        assert "Validate" in summary["aggregated_result"]["action"] or "Resequence" in summary["aggregated_result"]["action"]
    
    def test_full_qc_workflow_safe_scenario(self):
        """Test complete QC workflow for safe scenario"""
        homology_analyzer = HomologyAnalyzer()
        risk_detector = PseudogeneRiskDetector()
        breadth = BreadthAnalyzer()
        uniformity = UniformityAnalyzer()
        classifier = SeverityClassifier()
        
        depth_uniform = [60] * 96 + [50] * 4
        breadth_result = breadth.calculate_breadth(depth_uniform)
        fold_80_result = uniformity.calculate_fold_80(depth_uniform)
        
        risk_result = risk_detector.calculate_risk_score(
            homology_pct=30,
            coverage_depth=120,
            mapeability=0.9,
            variant_type="SNV"
        )
        
        summary = classifier.generate_qc_summary({
            "breadth_ge_20x": breadth_result["bases_ge_20x"],
            "fold_80": fold_80_result["fold_80"],
            "pseudogene_risk_score": risk_result["risk_score"],
            "pseudogene_confidence": risk_result["confidence_pct"]
        })
        
        assert summary["aggregated_result"]["overall_severity"] in ["LOW", "MEDIUM"]
        assert "Monitor" in summary["aggregated_result"]["action"] or "Review" in summary["aggregated_result"]["action"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
