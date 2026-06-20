"""
🎨 Smart MCP - Seed patterns : formes géométriques pour ChromaDB
Templates de formes individuelles pour le routing macro → RAG
"""

import sys
sys.path.insert(0, "/home/malek/workspace/smart-mcp")

from brain.rag import get_brain

# ── PATTERNS DE FORMES INDIVIDUELLES ──────────────────────────────

SHAPE_PATTERNS = [
    {
        "title": "Carré/Rectangle simple",
        "description": "Carré ou rectangle simple, sans texte. Style rounded=0, remplissage plein.",
        "tags": ["forme", "carre", "rectangle", "carré", "shape", "square", "rect"],
        "xml": """<mxCell id="shape-1" value="" style="rounded=0;fillColor=#FF9999;strokeColor=#CC0000;fontSize=14;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="120" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Rectangle arrondi avec texte",
        "description": "Rectangle avec bords arrondis et texte à l'intérieur. Style rounded=1, fillColor personnalisable.",
        "tags": ["forme", "rectangle", "arrondi", "rounded", "boîte", "box", "shape"],
        "xml": """<mxCell id="box-1" value="Mon Texte" style="rounded=1;fillColor=#4FC3F7;strokeColor=#0288D1;fontSize=14;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Cercle / Ellipse",
        "description": "Cercle ou ellipse. Style ellipse, fillColor, taille symétrique pour un cercle parfait.",
        "tags": ["forme", "cercle", "rond", "ellipse", "circle", "round", "shape"],
        "xml": """<mxCell id="circle-1" value="" style="ellipse;fillColor=#3498DB;strokeColor=#2980B9;fontSize=14;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="120" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Cercle avec texte",
        "description": "Cercle avec texte centré à l'intérieur. width=height pour cercle parfait.",
        "tags": ["forme", "cercle", "rond", "texte", "circle", "label", "shape"],
        "xml": """<mxCell id="cl-1" value="Texte" style="ellipse;fillColor=#3498DB;strokeColor=#2980B9;fontColor=#FFFFFF;fontSize=14;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="120" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Triangle (haut)",
        "description": "Triangle pointant vers le haut. Style shape=triangle, whiteSpace=wrap, html=1.",
        "tags": ["forme", "triangle", "triangulaire", "pyramide", "shape", "tri"],
        "xml": """<mxCell id="tri-1" value="Texte" style="shape=triangle;whiteSpace=wrap;html=1;fillColor=#FF9999;strokeColor=#CC0000;fontColor=#FFFFFF;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="40" y="200" width="160" height="150" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Losange / Diamant",
        "description": "Losange ou diamant, utilisé pour les décisions. Style shape=diamond, whiteSpace=wrap, html=1.",
        "tags": ["forme", "losange", "diamant", "diamond", "decision", "shape"],
        "xml": """<mxCell id="dmd-1" value="Décision" style="shape=diamond;whiteSpace=wrap;html=1;fillColor=#FFF59D;strokeColor=#F57F17;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="120" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Parallélogramme",
        "description": "Parallélogramme, utilisé pour les intrants/extrants. Style shape=parallelogram, whiteSpace=wrap, html=1.",
        "tags": ["forme", "parallelogramme", "parallelogram", "input", "output", "shape"],
        "xml": """<mxCell id="para-1" value="Entrée/Sortie" style="shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#81C784;strokeColor=#388E3C;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Cylindre (base de données)",
        "description": "Cylindre représentant une base de données. Style shape=cylinder, whiteSpace=wrap, html=1.",
        "tags": ["forme", "cylindre", "base", "données", "database", "db", "storage", "shape"],
        "xml": """<mxCell id="cyl-1" value="Base de données" style="shape=cylinder;whiteSpace=wrap;html=1;fillColor=#D7CCC8;strokeColor=#795548;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="80" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Étiquette hexagonale",
        "description": "Hexagone, utilisé pour les processus ou labels. Style shape=hexagon, whiteSpace=wrap, html=1.",
        "tags": ["forme", "hexagone", "hexagon", "process", "label", "shape"],
        "xml": """<mxCell id="hex-1" value="Processus" style="shape=hexagon;whiteSpace=wrap;html=1;fillColor=#B39DDB;strokeColor=#673AB7;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="140" height="80" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Flèche directionnelle simple",
        "description": "Flèche (edge) entre deux formes. Style endArrow=classic, edgeStyle=orthogonalEdgeStyle.",
        "tags": ["forme", "fleche", "flèche", "arrow", "edge", "connection", "lien"],
        "xml": """<mxCell id="edge-1" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="src" target="tgt">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>"""
    },
    {
        "title": "Flèche avec texte",
        "description": "Flèche avec label texte. Style endArrow=classic, edgeStyle=orthogonalEdgeStyle, fontSize.",
        "tags": ["forme", "fleche", "flèche", "label", "edge", "connection", "lien"],
        "xml": """<mxCell id="edge-2" value="Label" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;fontSize=12;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="src" target="tgt">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>"""
    },
    # ── PALETTES DE COULEURS ──
    {
        "title": "Palette de couleurs - Rouge",
        "description": "Palette rouge pour formes draw.io : fill=#FF9999, stroke=#CC0000, font=#FFFFFF",
        "tags": ["couleur", "palette", "red", "rouge", "color"],
        "xml": """<!-- Rouge: fillColor=#FF9999 strokeColor=#CC0000 fontColor=#FFFFFF -->"""
    },
    {
        "title": "Palette de couleurs - Bleu",
        "description": "Palette bleue pour formes draw.io : fill=#3498DB, stroke=#2980B9, font=#FFFFFF",
        "tags": ["couleur", "palette", "blue", "bleu", "color"],
        "xml": """<!-- Bleu: fillColor=#3498DB strokeColor=#2980B9 fontColor=#FFFFFF -->"""
    },
    {
        "title": "Palette de couleurs - Vert",
        "description": "Palette verte pour formes draw.io : fill=#81C784, stroke=#388E3C, font=#FFFFFF",
        "tags": ["couleur", "palette", "green", "vert", "color"],
        "xml": """<!-- Vert: fillColor=#81C784 strokeColor=#388E3C fontColor=#FFFFFF -->"""
    },
    {
        "title": "Palette de couleurs - Jaune",
        "description": "Palette jaune pour formes draw.io : fill=#FFF59D, stroke=#F57F17, font=#333333",
        "tags": ["couleur", "palette", "yellow", "jaune", "color"],
        "xml": """<!-- Jaune: fillColor=#FFF59D strokeColor=#F57F17 fontColor=#333333 -->"""
    },
]


def seed_shapes():
    """Seede les templates de formes dans ChromaDB"""
    b = get_brain()
    before = b.get_stats()["patterns_count"]
    print(f"🎨 Patterns existants: {before}")
    
    for p in SHAPE_PATTERNS:
        pid = b.add_pattern(
            title=p["title"],
            description=p["description"],
            xml_fragment=p["xml"],
            tags=p["tags"],
            source="shape_template"
        )
        print(f"  ✅ {p['title']} -> {pid}")
    
    after = b.get_stats()["patterns_count"]
    print(f"\n📊 {after - before} formes ajoutées. Total: {after}")


# Alias pour compatibilité
SHAPE_TEMPLATES = {}
for p in SHAPE_PATTERNS:
    name = p["title"].lower().split()[0]
    SHAPE_TEMPLATES[name] = p
STYLES = {
    "default": "rounded=1;fillColor=#4FC3F7;strokeColor=#0288D1;fontSize=14;whiteSpace=wrap;html=1;",
    "rouge": "rounded=1;fillColor=#FF9999;strokeColor=#CC0000;fontSize=14;whiteSpace=wrap;html=1;",
    "bleu": "rounded=1;fillColor=#3498DB;strokeColor=#2980B9;fontSize=14;whiteSpace=wrap;html=1;",
    "vert": "rounded=1;fillColor=#81C784;strokeColor=#388E3C;fontSize=14;whiteSpace=wrap;html=1;",
}

def create_pattern_xml(shape_type: str, color: str = "default", width: int = 100, height: int = 60) -> str:
    """Génère un XML mxCell pour un pattern donné"""
    return f"""<mxCell id="pattern-1" value="{shape_type}" style="rounded=1;fillColor=#4FC3F7;strokeColor=#0288D1;fontSize=14;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="{width}" height="{height}" as="geometry"/>
</mxCell>"""

if __name__ == "__main__":
    seed_shapes()
