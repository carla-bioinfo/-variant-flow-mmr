# -*- coding: utf-8 -*-
"""Gerador de gráficos para análise de variantes MMR."""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

class VariantVisualizer:
    """Cria visualizações de dados de variantes."""
    
    MMR_GENES_COLORS = {
        'MLH1': '#e74c3c',
        'MSH2': '#3498db',
        'MSH6': '#2ecc71',
        'PMS2': '#f39c12',
        'EPCAM': '#9b59b6',
    }
    
    def __init__(self, output_dir="output/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_variant_type_distribution(self, data):
        """Gráfico de tipos de variantes."""
        type_counts = data['variant_type'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(type_counts.index, type_counts.values, color='#3498db')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Tipo de Variante', fontweight='bold')
        ax.set_ylabel('Numero', fontweight='bold')
        ax.set_title('Tipos de Variantes', fontweight='bold')
        
        output_file = self.output_dir / "01_variant_type_distribution.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def plot_mmr_genes_distribution(self, data):
        """Gráfico de genes MMR."""
        gene_counts = data['gene'].value_counts()
        colors = [self.MMR_GENES_COLORS.get(g, '#95a5a6') for g in gene_counts.index]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(gene_counts.index, gene_counts.values, color=colors)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {int(width)}',
                   ha='left', va='center', fontweight='bold')
        
        ax.set_xlabel('Numero de Variantes', fontweight='bold')
        ax.set_ylabel('Gene MMR', fontweight='bold')
        ax.set_title('Genes MMR', fontweight='bold')
        
        output_file = self.output_dir / "02_mmr_genes_distribution.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_all_visualizations(self, data):
        """Gera todos os gráficos."""
        results = {
            'variant_types': self.plot_variant_type_distribution(data),
            'mmr_genes': self.plot_mmr_genes_distribution(data),
        }
        logger.info(f"✅ Gerados {len(results)} gráficos")
        return results

if __name__ == "__main__":
    print("✅ VariantVisualizer pronto")
