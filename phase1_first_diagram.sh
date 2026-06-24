#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# 🚀 Phase 1 — Premier diagramme Smart-MCP
#   Teacher : DeepSeek V4 Flash (cloud) génère
#   Student : ChromaDB se remplit
#   Toi     : Tu valides le rendu visuel
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Activer le venv du projet
VENV="$ROOT_DIR/.venv"
if [[ -f "$VENV/bin/activate" ]]; then
    source "$VENV/bin/activate"
    PYTHON="$VENV/bin/python3"
else
    PYTHON="python3"
fi

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🧠 Smart-MCP Phase 1 — Premier diagramme                    ║"
echo "║  Modèle : DeepSeek V4 Flash (cloud)                          ║"
echo "║  Cible  : draw.io MCP Server                                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Sourcer la clé OpenRouter ──
if [[ -f "$HOME/.hermes/.env" ]]; then
    echo "📡 Source de OPENROUTER_API_KEY depuis ~/.hermes/.env..."
    set +o allexport 2>/dev/null || true
    source <(grep "^OPENROUTER_API_KEY" "$HOME/.hermes/.env")
    export OPENROUTER_API_KEY
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
    echo "❌ OPENROUTER_API_KEY non trouvée ! Définis-la dans ~/.hermes/.env"
    exit 1
fi
echo "   ✅ Clé chargée : ${OPENROUTER_API_KEY:0:12}..."

# ── 2. Vérifier le MCP server ──
MCP_SERVER="/home/malek/workspace/mcp-server-patched/dist/index.js"
if [[ ! -f "$MCP_SERVER" ]]; then
    echo "❌ MCP server introuvable: $MCP_SERVER"
    exit 1
fi
echo "   ✅ MCP server : $(realpath "$MCP_SERVER")"

# ── 3. Exporter les variables Phase 1 — FORCER LE CLOUD ──
export SMART_MCP_SINGLE_MODEL="false"           # Désactive le mode mono-modèle local
export SMART_MCP_PREFER_LOCAL="false"           # Ne pas préférer le local
export SMART_MCP_MODEL="deepseek/deepseek-v4-flash"  # Forcer DeepSeek V4
export SMART_MCP_BUDGET_CENT="500"             # Budget 5€ pour la Phase 1
export DRAWIO_MCP_PATH="$MCP_SERVER"

# Variables LLM — planner en local (intention, classification), générateur en cloud
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
export SMART_MCP_CLOUD_MODEL="deepseek/deepseek-v4-flash"      # Générateur cloud
export SMART_MCP_GENERATOR_MODEL="deepseek/deepseek-v4-flash"  # Générateur cloud
export SMART_MCP_PLANNER_MODEL="gemma4:e4b-hermes"             # Planner local (Ollama)

# Variables locales — on les garde au cas où le cloud échoue
export OLLAMA_GPU_URL="http://localhost:11434/v1"
export OLLAMA_API_KEY="ollama"

echo ""
echo "📋 Configuration Phase 1 :"
echo "   SMART_MCP_SINGLE_MODEL = $SMART_MCP_SINGLE_MODEL"
echo "   SMART_MCP_CLOUD_MODEL  = $SMART_MCP_CLOUD_MODEL"
echo "   SMART_MCP_BUDGET_CENT  = ${SMART_MCP_BUDGET_CENT}¢ (5€)"
echo "   DRAWIO_MCP_PATH        = $DRAWIO_MCP_PATH"
echo ""

# ── 4. Seed ChromaDB (patterns de base) ──
echo "🌱 Seed du cerveau RAG (patterns XML initiaux)..."
$PYTHON -c "
from brain.seed_patterns import seed
seed()
print('   ✅ Seed OK — ChromaDB initialisée')
"

# ── 5. Lancer le diagramme — LA BOUCLE D'APPRENTISSAGE SMART-MCP ──
echo ""
echo "🎨 Génération du diagramme : Smart-MCP — Boucle d'apprentissage"
echo ""

$PYTHON << 'PYEOF'
import json, sys, time
from pathlib import Path

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent))

from brain.rag import get_brain
from models.llm_client import get_llm, LLMClient
from mcp_client.drawio import get_drawio

start = time.time()

# ── Initialisation ──
print("🔧 Initialisation...")
llm = get_llm()
brain = get_brain()
drawio = get_drawio()

# ── Prompt pour la boucle d'apprentissage ──
prompt = """Diagramme de la boucle d'apprentissage Smart-MCP en 4 phases.

Le diagramme doit montrer 4 boîtes alignées horizontalement, reliées par des flèches, représentant :

1. **Phase 1 — TEACHER** (boîte bleue, en haut à gauche)
   - Cloud génère 100% des diagrammes
   - ChromaDB se remplit de patterns XML
   - Élève observe passivement
   Format : boîte avec icône 🎓

2. **Phase 2 — TRANSFERT** (boîte verte, en haut à droite)
   - Cloud délègue au modèle local
   - Local fait des tâches simples (ajouter nœud, colorer)
   - Gagne en confiance
   Format : boîte avec icône 📤

3. **Phase 3 — COACHING** (boîte orange, en bas à gauche)
   - Local tente la génération complète
   - Cloud vérifie le XML avant exécution
   - Feedback humain valide le rendu
   Format : boîte avec icône 🎯

4. **Phase 4 — AUTONOMIE** (boîte violette, en bas à droite)
   - Local génère 90%+ des diagrammes
   - Cloud = secours uniquement
   - Supervision légère humaine
   Format : boîte avec icône 🚀

Chaque boîte doit être un rectangle arrondi (rounded=1) de 200x140, avec un titre en gras,
et des sous-éléments en texte plus petit. Les flèches vont de:
- Phase 1 → Phase 2 (flèche horizontale)
- Phase 2 → Phase 3 (flèche diagonale)
- Phase 3 → Phase 4 (flèche horizontale)

En dessous, ajouter un bloc "VALIDATION HUMAINE" avec un cercle rouge et le texte
"Toi (Malek) valides visuellement chaque diagramme — ton feedback = ChromaDB enrichi".

Tout en haut, un titre : "🧠 Smart-MCP — Boucle d'Apprentissage Teacher → Student → Autonomie"

Utilise des couleurs distinctes :
- Phase 1: fillColor=#4A90D9 (bleu)
- Phase 2: fillColor=#50B848 (vert)
- Phase 3: fillColor=#F5A623 (orange)
- Phase 4: fillColor=#9B59B6 (violet)
- Validation: fillColor=#E74C3C (rouge)

Chaque élément doit avoir un mxCell avec mxGeometry complète.
Les flèches (edges) doivent avoir source et target valides pointant vers les IDs des boîtes."""

# ── Classification ──
print("🔍 Classification de l'intention...")
classification = llm.classify_intent(prompt)
print(f"   Type: {classification.get('macro_class', '?')} | "
      f"Complexité: {classification.get('complexity', '?')} | "
      f"Confiance: {classification.get('confidence', 0):.2f}")

# ── Recherche RAG ──
print("🧠 Recherche dans ChromaDB...")
patterns = brain.search_similar(prompt, n_results=3, min_score=0.5)
print(f"   Patterns trouvés: {len(patterns)}")

context = ""
if patterns:
    best = patterns[0]
    context = f"Exemple similaire: {best['title']} (score: {best['similarity']})\n{best['xml'][:500]}"
    print(f"   Pattern principal: {best['title']} ({best['similarity']:.2f})")
else:
    print("   Aucun pattern similaire — base neuve, c'est attendu pour le premier diagramme !")

# ── Génération XML via DeepSeek V4 ──
print("🎨 Génération XML via DeepSeek V4 Flash...")
sys.stdout.flush()

complexity = classification.get("complexity", "complex")  # On force complex pour utiliser le cloud
xml_raw = llm.generate(prompt, context=context, complexity="complex")

if not xml_raw:
    print("❌ ÉCHEC : DeepSeek n'a pas répondu")
    print("\n📋 DIAGNOSTIC :")
    print(f"   Clé API dispo ? {bool(llm.cloud and llm.cloud.api_key and len(llm.cloud.api_key) > 10)}")
    print(f"   Cloud model: {llm.cloud.model if llm.cloud else 'AUCUN'}")
    print(f"   Cloud URL: {llm.cloud.base_url if llm.cloud else 'AUCUN'}")
    print(f"   Cloud key len: {len(llm.cloud.api_key) if llm.cloud and llm.cloud.api_key else 0}")
    sys.exit(1)

print(f"   ✅ Réponse reçue ({len(xml_raw)} caractères)")
print(f"   Début: {xml_raw[:200]}...")

# ── Extraction XML ──
from smart_mcp_server import _extract_xml, _fix_xml_common, _validate_xml

xml_clean = _extract_xml(xml_raw)
print(f"   XML extrait: {len(xml_clean)} caractères")

if not xml_clean:
    print("❌ ÉCHEC : Extraction XML vide")
    sys.exit(1)

xml_clean = _fix_xml_common(xml_clean)
valid, errors = _validate_xml(xml_clean)

if not valid:
    print(f"⚠️  XML invalide: {errors}")
    print("📋 Tentative d'amélioration via DeepSeek...")
    improved = llm.improve_xml(xml_clean, prompt, "; ".join(errors))
    if improved:
        xml_clean = _extract_xml(improved)
        if xml_clean:
            xml_clean = _fix_xml_common(xml_clean)
            valid, errors = _validate_xml(xml_clean)
            if valid:
                print("   ✅ XML corrigé !")
            else:
                print(f"❌ Toujours invalide: {errors}")
                sys.exit(1)

# ── Sauvegarde du XML brut ──
output_dir = Path.home() / ".smart-mcp/output"
output_dir.mkdir(parents=True, exist_ok=True)
xml_file = output_dir / "smartmcp_learning_loop.drawio"
xml_file.write_text(xml_clean)
print(f"   💾 XML sauvegardé: {xml_file}")

# ── Envoi à draw.io ──
print("🚀 Envoi à draw.io...")
try:
    drawio.start_session()
    drawio.create_new_diagram(xml_clean)
    print("   ✅ Diagramme créé dans draw.io !")
    print("   🌐 Ouvre http://localhost:8080 pour voir le rendu")
except Exception as e:
    print(f"⚠️  draw.io: {e}")
    print("   📄 Le XML est sauvegardé, tu peux l'importer manuellement")

# ── Apprentissage ChromaDB ──
print("💾 Enregistrement dans ChromaDB...")
pattern_id = brain.add_pattern(
    title="🎓 Smart-MCP — Boucle d'apprentissage Teacher→Student→Autonomie",
    description=prompt,
    xml_fragment=xml_clean,
    tags=["APPRENTISSAGE", "PHASES", "TEACHER", "STUDENT", "AUTONOMIE", "SMART-MCP", "ARCHITECTURE"],
    source="generated"
)
print(f"   ✅ Pattern sauvegardé (ID: {pattern_id})")

# ── Stats finales ──
elapsed = time.time() - start
stats = brain.get_stats()
print(f"\n╔══════════════════════════════════════════════════════════════╗")
print(f"║  ✅ PREMIER DIAGRAMME SMART-MCP TERMINÉ !                    ║")
print(f"╠══════════════════════════════════════════════════════════════╣")
print(f"║  ⏱️  Temps total : {elapsed:.1f}s                              ║")
print(f"║  🧠 Patterns ChromaDB : {stats['patterns_count']}                  ║")
print(f"║  💾 Feedback patterns : {stats['feedback_count']}                  ║")
print(f"║  📄 XML : {len(xml_clean)} chars                               ║")
print(f"╚══════════════════════════════════════════════════════════════╝")
print(f"\n📂 Fichier: {xml_file}")
print(f"🌐 draw.io: http://localhost:8080")
PYEOF