# 🧬 VariantFlow-MMR: CLI Profissional para Análise Lynch/MMR

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Typer](https://img.shields.io/badge/Typer-0.9.0-green.svg)](https://typer.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-39%2F39%20PASSED-brightgreen.svg)](https://github.com/carla-bioinfo/variant-flow-mmr)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 O que é VariantFlow-MMR?

Uma ferramenta profissional de **QC (Quality Control) e análise ACMG** para genes MMR (Mismatch Repair) com foco em **Síndrome de Lynch**.

**Versão Atual**: 0.2.0 (ETAPA 4 - CLI Completa)

---

## ✨ Principais Características

### 🖥️ CLI Profissional com Typer
```bash
vflow version              # Mostra versão
vflow qc --gene MLH1       # Quality Control
vflow analyze file.vcf     # Análise ACMG
vflow --help               # Ajuda completa
```

### 🧪 Módulos de Análise
- ✅ **ACMGEvidenceCollector**: Coleta evidências ACMG/AMP 2015
- ✅ **PMS2Assessor**: Avaliação especializada de pseudogenes PMS2
- ✅ **CoverageAnalyzer**: Análise de cobertura exon-by-exon
- ✅ **AuditTrail**: Rastreabilidade completa com SHA256

### 🔬 Foco Clínico
- Detecção de pseudogenes PMS2
- Critérios ACMG/AMP 2015 completos
- Recomendações de validação ortogonal
- Auditoria profissional com git integration

---

## 📊 Status Atual (ETAPA 4)
✅ CLI Typer profissional     (80 linhas)

✅ 3 comandos funcionando     (version, qc, analyze)

✅ 39/39 testes passando      (100% success rate)

✅ Integração ETAPA 3         (4 módulos importados)

✅ Entry point executável     (vflow command)

✅ Documentação completa      (docstrings + README)
---

## 🚀 Quick Start

### Instalação

```bash
# Clonar repositório
git clone https://github.com/carla-bioinfo/variant-flow-mmr.git
cd variant-flow-mmr

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar
pip install -e .
```

### Uso Básico

```bash
# Ver versão
vflow version

# Quality Control para MLH1
vflow qc --gene MLH1

# Análise ACMG de um VCF
vflow analyze examples/sample.vcf --gene PMS2 --output results.json

# Listar todos os comandos
vflow --help
```

---

## 📁 Estrutura do Projeto
variant-flow-mmr/

│

├── src/vflow/

│   ├── cli/                    ← CLI (ETAPA 4)

│   │   ├── main.py             (80 linhas - Typer app)

│   │   └── init.py

│   │

│   ├── core/                   ← Módulos de Análise (ETAPA 3)

│   │   ├── acmg_evidence.py    (380 linhas)

│   │   ├── pms2_assessment.py  (260 linhas)

│   │   ├── audit_trail.py      (320 linhas)

│   │   ├── coverage_analysis.py

│   │   ├── data_models.py

│   │   └── models.py

│   │

│   ├── reports/

│   ├── validators/

│   └── version.py

│

├── tests/

│   ├── test_cli.py             (4 testes - CLI)

│   ├── unit/                   (35 testes - ETAPA 3)

│   │   ├── test_acmg.py

│   │   ├── test_pms2.py

│   │   ├── test_audit.py

│   │   └── test_models.py

│   └── conftest.py

│

├── examples/                   ← Dados de exemplo

├── resources/                  ← Dados de referência

├── docs/                       ← Documentação

│

├── pyproject.toml             (configuração moderna)

├── setup.py

├── requirements.txt

├── Dockerfile

└── README.md (este arquivo)
---

## 🧪 Testes

### Rodar Todos os Testes

```bash
# Resumo rápido
pytest tests/ -q

# Verboso
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src/vflow
```

### Status Atual
39 testes passando (100%)

├── ETAPA 3: 35 testes (análise)

└── ETAPA 4: 4 testes (CLI)
---

## 📚 Documentação

### Módulos Principais

| Módulo | Descrição | Status |
|--------|-----------|--------|
| **acmg_evidence.py** | Coleta evidências ACMG/AMP 2015 | ✅ Pronto |
| **pms2_assessment.py** | Avaliação PMS2 com pseudogenes | ✅ Pronto |
| **audit_trail.py** | Rastreabilidade com SHA256 | ✅ Pronto |
| **coverage_analysis.py** | Análise de cobertura | ✅ Pronto |
| **cli/main.py** | CLI com Typer | ✅ Pronto |

### Documentação Detalhada

- [CONTEXTO_COMPLETO_PARA_PROXIMA_SESSAO.md](docs/) - Guia completo para desenvolvedores
- [ETAPA_4_CONCLUSAO_FINAL.md](docs/) - Resumo técnico ETAPA 4
- [CHEAT_SHEET_ETAPA4.md](docs/) - Referência rápida

---

## 🔧 Tecnologias
Linguagem:        Python 3.9.2

CLI Framework:    Typer 0.9.0

Output Format:    Rich 13.9.4

Testing:          pytest 7.4.0

Bioinformatics:   pysam, biopython, pandas

Audit:            SHA256 hashing, git integration
---

## 🎯 Roadmap

### ✅ Concluído
- [x] ETAPA 1: Setup e estrutura
- [x] ETAPA 2: Package profissional
- [x] ETAPA 3: Módulos de análise (35 testes)
- [x] ETAPA 4: CLI com Typer (4 testes)

### 🔄 Em Progresso
- [ ] ETAPA 5: VCF parsing real + relatórios HTML
- [ ] ETAPA 6: Docker + CI/CD
- [ ] ETAPA 7: Publicação científica

---

## 💡 Características Principais

### 🔍 Análise ACMG Completa
- 28 critérios ACMG/AMP 2015
- Integração ClinVar, gnomAD, InSiGHT (simulada)
- NÃO classifica automaticamente (decisão do geneticista)

### 🧬 PMS2 Especializado
- Detecção de pseudogenes
- Avaliação de homologia
- Recomendações de validação ortogonal
- 3 níveis de risco (LOW/MEDIUM/HIGH/CRITICAL)

### 📊 Quality Control
- Cobertura exon-by-exon
- Breadth analysis (% bases ≥20x, 50x, 100x)
- Uniformidade (Fold-80 base penalty)
- Flags de QC com severidade

### 🔐 Auditoria Profissional
- Rastreabilidade completa
- Timestamps ISO 8601 UTC
- SHA256 hashing de entrada/saída
- Integração com git (commits, branches)

---

## 👤 Autor

**Carla Rodrigues** (@carla-bioinfo)

Bioinformatics Researcher in Training  
Focused on Lynch Syndrome & Variant Interpretation

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

---

## 🙋 Contribuindo

Pull requests são bem-vindos!

Para mudanças maiores:
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit suas mudanças (`git commit -m 'Adiciona melhoria'`)
4. Push para a branch (`git push origin feature/melhoria`)
5. Abra um Pull Request

---

## 📞 Suporte

Dúvidas ou sugestões? Abra uma [Issue](https://github.com/carla-bioinfo/variant-flow-mmr/issues)

---

## 🙏 Agradecimentos

Inspirado em:
- ACMG/AMP 2015 Standards
- InSiGHT MMR Database
- ClinVar
- gnomAD Project

---

## 📜 Histórico

- **v0.2.0** (18 Jun 2026): CLI Typer profissional com 3 comandos + 39/39 testes
- **v0.1.0** (17 Jun 2026): Estrutura inicial com módulos de análise

---

**Última atualização**: 18 de Junho de 2026  
**Próxima etapa**: ETAPA 5 - VCF Parsing Real + HTML Reports
