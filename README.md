# VariantFlow-MMR 🧬

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-35%2F35-brightgreen)](tests/unit/)
[![Status](https://img.shields.io/badge/Status-ETAPA%203.2%20✅-success)](https://github.com/carla-bioinfo/variant-flow-mmr)

**Clinical-Grade Quality Control Pipeline for Lynch Syndrome Variant Analysis**

## 📋 Overview

**VariantFlow-MMR** is a professional bioinformatics tool for comprehensive analysis of mismatch repair (MMR) gene variants associated with Lynch Syndrome.

## 🎯 Current Status: ✅ ETAPA 3 - PARTE 2 COMPLETE
✅ ETAPA 3 - PARTE 1: Core Models & Coverage (5 tests)

✅ ETAPA 3 - PARTE 2: PMS2 + ACMG + Audit (30 tests)

⏳ ETAPA 4: CLI & Orchestration (próximo)
TOTAL: 35/35 Tests Passing ✅

PROGRESS: 65% Complete
## 🏗️ Modules Implemented

- **PMS2Assessor** (7 tests)
  - Detects pseudogene interference
  - Risk stratification (LOW/MEDIUM/HIGH/CRITICAL)
  - Orthogonal validation recommendations

- **ACMGEvidenceCollector** (10 tests)
  - ACMG/AMP 2015 criteria collection
  - Pathogenic vs Benign evidence gathering
  - Clinical interpretation support

- **AuditTrail** (13 tests)
  - Comprehensive execution logging
  - SHA256 data integrity verification
  - Git reproducibility integration
  - Clinical compliance (CAP/CLIA/ISO 15189)

## 🚀 Installation

```bash
git clone https://github.com/carla-bioinfo/variant-flow-mmr.git
cd variant-flow-mmr
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/unit/ -v
```

## 📊 Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Models | 5 | ✅ PASSED |
| PMS2Assessor | 7 | ✅ PASSED |
| ACMGEvidenceCollector | 10 | ✅ PASSED |
| AuditTrail | 13 | ✅ PASSED |
| **TOTAL** | **35** | **✅ PASSED** |

## 📚 Key Features

✅ PMS2 Pseudogene Detection  
✅ ACMG/AMP 2015 Evidence Collection  
✅ Comprehensive Audit Trails  
✅ SHA256 Data Integrity  
✅ Git Reproducibility  
✅ Clinical Compliance  

## 🎓 Built With

- Python 3.9+
- Dataclasses & Type Hints
- Pytest (TDD)
- Git (Reproducibility)

## 📝 Maintainer

Carla Rodrigues (@carla-bioinfo)

**Built with ❤️ for genetic medicine**
