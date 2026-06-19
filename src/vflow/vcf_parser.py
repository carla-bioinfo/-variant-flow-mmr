"""
VCF Parser Module - VariantFlow-MMR ETAPA 5

Este módulo lê arquivos VCF (Variant Call Format) e extrai variantes
estruturadas para análise ACMG e avaliação de Síndrome de Lynch.

Classes:
    - VCFVariant: Modelo estruturado de uma variante
    - VCFParser: Leitor eficiente de arquivos VCF

Exemplo:
    >>> parser = VCFParser('sample.vcf')
    >>> for variant in parser.parse():
    ...     print(f"{variant.chrom}:{variant.pos} {variant.ref}->{variant.alt}")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Tuple
import pysam
import logging

logger = logging.getLogger(__name__)


@dataclass
class VCFVariant:
    """Representação estruturada de uma variante genômica.
    
    Attributes:
        chrom (str): Cromossomo (ex: "chr3", "chr2")
        pos (int): Posição genomica (1-based)
        ref (str): Alelo de referência
        alt (str): Alelo alternativo
        genotype (Tuple[int, int]): Genótipo (ex: (0,1) heterozigoto)
        qual (float): Score de qualidade
        depth (Optional[int]): Cobertura de sequenciamento
        filter_status (str): Status de filtro (PASS, .)
    """
    chrom: str
    pos: int
    ref: str
    alt: str
    genotype: Tuple[int, int]
    qual: float
    depth: Optional[int] = None
    filter_status: str = "PASS"
    
    def __str__(self) -> str:
        """Representação legível da variante."""
        return f"{self.chrom}:{self.pos} {self.ref}->{self.alt} ({self.genotype})"
    
    @property
    def variant_type(self) -> str:
        """Classifica o tipo de variante.
        
        Returns:
            str: "SNV", "Deletion", "Insertion" ou "Other"
        """
        ref_len = len(self.ref)
        alt_len = len(self.alt)
        
        if ref_len == alt_len == 1:
            return "SNV"
        elif ref_len > alt_len:
            return "Deletion"
        elif ref_len < alt_len:
            return "Insertion"
        else:
            return "Other"
    
    @property
    def is_heterozygous(self) -> bool:
        """Retorna True se heterozigoto."""
        return self.genotype == (0, 1)
    
    @property
    def is_homozygous_alt(self) -> bool:
        """Retorna True se homozigoto alternativo."""
        return self.genotype == (1, 1)


class VCFParser:
    """Parser eficiente para arquivos VCF.
    
    Lê arquivos VCF (ou .vcf.gz comprimido) e fornece iterador
    de variantes estruturadas para análise downstream.
    
    Attributes:
        vcf_path (Path): Caminho do arquivo VCF
        sample_name (Optional[str]): Nome da amostra (se múltiplas)
    """
    
    def __init__(self, vcf_path: str, sample_name: Optional[str] = None):
        """Inicializa o parser VCF.
        
        Args:
            vcf_path (str): Caminho do arquivo VCF
            sample_name (Optional[str]): Nome específico da amostra.
                Se None, usa primeira amostra.
        
        Raises:
            FileNotFoundError: Se arquivo não existe
            ValueError: Se arquivo não é VCF válido
        """
        self.vcf_path = Path(vcf_path)
        self.sample_name = sample_name
        
        if not self.vcf_path.exists():
            raise FileNotFoundError(f"Arquivo VCF não encontrado: {vcf_path}")
        
        logger.info(f"Inicializando parser VCF: {vcf_path}")
    
    def parse(self) -> Iterator[VCFVariant]:
        """Itera sobre variantes do arquivo VCF.
        
        Yields:
            VCFVariant: Objeto estruturado com dados da variante
        
        Raises:
            ValueError: Se amostra não encontrada
        """
        try:
            vcf = pysam.VariantFile(str(self.vcf_path))
        except Exception as e:
            logger.error(f"Erro ao abrir VCF: {e}")
            raise ValueError(f"Arquivo VCF inválido: {self.vcf_path}") from e
        
        # Determina nome da amostra
        if self.sample_name:
            if self.sample_name not in vcf.header.samples:
                raise ValueError(
                    f"Amostra '{self.sample_name}' não encontrada. "
                    f"Disponíveis: {list(vcf.header.samples)}"
                )
            sample = self.sample_name
        else:
            if not vcf.header.samples:
                raise ValueError("Nenhuma amostra encontrada no VCF")
            sample = vcf.header.samples[0]
            logger.info(f"Usando primeira amostra: {sample}")
        
        # Itera variantes
        variant_count = 0
        try:
            for record in vcf:
                variant_count += 1
                
                # Extrai genótipo
                gt_data = record.samples[sample].get('GT')
                if gt_data is None:
                    logger.warning(
                        f"Genótipo não encontrado em {record.chrom}:{record.pos}"
                    )
                    genotype = (None, None)
                else:
                    genotype = gt_data
                
                # Extrai cobertura (DP)
                depth = record.info.get('DP')
                
                # Extrai ALT (pega primeiro se múltiplos)
                alt = record.alts[0] if record.alts else "."
                
                # Cria objeto VCFVariant
                variant = VCFVariant(
                    chrom=record.chrom,
                    pos=record.pos,
                    ref=record.ref,
                    alt=alt,
                    genotype=genotype,
                    qual=record.qual if record.qual else 0.0,
                    depth=depth,
                    filter_status=record.filter[0] if record.filter else "."
                )
                
                yield variant
        
        finally:
            vcf.close()
            logger.info(f"Parser VCF finalizado. {variant_count} variantes processadas")
    
    def filter_by_gene(
        self, 
        variants: Iterator[VCFVariant], 
        gene_name: str
    ) -> Iterator[VCFVariant]:
        """Filtra variantes por gene MMR (MLH1, MSH2, MSH6, PMS2, EPCAM).
        
        Args:
            variants (Iterator[VCFVariant]): Iterator de variantes
            gene_name (str): Nome do gene (ex: "MLH1", "PMS2")
        
        Yields:
            VCFVariant: Variantes que correspondem ao gene
        
        Note:
            Implementação simplificada. Versão real usaria
            anotação VEP ou coordenadas precisas de cada gene.
        """
        # Mapeamento cromossomo -> gene (simplificado)
        gene_chroms = {
            "MLH1": ["chr3"],
            "MSH2": ["chr2"],
            "MSH6": ["chr2"],
            "PMS2": ["chr7"],
            "EPCAM": ["chr2"]
        }
        
        if gene_name.upper() not in gene_chroms:
            logger.warning(f"Gene desconhecido: {gene_name}")
            return
        
        target_chroms = gene_chroms[gene_name.upper()]
        
        for variant in variants:
            if variant.chrom in target_chroms:
                yield variant
    
    def validate_quality(
        self,
        variants: Iterator[VCFVariant],
        min_depth: int = 20,
        min_qual: float = 20.0
    ) -> Iterator[VCFVariant]:
        """Filtra variantes por critérios de qualidade.
        
        Args:
            variants (Iterator[VCFVariant]): Iterator de variantes
            min_depth (int): Cobertura mínima (padrão: 20x)
            min_qual (float): Score QUAL mínimo (padrão: 20)
        
        Yields:
            VCFVariant: Variantes que passam no QC
        """
        for variant in variants:
            if variant.depth is None or variant.depth < min_depth:
                logger.debug(
                    f"Variante filtrada (cobertura baixa): {variant} "
                    f"(DP={variant.depth})"
                )
                continue
            
            if variant.qual < min_qual:
                logger.debug(
                    f"Variante filtrada (qualidade baixa): {variant} "
                    f"(QUAL={variant.qual})"
                )
                continue
            
            yield variant


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = VCFParser("examples/sample_lynch.vcf")
    
    print("🧬 Todas as variantes:")
    print("-" * 70)
    
    all_variants = list(parser.parse())
    for var in all_variants:
        print(f"{var} - Tipo: {var.variant_type}")
    
    print("\n✅ Filtrando por qualidade (DP>=20):")
    print("-" * 70)
    
    parser = VCFParser("examples/sample_lynch.vcf")
    variants = parser.parse()
    variants = parser.validate_quality(variants, min_depth=20)
    
    for var in variants:
        print(f"{var}")
