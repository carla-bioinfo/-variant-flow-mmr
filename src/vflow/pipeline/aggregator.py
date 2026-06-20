"""
ResultsAggregator: Consolida resultados de múltiplas análises
Entrada: AnalysisReport + QCFlags + Métricas de 6 análises
Saída: Dataset unificado pronto para HTMLReportGenerator
"""
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ResultsAggregator:
    """Consolida resultados de todas as análises em um dataset único"""
    
    def __init__(self):
        """Inicializa agregador"""
        self.logger = logger
        self.consolidated_data = {}
    
    def add_analysis_report(self, analysis_report):
        """Adiciona AnalysisReport (ACMG + variantes)"""
        self.consolidated_data['analysis_report'] = analysis_report
        logger.info("AnalysisReport adicionado ao agregador")
    
    def add_qc_flags(self, qc_flags: List):
        """Adiciona QCFlags da análise"""
        self.consolidated_data['qc_flags'] = qc_flags
        logger.info(f"Adicionados {len(qc_flags)} QC flags")
    
    def add_coverage_metrics(self, coverage_data):
        """Adiciona métricas de cobertura"""
        self.consolidated_data['coverage_metrics'] = coverage_data
        logger.info("Coverage metrics adicionado")
    
    def add_breadth_metrics(self, breadth_data):
        """Adiciona métricas de breadth"""
        self.consolidated_data['breadth_metrics'] = breadth_data
        logger.info("Breadth metrics adicionado")
    
    def add_uniformity_metrics(self, uniformity_data):
        """Adiciona métricas de uniformidade"""
        self.consolidated_data['uniformity_metrics'] = uniformity_data
        logger.info("Uniformity metrics adicionado")
    
    def add_pms2_results(self, pms2_data):
        """Adiciona resultados de PMS2Assessor"""
        self.consolidated_data['pms2_results'] = pms2_data
        logger.info("PMS2 results adicionado")
    
    def add_homology_results(self, homology_data):
        """Adiciona resultados de HomologyAnalyzer"""
        self.consolidated_data['homology_results'] = homology_data
        logger.info("Homology results adicionado")
    
    def add_severity_results(self, severity_data):
        """Adiciona resultados de SeverityClassifier"""
        self.consolidated_data['severity_results'] = severity_data
        logger.info("Severity results adicionado")
    
    def consolidate(self) -> Dict[str, Any]:
        """
        Consolida TODOS os dados em um dataset único
        
        Returns:
            dict com estrutura unificada pronta para HTMLReportGenerator
        """
        unified = {
            **self.consolidated_data,
            'timestamp': datetime.now().isoformat(),
            'aggregator_version': '1.0',
        }
        logger.info("Dados consolidados com sucesso")
        return unified
    
    def get_summary(self) -> str:
        """Retorna resumo textual dos resultados consolidados"""
        summary = f"""
========== AGGREGATOR SUMMARY ==========
Analysis Report: {'✅' if 'analysis_report' in self.consolidated_data else '❌'}
QC Flags: {'✅' if 'qc_flags' in self.consolidated_data else '❌'}
PMS2 Results: {'✅' if 'pms2_results' in self.consolidated_data else '❌'}
Coverage Metrics: {'✅' if 'coverage_metrics' in self.consolidated_data else '❌'}
Breadth Metrics: {'✅' if 'breadth_metrics' in self.consolidated_data else '❌'}
Uniformity Metrics: {'✅' if 'uniformity_metrics' in self.consolidated_data else '❌'}
Homology Results: {'✅' if 'homology_results' in self.consolidated_data else '❌'}
Severity Results: {'✅' if 'severity_results' in self.consolidated_data else '❌'}
========================================
"""
        return summary
    
    def to_dict(self) -> Dict:
        """Retorna dados consolidados como dicionário"""
        return self.consolidate()
