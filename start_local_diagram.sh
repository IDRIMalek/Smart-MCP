#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Smart MCP — Mode MONO-MODÈLE (Gemma 4B uniquement)
# Pour le profil Hermes "local-diagram"
# ═══════════════════════════════════════════════════════════════════
set -e

SMART_MCP_DIR="$HOME/workspace/Smart-MCP"
DRAWIO_MCP_DIR="$HOME/workspace/mcp-server-patched"

echo "╔══════════════════════════════════════════════════╗"
echo "║  🧠 Smart MCP — Mode Gemma 4B Mono-Modèle      ║"
echo "╚══════════════════════════════════════════════════╝"

# ── 1. Vérifier que le modèle Gemma existe ──
echo ""
echo "📋 Vérification du modèle..."
MODEL="gemma4:e4b-hermes"
if ollama list 2>/dev/null | grep -q "$MODEL"; then
  echo "  ✅ Modèle $MODEL trouvé"
else
  echo "  ❌ Modèle $MODEL introuvable !"
  echo "  → Crée-le avec : ollama create $MODEL -f Modelfile"
  echo "  (Modelfile doit contenir num_ctx 65536 et num_predict 16384)"
  exit 1
fi

# ── 2. Arrêter les processus existants ──
echo ""
echo "🛑 Arrêt des serveurs existants..."
pkill -f "smart_mcp_server.py" 2>/dev/null && echo "  ✅ Smart MCP arrêté" || echo "  ℹ️  Smart MCP pas en cours"
pkill -f "mcp-server-patched" 2>/dev/null && echo "  ✅ Draw.io MCP arrêté" || echo "  ℹ️  Draw.io MCP pas en cours"

# ── 3. Lancer draw.io MCP ──
echo ""
echo "🔌 Démarrage serveur draw.io MCP..."
cd "$DRAWIO_MCP_DIR"
node dist/index.js &
DRAWIO_PID=$!
sleep 2
echo "  ✅ Draw.io MCP lancé (PID: $DRAWIO_PID)"
echo "  📍 http://192.168.1.100:8080"

# ── 4. Lancer Smart MCP (mode mono-modèle) ──
echo ""
echo "🧠 Démarrage Smart MCP (Gemma 4B Mono-Modèle)..."
cd "$SMART_MCP_DIR"
SMART_MCP_SINGLE_MODEL=true \
SMART_MCP_MODEL="$MODEL" \
SMART_MCP_MAX_TOKENS=16384 \
SMART_MCP_TIMEOUT=120 \
  python3 smart_mcp_server.py &
SMART_PID=$!
echo "  ✅ Smart MCP lancé (PID: $SMART_PID)"

# ── 5. Récupérer l'état du singleton LLM ──
echo ""
echo "📊 État LLM (Gemma 4B mono-modèle) :"
SMART_MCP_SINGLE_MODEL=true python3 -c "
import sys; sys.path.insert(0, '$SMART_MCP_DIR')
from models.llm_client import get_llm
llm = get_llm()
print(f'  Planner: {llm.planner.model}')
print(f'  Generator: {llm.generator.model}')
print(f'  Cloud: {llm.cloud}')
print(f'  Mode: {\"MONO-MODÈLE\" if llm.planner is llm.generator else \"SPLIT\"}')
"

# ── 6. Profil Hermes ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Profil Hermes prêt :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Lance Hermes avec :"
echo "    hermes --profile local-diagram"
echo ""
echo "  Le profil utilise Gemma 4B (gemma4:e4b-hermes)"
echo "  avec draw.io MCP + Smart MCP MCP intégrés."
echo ""
echo "  Commandes disponibles dans la conversation :"
echo "    - create a mindmap : \"mindmap about <sujet>\""
echo "    - add a node       : \"add <label> under <parent>\""
echo "    - change color     : \"change <label> to <color>\""
echo "    - delete node     : \"delete <label>\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Prêt ! Bonne session Malek 🚀"