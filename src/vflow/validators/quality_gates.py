"""
Quality Gates and Severity Classification
Translates technical metrics into clinical actions.
"""

from enum import Enum
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ActionLevel(Enum):
    """Clinical action levels"""
    INFO = "ℹ️"        # Informativo apenas
    MONITOR = "📋"     # Monitorar e revisar
    REVIEW = "⚠️"      # Revisão recomendada
    VALIDATE = "🔬"    # Validação ortogonal
    RESEQUENCE = "🚫"  # Resequenciamento obrigatório


class SeverityClassifier:
    """
    Classifies QC issues by clinical severity.
    
    Combines technical metrics into actionable clinical recommendations.
    """
    
    # Severity levels with metadata
    SEVERITY_MAP = {
        "LOW": {
            "symbol": "ℹ️",
            "color": "blue",
            "numeric": 1,
            "clinical_action": "Monitor",
            "description": "Informativo, não afeta interpretação"
        },
        "MEDIUM": {
            "symbol": "⚠️",
            "color": "yellow",
            "numeric": 2,
            "clinical_action": "Review",
            "description": "Atenção recomendada, pode afetar confiabilidade"
        },
        "HIGH": {
            "symbol": "🚨",
            "color": "orange",
            "numeric": 3,
            "clinical_action": "Validate",
            "description": "Afeta confiabilidade do resultado"
        },
        "CRITICAL": {
            "symbol": "🚫",
            "color": "red",
            "numeric": 4,
            "clinical_action": "Resequence",
            "description": "Impede interpretação confiável"
        }
    }
    
    def __init__(self):
        """Initialize SeverityClassifier"""
        logger.info("SeverityClassifier initialized")
    
    def classify_coverage_breadth(self, breadth_ge_20x: float) -> dict:
        """
        Classify breadth of coverage (% bases ≥20x).
        
        Args:
            breadth_ge_20x: Fraction of bases with ≥20x coverage
        
        Returns:
            dict with severity and action
        """
        if breadth_ge_20x >= 0.95:
            severity = "LOW"
            message = f"Excellent breadth: {breadth_ge_20x*100:.1f}% bases ≥20x"
        elif breadth_ge_20x >= 0.90:
            severity = "MEDIUM"
            message = f"Good breadth: {breadth_ge_20x*100:.1f}% bases ≥20x (recommend ≥95%)"
        elif breadth_ge_20x >= 0.80:
            severity = "HIGH"
            message = f"Acceptable breadth: {breadth_ge_20x*100:.1f}% bases ≥20x - review low-coverage regions"
        else:
            severity = "CRITICAL"
            message = f"Poor breadth: {breadth_ge_20x*100:.1f}% bases ≥20x - resequencing recommended"
        
        return {
            "severity": severity,
            "message": message,
            "symbol": self.SEVERITY_MAP[severity]["symbol"],
            "action": self.SEVERITY_MAP[severity]["clinical_action"]
        }
    
    def classify_coverage_uniformity(self, fold_80: float) -> dict:
        """
        Classify coverage uniformity (Fold-80 metric).
        
        Args:
            fold_80: Fold-80 value (80th percentile / median)
        
        Returns:
            dict with severity and action
        """
        if fold_80 <= 1.5:
            severity = "LOW"
            message = f"Excellent uniformity: Fold-80 = {fold_80:.2f}"
        elif fold_80 <= 2.0:
            severity = "MEDIUM"
            message = f"Good uniformity: Fold-80 = {fold_80:.2f} (check for bias)"
        elif fold_80 <= 3.0:
            severity = "HIGH"
            message = f"Acceptable uniformity: Fold-80 = {fold_80:.2f} - may indicate bias"
        else:
            severity = "CRITICAL"
            message = f"Poor uniformity: Fold-80 = {fold_80:.2f} - check for amplification bias"
        
        return {
            "severity": severity,
            "message": message,
            "symbol": self.SEVERITY_MAP[severity]["symbol"],
            "action": self.SEVERITY_MAP[severity]["clinical_action"]
        }
    
    def classify_pseudogene_risk(self, risk_score: float, confidence: float) -> dict:
        """
        Classify pseudogene contamination risk.
        
        Args:
            risk_score: Risk score (0-100)
            confidence: Confidence in interpretation (0-100)
        
        Returns:
            dict with severity and action
        """
        if risk_score <= 25:
            severity = "LOW"
            message = f"Low pseudogene risk (score: {risk_score:.1f}, confidence: {confidence:.1f}%)"
        elif risk_score <= 50:
            severity = "MEDIUM"
            message = f"Moderate pseudogene risk (score: {risk_score:.1f}) - caution advised"
        elif risk_score <= 75:
            severity = "HIGH"
            message = f"High pseudogene risk (score: {risk_score:.1f}) - orthogonal validation recommended"
        else:
            severity = "CRITICAL"
            message = f"CRITICAL pseudogene risk (score: {risk_score:.1f}) - resequencing required"
        
        return {
            "severity": severity,
            "message": message,
            "symbol": self.SEVERITY_MAP[severity]["symbol"],
            "action": self.SEVERITY_MAP[severity]["clinical_action"]
        }
    
    def aggregate_flags(self, flags: List[dict]) -> dict:
        """
        Aggregate multiple QC flags into single recommendation.
        
        Args:
            flags: List of flag dicts from classify_* methods
        
        Returns:
            Aggregated result with highest severity
        """
        if not flags:
            return {
                "overall_severity": "LOW",
                "symbol": self.SEVERITY_MAP["LOW"]["symbol"],
                "action": "Monitor",
                "message": "All QC metrics pass",
                "flag_count": 0
            }
        
        # Find highest severity
        severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        max_severity = "LOW"
        
        for flag in flags:
            sev = flag.get("severity", "LOW")
            if severity_levels.index(sev) > severity_levels.index(max_severity):
                max_severity = sev
        
        # Generate aggregated message
        messages = [f["message"] for f in flags]
        
        return {
            "overall_severity": max_severity,
            "symbol": self.SEVERITY_MAP[max_severity]["symbol"],
            "action": self.SEVERITY_MAP[max_severity]["clinical_action"],
            "message": f"Highest concern: {max_severity}",
            "details": messages,
            "flag_count": len(flags),
            "recommendation": self._generate_recommendation(max_severity)
        }
    
    def _generate_recommendation(self, severity: str) -> str:
        """Generate clinical recommendation based on severity"""
        recommendations = {
            "LOW": "Proceed with standard interpretation",
            "MEDIUM": "Review flagged regions before reporting",
            "HIGH": "Recommend orthogonal validation (e.g., Sanger sequencing)",
            "CRITICAL": "RESEQUENCING REQUIRED - Do not report based on NGS alone"
        }
        return recommendations.get(severity, "Unknown severity")
    
    def generate_qc_summary(self, metrics: dict) -> dict:
        """
        Generate complete QC summary from multiple metrics.
        
        Args:
            metrics: dict containing:
                - breadth_ge_20x: float
                - fold_80: float
                - pseudogene_risk_score: float
                - pseudogene_confidence: float
        
        Returns:
            Complete QC summary with all flags and recommendations
        """
        flags = []
        
        # Classify breadth
        if "breadth_ge_20x" in metrics:
            breadth_flag = self.classify_coverage_breadth(metrics["breadth_ge_20x"])
            flags.append(breadth_flag)
        
        # Classify uniformity
        if "fold_80" in metrics:
            uniformity_flag = self.classify_coverage_uniformity(metrics["fold_80"])
            flags.append(uniformity_flag)
        
        # Classify pseudogene risk
        if "pseudogene_risk_score" in metrics:
            risk_flag = self.classify_pseudogene_risk(
                metrics["pseudogene_risk_score"],
                metrics.get("pseudogene_confidence", 50)
            )
            flags.append(risk_flag)
        
        # Aggregate
        aggregated = self.aggregate_flags(flags)
        
        return {
            "individual_flags": flags,
            "aggregated_result": aggregated,
            "clinical_interpretation": self._generate_interpretation(aggregated)
        }
    
    def _generate_interpretation(self, aggregated: dict) -> str:
        """Generate human-readable clinical interpretation"""
        severity = aggregated["overall_severity"]
        
        interpretations = {
            "LOW": "Quality metrics are excellent. Interpretation confidence is high.",
            "MEDIUM": "Quality metrics are acceptable but require attention to flagged regions.",
            "HIGH": "Quality concerns require orthogonal validation before clinical reporting.",
            "CRITICAL": "CRITICAL quality issues prevent reliable interpretation. Resequencing is mandatory."
        }
        
        return interpretations.get(severity, "Unknown interpretation")

