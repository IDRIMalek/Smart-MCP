# Smart MCP Pipeline — Skill

## Objectif
Générer des diagrammes draw.io via un petit modèle local (9B) avec RAG + classification macro.

## Workflow
1. **Classification** : FORME / TABLEAU / KANBAN / AGENDA / GANTT / TEXTE
2. **RAG** : Cherche patterns similaires dans ChromaDB
3. **Génération XML** : LLM produit du XML draw.io
4. **Validation** : XML bien formé, cellules valides
5. **Dashboard** : Résultats persistants, tendances, filtres

## Commandes
```bash
# Démarrer le MCP server
python smart_mcp_server.py

# Lancer le dashboard
python dashboard/app.py

# Lancer tous les tests
python ci_tests.py

# Seeder ChromaDB
python -c "from brain.seed_patterns import seed; seed()"

# Obtenir les stats
python -c "from dashboard.test_runner import get_stats; import json; print(json.dumps(get_stats(), indent=2))"
```

## Endpoints API
- POST /api/result — Ajouter un résultat manuel
- GET /api/results — Tous les résultats
- GET /api/stats — Statistiques agrégées

## ChromaDB
- Path: ~/.smart-mcp/brain/
- Collections: diagram_patterns (patterns XML), feedback_history (feedback)
- Seed: 26 patterns initiaux (architectures, pipelines, flux, formes)
