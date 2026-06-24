# Smart MCP Pipeline

## 🎯 Le défi
Utiliser **un petit modèle local (9B) sur un GPU grand public (RTX 3060 12Go)** pour générer automatiquement des diagrammes draw.io complexes — tableaux, kanbans, GANTT, formes — une tâche où même de gros modèles cloud échouent.

## 🧠 L'approche
- **RAG** (ChromaDB) : 26+ patterns de diagrammes stockés et réinjectés dans le prompt
- **Classification macro** : FORME/TABLEAU/KANBAN/GANTT/AGENDA/TEXTE → spécialisation du prompt
- **Modèle local** : `qwen3.5:9b-hermes` (65536 tokens contexte, entièrement sur GPU)
- **Coût : 0€** (pas d'API cloud)

## 📊 Dashboard temps réel
```
🚀 http://192.168.1.100:8050
```
- Auto-refresh 3s avec tendances et graphiques
- **Toggle AUTO/MANUEL** : mode auto = batchs de tests, mode manuel = exécution live du pipeline
- **Filtres** : source, macro, status, modèle — tous les résultats historiques visibles
- **Diagrammes persistants** : liens cliquables → ouvrir direct dans draw.io (GitHub)
- **Vue ChromaDB** : patterns, types, stats en haut du dashboard

## 📐 Diagramme persistant F1-F17
Le diagramme complet de l'architecture Smart MCP est versionné dans le repo :
- **13 pages** : Vue Macro, Pipeline, Infrastructure, Workflows, Benchmarks, Carte Systémique, Architecture LLM, Optimisation, Kanban, Test, Banc de Test (F16), Amélioration Continue (F17)
- **Liens permanents** (après push GitHub) :
  - [Ouvrir dans draw.io](https://app.diagrams.net/#HIDRIMalek/Smart-MCP/main/diagrams/smart-mcp-full-persistent.drawio)
  <!-- Lien supprimé — fichier retiré du repo -->

## 🧪 Résultats

| Métrique | Smart MCP (9B local) |
|----------|---------------------|
| Coût | **0€ / mois** |
| Tests CI | **214 ✅ local / 208 ✅ CI** |
| Tableaux | ✅ 100% |
| Kanbans | ✅ 90% |
| Formes | ✅ 100% |
| Temps moyen | 5-15s |
| Contexte | 65536 tokens |
| VRAM | 6.6 GB |

## 🏗 Architecture
```
User Prompt → Classifier (LLM) → RAG ChromaDB (26 patterns)
                                    ↓
                              LLM local (9B) → XML draw.io → Dashboard
                                    ↓
                              Test Runner (214 tests) → CI/CD GitHub Actions
```

## 🚀 Démarrage rapide
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Seeder ChromaDB
python -c "from brain.seed_patterns import seed; from brain.shape_templates import seed_shapes; seed(); seed_shapes()"

# 3. Lancer le dashboard
python dashboard/app.py     # → http://0.0.0.0:8050

# 4. Lancer les tests (214)
python ci_tests.py          # → ci_results.json

# 5. Mode CI (sans ChromaDB réelle)
CI=true CI_CHROMA_PATH=/tmp/chroma python ci_tests.py  # → 208 tests
```

## 🔬 CI/CD (GitHub Actions)
- **Workflow** : `.github/workflows/ci.yml`
- **Jobs** : lint (ruff) → test (208 tests sans LLM, seed ChromaDB dynamique)
- **Déclenché** : push/PR vers main

## 📁 Structure
```
Smart-MCP/
├── brain/                  # RAG, seed patterns, templates XML
│   ├── rag.py             # ChromaDB RAGBrain
│   ├── seed_patterns.py   # Seed 26 patterns
│   └── shape_templates.py # SHAPE_PATTERNS (15 formes + 5 architectures)
├── dashboard/              # Dash dashboard + test runner
│   ├── app.py             # App Dash (956 lignes)
│   └── test_runner.py     # Runner pipelines
├── diagrams/               # Diagrammes .drawio persistants (13 pages)
├── models/                 # LLM client
│   └── llm_client.py      # LLMClient avec classify_intent
├── mcp_client/             # MCP draw.io client
│   └── drawio.py
├── skills/                 # Skills Hermes pour agents
│   ├── smart-mcp-pipeline.md
│   └── drawio-mcp-integration.md
├── .github/workflows/      # CI/CD
│   └── ci.yml             # Lint + 208 tests
├── tests/                  # Tests unitaires
├── smart_mcp.py            # Pipeline principal
├── smart_mcp_server.py     # Serveur MCP
├── ci_tests.py             # Suite >200 tests (8 sections A-H)
├── SOUL.md                 # Macro-règles de classification
└── README.md               # Ce fichier
```

## 🧠 ChromaDB Visualisation
- **2 collections** : `diagram_patterns` (patterns XML) + `feedback_history`
- **26 patterns** : 5 architectures + 15 formes + 4 couleurs + 1 test + 1 généré
- **Chemin** : `~/.hermes/profiles/default2/home/.smart-mcp/brain/chroma.sqlite3`

## 🔑 Points clés
- [x] Classification automatique via LLM local
- [x] RAG avec ChromaDB (26+ patterns)
- [x] Dashboard temps réel avec mode auto/manuel
- [x] CI/CD GitHub Actions (208 tests sans LLM)
- [x] 214 tests local / 208 CI — 100% verts
- [x] Diagramme persistant F1-F17 lié au dashboard
- [x] Mode manuel avec exécution live du pipeline
- [ ] Visualisation ChromaDB (Neo4J / graphe)
- [ ] Mode auto-apprentissage
