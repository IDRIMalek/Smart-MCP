# Smart MCP Pipeline — Skill

## Objectif
Générer des diagrammes draw.io via un petit modèle local (9B) avec classification macro (FORME/TABLEAU/KANBAN/AGENDA/GANTT/TEXTE), RAG ChromaDB, et pipeline de test automatisé.

## Workflow
1. **Classification** : LLM classifie le prompt en 6 macro-classes
2. **RAG** : Cherche patterns similaires dans ChromaDB (26+ patterns)
3. **Génération XML** : LLM produit du XML draw.io avec patterns RAG en contexte
4. **Validation** : XML bien formé, cellules valides, mxGraphModel complet
5. **Dashboard** : Résultats persistants (append-only), tendances, filtres, GANTT

## Architecture du repo
```
Smart-MCP/                    ← Repo GitHub canonique
├── brain/
│   ├── rag.py                ← RAGBrain : ChromaDB interface
│   ├── seed_patterns.py      ← Seed 26 patterns (5 archi + 15 formes + couleurs)
│   └── shape_templates.py    ← SHAPE_PATTERNS + STYLES + seed_shapes()
├── dashboard/
│   ├── app.py                ← Dash dashboard (auto-refresh, toggle auto/manual, GANTT)
│   └── test_runner.py        ← Runner de tests automatisés (>200)
├── diagrams/                 ← Fichiers .drawio persistants (trackés dans Git)
│   └── smart-mcp-full-persistent.drawio  ← 13 pages F1-F17, Zones A-E
├── models/
│   └── llm_client.py         ← LLMClient avec classify_intent
├── mcp_client/
│   └── drawio.py             ← Client MCP draw.io
├── .github/workflows/ci.yml  ← CI/CD (lint + 208 tests sans LLM)
├── ci_tests.py               ← Suite >200 tests (8 sections A-H)
├── SOUL.md                   ← Macro-règles de classification (versionné)
├── README.md                 ← Documentation principale
├── skills/                   ← Skills Hermes pour agents
└── requirements.txt          ← Dépendances
```

## Tests — CI

```bash
# Mode local (avec ChromaDB réelle, 26 patterns)
python ci_tests.py          # → 214 ✅ / 0 ❌

# Mode CI (seed fraîche, pas de générés)
CI=true CI_CHROMA_PATH=/tmp/test python ci_tests.py  # → 208 ✅ / 0 ❌

# Résultats sauvegardés dans ci_results.json
```

| Section | Tests | Contenu |
|---------|-------|---------|
| A — Structure | 25 | Fichiers, dossiers, .drawio |
| B — Brain/ChromaDB | 60 | Connexion, seed, patterns, recherche |
| C — XML | 50 | Syntaxe, extraction, validation |
| D — MCP | 20 | Imports, classes, API |
| E — Dashboard | 30 | Structure, CRUD, stats |
| F — CI/CD | 30 | GitHub Actions, .gitignore, README |
| G — Performance | 20 | Tailles fichiers, secrets, imports |
| H — Templates | 15 | SHAPE_PATTERNS, STYLES, create_xml |

## Dashboard

- **URL** : http://192.168.1.100:8050
- **Auto-refresh** : 3s
- **Mode AUTO** : batchs de tests par macro-classe
- **Mode MANUEL** : exécution live du pipeline complet + sauvegarde auto
- **Diagrammes persistants** : liens cliquables GitHub → draw.io

### Filtres disponibles
- Source (Auto / Manuel)
- Macro (FORME / TABLEAU / KANBAN / AGENDA / GANTT / TEXTE)
- Status (Success / Classifié OK / XML invalide / Échec)
- Modèle (liste dynamique)

## ChromaDB

- **Chemin** : `~/.hermes/profiles/default2/home/.smart-mcp/brain/`
- **Collections** : diagram_patterns, feedback_history
- **26 patterns** : 15 formes, 5 architectures, 4 couleurs, 1 test, 1 generé
- **Seed** : `python -c "from brain.seed_patterns import seed; from brain.shape_templates import seed_shapes; seed(); seed_shapes()"`

⚠️ **Important** : Ne JAMAIS utiliser `Path.home()` pour construire le chemin — Hermes modifie `$HOME`. Toujours utiliser un chemin absolu en dur.

## Points critiques — Imports

```python
# ✅ ROBUSTE — import par chemin absolu
import importlib.util
_spec = importlib.util.spec_from_file_location("smart_mcp_server",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_mcp_server.py"))

# ✅ ROBUSTE — imports relatifs pour seed/templates
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brain.seed_patterns import seed
```

## Modèles

| Modèle | VRAM | Contexte | Usage |
|--------|------|----------|-------|
| qwen3.5:9b-hermes | 6.6GB | 65536 | RECOMMANDÉ (profil local-diagram) |
| gemma4:e4b (4B) | 3.8GB | 65536 | Alternative plus rapide |

⚠️ **Tout modèle Ollama utilisé dans Hermes WebUI DOIT avoir un Modelfile avec `PARAMETER num_ctx 65536`** — sinon contexte par défaut à 2048 → réponses vides.

## Push GitHub

```bash
cd ~/workspace/Smart-MCP
git add -A
git commit -m "itération: description"
# Nécessite token GitHub
git push origin main
```
