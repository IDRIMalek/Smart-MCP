# 🧠 Smart MCP — Mindmap Agent Tutorial

## Créer des mindmaps interactives en FULL LOCAL avec Gemma 4B + Qwen 9B

---

## 📚 Table des matières

1. [Qu'est-ce que le Mindmap Agent ?](#-quest-ce-que-le-mindmap-agent-)
2. [Architecture : le paradigme "décodeur"](#-architecture--le-paradigme-décodeur)
3. [Prérequis](#-prérequis)
4. [Installation](#-installation)
5. [Première utilisation : créer une mindmap](#️-première-utilisation--créer-une-mindmap)
6. [Éditer interactivement](#-éditer-interactivement)
7. [Changer les couleurs (statut To Do / In Progress / Done)](#-changer-les-couleurs)
8. [Ajouter / supprimer des branches](#-ajouter--supprimer-des-branches)
9. [Workflow complet en 3 étapes](#-workflow-complet-en-3-étapes)
10. [Dépannage](#-dépannage)
11. [Roadmap](#-roadmap)

---

## 🎯 Qu'est-ce que le Mindmap Agent ?

Le **Mindmap Agent** est une spécialisation de Smart MCP dédiée à un seul type de diagramme : **les mindmaps**.

**Philosophie :** plutôt que de demander à un petit modèle local (4B / 9B) de générer un XML parfait de 50 éléments en une seule fois — ce qu'il rate — on lui fait **planifier la structure**, puis chaque nœud est ajouté **un par un** sur le canvas draw.io.

Résultat : **21 nœuds créés en 64s, 100% local, 0€ de coût cloud.**

### Ce que l'agent PEUT faire :
- ✅ Créer une mindmap complète depuis une phrase
- ✅ Ajouter interactivement des nœuds et sous-branches
- ✅ Changer les couleurs (To Do / In Progress / Done)
- ✅ Supprimer des branches
- ✅ Tout en FULL LOCAL sur RTX 3060 12GB

### Ce que l'agent NE PEUT PAS ENCORE faire :
- ❌ Voir le rendu visuel (vision feedback — bientôt)
- ❌ Déplacer des nœuds (drag & drop — bientôt)
- ❌ Autres types de diagrammes (brainstorming — prochaine étape)

---

## 🏗 Architecture : le paradigme "décodeur"

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Utilisateur │───▶│  PLANNER         │───▶│  GENERATOR       │
│  "mindmap    │    │  (Qwen 9B)       │    │  (Gemma 4B)      │
│  remote work"│    │  planifie la     │    │  exécute les     │
└─────────────┘    │  structure        │    │  opérations      │
                   │  {root, branches, │    │  atomiques       │
                   │   children,       │    │  add_node,       │
                   │   colors, angles} │    │  add_edge,       │
                   └────────┬─────────┘    │  update_style    │
                            │              └────────┬─────────┘
                            ▼                       ▼
                   ┌──────────────────────────────────────┐
                   │         MindmapAgent                 │
                   │  - add_root(label)                   │
                   │  - add_node(parent, label, angle)    │
                   │  - update_node(id, color/label)      │
                   │  - delete_node(id)                   │
                   │  - get_canvas_state()                │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │     Draw.io MCP Server       │
                   │  (port 8080, stdio transport) │
                   └──────────────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │    NAVIGATEUR DRAW.IO         │
                   │  http://192.168.1.100:8080    │
                   │  Vois le canvas en temps réel │
                   └──────────────────────────────┘
```

**Principe clé :** Le LLM décode la **structure** (root, branches, couleurs). L'agent se charge de la **mécanique** (positions, IDs, connexions draw.io). Le modèle fait ce qu'il sait faire (raisonner, planifier) et ne fait pas ce qu'il rate (générer 50 shapes XML parfaites d'un coup).

---

## 📋 Prérequis

### Matériel
- **GPU NVIDIA** avec ≥ 8GB VRAM (testé sur RTX 3060 12GB)
- **RAM système** ≥ 16GB (32GB recommandé)
- **Stockage** ~10GB pour les modèles

### Logiciel
- **Ollama** installé et service GPU actif
- **Node.js 18+** (pour le serveur draw.io MCP)
- **Python 3.10+** avec `pip`
- **Navigateur** (Chrome / Firefox)

### Modèles Ollama nécessaires

```bash
# Vérifier les modèles disponibles
ollama list

# Si manquants, les créer avec les Modelfiles anti-truncation :
ollama create qwen3.5:9b-hermes -f Modelfile.qwen3.5
ollama create gemma4:e4b-hermes -f Modelfile.gemma4
```

> ⚠️ **Crucial :** Chaque modèle DOIT avoir `num_ctx 65536` dans son Modelfile, sinon les prompts sont tronqués à 2048 tokens et le modèle répond vide.

---

## 🔧 Installation

### 1. Cloner Smart MCP

```bash
cd ~/workspace
git clone https://github.com/IDRIMalek/Smart-MCP.git
cd Smart-MCP
```

### 2. Installer les dépendances

```bash
pip install openai chromadb httpx
```

### 3. Installer le serveur draw.io MCP

```bash
cd ~/workspace/mcp-server-patched
npm install
node dist/index.js --version  # Vérifier que ça tourne
```

### 4. Configurer les variables d'environnement

```bash
# ~/.bashrc ou .env
export OLLAMA_GPU_URL=http://localhost:11434/v1
export OLLAMA_API_KEY=ollama
export SMART_MCP_PLANNER_MODEL=qwen3.5:9b-hermes
export SMART_MCP_GENERATOR_MODEL=gemma4:e4b-hermes
export SMART_MCP_PREFER_LOCAL=true
export DRAWIO_MCP_PATH=/home/malek/workspace/mcp-server-patched/dist/index.js
```

### 5. Lancer le serveur Smart MCP

```bash
cd ~/workspace/Smart-MCP
python smart_mcp_server.py
```

Le serveur écoute sur stdio — Hermes le découvre automatiquement si configuré en tant que MCP server.

---

## 🖱️ Première utilisation : créer une mindmap

### Via l'API Python directe (recommandé pour le test)

```python
from brain.mindmap_agent import get_agent

agent = get_agent()
result = agent.create_mindmap(
    "mindmap about remote work: productivity, challenges, tools"
)

print(f"Statut: {result['status']}")
print(f"Nœuds créés: {result['nodes']}")

# Voir la structure
for line in result['canvas'].split('\n'):
    print(' ', line)
```

### Via le serveur MCP

```bash
# Envoyé comme outil MCP depuis Hermes
mindmap_agent(action="create", prompt="mindmap about cloud native: microservices, observability, CI/CD")
```

### Résultat attendu

```
✅ Création réussie en 63.9s — 21 nœuds créés
  [2] Architecture Cloud Native → parent: ROOT
  [3] Microservices → parent: Architecture Cloud Native
  [5] API Gateway → parent: Microservices
  [7] Observability → parent: Architecture Cloud Native
  [9] CI/CD Pipelines → parent: Architecture Cloud Native
  ...
```

Ouvre `http://192.168.1.100:8080` dans ton navigateur — tu vois la mindmap se construire **en temps réel**, nœud par nœud.

---

## ✏️ Éditer interactivement

Une fois la mindmap créée, tu peux continuer à la modifier par la conversation.

### Ajouter un nœud

```python
# Depuis Python
result = agent.edit_mindmap(
    "add a 'Kubernetes' sub-branch under tools in blue"
)

# Depuis Hermes / MCP
# mindmap_agent(action="edit", prompt="add a 'Kubernetes' sub-branch under tools in blue")
```

### Résultat

```
Status: success
Action: add
Label: Kubernetes
```

Le nouveau nœud apparaît instantanément sur le navigateur draw.io.

---

## 🎨 Changer les couleurs

C'est LA fonctionnalité clé pour le suivi de projet : colorer les nœuds selon leur statut.

```python
# Marquer comme "En cours" (orange)
agent.edit_mindmap("change color of 'Microservices' to orange")
# → #FF9800

# Marquer comme "Terminé" (vert)
agent.edit_mindmap("change color of 'API Gateway' to green")
# → #4CAF50

# Marquer comme "Problème" (rouge)
agent.edit_mindmap("change color of 'Testing' to red")
# → #F44336
```

**Palette de couleurs disponibles :**

| Usage | Couleur | Code hex | Émotion |
|-------|---------|----------|---------|
| Root | Vert | `#4CAF50` | Central |
| Branche principale | Bleu | `#2196F3` | Standard |
| En cours / WIP | Orange | `#FF9800` | Attention |
| Terminé / Done | Vert | `#4CAF50` | Validé |
| Bloqué / Problème | Rouge | `#F44336` | Alerte |
| Nouveau | Violet | `#9C27B0` | Innovation |
| Info | Cyan | `#00BCD4` | Information |
| Secondaire | Rose | `#E91E63` | Auxiliaire |

---

## ➕ Ajouter / supprimer des branches

```python
# Ajout simple
agent.edit_mindmap("add a branch called 'Security' under the root")

# Ajout avec couleur spécifique
agent.edit_mindmap("add 'Data Analytics' as a child of tools in purple")

# Suppression (supprime aussi les enfants !)
agent.edit_mindmap("delete the 'Challenges' branch")

# Renommer
agent.edit_mindmap("rename 'Productivity' to 'Efficiency'")
```

---

## 🔄 Workflow complet en 3 étapes

### Étape 1 : Idéation (Brainstorming → Mindmap)

```
Toi : "mindmap about starting my freelance business: clients, pricing, tools, admin"
Agent : [21 nœuds créés, structure complète visible dans draw.io]
```

### Étape 2 : Priorisation (Couleurs de statut)

```
Toi : "mark 'clients' in green, 'pricing' in orange, 'admin' in red"
Agent : [Couleurs changées en direct sur le canvas]
```

### Étape 3 : Itération (Ajout / modification)

```
Toi : "add 'invoicing' under admin in cyan"
Agent : [Nouveau nœud ajouté et connecté]
Toi : "add 'prospecting' under clients"
Agent : [Encore un nœud]
```

**Résultat final :** Une mindmap dynamique qui vit avec ta réflexion, sans jamais toucher à la souris.

---

## 🔍 Dépannage

### "Le LLM ne répond pas" (timeout)

```bash
# Vérifier que le modèle est chargé en VRAM
ollama ps

# Si pas chargé, le forcer avec une requête
ollama run gemma4:e4b-hermes "hello" --nowordwrap

# Vérifier le contexte
ollama show gemma4:e4b-hermes | grep num_ctx
# Doit être >= 65536
```

### "Le nœud n'apparaît pas dans draw.io"

```bash
# Vérifier que le serveur MCP respond
curl http://192.168.1.100:8080/health

# Redémarrer si besoin
cd ~/workspace/mcp-server-patched && node dist/index.js
```

### "Erreur 'Pas de JSON' dans l'édition"

Le LLM a répondu mais pas en JSON. C'est normal pour Gemma 4B qui a un taux de dérapage plus élevé. **Relance la même demande** — 8 fois sur 10 ça marche au second essai.

```python
# Fallback automatique : l'agent réessaye
result = agent.edit_mindmap("add 'Kubernetes' under tools")
if result.get("status") == "error":
    # Essai API directe
    from brain.mindmap_agent import get_agent
    agent = get_agent()
    parent = agent.agent.get_node_by_label("tools")
    if parent:
        agent.agent.add_node(parent, "Kubernetes", angle=15, color="#2196F3")
```

### "Canvas vide" après création

Tu utilises peut-être une **nouvelle instance Python**. Le singleton `get_agent()` vit dans un seul processus. Utilise le serveur MCP (qui tourne en continu) plutôt que des scripts Python séparés.

---

## 🗺 Roadmap

### Prochaines étapes (juin-juillet 2026)

| Fonctionnalité | Priorité | Statut |
|----------------|---------|--------|
| ✨ **Vision feedback** — export PNG → analyse visuelle → ajustement | 🔴 Haute | 📝 Design |
| 🔄 **Brainstorming** — 2e type de diagramme (nuage de mots) | 🟡 Moyenne | 📝 Design |
| 🎯 **Mindmap from code** — parser une architecture YAML/JSON en mindmap | 🟢 Basse | 💡 Idée |
| 🖱 **Drag & drop assisté** — le LLM déplace des nœuds existants | 🟢 Basse | 💡 Idée |
| 💾 **Save / Load** — exporter la mindmap en image + XML | 🟢 Basse | 💡 Idée |

### Le grand pari

> **"Un petit modèle local spécialisé sur 1 type de diagramme bat un gros modèle cloud qui doit tous les gérer."**

Les 64 secondes et 21 nœuds du test valident ce pari. La prochaine révolution sera le **vision feedback** : le LLM voit ce qu'il a dessiné et s'auto-corrige, comme un humain.

---

## 📖 Résumé des commandes

| Action | Commande | Temps |
|--------|----------|-------|
| Créer une mindmap | `create_mindmap("sujet: ...")` | 60-90s |
| Ajouter un nœud | `edit_mindmap("add X under Y")` | 10-15s |
| Changer une couleur | `edit_mindmap("change X to COLOR")` | 10-15s |
| Supprimer un nœud | `edit_mindmap("delete X")` | 10-15s |
| Voir l'état | `get_canvas_text()` | 0.1s |
| Ouvrir draw.io | http://192.168.1.100:8080 | instantané |

---

*Créé par Malek IDRI — Juin 2026*
*Smart MCP v2 — Mindmap Agent*
*Full local sur RTX 3060 12GB + Gemma 4B + Qwen 9B*