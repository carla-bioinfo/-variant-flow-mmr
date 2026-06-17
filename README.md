# 🧬 VariantFlow-MMR

Clinical-grade quality control tool for Lynch Syndrome MMR gene analysis.

## Overview

VariantFlow-MMR is a professional bioinformatics tool designed to:

- ✅ Analyze sequencing coverage for MMR genes (MLH1, MSH2, MSH6, PMS2, EPCAM)
- ✅ Detect quality issues and pseudogene contamination (especially PMS2)
- ✅ Collect ACMG evidence for variant classification
- ✅ Generate professional clinical reports
- ✅ Maintain complete audit trails

## Features

- **Coverage Analysis**: Exon-by-exon depth evaluation
- **PMS2 Assessment**: Pseudogene risk detection
- **ACMG Evidence**: Transparent evidence collection (not auto-classification)
- **Quality Gates**: Clinical-grade QC metrics
- **Audit Trail**: Full reproducibility tracking

## Installation

\`\`\`bash
# Clone repository
git clone https://github.com/carla-bioinfo/variant-flow-mmr.git
cd variant-flow-mmr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install dev tools
pip install -e ".[dev]"
\`\`\`

## Quick Start

\`\`\`bash
vflow qc --bam sample.bam --vcf sample.vcf --config config.yaml
\`\`\`

## Documentation

See \`/docs/\` for detailed documentation.

## Status

**Version:** 0.1.0 (Alpha)

**Project Stage:** Initial development

## Author

Carla Rodrigues  
GitHub: [@carla-bioinfo](https://github.com/carla-bioinfo)  
Email: Carlabio.biomol@gmail.com

## License

MIT License
