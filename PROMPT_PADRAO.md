# 🚀 PROMPT PADRÃO UNIVERSAL

## Cole isto na próxima conversa:

```bash
cd /home/bioinfo/variant-flow-mmr && \
source venv/bin/activate && \
echo "════════════════════════════════════════════════" && \
echo "🧬 VariantFlow-MMR: Sessão Iniciada" && \
echo "════════════════════════════════════════════════" && \
echo "" && \
echo "📂 $(pwd)" && \
echo "🐍 $VIRTUAL_ENV" && \
echo "📌 $(git branch | grep '*')" && \
echo "" && \
git log --oneline | head -3 && \
echo "" && \
pytest tests/unit/ -q --tb=no 2>/dev/null || echo "Testes não encontrados" && \
echo "" && \
ls -1 ETAPA_*_SETUP.md 2>/dev/null && \
echo "" && \
echo "════════════════════════════════════════════════" && \
echo "✅ COMANDO 1 = Execute" && \
echo "❌ COMANDO 2 = Leia apenas" && \
echo "════════════════════════════════════════════════"
```

## Depois diga:
"Venv ativado, pronto para ETAPA 8"
