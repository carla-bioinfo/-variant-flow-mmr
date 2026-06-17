"""
Data models for VariantFlow-MMR

Defines the core data structures used throughout the application.
Uses Python dataclasses for type safety and clarity.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Clinical severity classification"""
    LOW = "LOW"              # Informativo apenas
    MEDIUM = "MEDIUM"        # Atenção recomendada
    HIGH = "HIGH"            # Afeta confiabilidade
    CRITICAL = "CRITICAL"    # Impede interpretação


@dataclass
class CoverageMetrics:
    """Metrics for sequencing depth analysis"""
    
    gene: str                 # Gene name (MLH1, MSH2, etc)
    mean_depth: float         # Average coverage across gene
    min_depth: float          # Minimum coverage (critical value)
    max_depth: float          # Maximum coverage
    median_depth: float       # Median coverage
    
    # Clinical metrics
    bases_ge_20x: float       # % of bases ≥20x (minimum for clinical)
    bases_ge_50x: float       # % of bases ≥50x (recommended)
    bases_ge_100x: float      # % of bases ≥100x (optimal)
    
    # Quality assessment
    breadth: float            # Overall coverage breadth (0.0-1.0)
    uniformity: float         # Uniformity score (0.0-1.0)
    
    def is_acceptable(self) -> bool:
        """Check if coverage meets clinical standards"""
        # Clinical standard: ≥20x for ≥95% of bases
        return self.bases_ge_20x >= 0.95


@dataclass
class QCFlag:
    """Quality control warning/alert"""
    
    severity: SeverityLevel
    category: str             # e.g., "COVERAGE", "PMS2", "UNIFORMITY"
    message: str              # Human-readable message
    exon: Optional[str] = None  # Affected exon (if applicable)
    recommendation: str = "Review"  # Recommended action


@dataclass
class GeneAnalysisResult:
    """Complete analysis result for one gene"""
    
    gene: str
    metrics: CoverageMetrics
    flags: List[QCFlag]
    overall_quality: SeverityLevel
    
    def summary(self) -> str:
        """Generate human-readable summary"""
        return (
            f"{self.gene}: {self.overall_quality.value} "
            f"({self.metrics.mean_depth:.1f}x mean depth, "
            f"{self.metrics.bases_ge_20x*100:.1f}% ≥20x)"
        )


@dataclass
class PMS2AssessmentResult:
    """Specialized assessment for PMS2 (due to pseudogene risk)"""
    
    gene: str = "PMS2"
    coverage: CoverageMetrics = None
    
    # Homology analysis
    high_homology_regions: List[Dict] = None
    pseudogene_risk: SeverityLevel = SeverityLevel.MEDIUM
    
    # Variants in risky regions
    variants_in_homologous_regions: List[Dict] = None
    
    # Recommendations
    requires_orthogonal_confirmation: bool = False
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.high_homology_regions is None:
            self.high_homology_regions = []
        if self.variants_in_homologous_regions is None:
            self.variants_in_homologous_regions = []
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ACMGEvidence:
    """ACMG criteria evidence for a variant"""
    
    variant_id: str           # e.g., "MLH1:c.1234C>T"
    gene: str
    hgvs_notation: str
    
    # ACMG PVS1 (Null variant)
    pvs1: Optional[str] = None
    
    # ACMG PS (Strong pathogenic)
    ps1: Optional[str] = None  # Same amino acid change
    ps2: Optional[str] = None  # Occurs de novo
    ps3: Optional[str] = None  # Functional studies
    ps4: Optional[str] = None  # Prevalence in affected/unaffected
    
    # ACMG PM (Moderate pathogenic)
    pm1: Optional[str] = None  # Located in mutation hotspot
    pm2: Optional[str] = None  # Absent from large databases
    pm3: Optional[str] = None  # Detected in trans with de novo
    pm4: Optional[str] = None  # Protein altering in conserved region
    pm5: Optional[str] = None  # Novel missense in gene with few missense
    pm6: Optional[str] = None  # Assumed de novo
    
    # ACMG BA (Benign) - present if applicable
    ba1: Optional[str] = None  # Frequency in databases >5%
    
    def evidence_summary(self) -> Dict:
        """Summarize collected evidence"""
        evidence = {}
        for criterion in ['pvs1', 'ps1', 'ps2', 'ps3', 'ps4', 
                         'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'ba1']:
            value = getattr(self, criterion, None)
            if value is not None:
                evidence[criterion] = value
        return evidence


@dataclass
class AuditTrailEntry:
    """Log entry for reproducibility"""
    
    timestamp: str            # ISO format timestamp
    action: str               # What happened (e.g., "COVERAGE_ANALYSIS")
    details: Dict             # Additional context
    software_version: str     # VariantFlow version
    user: Optional[str] = None  # Who ran it
    git_commit: Optional[str] = None  # Git commit hash
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.action}: {self.details}"


if __name__ == "__main__":
    # Example: Create a coverage metric
    cov = CoverageMetrics(
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
    
    print(f"Gene: {cov.gene}")
    print(f"Mean depth: {cov.mean_depth}x")
    print(f"Acceptable: {cov.is_acceptable()}")
