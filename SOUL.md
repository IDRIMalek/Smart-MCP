# Smart MCP Pipeline — SOUL.md

## 🎯 Mission
Générer automatiquement des diagrammes draw.io de qualité professionnelle avec un petit LLM local (9B) sur GPU grand public (RTX 3060 12GB), sans dépendance aux API cloud.

## 🧠 Architecture
```
User Prompt → Classifier (macro-classe) → RAG (ChromaDB patterns) → LLM local (qwen3.5:9b) → XML draw.io → Navigateur
```

## 📊 Macro-classes
- **FORME** : formes géométriques (carrés, cercles, triangles, etc.)
- **TABLEAU** : diagrammes d'architecture, pipelines, flux
- **KANBAN** : tableaux kanban / boards
- **AGENDA** : calendriers, plannings
- **GANTT** : diagrammes de Gantt, planning projet
- **TEXTE** : questions/réponses (pas de diagramme)

## 🧪 Tests
- Automatiques (boutons du dashboard) + Manuels (via Hermes WebUI → API)
- Résultats persistants dans results.json
- Dashboard temps réel sur http://192.168.1.100:8050

## 📁 Structure du repo
```
Smart-MCP/
├── src/              # Code source (pipeline, LLM, RAG, MCP server)
├── dashboard/        # Dashboard Dash + test runner
├── diagrams/         # Fichiers .drawio (diagrammes)
├── tests/            # Tests unitaires
├── .github/          # CI/CD GitHub Actions
├── SOUL.md           # Ce fichier
├── README.md         # Documentation principale
└── requirements.txt  # Dépendances
```

## 🚀 Démarrage rapide
```bash
# Installer les dépendances
pip install -r requirements.txt

# Seeder ChromaDB
python -c "from src.seed_patterns import seed; seed()"

# Lancer le MCP server
python src/smart_mcp_server.py

# Lancer le dashboard
python dashboard/app.py
```

## 📈 Objectifs
- [x] Classification en 6 macro-classes
- [x] RAG avec ChromaDB (26+ patterns)
- [x] Dashboard temps réel
- [x] API REST pour tests manuels
- [x] CI/CD GitHub Actions
- [ ] >200 tests validés
- [ ] Visualisation ChromaDB (Neo4J / graphe)
- [ ] Mode auto-apprentissage
