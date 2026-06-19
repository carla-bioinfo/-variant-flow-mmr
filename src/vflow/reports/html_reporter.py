# -*- coding: utf-8 -*-
"""Gerador de relatórios HTML profissionais."""

import logging
from pathlib import Path
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class HTMLReporter:
    """Cria relatórios HTML com gráficos e tabelas."""
    
    def __init__(self, output_dir="output/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def image_to_base64(self, image_path):
        """Converte imagem PNG em base64 para embutir no HTML."""
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode()
    
    def render_html(self, title, variant_data, chart_paths):
        """Renderiza HTML com dados e gráficos.
        
        Args:
            title: Título do relatório
            variant_data: DataFrame com variantes
            chart_paths: Dict com caminhos dos gráficos
        """
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Contar variantes por tipo
        type_counts = variant_data['variant_type'].value_counts().to_dict()
        gene_counts = variant_data['gene'].value_counts().to_dict()
        
        # Converter imagens para base64
        charts_html = ""
        for chart_name, chart_path in chart_paths.items():
            if chart_path.exists():
                b64 = self.image_to_base64(chart_path)
                charts_html += f'<img src="data:image/png;base64,{b64}" style="max-width:100%; margin:20px 0;">\n'
        
        # HTML completo
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Gerado em: {now}</p>
    </div>
    
    <div class="section">
        <h2>Resumo Estatistico</h2>
        <p><strong>Total de variantes:</strong> {len(variant_data)}</p>
        <p><strong>Tipos encontrados:</strong> {', '.join(type_counts.keys())}</p>
        <p><strong>Genes MMR:</strong> {', '.join(gene_counts.keys())}</p>
    </div>
    
    <div class="section">
        <h2>Gráficos</h2>
        {charts_html}
    </div>
    
    <div class="section">
        <h2>Tabela de Variantes</h2>
        <table>
            <tr>
                <th>Gene</th>
                <th>Tipo</th>
            </tr>
"""
        
        # Adicionar linhas da tabela
        for _, row in variant_data.iterrows():
            html += f"<tr><td>{row['gene']}</td><td>{row['variant_type']}</td></tr>\n"
        
        html += """
        </table>
    </div>
</body>
</html>"""
        
        return html
    
    def save_report(self, html, filename="report.html"):
        """Salva relatório HTML em arquivo."""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Relatorio salvo: {output_path}")
        return output_path

if __name__ == "__main__":
    print("✅ HTMLReporter pronto")
