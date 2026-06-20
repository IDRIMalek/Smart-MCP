"""
🧠 Smart MCP — Seed patterns : Mind Maps, Brainstorming & Classification
Ajoute des patterns de mind maps, brainstorming et diagrammes de classification
trouvés dans les templates officiels draw.io / jgraph
"""

import sys, re, json, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from brain.rag import RAGBrain, get_brain
from brain.drawio_decoder import decode_drawio

# ── Téléchargement des templates officiels draw.io ──────────────────────────
BASE = "https://raw.githubusercontent.com/jgraph/drawio/master/src/main/webapp/templates"

TEMPLATES = [
    # ── MIND MAPS ─────────────────────────────────────────────────────────
    {
        "file": f"{BASE}/maps/mind_map.xml",
        "title": "Mind Map — Carte mentale générale",
        "desc": "Mind map complète avec centre 'MIND MAPPING' et 4 branches (Planning, Projects, Goals, Strategies, Creativity). Branches courbes, style organique.",
        "tags": ["mind-map", "carte-mentale", "brainstorming", "ideation", "organisation", "creativite"],
    },
    {
        "file": f"{BASE}/maps/living_beings_mind_map.xml",
        "title": "Mind Map — Classification des êtres vivants",
        "desc": "Mind map de classification : Mammal, Insect, Bird, Fish, Reptile, Plant. Cercle central, couleurs distinctes par catégorie.",
        "tags": ["mind-map", "classification", "taxonomie", "carte-mentale", "education", "sciences"],
    },
    # ── CONCEPT MAPS (Brainstorming) ────────────────────────────────────────
    {
        "file": f"{BASE}/maps/concept_map_1.xml",
        "title": "Concept Map 1 — Carte conceptuelle brainstorming",
        "desc": "Carte conceptuelle/graph organizer : central theme with radiating sub-concepts. Style brainstorming visuel.",
        "tags": ["concept-map", "brainstorming", "carte-conceptuelle", "ideation", "cognition"],
    },
    {
        "file": f"{BASE}/maps/concept_map_2.xml",
        "title": "Concept Map 2 — Graphe de relations",
        "desc": "Concept map avancée avec relations multiples entre nœuds. Adapté au brainstorming créatif et à l'analyse de problèmes.",
        "tags": ["concept-map", "brainstorming", "carte-conceptuelle", "relations", "analyse"],
    },
    # ── CLASSIFICATION / HIERARCHY ─────────────────────────────────────────
    {
        "file": f"{BASE}/charts/org_chart_1.xml",
        "title": "Organigramme hiérarchique (Org Chart)",
        "desc": "Organigramme d'entreprise classique : CEO → VP(s) → Directors → Managers. Structure arborescente verticale.",
        "tags": ["classification", "organigramme", "hierarchie", "org-chart", "entreprise", "structure"],
    },
    {
        "file": f"{BASE}/basic/orgchart.xml",
        "title": "Organigramme simple (3 niveaux)",
        "desc": "Org chart 3 niveaux : racine → 3 branches → 6 feuilles. Style épuré, idéal pour classification taxonomique.",
        "tags": ["classification", "organigramme", "hierarchie", "org-chart", "taxonomie"],
    },
    {
        "file": f"{BASE}/charts/work_breakdown_structure.xml",
        "title": "Work Breakdown Structure (WBS)",
        "desc": "Structure de découpage de projet : Projet → Phases → Tâches. Arbre hiérarchique de classification des livrables.",
        "tags": ["classification", "wbs", "work-breakdown", "hierarchie", "projet", "gestion"],
    },
    # ── DECISION / BRAINSTORMING ─────────────────────────────────────────
    {
        "file": f"{BASE}/other/decision_tree.xml",
        "title": "Arbre de décision (Decision Tree)",
        "desc": "Arbre de décision binaire : décision → oui/non → branches. Adapté à la classification et à l'aide à la décision.",
        "tags": ["classification", "decision-tree", "arbre-decision", "analyse", "brainstorming", "logique"],
    },
    {
        "file": f"{BASE}/business/ishikawa_1.xml",
        "title": "Diagramme d'Ishikawa (Fishbone)",
        "desc": "Diagramme cause-effet Ishikawa (arête de poisson). Idéal pour brainstorming de résolution de problèmes et analyse des causes racines.",
        "tags": ["brainstorming", "ishikawa", "cause-effect", "fishbone", "analyse", "probleme", "qualite"],
    },
    {
        "file": f"{BASE}/basic/mindmap.xml",
        "title": "Mind Map — Template de base draw.io",
        "desc": "Mind map officielle draw.io avec nœud central 'MIND MAPPING', 5 branches, style Comic Sans MS. Arêtes courbes avec labels.",
        "tags": ["mind-map", "carte-mentale", "template", "drawio", "branches", "creativite"],
    },
]


def _download(url: str) -> str:
    """Télécharge un fichier texte depuis une URL"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


def _extract_mxgraphmodel(data: str) -> str | None:
    """Extrait le premier <mxGraphModel>...</mxGraphModel> du XML draw.io"""
    # Chercher dans tout le fichier
    m = re.search(r'<mxGraphModel[^>]*>.*?</mxGraphModel>', data, re.DOTALL)
    if m:
        return m.group()
    
    # Fallback: chercher dans <diagram>
    m = re.search(r'<diagram[^>]*>(.*?)</diagram>', data, re.DOTALL)
    if m:
        inner = m.group(1)
        m2 = re.search(r'<mxGraphModel[^>]*>.*?</mxGraphModel>', inner, re.DOTALL)
        if m2:
            return m2.group()
    return None


def seed():
    """Télécharge et ajoute tous les patterns"""
    brain = get_brain()
    before = brain.get_stats()["patterns_count"]
    added = 0
    errors = []

    for tpl in TEMPLATES:
        try:
            print(f"\n📥 {tpl['title']}...", end=" ")
            raw = _download(tpl["file"])
            xml = decode_drawio(raw)
            if not xml:
                print(f"❌ XML non trouvé")
                errors.append(tpl["title"])
                continue

            # Nettoyer les espaces superflus
            xml = re.sub(r'>\s+<', '><', xml.strip())

            pid = brain.add_pattern(
                title=tpl["title"],
                description=tpl["desc"],
                xml_fragment=xml,
                tags=tpl["tags"],
                source="seed"
            )
            print(f"✅ {pid}")
            added += 1
        except Exception as e:
            print(f"❌ {e}")
            errors.append(tpl["title"])

    after = brain.get_stats()["patterns_count"]
    print(f"\n{'='*50}")
    print(f"📊 Résultat : {added} patterns ajoutés sur {len(TEMPLATES)}")
    print(f"📈 ChromaDB : {before} → {after} patterns")
    if errors:
        print(f"⚠️  Erreurs : {', '.join(errors)}")


if __name__ == "__main__":
    seed()