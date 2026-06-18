"""
ACMG Evidence Collection Module for VariantFlow-MMR

Implements ACMG/AMP 2015 criteria for variant classification.
Reference: Richards et al. (2015). Standards and guidelines for interpretation 
of sequence variants. Genetics in Medicine 17:405-423.

CRITICAL: This module COLLECTS EVIDENCE only.
It does NOT classify variants (that's the geneticist's responsibility).

Categories of evidence:
- Pathogenic: PVS1, PS1-PS4, PM1-PM6
- Benign: BA1-BA2, BS1-BS4, BP1-BP7
- Supporting: PP1-PP5
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ACMGCriterion:
    """
    A single ACMG/AMP 2015 criterion (piece of evidence).
    
    This represents ONE evidence point that contributes to 
    variant classification.
    """
    code: str                    # "PVS1", "PS1", "PM1", "BA1", etc
    category: str                # "Pathogenic", "Benign", "Supporting"
    strength: str                # "Very Strong", "Strong", "Moderate", "Supporting"
    description: str             # Human-readable explanation
    evidence: str                # Specific data found (e.g., "ClinVar: frequency=...")
    source: str                  # Where data came from ("ClinVar", "gnomAD", "InSiGHT")
    references: List[str] = field(default_factory=list)  # PMID, URLs, etc
    confidence: float = 0.85     # 0.0-1.0 (how confident in this evidence?)
    
    def __str__(self) -> str:
        """Human-readable representation"""
        return (
            f"[{self.code}] {self.description}\n"
            f"  Source: {self.source}\n"
            f"  Evidence: {self.evidence}\n"
            f"  Confidence: {self.confidence:.0%}"
        )


@dataclass
class ACMGEvidenceResult:
    """
    Result of ACMG evidence collection for a variant.
    
    Contains all evidence collected, organized by category.
    The geneticist uses this to make final classification decision.
    """
    variant: str                                    # "PMS2:chr7:6012876:C>T"
    gene: str                                       # "PMS2"
    pathogenic_criteria: List[ACMGCriterion] = field(default_factory=list)
    benign_criteria: List[ACMGCriterion] = field(default_factory=list)
    supporting_criteria: List[ACMGCriterion] = field(default_factory=list)
    total_criteria_found: int = 0
    suggested_interpretation: str = "Uncertain"    # NOT a classification!
    clinical_note: Optional[str] = None
    
    def summary(self) -> str:
        """Generate human-readable summary for clinical report"""
        summary_text = (
            f"\n{'='*70}\n"
            f"ACMG EVIDENCE COLLECTION FOR: {self.variant}\n"
            f"Gene: {self.gene}\n"
            f"{'='*70}\n\n"
        )
        
        if self.pathogenic_criteria:
            summary_text += f"PATHOGENIC EVIDENCE ({len(self.pathogenic_criteria)}):\n"
            summary_text += "-" * 70 + "\n"
            for crit in self.pathogenic_criteria:
                summary_text += f"{str(crit)}\n\n"
        
        if self.benign_criteria:
            summary_text += f"BENIGN EVIDENCE ({len(self.benign_criteria)}):\n"
            summary_text += "-" * 70 + "\n"
            for crit in self.benign_criteria:
                summary_text += f"{str(crit)}\n\n"
        
        if self.supporting_criteria:
            summary_text += f"SUPPORTING EVIDENCE ({len(self.supporting_criteria)}):\n"
            summary_text += "-" * 70 + "\n"
            for crit in self.supporting_criteria:
                summary_text += f"{str(crit)}\n\n"
        
        summary_text += f"{'='*70}\n"
        summary_text += f"TOTAL CRITERIA FOUND: {self.total_criteria_found}\n"
        summary_text += f"SUGGESTED INTERPRETATION: {self.suggested_interpretation}\n"
        summary_text += f"(IMPORTANT: Geneticist must review all evidence and make final classification)\n"
        summary_text += f"{'='*70}\n"
        
        if self.clinical_note:
            summary_text += f"\nCLINICAL NOTE:\n{self.clinical_note}\n"
        
        return summary_text


class ACMGEvidenceCollector:
    """
    Collect ACMG/AMP 2015 evidence for variant classification.
    
    This class queries multiple databases and sources to gather
    evidence, but does NOT make a final classification.
    That decision belongs to the geneticist.
    """
    
    # MMR genes that we specialize in
    MMR_GENES = ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"]
    
    # ACMG criterion strengths (ordered from strongest to weakest)
    STRENGTH_ORDER = {
        "Very Strong": 4,
        "Strong": 3,
        "Moderate": 2,
        "Supporting": 1
    }
    
    def __init__(self):
        """Initialize ACMG evidence collector"""
        logger.info("ACMGEvidenceCollector initialized")
    
    def collect_evidence(
        self,
        gene: str,
        chromosome: str,
        position: int,
        reference: str,
        alternate: str,
        variant_type: str = "SNV"
    ) -> ACMGEvidenceResult:
        """
        Collect ACMG evidence for a variant.
        
        Args:
            gene: Gene name (e.g., "PMS2")
            chromosome: Chromosome (e.g., "chr7")
            position: Genomic position
            reference: Reference allele
            alternate: Alternate allele
            variant_type: Type of variant ("SNV", "indel", "deletion", etc)
            
        Returns:
            ACMGEvidenceResult with all collected evidence
        """
        
        # Validate gene
        if gene not in self.MMR_GENES:
            logger.warning(f"Gene {gene} is not an MMR gene. Evidence may be incomplete.")
        
        # Create variant identifier
        variant_id = f"{gene}:{chromosome}:{position}:{reference}>{alternate}"
        logger.info(f"Collecting ACMG evidence for {variant_id}")
        
        # Collect evidence from different sources
        pathogenic_criteria = []
        benign_criteria = []
        supporting_criteria = []
        
        # 1. Check ClinVar (simulated)
        clinvar_evidence = self._check_clinvar(gene, variant_id, variant_type)
        if clinvar_evidence:
            if "Pathogenic" in clinvar_evidence.category:
                pathogenic_criteria.append(clinvar_evidence)
            elif "Benign" in clinvar_evidence.category:
                benign_criteria.append(clinvar_evidence)
            else:
                supporting_criteria.append(clinvar_evidence)
        
        # 2. Check gnomAD (simulated)
        gnomad_evidence = self._check_gnomad(position, variant_type)
        if gnomad_evidence:
            if "Benign" in gnomad_evidence.category:
                benign_criteria.append(gnomad_evidence)
            else:
                supporting_criteria.append(gnomad_evidence)
        
        # 3. Check InSiGHT (for MMR genes)
        insight_evidence = self._check_insight(gene, position)
        if insight_evidence:
            for evidence in insight_evidence:
                if "Pathogenic" in evidence.category:
                    pathogenic_criteria.append(evidence)
                elif "Benign" in evidence.category:
                    benign_criteria.append(evidence)
                else:
                    supporting_criteria.append(evidence)
        
        # 4. Check variant type
        vartype_evidence = self._check_variant_type(variant_type)
        if vartype_evidence:
            pathogenic_criteria.append(vartype_evidence)
        
        # 5. Conservation check (simulated)
        conservation_evidence = self._check_conservation(gene, position)
        if conservation_evidence:
            supporting_criteria.append(conservation_evidence)
        
        # Determine suggested interpretation (NOT final classification!)
        suggested_interpretation = self._suggest_interpretation(
            pathogenic_criteria, benign_criteria, supporting_criteria
        )
        
        # Build result
        result = ACMGEvidenceResult(
            variant=variant_id,
            gene=gene,
            pathogenic_criteria=pathogenic_criteria,
            benign_criteria=benign_criteria,
            supporting_criteria=supporting_criteria,
            total_criteria_found=len(pathogenic_criteria) + len(benign_criteria) + len(supporting_criteria),
            suggested_interpretation=suggested_interpretation,
            clinical_note=self._generate_clinical_note(gene, variant_type)
        )
        
        logger.info(f"Evidence collection complete: {result.total_criteria_found} criteria found")
        return result
    
    def _check_clinvar(self, gene: str, variant_id: str, variant_type: str) -> Optional[ACMGCriterion]:
        """
        Check ClinVar for existing reports of this variant.
        
        Simulated: In production, this would query the actual ClinVar API.
        """
        # Simulated ClinVar response
        if variant_type == "SNV" and "chr7" in variant_id:
            return ACMGCriterion(
                code="PS1",
                category="Pathogenic",
                strength="Strong",
                description="Same nucleotide change as a previously established pathogenic variant",
                evidence="ClinVar: This variant is reported as Pathogenic in 5+ independent submissions",
                source="ClinVar",
                references=["ClinVar:RCV000000001", "PMID:12345678"],
                confidence=0.95
            )
        return None
    
    def _check_gnomad(self, position: int, variant_type: str) -> Optional[ACMGCriterion]:
        """
        Check gnomAD for population frequency.
        
        Simulated: In production, this would query the gnomAD API.
        """
        # Simulated gnomAD response
        # Rare variants get supporting evidence
        if variant_type == "SNV":
            return ACMGCriterion(
                code="PM2",
                category="Supporting",
                strength="Moderate",
                description="Absent (or at extremely low frequency) in population databases",
                evidence="gnomAD v3: Frequency = 0.00001 (1 in 100,000)",
                source="gnomAD",
                references=["gnomAD v3.1.2"],
                confidence=0.90
            )
        return None
    
    def _check_insight(self, gene: str, position: int) -> List[ACMGCriterion]:
        """
        Check InSiGHT for MMR-specific evidence.
        
        Simulated: In production, this would read from InSiGHT database file.
        """
        evidence = []
        
        if gene in self.MMR_GENES:
            # Simulated InSiGHT response
            if position > 6000000 and position < 6020000:  # Example region
                evidence.append(ACMGCriterion(
                    code="PM1",
                    category="Pathogenic",
                    strength="Moderate",
                    description="Located in a mutational hotspot and/or critical and well-established functional domain",
                    evidence=f"InSiGHT: Position {position} is in known hotspot region for {gene}",
                    source="InSiGHT",
                    references=["InSiGHT Lynch Syndrome Database"],
                    confidence=0.88
                ))
        
        return evidence
    
    def _check_variant_type(self, variant_type: str) -> Optional[ACMGCriterion]:
        """
        Check if variant type is indicative of pathogenicity.
        """
        if variant_type in ["frameshift", "nonsense"]:
            return ACMGCriterion(
                code="PVS1",
                category="Pathogenic",
                strength="Very Strong",
                description="Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon) in a gene where loss of function is a known mechanism of disease",
                evidence=f"Variant type: {variant_type} causes premature termination",
                source="Variant Annotation",
                references=["ACMG/AMP 2015"],
                confidence=0.98
            )
        return None
    
    def _check_conservation(self, gene: str, position: int) -> Optional[ACMGCriterion]:
        """
        Check sequence conservation (simulated).
        """
        # Simulated: In production, would query PHYLOP/PHRED scores
        return ACMGCriterion(
            code="PP3",
            category="Supporting",
            strength="Supporting",
            description="Multiple lines of computational evidence support a deleterious effect on the gene or gene product",
            evidence="SIFT: Deleterious | PolyPhen: Probably damaging | CADD: 25.3",
            source="Bioinformatic Prediction",
            references=["SIFT", "PolyPhen-2", "CADD"],
            confidence=0.80
        )
    
    def _suggest_interpretation(
        self,
        pathogenic: List[ACMGCriterion],
        benign: List[ACMGCriterion],
        supporting: List[ACMGCriterion]
    ) -> str:
        """
        Suggest an interpretation based on evidence count.
        
        IMPORTANT: This is a SUGGESTION ONLY.
        The geneticist makes the final classification.
        """
        pathogenic_count = len(pathogenic)
        benign_count = len(benign)
        supporting_count = len(supporting)
        
        # Very simple heuristic (in reality, much more complex)
        if pathogenic_count >= 2:
            return "Likely Pathogenic (requires geneticist review)"
        elif benign_count >= 2:
            return "Likely Benign (requires geneticist review)"
        elif pathogenic_count >= 1:
            return "Uncertain (leaning Pathogenic - requires geneticist review)"
        elif benign_count >= 1:
            return "Uncertain (leaning Benign - requires geneticist review)"
        else:
            return "Uncertain - Insufficient evidence"
    
    def _generate_clinical_note(self, gene: str, variant_type: str) -> str:
        """Generate a note for the clinical report"""
        return (
            f"This report contains EVIDENCE collected for variant classification according to ACMG/AMP 2015 standards. "
            f"Classification of this variant ({gene} {variant_type}) must be performed by a qualified geneticist "
            f"who reviews all evidence in the clinical context of the patient and family."
        )


# Example usage (for testing)
if __name__ == "__main__":
    collector = ACMGEvidenceCollector()
    
    # Test case 1: Frameshift in PMS2 (critical region)
    print("\n" + "="*70)
    print("TEST 1: Frameshift in PMS2 critical region")
    print("="*70)
    result1 = collector.collect_evidence(
        gene="PMS2",
        chromosome="chr7",
        position=6012876,
        reference="CG",
        alternate="C",
        variant_type="frameshift"
    )
    print(result1.summary())
    
    # Test case 2: Common SNV (likely benign)
    print("\n" + "="*70)
    print("TEST 2: SNV with population evidence")
    print("="*70)
    result2 = collector.collect_evidence(
        gene="MLH1",
        chromosome="chr3",
        position=36993942,
        reference="A",
        alternate="G",
        variant_type="SNV"
    )
    print(result2.summary())
    
    # Test case 3: Nonsense mutation
    print("\n" + "="*70)
    print("TEST 3: Nonsense mutation in MMR gene")
    print("="*70)
    result3 = collector.collect_evidence(
        gene="MSH2",
        chromosome="chr2",
        position=47641559,
        reference="G",
        alternate="A",
        variant_type="nonsense"
    )
    print(result3.summary())
