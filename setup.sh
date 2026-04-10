#!/bin/bash
echo "🌊 Configurando Beach API Brasil..."

python -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate

pip install -r requirements.txt

echo ""
echo "✅ Tudo pronto! Rode o servidor com:"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "🌍 Acesse:"
echo "   Dashboard  → http://localhost:8000"
echo "   API Docs   → http://localhost:8000/docs"
