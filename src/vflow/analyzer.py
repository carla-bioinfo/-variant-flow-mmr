"""
Variant Analyzer - VariantFlow-MMR ETAPA 5

Integra VCF parsing com análise ACMG para pipeline completo.

Classes:
    - VariantAnalyzer: Orquestra análise de variantes
    - AnalysisReport: Resultado consolidado da análise

Exemplo:
    >>> analyzer = VariantAnalyzer(vcf_file='sample.vcf')
    >>> report = analyzer.analyze()
    >>> print(report.summary())
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import logging

from vflow.vcf_parser import VCFParser, VCFVariant
from vflow.core.acmg_evidence import ACMGEvidenceCollector, ACMGEvidenceResult

logger = logging.getLogger(__name__)


@dataclass
class AnalysisReport:
    """Relatório consolidado de análise de variantes.
    
    Attributes:
        vcf_file (str): Arquivo VCF analisado
        variants_total (int): Total de variantes lidas
        variants_analyzed (int): Variantes com resultado ACMG
        results (List[ACMGEvidenceResult]): Resultados ACMG de cada variante
        analysis_date (str): Data/hora da análise
    """
    vcf_file: str
    variants_total: int
    variants_analyzed: int
    results: List[ACMGEvidenceResult] = field(default_factory=list)
    analysis_date: Optional[str] = None
    
    def summary(self) -> str:
        """Gera resumo legível do relatório."""
        summary = f"""
{'='*70}
VARIANT ANALYSIS REPORT - VariantFlow-MMR
{'='*70}

Input VCF: {self.vcf_file}
Total Variants: {self.variants_total}
Analyzed: {self.variants_analyzed}
Analysis Date: {self.analysis_date}

{'='*70}
RESULTS BY GENE:
{'='*70}
"""
        
        # Agrupa por gene
        by_gene = {}
        for result in self.results:
            gene = result.gene
            if gene not in by_gene:
                by_gene[gene] = []
            by_gene[gene].append(result)
        
        # Formata por gene
        for gene in sorted(by_gene.keys()):
            summary += f"\n{gene}:\n"
            summary += "-" * 70 + "\n"
            
            for result in by_gene[gene]:
                summary += f"  {result.variant}\n"
                summary += f"    Criteria Found: {result.total_criteria_found}\n"
                summary += f"    Interpretation: {result.suggested_interpretation}\n"
                summary += f"    Pathogenic: {len(result.pathogenic_criteria)} | "
                summary += f"Benign: {len(result.benign_criteria)}\n\n"
        
        summary += f"{'='*70}\n"
        return summary


class VariantAnalyzer:
    """Orquestra análise completa de variantes de um arquivo VCF.
    
    Attributes:
        vcf_file (Path): Caminho do arquivo VCF
        collector (ACMGEvidenceCollector): Ferramenta ACMG
    """
    
    def __init__(self, vcf_file: str):
        """Inicializa o analisador.
        
        Args:
            vcf_file (str): Caminho do arquivo VCF
            
        Raises:
            FileNotFoundError: Se arquivo não existe
        """
        self.vcf_file = Path(vcf_file)
        
        if not self.vcf_file.exists():
            raise FileNotFoundError(f"VCF file not found: {vcf_file}")
        
        self.collector = ACMGEvidenceCollector()
        logger.info(f"VariantAnalyzer initialized for {vcf_file}")
    
    def analyze(
        self, 
        min_depth: int = 20, 
        min_qual: float = 20.0
    ) -> AnalysisReport:
        """Executa análise completa do VCF.
        
        Args:
            min_depth (int): Cobertura mínima para incluir (padrão: 20x)
            min_qual (float): Score QUAL mínimo (padrão: 20)
        
        Returns:
            AnalysisReport: Relatório consolidado
        """
        logger.info(f"Starting analysis of {self.vcf_file}")
        
        # Inicializa parser
        parser = VCFParser(str(self.vcf_file))
        
        # Lê variantes e filtra qualidade
        variants = parser.parse()
        variants = parser.validate_quality(variants, min_depth, min_qual)
        
        # Processa cada variante
        results = []
        variant_count = 0
        analyzed_count = 0
        
        try:
            for variant in variants:
                variant_count += 1
                
                # Coleta evidência ACMG
                try:
                    result = self.collector.collect_evidence(
                        gene=self._infer_gene(variant.chrom),
                        chromosome=variant.chrom,
                        position=variant.pos,
                        reference=variant.ref,
                        alternate=variant.alt,
                        variant_type=variant.variant_type
                    )
                    
                    results.append(result)
                    analyzed_count += 1
                    
                    logger.info(
                        f"Analyzed {variant}: "
                        f"{result.total_criteria_found} criteria found"
                    )
                
                except Exception as e:
                    logger.warning(f"Failed to analyze {variant}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
        
        # Cria relatório final
        report = AnalysisReport(
            vcf_file=str(self.vcf_file),
            variants_total=variant_count,
            variants_analyzed=analyzed_count,
            results=results
        )
        
        logger.info(
            f"Analysis complete: {analyzed_count}/{variant_count} variants analyzed"
        )
        
        return report
    
    @staticmethod
    def _infer_gene(chrom: str) -> str:
        """Infere gene a partir do cromossomo.
        
        Args:
            chrom (str): Cromossomo (ex: "chr3")
        
        Returns:
            str: Gene mais provável (ex: "MLH1")
        """
        # Mapeamento simplificado
        chrom_to_gene = {
            "chr3": "MLH1",
            "chr2": "MSH2",  # ou MSH6 ou EPCAM
            "chr7": "PMS2"
        }
        
        return chrom_to_gene.get(chrom, "Unknown")


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    analyzer = VariantAnalyzer("examples/sample_lynch.vcf")
    report = analyzer.analyze(min_depth=20)
    
    print(report.summary())
