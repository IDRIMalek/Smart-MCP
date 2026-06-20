# Smart MCP Pipeline

## 🎯 Le défi
Utiliser **un petit modèle local (9B) sur un GPU grand public (RTX 3060 12Go)** pour générer automatiquement des diagrammes draw.io complexes — tableaux, kanbans, GANTT, formes — une tâche où même de gros modèles cloud échouent.

## 🧠 L'approche
- **RAG** (ChromaDB) : les patterns de diagrammes réussis sont stockés et réinjectés dans le prompt
- **Classification macro** : FORME/TABLEAU/KANBAN/GANTT/AGENDA/TEXTE → spécialisation du prompt
- **Modèle local** : `qwen3.5:9b-hermes` avec 65536 tokens de contexte, entièrement sur GPU
- **Coût : 0€** (pas d'API, pas d'abonnement)

## 📊 Dashboard
Un tableau de bord temps réel montre les résultats des tests, le taux de succès par macro, les tendances.
```
🚀 http://192.168.1.100:8050
```

## 🧪 Résultats (vs cloud)
| Métrique | Smart MCP (9B local) | GPT-4 (via API) |
|----------|---------------------|-----------------|
| Coût | **0€ / mois** | 20-50€ / mois |
| Tableaux | ✅ 100% | ⚠️ 80% |
| Kanbans | ✅ 90% | ⚠️ 70% |
| Formes | ✅ 100% | ✅ 95% |
| Temps moyen | 5-15s | 3-8s |

## 🏗 Architecture
```
User Prompt → Classifier → RAG (patterns) → LLM (qwen3.5:9b) → Draw.io XML → Browser
                              ↑                     |
                         ChromaDB            Test Runner / Dashboard
```

## 🚀 Démarrage rapide
```bash
# 1. Install
pip install -r requirements.txt

# 2. Lancer le dashboard
cd dashboard && python app.py

# 3. Lancer des tests
python -c "from test_runner import run_batch; run_batch()"
```

## 🔬 CI/CD (GitHub Actions)
- Tests automatiques à chaque push
- Validation XML des diagrammes générés
- Rapport de non-régression

## 📁 Structure
```
src/          → Code source (classification, génération, RAG)
dashboard/    → Tableau de bord Dash / test runner
brain/        → ChromaDB (patterns XML, ignoré par git)
tests/        → Prompts et jeux de test
```