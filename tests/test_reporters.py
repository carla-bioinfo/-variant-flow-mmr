# -*- coding: utf-8 -*-
"""Testes para módulos de reports."""

import sys
sys.path.insert(0, '/home/bioinfo/variant-flow-mmr')

from reports.visualizations import VariantVisualizer
from reports.html_reporter import HTMLReporter

def test_visualizer_init():
    """Testa inicialização do visualizador."""
    viz = VariantVisualizer()
    assert viz.output_dir.exists()
    print("✅ test_visualizer_init passou")

def test_html_reporter_init():
    """Testa inicialização do reporter."""
    reporter = HTMLReporter()
    assert reporter.output_dir.exists()
    print("✅ test_html_reporter_init passou")

if __name__ == "__main__":
    test_visualizer_init()
    test_html_reporter_init()
    print("\n✅ Todos os testes passaram!")
