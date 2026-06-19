# 🧬 VariantFlow-MMR: Análise Genômica de Síndrome de Lynch

**Status**: ETAPA 7 Completa ✅ | Score: 7.0/10  
**Próxima**: ETAPA 8 (Integração + Relatórios HTML)  
**Data**: 18 de Junho de 2026

---

## 📋 Visão Geral

Sistema de **análise de variantes MMR (Mismatch Repair)** com foco especial em **PMS2**, o gene mais desafiador devido à pseudogene contamination.

**Objetivo**: Detectar variantes patogênicas em genes MLH1, MSH2, MSH6, PMS2 e EPCAM com confiabilidade clínica.

---

## 🎯 Status do Projeto

### ✅ ETAPA 7: PMS2 Assessment Profundo + Métricas QC Clínicas

**Implementado**:
- ✅ **HomologyAnalyzer** (109 linhas)
  - Detecta regiões com alta homologia ao pseudogene PMS2CL
  - 3 regiões críticas mapeadas (exon 11, 15, 5-6)
  - Recomenda validação ortogonal

- ✅ **PseudogeneRiskDetector** (155 linhas)
  - Calcula score de risco pseudogênico (0-100)
  - 4 fatores ponderados: homologia (40%), cobertura (30%), mapeability (20%), tipo variante (10%)
  - Classifica em 4 níveis: LOW, MEDIUM, HIGH, CRITICAL

- ✅ **BreadthAnalyzer** (169 linhas)
  - % de bases com cobertura ≥ 20x, 50x, 100x
  - Status: PASS/WARNING/FAIL
  - Detecta "blind spots" em cobertura

- ✅ **UniformityAnalyzer** (136 linhas)
  - Fold-80 metric (80º percentil / mediana)
  - Detecta amplification bias
  - Status: EXCELLENT/GOOD/ACCEPTABLE/POOR

- ✅ **SeverityClassifier** (262 linhas)
  - Converte métricas técnicas em ações clínicas
  - Símbolos: ℹ️ LOW / ⚠️ MEDIUM / 🚨 HIGH / 🚫 CRITICAL
  - Agregação de múltiplos sinais

**Testes**: 39/39 passando ✅

---

## 📊 Estatísticas

### ETAPA 7 Adicionadas
Total linhas: 1,490

├── pms2_assessment.py:    234 → 498 linhas (+264)

├── coverage.py:           138 → 307 linhas (+169)

├── quality_gates.py:        0 → 262 linhas (NOVO)

└── test_etapa7.py:          0 → 423 linhas (NOVO)
Classes novas: 5

Testes: 39 (todos passando)

Commits: 6
### Projeto Total
Linhas de código: ~1,490 (ETAPA 7)

Score esperado: 7.0/10

Próximo milestone: 8.0/10 (ETAPA 8)
---

## 🏗️ Arquitetura

### Fluxo de Análise Completo
Input (Gene, Position, Coverage)

↓

HomologyAnalyzer

├─ "Está em zona pseudogene?"

├─ homology_pct: 0-100

└─ risk_level: LOW/MEDIUM/HIGH/CRITICAL

↓

PseudogeneRiskDetector

├─ Score de risco: 0-100

├─ 4 fatores ponderados

└─ Confidence: 0-100%

↓

BreadthAnalyzer + UniformityAnalyzer

├─ Breadth (% bases ≥ threshold)

├─ Fold-80 (uniformidade)

└─ Status: PASS/WARNING/FAIL

↓

SeverityClassifier

├─ Agrega múltiplos sinais

├─ Classifica por severidade

└─ Recomendação: Monitor/Review/Validate/Resequence

↓

Output (Actionable Insight)
---

## 🚀 Próxima Etapa: ETAPA 8

### O que será implementado:
1. **PipelineIntegrator** (~200 linhas)
   - Conecta HomologyAnalyzer → PseudogeneRiskDetector → SeverityClassifier
   
2. **HTMLReportGenerator** (~300 linhas)
   - Gera relatórios clínicos em HTML com Jinja2
   - Gráficos de cobertura
   - Visualização de severidade com cores
   
3. **ResultsAggregator** (~150 linhas)
   - Consolida múltiplos resultados
   - Prepara dados para relatório
   
4. **CLI Interface** (~100 linhas)
   - Linha de comando com Typer
   - `variant-flow analyze --gene PMS2 --position 33560500`
   
5. **Testes** (~250 linhas)
   - Testes para cada novo componente
   - Testes de integração

**Meta**: 1,000 linhas + 40+ testes | Score: 8.0/10

---

## 🔧 Setup & Instalação

### Pré-requisitos
- Python 3.9+
- pip/virtualenv

### Instalar
```bash
# Clone o repositório
git clone https://github.com/carla-bioinfo/variant-flow-mmr.git
cd variant-flow-mmr

# Criar e ativar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Rodar Testes
```bash
# ETAPA 7 tests
pytest tests/unit/test_etapa7.py -v

# Todos os testes
pytest tests/ -v --cov=src/vflow
```

---

## 📁 Estrutura do Projeto
variant-flow-mmr/

├── src/vflow/

│   ├── core/

│   │   ├── pms2_assessment.py    (498 linhas - ETAPA 7)

│   │   ├── coverage.py            (307 linhas - ETAPA 7)

│   │   ├── models.py

│   │   └── init.py

│   ├── validators/

│   │   └── quality_gates.py       (262 linhas - ETAPA 7)

│   ├── reporters/                 (NOVO - ETAPA 8)

│   │   └── html_generator.py

│   ├── cli.py                     (NOVO - ETAPA 8)

│   └── init.py

├── tests/

│   ├── unit/

│   │   └── test_etapa7.py         (423 linhas - 39 testes)

│   └── integration/

├── docs/

│   └── ETAPA_8_SETUP.md           (Preparação próxima etapa)

├── requirements.txt

├── setup.py

└── README.md
---

## 📚 Documentação

- **ETAPA_8_SETUP.md**: Preparação para próxima etapa
- **src/vflow/core/pms2_assessment.py**: Docstrings detalhadas
- **src/vflow/validators/quality_gates.py**: Interpretações clínicas

---

## 🧪 Testes

### ETAPA 7 - 39 Testes
TestHomologyAnalyzer:           9 testes ✅

TestPseudogeneRiskDetector:     6 testes ✅

TestBreadthAnalyzer:            6 testes ✅

TestUniformityAnalyzer:         6 testes ✅

TestSeverityClassifier:        10 testes ✅

TestETAPA7Integration:          2 testes ✅

─────────────────────────────────────────

Total:                         39 testes ✅
### Executar testes
```bash
# Apenas ETAPA 7
pytest tests/unit/test_etapa7.py -v

# Com cobertura
pytest tests/unit/test_etapa7.py -v --cov=src/vflow --cov-report=html
```

---

## 💡 Conceitos Principais

### PMS2 e Pseudogene
PMS2 é o único gene MMR com pseudogene significativo (PMS2CL, ~95% identidade em exon 11-15). Isto causa:
- Difícil mapeamento de reads
- Baixa cobertura em regiões problemáticas
- Potencial de falsos positivos

**Solução ETAPA 7**: HomologyAnalyzer + PseudogeneRiskDetector detectam isto.

### Métricas de Qualidade
- **Breadth**: % bases com cobertura adequada
- **Fold-80**: Uniformidade de distribuição
- **Mapeability**: Dificuldade de mapear reads naquela região

### Severidade Clínica
Traduz dados técnicos em ações clínicas:
- ℹ️ **LOW**: Monitor
- ⚠️ **MEDIUM**: Review
- 🚨 **HIGH**: Validate (Sanger)
- 🚫 **CRITICAL**: Resequence

---

## 🔗 Referências

- **InSiGHT Database**: https://www.insightdatabase.org/
- **PMS2 Pseudogene**: DOI:10.1186/s12881-016-0356-5
- **ACMG Guidelines**: https://www.acmg.net/

---

## 📝 Commits Recentes
47dbb1f - ETAPA 7 COMPLETA: Documento de resumo para ETAPA 8

274deb5 - ETAPA 7: Criar 39 testes

d3ac7ec - ETAPA 7: Criar SeverityClassifier

acb21eb - ETAPA 7: Adicionar BreadthAnalyzer e UniformityAnalyzer

dd1a86b - ETAPA 7: Adicionar PseudogeneRiskDetector

050050e - ETAPA 7: Adicionar HomologyAnalyzer
---

## 🤝 Contribuições

Este projeto é desenvolvido como parte de aprendizado estruturado em Bioinformática Clínica.

**Autor**: Carla Rodrigues (@carla-bioinfo)  
**Data**: 18 de Junho de 2026

---

## 📞 Próximas Etapas
ETAPA 8: Pipeline Integration + HTML Reports

├─ PipelineIntegrator (~200 linhas)

├─ HTMLReportGenerator (~300 linhas)

├─ ResultsAggregator (~150 linhas)

├─ CLI Interface (~100 linhas)

└─ Testes (~250 linhas)
Tempo: 4-5 horas

Score esperado: 8.0/10
---

**Status**: ✅ ETAPA 7 Completa | 🚀 Pronto para ETAPA 8

