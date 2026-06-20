# Smart MCP Pipeline — SOUL.md

## 🎯 Mission
Générer automatiquement des diagrammes draw.io de qualité professionnelle avec un petit LLM local (9B) sur GPU grand public (RTX 3060 12GB), sans dépendance aux API cloud.

## 🧠 Architecture
```
User Prompt → Classifier (LLM) → RAG (ChromaDB patterns) → LLM local (9B) → XML draw.io → Navigateur
```

## 📊 Macro-classes
- **FORME** : formes géométriques (carrés, cercles, triangles, etc.)
- **TABLEAU** : diagrammes d'architecture, pipelines, flux
- **KANBAN** : tableaux kanban / boards
- **AGENDA** : calendriers, plannings
- **GANTT** : diagrammes de Gantt, planning projet
- **TEXTE** : questions/réponses (pas de diagramme)
- **AUTO** : classification automatique via LLM local

## 🧪 Tests
- Suite CI complète : **214 tests** couvrant structure, ChromaDB, search, templates XML, validation, et performance
- Résultats persistants dans ci_results.json
- Dashboard temps réel sur http://192.168.1.100:8050

## 📁 Structure du repo
```
Smart-MCP/
├── brain/             # RAG, seed patterns, templates XML
│   ├── rag.py        # ChromaDB RAGBrain
│   ├── seed_patterns.py  # 26 patterns initiaux
│   └── shape_templates.py  # Templates XML draw.io
├── dashboard/        # Dashboard Dash + test runner
├── diagrams/         # Fichiers .drawio (13 pages)
├── models/           # LLM client
├── mcp_client/       # MCP draw.io client
├── tests/            # Tests unitaires
├── skills/           # Skills Hermes pour les agents
├── .github/          # CI/CD GitHub Actions
├── smart_mcp.py      # Pipeline principal
├── smart_mcp_server.py  # MCP server
├── ci_tests.py       # Suite de 214 tests
├── SOUL.md           # Ce fichier
├── README.md         # Documentation principale
└── requirements.txt  # Dépendances
```

## 🚀 Démarrage rapide
```bash
# Installer les dépendances
pip install -r requirements.txt

# Seeder ChromaDB
python -c "from brain.seed_patterns import seed; seed()"

# Lancer le MCP server
python smart_mcp_server.py

# Lancer le dashboard
python dashboard/app.py

# Lancer tous les tests (214)
python ci_tests.py
```

## 📈 Objectifs
- [x] Classification automatique via LLM local
- [x] RAG avec ChromaDB (26+ patterns)
- [x] Dashboard temps réel avec visualisation ChromaDB
- [x] API REST pour tests manuels
- [x] CI/CD GitHub Actions
- [x] >200 tests validés (214 ✅ local, 208 ✅ CI)
- [x] Mode MANUEL avec exécution live du pipeline (plus de curl)
- [x] Dashboard avec lien direct draw.io vers GitHub (persistant)
- [x] Toggle AUTO/MANUEL amélioré — banc de test intégré
- [ ] Visualisation ChromaDB (Neo4J / graphe relationnel)
- [ ] Mode auto-apprentissage
- [ ] Push GitHub automatique après tests verts
