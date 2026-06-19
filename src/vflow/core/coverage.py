"""
Coverage Analysis Module

Analyzes sequencing depth across MMR genes.
Reads BAM files and calculates clinical-grade QC metrics.
"""

from typing import Dict, List
from pathlib import Path
import logging

from .models import CoverageMetrics, QCFlag, SeverityLevel

logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """Analyzes coverage depth from BAM files"""
    
    # Clinical thresholds
    MINIMUM_ACCEPTABLE_DEPTH = 20       # Minimum for clinical report
    RECOMMENDED_DEPTH = 50              # Recommended for high confidence
    OPTIMAL_DEPTH = 100                 # Optimal coverage
    
    # Clinical standards
    MINIMUM_BASES_GE_20X = 0.95         # 95% of bases ≥20x
    MINIMUM_BASES_GE_50X = 0.80         # 80% of bases ≥50x
    
    def __init__(self, bam_file: str):
        """Initialize with BAM file path"""
        self.bam_file = Path(bam_file)
        
        if not self.bam_file.exists():
            raise FileNotFoundError(f"BAM file not found: {bam_file}")
        
        logger.info(f"Initialized CoverageAnalyzer with {bam_file}")
    
    def analyze_gene(self, gene: str, start: int, end: int) -> CoverageMetrics:
        """
        Analyze coverage for a specific gene region
        
        Args:
            gene: Gene name (e.g., "MLH1")
            start: Start position (bp)
            end: End position (bp)
        
        Returns:
            CoverageMetrics object with analysis results
        """
        
        logger.info(f"Analyzing {gene} ({start}-{end})")
        
        # NOTE: This is placeholder code
        # Real implementation would use pysam to read BAM
        # For now, we show the structure and types
        
        # Simulated data for demonstration
        depths = [95.2, 92.1, 88.5, 96.3, 94.7]  # Example depths
        
        mean_depth = sum(depths) / len(depths)
        min_depth = min(depths)
        max_depth = max(depths)
        median_depth = sorted(depths)[len(depths)//2]
        
        # Calculate percentage of bases meeting clinical thresholds
        bases_ge_20x = len([d for d in depths if d >= 20]) / len(depths)
        bases_ge_50x = len([d for d in depths if d >= 50]) / len(depths)
        bases_ge_100x = len([d for d in depths if d >= 100]) / len(depths)
        
        metrics = CoverageMetrics(
            gene=gene,
            mean_depth=mean_depth,
            min_depth=min_depth,
            max_depth=max_depth,
            median_depth=median_depth,
            bases_ge_20x=bases_ge_20x,
            bases_ge_50x=bases_ge_50x,
            bases_ge_100x=bases_ge_100x,
            breadth=bases_ge_20x,  # Simplified
            uniformity=0.89  # Placeholder
        )
        
        logger.info(f"{gene} analysis complete: {metrics.summary()}")
        
        return metrics
    
    def assess_quality(self, metrics: CoverageMetrics) -> List[QCFlag]:
        """
        Assess coverage quality and generate flags
        
        Returns:
            List of QCFlag objects indicating issues
        """
        
        flags = []
        
        # Check minimum acceptable depth
        if metrics.mean_depth < self.MINIMUM_ACCEPTABLE_DEPTH:
            flags.append(QCFlag(
                severity=SeverityLevel.CRITICAL,
                category="COVERAGE",
                message=f"Mean depth {metrics.mean_depth:.1f}x below minimum {self.MINIMUM_ACCEPTABLE_DEPTH}x",
                recommendation="Insufficient coverage. Consider resequencing."
            ))
        
        # Check breadth (% bases meeting minimum)
        if metrics.bases_ge_20x < self.MINIMUM_BASES_GE_20X:
            flags.append(QCFlag(
                severity=SeverityLevel.HIGH,
                category="COVERAGE",
                message=f"Only {metrics.bases_ge_20x*100:.1f}% of bases ≥20x (requires ≥95%)",
                recommendation="Review low-coverage regions"
            ))
        
        # Check uniformity
        if metrics.uniformity < 0.7:
            flags.append(QCFlag(
                severity=SeverityLevel.MEDIUM,
                category="UNIFORMITY",
                message=f"Poor uniformity ({metrics.uniformity:.2f}). May indicate bias.",
                recommendation="Check for amplification bias"
            ))
        
        return flags


if __name__ == "__main__":
    # Example usage
    analyzer = CoverageAnalyzer("example.bam")
    
    # Analyze MLH1 gene
    metrics = analyzer.analyze_gene("MLH1", 36999992, 37092337)
    print(metrics.summary())
    
    # Assess quality
    flags = analyzer.assess_quality(metrics)
    for flag in flags:
        print(f"  {flag.severity.value}: {flag.message}")


# ============================================================================
# ETAPA 7: BreadthAnalyzer - Calculate breadth of coverage
# ============================================================================

class BreadthAnalyzer:
    """
    Analyzes breadth of coverage (% of bases meeting depth thresholds).
    
    Breadth = percentage of bases with coverage ≥ threshold
    Important for detecting "blind spots" in coverage
    """
    
    # Clinical thresholds for breadth
    BREADTH_THRESHOLDS = {
        "ge_20x": 0.95,   # 95% of bases should be ≥20x
        "ge_50x": 0.80,   # 80% of bases should be ≥50x
        "ge_100x": 0.50   # 50% of bases should be ≥100x
    }
    
    def __init__(self):
        """Initialize BreadthAnalyzer"""
        logger.info("BreadthAnalyzer initialized")
    
    def calculate_breadth(self, depth_array: list) -> dict:
        """
        Calculate breadth at multiple thresholds.
        
        Args:
            depth_array: List of depth values per base
        
        Returns:
            dict with breadth at each threshold
        """
        if not depth_array or len(depth_array) == 0:
            return {
                "bases_ge_20x": 0.0,
                "bases_ge_50x": 0.0,
                "bases_ge_100x": 0.0,
                "status": "FAIL",
                "message": "Empty depth array"
            }
        
        total_bases = len(depth_array)
        
        # Count bases meeting each threshold
        bases_ge_20x = sum(1 for d in depth_array if d >= 20)
        bases_ge_50x = sum(1 for d in depth_array if d >= 50)
        bases_ge_100x = sum(1 for d in depth_array if d >= 100)
        
        # Calculate percentages
        breadth_20x = bases_ge_20x / total_bases
        breadth_50x = bases_ge_50x / total_bases
        breadth_100x = bases_ge_100x / total_bases
        
        # Determine status
        status = self._assess_status(breadth_20x, breadth_50x)
        
        return {
            "bases_ge_20x": round(breadth_20x, 4),
            "bases_ge_50x": round(breadth_50x, 4),
            "bases_ge_100x": round(breadth_100x, 4),
            "total_bases_analyzed": total_bases,
            "status": status,
            "message": self._generate_message(breadth_20x, breadth_50x)
        }
    
    def _assess_status(self, breadth_20x: float, breadth_50x: float) -> str:
        """Assess quality status based on breadth values"""
        if breadth_20x >= self.BREADTH_THRESHOLDS["ge_20x"]:
            return "PASS"
        elif breadth_20x >= 0.90:
            return "WARNING"
        else:
            return "FAIL"
    
    def _generate_message(self, breadth_20x: float, breadth_50x: float) -> str:
        """Generate clinical interpretation message"""
        msg_20x = f"{breadth_20x*100:.1f}% of bases ≥20x"
        msg_50x = f"{breadth_50x*100:.1f}% of bases ≥50x"
        return f"{msg_20x} ({msg_50x})"


# ============================================================================
# ETAPA 7: UniformityAnalyzer - Calculate coverage uniformity
# ============================================================================

class UniformityAnalyzer:
    """
    Analyzes coverage uniformity using Fold-80 metric.
    
    Fold-80 = 80th percentile / median
    Lower values = better uniformity
    Typical: 1.0-2.0 = good, >2.0 = poor
    """
    
    def __init__(self):
        """Initialize UniformityAnalyzer"""
        self.fold_80_threshold = 2.0  # Good uniformity
        logger.info("UniformityAnalyzer initialized")
    
    def calculate_fold_80(self, depth_array: list) -> dict:
        """
        Calculate Fold-80 uniformity metric.
        
        Args:
            depth_array: List of depth values per base
        
        Returns:
            dict with fold-80 value and interpretation
        """
        if not depth_array or len(depth_array) < 2:
            return {
                "fold_80": None,
                "median": None,
                "percentile_80": None,
                "status": "FAIL",
                "message": "Insufficient data"
            }
        
        import statistics
        
        # Calculate statistics
        median = statistics.median(depth_array)
        
        # Calculate 80th percentile manually
        sorted_depths = sorted(depth_array)
        percentile_80_idx = int(len(sorted_depths) * 0.80)
        percentile_80 = sorted_depths[percentile_80_idx]
        
        # Calculate Fold-80
        if median == 0:
            fold_80 = float('inf')
        else:
            fold_80 = percentile_80 / median
        
        # Assess status
        status = self._assess_uniformity(fold_80)
        
        return {
            "fold_80": round(fold_80, 2),
            "median": float(median),
            "percentile_80": float(percentile_80),
            "status": status,
            "message": self._generate_message(fold_80, status)
        }
    
    def _assess_uniformity(self, fold_80: float) -> str:
        """Assess uniformity quality"""
        if fold_80 <= 1.5:
            return "EXCELLENT"
        elif fold_80 <= 2.0:
            return "GOOD"
        elif fold_80 <= 3.0:
            return "ACCEPTABLE"
        else:
            return "POOR"
    
    def _generate_message(self, fold_80: float, status: str) -> str:
        """Generate clinical interpretation"""
        interpretations = {
            "EXCELLENT": f"Fold-80={fold_80:.2f}: Excellent uniformity",
            "GOOD": f"Fold-80={fold_80:.2f}: Good uniformity",
            "ACCEPTABLE": f"Fold-80={fold_80:.2f}: Acceptable but check for bias",
            "POOR": f"Fold-80={fold_80:.2f}: Poor uniformity - may indicate bias"
        }
        return interpretations.get(status, "Unknown status")

