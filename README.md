# 🧬 VariantFlow-MMR: Análise Profissional Lynch/MMR

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-0.3.0-green.svg)](https://github.com/carla-bioinfo/variant-flow-mmr/releases)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-ETAPA%206%2F11-orange.svg)](ROADMAP.md)

---

## 🎯 O que é VariantFlow-MMR?

Uma **ferramenta profissional de QC e análise ACMG** para genes MMR (Mismatch Repair) com foco em **Síndrome de Lynch**.

**Versão**: 0.3.0 (ETAPA 6 - Reports + Visualizações)
**Status**: Em desenvolvimento ativo (55% completo)
**Meta**: Versão 1.0 profissional (10/10)

---

## ✨ O que você pode fazer AGORA

\`\`\`bash
vflow version                                  # Ver versão
vflow analyze sample.vcf --gene MLH1           # Análise ACMG
vflow qc --gene PMS2                           # Quality Control
vflow report sample.vcf --output relatorio.html # 🆕 ETAPA 6: Gerar HTML!
\`\`\`

---

## 📊 Status Atual (ETAPA 6)

✅ COMPLETO
  ├─ CLI Typer profissional (3 comandos)
  ├─ VCF Parser robusto (pysam)
  ├─ ACMG Evidence (28 critérios ACMG/AMP 2015)
  ├─ PMS2 Assessment básico
  ├─ Audit Trail (SHA256 + git)
  ├─ Coverage Analysis (mean/min)
  ├─ 42+ Testes unitários (100% passa)
  └─ Logging profissional + HTML Reports 🆕

---

## 🎯 Roadmap

CONCLUÍDO:
✅ ETAPA 1: Setup
✅ ETAPA 2: Package profissional
✅ ETAPA 3: Módulos análise (ACMG, PMS2, Coverage, Audit)
✅ ETAPA 4: CLI Typer
✅ ETAPA 5: VCF Parser (pysam, variant parsing)
✅ ETAPA 6: Reports + Visualizações (🆕 HTML + gráficos - VOCÊ ESTÁ AQUI!)

PRÓXIMAS:
⏳ ETAPA 7: PMS2 + Métricas QC (breadth, uniformity, homology - 8-10h)
⏳ ETAPA 8: Severity + Audit expand (LOW/MEDIUM/HIGH/CRITICAL - 8-10h)
⏳ ETAPA 9: Docs científicas (LIMITATIONS, CLINICAL_NOTES - 8-10h)
⏳ ETAPA 10: Docker + CI/CD (GitHub Actions, Dockerfile - 6-8h)
⏳ ETAPA 11: Polimento + Publicação (Preprint, final QA - 4-6h)

📊 PROGRESS: 55% completo (ETAPA 6 / 11)

---

## 🚀 Quick Start

\`\`\`bash
git clone https://github.com/carla-bioinfo/variant-flow-mmr.git
cd variant-flow-mmr
python3 -m venv venv
source venv/bin/activate
pip install -e .
\`\`\`

---

## 📚 Módulos Principais

| Módulo | Status |
|--------|--------|
| acmg_evidence.py | ✅ 28 critérios ACMG/AMP 2015 |
| pms2_assessment.py | ⚠️ Será expandido ETAPA 7 |
| coverage.py | ⚠️ Faltam métricas clínicas |
| vcf_parser.py | ✅ Parser VCF com pysam |
| cli/main.py | ✅ CLI Typer completa |
| html_reporter.py | ✅ 🆕 ETAPA 6 |
| visualizations.py | ✅ 🆕 ETAPA 6 |

---

## 🧪 Testes

\`\`\`bash
pytest tests/ -v
pytest tests/ --cov=src/vflow
\`\`\`

Status: 42+ testes passando ✅

---

## 🔧 Tecnologias

Python 3.9+
CLI: Typer 0.23.2
Testing: pytest 7.4.3
Bioinformatics: pysam, biopython, pandas
Visualização: matplotlib 3.8.2, seaborn 0.13.0
Reports: Jinja2 3.1.2

---

## 📜 Histórico

v0.3.0 (19 Jun 2026): ETAPA 6 - HTML Reports + Visualizações
v0.2.0 (18 Jun 2026): ETAPA 4-5 - CLI + VCF Parser
v0.1.0 (17 Jun 2026): ETAPA 3 - Módulos de análise

---

## 👤 Autor

**Carla Rodrigues** (@carla-bioinfo)
Bioinformatics Researcher
Focused on Lynch Syndrome & Variant Interpretation

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE)

---

**Última atualização**: 19 de Junho de 2026
**Próxima etapa**: ETAPA 7 - PMS2 Assessment Profundo + Métricas QC Clínicas
