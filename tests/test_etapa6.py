# -*- coding: utf-8 -*-
"""Testes para ETAPA 6: Reports e Visualizações."""

import sys
sys.path.insert(0, '/home/bioinfo/variant-flow-mmr')

import pandas as pd
from reports.visualizations import VariantVisualizer
from reports.html_reporter import HTMLReporter

def test_visualizer_generates_png():
    """Testa se visualizador cria PNG."""
    data = pd.DataFrame({
        'variant_type': ['SNV', 'Indel', 'SNV'],
        'gene': ['MLH1', 'MSH2', 'MLH1'],
    })
    
    viz = VariantVisualizer()
    output = viz.plot_variant_type_distribution(data)
    
    assert output.exists(), "PNG nao foi criado"
    assert output.suffix == '.png', "Nao e um PNG"
    assert output.stat().st_size > 10000, "Arquivo muito pequeno"
    
    print("✅ test_visualizer_generates_png passou")

def test_html_reporter_creates_file():
    """Testa se reporter cria arquivo HTML."""
    data = pd.DataFrame({
        'variant_type': ['SNV', 'Indel'],
        'gene': ['MLH1', 'MSH2'],
    })
    
    reporter = HTMLReporter()
    html = reporter.render_html("Teste", data, {})
    
    assert '<!DOCTYPE html>' in html, "HTML invalido"
    assert 'Teste' in html, "Titulo nao aparece"
    assert 'Total de variantes' in html, "Estatisticas faltam"
    
    print("✅ test_html_reporter_creates_file passou")

def test_base64_encoding():
    """Testa se imagem e convertida para base64."""
    data = pd.DataFrame({
        'variant_type': ['SNV', 'SNV'],
        'gene': ['MLH1', 'MSH2'],
    })
    
    viz = VariantVisualizer()
    png_path = viz.plot_variant_type_distribution(data)
    
    reporter = HTMLReporter()
    b64 = reporter.image_to_base64(png_path)
    
    assert len(b64) > 50000, "Base64 muito curto"
    assert 'iVBORw0KGgo' in b64, "Nao e PNG valido"
    
    print("✅ test_base64_encoding passou")

if __name__ == "__main__":
    test_visualizer_generates_png()
    test_html_reporter_creates_file()
    test_base64_encoding()
    print("\n✅ Todos os testes da ETAPA 6 passaram!")
