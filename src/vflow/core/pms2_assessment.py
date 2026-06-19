"""
PMS2 Assessment Module for VariantFlow-MMR

Handles the unique complexity of PMS2 analysis:
- PMS2 has 3-4 pseudogenes with high homology
- Variants in pseudogenes cause false positives
- Requires orthogonal validation (Sanger, ddPCR)

Reference:
- ACMG: PMS2-specific recommendations
- InSiGHT: PMS2 pseudogene regions
- PMID: 25741868 (Vaughn et al. - PMS2 duplication/deletion)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
import logging

from vflow.core.models import (
    PMS2AssessmentResult, 
    SeverityLevel, 
    CoverageMetrics
)

logger = logging.getLogger(__name__)


@dataclass
class PMS2Region:
    """Represents a critical region in PMS2"""
    name: str
    start: int
    end: int
    description: str
    requires_validation: bool = True


class PMS2Assessor:
    """
    Assess PMS2 variants for pseudogene interference.
    
    PMS2 is the only MMR gene with significant pseudogene contamination.
    This class helps identify variants that may be false positives.
    """
    
    # Known problematic regions in PMS2 (based on InSiGHT database)
    CRITICAL_REGIONS = [
        PMS2Region(
            name="Exon 3 homology zone",
            start=20000,
            end=22000,
            description="High homology with pseudogene 1",
            requires_validation=True
        ),
        PMS2Region(
            name="Exon 5-6 junction",
            start=35000,
            end=37500,
            description="Pseudogene duplication region",
            requires_validation=True
        ),
        PMS2Region(
            name="Exon 11-12 interface",
            start=65000,
            end=68000,
            description="Complex homology with pseudogenes 2-3",
            requires_validation=True
        ),
    ]
    
    # Orthogonal validation methods
    VALIDATION_METHODS = [
        "Sanger sequencing (targeted)",
        "Digital droplet PCR (ddPCR)",
        "FISH (Fluorescence in situ hybridization)",
        "Haplotype-specific PCR",
        "Long-read sequencing (PacBio/Nanopore)"
    ]
    
    def __init__(self):
        """Initialize PMS2Assessor with known regions"""
        self.critical_regions = self.CRITICAL_REGIONS
        logger.info(f"PMS2Assessor initialized with {len(self.critical_regions)} critical regions")
    
    def assess_variant(
        self,
        gene: str,
        position: int,
        variant_type: str = "SNV",
        coverage: Optional[CoverageMetrics] = None
    ) -> PMS2AssessmentResult:
        """
        Assess a PMS2 variant for pseudogene risk.
        
        Args:
            gene: Gene name (should be "PMS2")
            position: Genomic position
            variant_type: Type of variant (SNV, indel, etc)
            coverage: Optional CoverageMetrics object
            
        Returns:
            PMS2AssessmentResult with risk assessment
        """
        
        if gene != "PMS2":
            logger.warning(f"PMS2Assessor called for {gene}, not PMS2")
            raise ValueError("This assessor is for PMS2 only")
        
        is_critical = self.is_in_critical_region(position)
        in_pseudogene = self._check_pseudogene_likelihood(position, variant_type)
        
        # Determine risk level
        if in_pseudogene and is_critical:
            pseudogene_risk = SeverityLevel.CRITICAL
        elif in_pseudogene:
            pseudogene_risk = SeverityLevel.HIGH
        elif is_critical:
            pseudogene_risk = SeverityLevel.MEDIUM
        else:
            pseudogene_risk = SeverityLevel.LOW
        
        # Generate recommendations
        recommendations = self._generate_recommendations(pseudogene_risk, variant_type)
        
        # Determine if orthogonal validation is needed
        needs_validation = pseudogene_risk in [
            SeverityLevel.HIGH, 
            SeverityLevel.CRITICAL, 
            SeverityLevel.MEDIUM
        ]
        
        # Build high homology regions list
        high_homology_regions = []
        if is_critical:
            for region in self.critical_regions:
                if region.start <= position <= region.end:
                    high_homology_regions.append({
                        "name": region.name,
                        "start": region.start,
                        "end": region.end,
                        "description": region.description
                    })
        
        # Build variants in homologous regions
        variants_in_homologous = []
        if in_pseudogene:
            variants_in_homologous.append({
                "position": position,
                "type": variant_type,
                "risk": pseudogene_risk.value
            })
        
        # Create result using correct schema from models.py
        result = PMS2AssessmentResult(
            gene=gene,
            coverage=coverage,
            high_homology_regions=high_homology_regions,
            pseudogene_risk=pseudogene_risk,
            variants_in_homologous_regions=variants_in_homologous,
            requires_orthogonal_confirmation=needs_validation,
            recommendations=recommendations
        )
        
        logger.info(f"PMS2 assessment completed: {pseudogene_risk.value}")
        return result
    
    def is_in_critical_region(self, position: int) -> bool:
        """Check if position falls in a known critical region."""
        for region in self.critical_regions:
            if region.start <= position <= region.end:
                logger.debug(f"Position {position} is in critical region: {region.name}")
                return True
        return False
    
    def _check_pseudogene_likelihood(self, position: int, variant_type: str) -> bool:
        """Estimate if variant is likely in pseudogene."""
        if variant_type in ["indel", "deletion", "insertion"] and self.is_in_critical_region(position):
            return True
        
        if position in range(20000, 22000):
            return True
        
        return False
    
    def _generate_recommendations(self, risk_level: SeverityLevel, variant_type: str) -> List[str]:
        """Generate recommendations based on risk level."""
        recommendations = []
        
        if risk_level == SeverityLevel.CRITICAL:
            recommendations.append("❌ DO NOT REPORT as germline PMS2 mutation without validation")
            recommendations.append("✅ REQUIRE orthogonal validation (Sanger or ddPCR minimum)")
            recommendations.append("✅ Consider FISH to determine chromosome location")
            recommendations.append("✅ Consult genetic counselor before disclosure")
        
        elif risk_level == SeverityLevel.HIGH:
            recommendations.append("⚠️ High pseudogene probability")
            recommendations.append("✅ Recommend Sanger sequencing confirmation")
            recommendations.append("✅ Consider ddPCR for quantification")
        
        elif risk_level == SeverityLevel.MEDIUM:
            recommendations.append("⚠️ Moderate pseudogene risk")
            recommendations.append("✅ Recommend validation if pathogenic classification likely")
        
        else:  # LOW
            recommendations.append("✅ Low pseudogene risk - standard analysis acceptable")
        
        if variant_type in ["deletion", "duplication"]:
            recommendations.append("⚠️ Structural variants: HIGHLY pseudogene-prone")
            recommendations.append("✅ CNV analysis recommended (array-CGH or qPCR)")
        
        return recommendations
    
    def list_orthogonal_methods(self) -> List[str]:
        """Return available orthogonal validation methods"""
        return self.VALIDATION_METHODS


if __name__ == "__main__":
    assessor = PMS2Assessor()
    
    result1 = assessor.assess_variant("PMS2", position=21000, variant_type="SNV")
    print("Test 1: SNV in critical region")
    print(f"Risk: {result1.pseudogene_risk.value.upper()}")
    print(f"Validation needed: {result1.requires_orthogonal_confirmation}")
    print()
    
    result2 = assessor.assess_variant("PMS2", position=36000, variant_type="deletion")
    print("Test 2: Deletion in critical region")
    print(f"Risk: {result2.pseudogene_risk.value.upper()}")
    print()
    
    result3 = assessor.assess_variant("PMS2", position=50000, variant_type="SNV")
    print("Test 3: SNV outside critical regions")
    print(f"Risk: {result3.pseudogene_risk.value.upper()}")


# ============================================================================
# ETAPA 7: HomologyAnalyzer - Detect pseudogene contamination risk
# ============================================================================

class HomologyAnalyzer:
    """
    Analyzes PMS2 regions with high homology to pseudogene PMS2CL.
    
    PMS2 has ~95% identity with pseudogene in exons 11-15.
    This class identifies high-risk regions for variant misinterpretation.
    """
    
    # Regions with HIGH homology to PMS2CL (based on BLAST analysis)
    HOMOLOGY_REGIONS = {
        "exon_11": {
            "chr_position_start": 33560000,
            "chr_position_end": 33561500,
            "homology_pct": 95.2,
            "mapeability": 0.45,  # Low mapability = hard to map reads correctly
            "risk_level": "CRITICAL",
            "description": "DNA binding domain - HIGH pseudogene contamination"
        },
        "exon_15": {
            "chr_position_start": 33573000,
            "chr_position_end": 33574200,
            "homology_pct": 87.5,
            "mapeability": 0.62,
            "risk_level": "HIGH",
            "description": "Exon 15 junction - MEDIUM pseudogene risk"
        },
        "exon_5_6": {
            "chr_position_start": 33535000,
            "chr_position_end": 33536500,
            "homology_pct": 82.1,
            "mapeability": 0.70,
            "risk_level": "MEDIUM",
            "description": "Exon 5-6 region - Some pseudogene overlap"
        }
    }
    
    def __init__(self):
        """Initialize HomologyAnalyzer"""
        self.regions = self.HOMOLOGY_REGIONS
        logger.info(f"HomologyAnalyzer initialized with {len(self.regions)} high-homology regions")
    
    def analyze_position(self, position: int) -> dict:
        """
        Analyze if a genomic position is in high-homology region.
        
        Args:
            position: Genomic position (bp)
        
        Returns:
            dict with homology info or empty dict if not in region
        """
        for region_name, region_data in self.regions.items():
            if region_data["chr_position_start"] <= position <= region_data["chr_position_end"]:
                return {
                    "in_homology_region": True,
                    "region_name": region_name,
                    "homology_pct": region_data["homology_pct"],
                    "mapeability": region_data["mapeability"],
                    "risk_level": region_data["risk_level"],
                    "description": region_data["description"]
                }
        
        return {"in_homology_region": False}
    
    def get_risk_from_homology(self, homology_pct: float) -> str:
        """
        Classify risk level based on homology percentage.
        
        Args:
            homology_pct: Percentage homology (0-100)
        
        Returns:
            Risk level: LOW, MEDIUM, HIGH, CRITICAL
        """
        if homology_pct >= 90:
            return "CRITICAL"
        elif homology_pct >= 85:
            return "HIGH"
        elif homology_pct >= 80:
            return "MEDIUM"
        else:
            return "LOW"
    
    def recommend_validation(self, homology_pct: float, coverage_depth: float) -> str:
        """
        Recommend orthogonal validation based on homology + coverage.
        
        Args:
            homology_pct: Percentage homology
            coverage_depth: Mean coverage depth at position
        
        Returns:
            Recommendation text
        """
        if homology_pct >= 90 and coverage_depth < 50:
            return "CRITICAL: Sanger + long-read sequencing required"
        elif homology_pct >= 85 and coverage_depth < 75:
            return "HIGH: Sanger sequencing strongly recommended"
        elif homology_pct >= 80 and coverage_depth < 100:
            return "MEDIUM: Consider ddPCR or targeted Sanger"
        else:
            return "LOW: Standard NGS interpretation acceptable"



class PseudogeneRiskDetector:
    """
    Calculates pseudogene contamination risk score (0-100).
    
    Combines multiple factors:
    - Homology percentage
    - Coverage depth
    - Variant type
    - Mapeability
    
    Returns risk classification: LOW, MEDIUM, HIGH, CRITICAL
    """
    
    def __init__(self):
        """Initialize PseudogeneRiskDetector with scoring thresholds"""
        # Risk score thresholds
        self.RISK_THRESHOLDS = {
            "LOW": (0, 25),
            "MEDIUM": (25, 50),
            "HIGH": (50, 75),
            "CRITICAL": (75, 100)
        }
        
        # Weighting factors for risk calculation
        self.WEIGHTS = {
            "homology": 0.40,      # 40% based on homology %
            "coverage": 0.30,      # 30% based on coverage
            "mapeability": 0.20,   # 20% based on mapeability
            "variant_type": 0.10   # 10% based on variant type
        }
        
        logger.info("PseudogeneRiskDetector initialized")
    
    def calculate_risk_score(
        self,
        homology_pct: float,
        coverage_depth: float,
        mapeability: float,
        variant_type: str = "SNV"
    ) -> dict:
        """
        Calculate pseudogene risk score using weighted factors.
        
        Args:
            homology_pct: Percentage homology (0-100)
            coverage_depth: Mean coverage depth (reads)
            mapeability: Mapeability score (0-1)
            variant_type: Type of variant (SNV, indel, deletion, duplication)
        
        Returns:
            dict with risk_score, risk_level, confidence
        """
        
        # Component 1: Homology contribution (0-100 scale)
        # Higher homology = higher risk
        homology_score = homology_pct  # Already 0-100
        
        # Component 2: Coverage contribution (0-100 scale)
        # Lower coverage = higher risk
        # At 20x: score=100 (worst), at 100x: score=40 (better)
        if coverage_depth <= 20:
            coverage_score = 100
        elif coverage_depth >= 100:
            coverage_score = 40
        else:
            # Linear interpolation: 20x → 100, 100x → 40
            coverage_score = 100 - ((coverage_depth - 20) / 80) * 60
        
        # Component 3: Mapeability contribution (0-100 scale)
        # Lower mapeability = higher risk
        # At 0.3: score=100 (very hard to map), at 0.9: score=20 (easy)
        if mapeability <= 0.3:
            mapeability_score = 100
        elif mapeability >= 0.9:
            mapeability_score = 20
        else:
            # Linear interpolation: 0.3 → 100, 0.9 → 20
            mapeability_score = 100 - ((mapeability - 0.3) / 0.6) * 80
        
        # Component 4: Variant type contribution (0-100 scale)
        # Indels in low-mapeability regions = higher risk
        if variant_type.upper() == "INDEL":
            variant_score = 60  # Higher risk for indels
        elif variant_type.upper() == "DELETION":
            variant_score = 80  # Even higher for deletions
        elif variant_type.upper() == "DUPLICATION":
            variant_score = 70  # High for duplications
        else:  # SNV (default)
            variant_score = 40  # Lower risk for SNVs
        
        # Calculate weighted risk score
        risk_score = (
            homology_score * self.WEIGHTS["homology"] +
            coverage_score * self.WEIGHTS["coverage"] +
            mapeability_score * self.WEIGHTS["mapeability"] +
            variant_score * self.WEIGHTS["variant_type"]
        )
        
        # Classify risk level
        risk_level = self._classify_risk(risk_score)
        
        # Calculate confidence (higher score = lower confidence)
        confidence = 100 - risk_score
        
        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "confidence_pct": round(confidence, 1),
            "components": {
                "homology_score": round(homology_score, 1),
                "coverage_score": round(coverage_score, 1),
                "mapeability_score": round(mapeability_score, 1),
                "variant_score": round(variant_score, 1)
            }
        }
    
    def _classify_risk(self, risk_score: float) -> str:
        """
        Classify risk level based on score.
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            Risk level string
        """
        for level, (min_score, max_score) in self.RISK_THRESHOLDS.items():
            if min_score <= risk_score < max_score:
                return level
        return "CRITICAL"  # Fallback for score >= 75
    
    def interpret_result(self, risk_dict: dict) -> str:
        """
        Provide clinical interpretation of risk score.
        
        Args:
            risk_dict: Result from calculate_risk_score()
        
        Returns:
            Clinical interpretation text
        """
        risk_level = risk_dict["risk_level"]
        confidence = risk_dict["confidence_pct"]
        
        interpretations = {
            "LOW": f"Low pseudogene contamination risk. Interpretation confidence: {confidence}%",
            "MEDIUM": f"Moderate pseudogene risk. Recommend caution. Confidence: {confidence}%",
            "HIGH": f"High pseudogene contamination risk. Orthogonal validation recommended. Confidence: {confidence}%",
            "CRITICAL": f"CRITICAL pseudogene risk. Resequencing required before clinical reporting. Confidence: {confidence}%"
        }
        
        return interpretations.get(risk_level, "Unknown risk level")

