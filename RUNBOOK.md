# 🏃 RUNBOOK Smart-MCP — Phase 1

> Tous les pièges rencontrés pendant le lancement de la Phase 1, et comment les éviter.
> À lire AVANT de relancer un pipeline.

---

## 🔴 Problème 1 — Session MCP perdue entre processus

**Symptôme :** L'utilisateur ouvre l'URL draw.io mais ne voit aucun diagramme (feuille blanche).

**Cause :** Chaque script Python `DrawioMCPClient` lance un nouveau sous-processus Node (`node index.js`). Si le premier script a créé une session sur le port 8080, le second script trouve le port occupé et monte sur **8082**. La nouvelle session existe sur 8082, mais l'utilisateur ouvre l'URL sur 8080. Le serveur 8080 n'a pas la session → rien n'affiche.

**Solution :**
```bash
# Un seul processus Python doit gérer le cycle de vie complet :
# 1. Lancer le serveur MCP
# 2. start_session()
# 3. create_new_diagram(xml)
# 4. GARDER LE PROCESSUS VIVANT (boucle infinie)
# 5. Seule cette même session a le diagramme

# Utiliser terminal(background=true) avec timeout long
```

**Dans Hermes :**
```python
terminal(
    command="python3 script_qui_garde_la_session.py",
    background=True,
    timeout=86400  # 24h
)
```

---

## 🔴 Problème 2 — URL sans `?mcp=` = spinner infini

**Symptôme :** La page draw.io s'ouvre mais reste bloquée sur le spinner gris « Loading... ».

**Cause :** Le navigateur ouvre `http://localhost:8080/` ou `http://192.168.1.100:8080/` sans le paramètre `?mcp=`. L'iframe `embed.diagrams.net` attend une connexion MCP pour s'initialiser. Sans le paramètre, le serveur SPA ne peut pas ouvrir le canal de communication.

**Solution :** Toujours inclure `?mcp=<sessionId>` dans l'URL :
```
http://192.168.1.100:8080/?mcp=mcp-mqsh0c8w-jgvyjm
```

---

## 🔴 Problème 3 — Le serveur MCP meurt avec le script Python

**Symptôme :** La session fonctionne pendant l'exécution du script, puis plus rien après.

**Cause :** `DrawioMCPClient._ensure_process()` lance `node index.js` en sous-processus via `subprocess.Popen`. Quand le script Python se termine, le sous-processus Node est tué (nettoyage de `Popen`).

**Solution :** Le script Python qui a créé la session doit **rester vivant** :
```python
# Après start_session() + create_new_diagram()
while True:
    time.sleep(60)
    # Heartbeat optionnel
    if drawio._process.poll() is not None:
        break  # Le serveur s'est arrêté
```

---

## 🔴 Problème 4 — Rendu drawio-headless : balises HTML en texte brut

**Symptôme :** Le SVG/PNG généré montre `<b>Phase 1</b><br>Contenu` en texte visible au lieu de mettre en forme.

**Cause :** Le XML draw.io utilise `html=1` avec des balises HTML `<b>`, `<br>` dans les valeurs des cellules. Le renderer `drawio-headless` (et `cairosvg`) ne les interprète pas.

**Solution :** Dans le XML généré par DeepSeek :
- Ne pas utiliser de balises HTML dans les `value`
- Utiliser `\n` pour les retours à la ligne
- Utiliser `fontStyle=1` dans le style pour le gras
- Garder `html=1;whiteSpace=wrap` dans le style

```xml
<!-- À ÉVITER -->
<mxCell value="<b>Titre</b><br>Contenu" style="html=1"/>

<!-- À UTILISER -->
<mxCell value="Titre\n─────────\nContenu" style="html=1;fontStyle=1"/>
```

---

## 🔴 Problème 5 — Export PNG via MCP non supporté

**Symptôme :** `drawio.export_diagram(path, format="png")` retourne toujours `False`.

**Cause :** Le serveur MCP `next-ai-draw-io` ne supporte pas l'export côté serveur. La méthode `export_diagram` vérifie l'existence du fichier après export, mais le fichier n'est jamais créé.

**Solution :** Utiliser `drawio-headless` (npm) pour convertir le `.drawio` XML en SVG, puis `cairosvg` (pip) pour le convertir en PNG :
```bash
npx drawio-headless render --format svg input.drawio output.svg
pip install cairosvg
python3 -c "
import cairosvg
cairosvg.svg2png(bytestring=open('output.svg','rb').read(),
                 write_to='output.png', scale=2)
"
```

---

## 🔴 Problème 6 — API publique draw.io inaccessible (DNS)

**Symptôme :** `httpx.post("https://www.draw.io/export2", ...)` → 404 ou erreur DNS.

**Cause :** Le serveur où tourne Hermes n'a pas d'accès DNS aux API externes de draw.io.

**Solution :** Passer par `drawio-headless` en local (voir Problème 5). Ne pas compter sur les API externes.

---

## 🔴 Problème 7 — Clé API OpenRouter non chargée dans l'environnement

**Symptôme :** Le pipeline échoue avec une erreur 401 ou « No API key provided ».

**Cause :** La clé `OPENROUTER_API_KEY` est stockée dans `~/.hermes/.env` mais n'est pas chargée dans l'environnement du shell ni du script Python.

**Solution :**
```bash
# En début de script, sourcer explicitement le fichier :
source ~/.hermes/.env
# Ou dans le script Python :
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
```

---

## 🔴 Problème 8 — IP LAN codée en dur (192.168.1.100)

**Symptôme :** Le serveur MCP ouvre le navigateur à `http://192.168.1.100:8080?mcp=...` au lieu de `localhost`.

**Cause :** Dans `index.js` (serveur MCP draw.io), l'URL d'ouverture du navigateur est codée en dur :
```javascript
const url = \`http://192.168.1.100:\${port}?mcp=\${sessionId}\`;
```
Le développeur travaille sur le LAN (accès depuis d'autres machines) donc l'IP fixe est intentionnelle. Mais ça ne marche pas si on est sur la même machine et qu'on utilise `localhost`.

**Solution :** Utiliser l'IP LAN fournie par le serveur pour les URLs distantes. Pour un accès local, remplacer par `localhost` dans l'URL manuellement.

---

## 🔴 Problème 9 — Navigateur headless timeout sur l'iframe draw.io

**Symptôme :** `browser_navigate("http://localhost:8080")` timeout après 60 secondes.

**Cause :** L'iframe draw.io charge depuis `https://embed.diagrams.net/` (externe). Dans un navigateur headless sans accès à ce CDN, l'iframe ne se charge jamais, le navigateur reste en attente, et `browser_navigate` timeout.

**Solution :** Ne pas utiliser le navigateur headless pour vérifier le rendu. Utiliser `drawio-headless` (local) pour générer une image PNG de vérification, puis l'analyser via vision.

---

## ✅ Checklist de vérification avant d'envoyer une URL

Avant de donner une URL draw.io à l'utilisateur :

- [ ] Le processus serveur Node tourne-t-il toujours ? (`ss -tlnp | grep 8080`)
- [ ] La session existe-t-elle sur CE serveur ? (appeler `start_session` ou vérifier par `get_diagram`)
- [ ] Le diagramme est-il stocké dans la session ? (`get_diagram()` retourne du contenu > 100 chars)
- [ ] L'URL inclut-elle le paramètre `?mcp=<sessionId>` ?
- [ ] Le processus Python qui a créé la session est-il gardé vivant ? (boucle infinie ou background)

---

## 📦 Dépendances installées

```bash
# Python (dans .venv du projet)
pip install chromadb openai httpx mcp cairosvg

# Node (global via npx)
npx --yes drawio-headless

# Clé API
# OPENROUTER_API_KEY dans ~/.hermes/.env
```

---

## 🧠 Pour les futurs IA

> L'objectif final est d'arriver en Phase 4 :
> **Le modèle local génère 90%+ des diagrammes, le cloud n'est que secours.**

Les problèmes ci-dessus sont principalement des problèmes d'infrastructure MCP/sessions. Une fois résolus, le pipeline est stable. La prochaine étape (Phase 2) consiste à déléguer des sous-tâches simples au modèle local (Gemma 4B) : ajouter un nœud, colorer, etc.