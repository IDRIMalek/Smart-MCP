#!/usr/bin/env python3
"""
🧠 Smart MCP — Mindmap Agent Loop
Agent interactif qui crée/édite des mindmaps via draw.io MCP tools.
Principe : une opération atomique à la fois, feedback visuel après chaque étape.

Le LLM planifie la structure, le MindmapAgent exécute sur le canvas draw.io.
Pas de génération XML en une shot — chaque nœud est ajouté individuellement.
"""

import json
import math
import os
import re
import time
from typing import Optional, Any

from mcp_client.drawio import get_drawio, DrawioMCPClient

# ─── Persistance ────────────────────────────────────────────────────
SAVE_DIR = "/home/malek/.smart-mcp"
SAVE_PATH = "/home/malek/.smart-mcp/mindmap_state.json"


# ─── Constantes de layout ─────────────────────────────────────────────

# Angles prédéfinis pour les branches de mindmap (en degrés)
# Le root est au centre, les branches rayonnent
LAYOUT_RIGHT = [0, -25, 25, -50, 50, -75, 75]       # arbre vers la droite
LAYOUT_LEFT = [180, 155, 205, 130, 230, 105, 255]    # arbre vers la gauche
LAYOUT_RADIAL = [0, 60, 120, 180, 240, 300]           # étoile 6 branches

# Palette d'expansion pour sous-branches
COLOR_PALETTE = [
    "#2196F3",  # bleu
    "#FF9800",  # orange
    "#9C27B0",  # violet
    "#00BCD4",  # cyan
    "#E91E63",  # rose
    "#4CAF50",  # vert
    "#FF5722",  # rouge-orangé
    "#607D8B",  # gris-bleu
]

ROOT_COLOR = "#4CAF50"    # vert
ROOT_WIDTH = 140
ROOT_HEIGHT = 80
NODE_WIDTH = 130
NODE_HEIGHT = 55
BRANCH_DISTANCE = 170     # distance entre parent et enfant
SUBBRANCH_DISTANCE = 150  # distance pour les niveaux suivants


# ─── MindmapAgent ────────────────────────────────────────────────────

class MindmapError(Exception):
    pass


class MindmapAgent:
    """
    Agent spécialisé pour créer/éditer des mindmaps via le MCP draw.io.

    Attributs d'état (vecteur interne) :
        nodes: dict[str, dict] — chaque nœud : {label, x, y, color, parent, level}
        pages: dict — état des pages draw.io
    """

    def __init__(self):
        self.drawio: DrawioMCPClient = get_drawio()
        self.nodes: dict[str, dict] = {}        # id -> {label, x, y, color, parent, level}
        self.root_id: Optional[str] = None
        self.page_name: str = "Page-1"
        self._next_id: int = 2
        self._session_started = False

    # ─── Session management ────────────────────────────────────────

    def ensure_session(self) -> bool:
        """Démarre une session draw.io si pas déjà fait"""
        if self._session_started and self.drawio.session_active:
            return True
        try:
            self.drawio._initialize()
            ok = self.drawio.start_session()
            if ok:
                self._session_started = True
                time.sleep(1)  # laisser le browser se stabiliser
            return ok
        except Exception as e:
            raise MindmapError(f"Impossible de démarrer draw.io: {e}")

    def reset_state(self):
        """Reset l'état interne (nouveau diagramme)"""
        self.nodes = {}
        self.root_id = None
        self._next_id = 2

    def _new_id(self) -> str:
        """Génère un ID unique pour une nouvelle cellule"""
        nid = str(self._next_id)
        self._next_id += 1
        return nid

    # ─── Opérations atomiques ─────────────────────────────────────

    def add_root(self, label: str) -> str:
        """
        Ajoute le nœud racine au centre du canvas.
        Retourne l'ID du nouveau root.
        """
        self.reset_state()
        root_id = self._new_id()

        # Position centrale
        cx, cy = 350, 250

        xml = (
            f'<mxCell id="{root_id}" value="{label}" '
            f'style="ellipse;whiteSpace=wrap;html=1;'
            f'fillColor={ROOT_COLOR};fontColor=#FFFFFF;fontSize=16;fontStyle=1;'
            f'" vertex="1" parent="1">'
            f'<mxGeometry x="{cx}" y="{cy}" width="{ROOT_WIDTH}" height="{ROOT_HEIGHT}" as="geometry"/>'
            f'</mxCell>'
        )

        # Créer le diagramme avec juste le root
        diagram_xml = (
            f'<mxGraphModel>'
            f'<root>'
            f'<mxCell id="0"/>'
            f'<mxCell id="1" parent="0"/>'
            f'{xml}'
            f'</root>'
            f'</mxGraphModel>'
        )

        ok = self.drawio.create_new_diagram(diagram_xml)
        if not ok:
            raise MindmapError("Échec de création du root sur draw.io")

        self.root_id = root_id
        self.nodes[root_id] = {
            "label": label,
            "x": cx,
            "y": cy,
            "color": ROOT_COLOR,
            "parent": None,
            "level": 0,
        }
        self.save_state()  # ⟵ persistant
        return root_id

    def add_node(self, parent_id: str, label: str,
                 angle: int | None = None, color: str | None = None,
                 sources: list[str] | None = None) -> str:
        """
        Ajoute un nœud enfant connecté à parent_id.

        Paramètres :
            parent_id : ID du parent
            label     : texte du nœud
            angle     : angle en degrés (0=est, 90=sud, etc.)
                       Si None, calculé automatiquement
            color     : couleur du nœud (hex). Si None, pris de la palette
            sources   : IDs additionnels à connecter (pour nœuds multi-parents)

        Retourne l'ID du nouveau nœud.
        """
        if parent_id not in self.nodes:
            raise MindmapError(f"Parent {parent_id} inconnu")

        parent = self.nodes[parent_id]
        node_id = self._new_id()

        # Angle automatique si non fourni
        if angle is None:
            angle = self._pick_angle(parent_id)

        # Couleur automatique si non fournie
        if color is None:
            color = self._pick_color(parent_id)

        # Calculer la position
        level = parent["level"] + 1
        dist = BRANCH_DISTANCE if level == 1 else SUBBRANCH_DISTANCE
        angle_rad = math.radians(angle)

        x = parent["x"] + parent.get("width", ROOT_WIDTH if level == 1 else NODE_WIDTH) / 2 + 30
        # Calculer y en fonction de l'angle
        y_offset = dist * math.sin(angle_rad)
        # Pour l'axe x, on utilise la distance horizontale
        x_offset = dist * math.cos(angle_rad)

        nx = parent["x"] + x_offset
        ny = parent["y"] + y_offset

        # Si branche vers la gauche (angle ~180°), inverser
        if 90 < angle < 270:
            nx = parent["x"] - NODE_WIDTH - abs(x_offset)

        # Ajuster pour éviter les collisions (si trop proche d'un nœud existant)
        nx, ny = self._avoid_collisions(nx, ny, NODE_WIDTH, NODE_HEIGHT)

        w = NODE_WIDTH
        h = NODE_HEIGHT

        xml = (
            f'<mxCell id="{node_id}" value="{label}" '
            f'style="rounded=1;whiteSpace=wrap;html=1;'
            f'fillColor={color};fontColor=#FFFFFF;fontSize=13;'
            f'" vertex="1" parent="1">'
            f'<mxGeometry x="{nx}" y="{ny}" width="{w}" height="{h}" as="geometry"/>'
            f'</mxCell>'
        )

        ok = self.drawio.edit_diagram(self.page_name, [
            {"operation": "add", "cell_id": node_id, "new_xml": xml}
        ])
        if not ok:
            raise MindmapError(f"Échec d'ajout du nœud {label} sur draw.io")

        # Connecter au parent
        edge_id = self._new_id()
        self._connect(edge_id, parent_id, node_id)

        # Connecter aux sources additionnelles
        if sources:
            for src in sources:
                if src in self.nodes:
                    extra_edge = self._new_id()
                    self._connect(extra_edge, src, node_id)

        self.nodes[node_id] = {
            "label": label,
            "x": nx,
            "y": ny,
            "color": color,
            "parent": parent_id,
            "level": level,
        }
        self.save_state()  # ⟵ persistant
        return node_id

    def _connect(self, edge_id: str, source_id: str, target_id: str):
        """Ajoute une arête entre source et target"""
        edge_xml = (
            f'<mxCell id="{edge_id}" '
            f'style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;'
            f'jettySize=auto;html=1;strokeColor=#666666;strokeWidth=2;" '
            f'edge="1" parent="1" source="{source_id}" target="{target_id}">'
            f'<mxGeometry relative="1" as="geometry"/>'
            f'</mxCell>'
        )
        self.drawio.edit_diagram(self.page_name, [
            {"operation": "add", "cell_id": edge_id, "new_xml": edge_xml}
        ])

    def update_node(self, node_id: str, **kwargs) -> bool:
        """
        Modifie les propriétés d'un nœud.
        kwargs : label, color, x, y
        """
        if node_id not in self.nodes:
            raise MindmapError(f"Nœud {node_id} inconnu")

        node = self.nodes[node_id]
        for key, val in kwargs.items():
            node[key] = val

        label = node["label"]
        color = node["color"]
        x = node.get("x", 100)
        y = node.get("y", 100)
        w = ROOT_WIDTH if node["level"] == 0 else NODE_WIDTH
        h = ROOT_HEIGHT if node["level"] == 0 else NODE_HEIGHT
        style_shape = "ellipse" if node["level"] == 0 else "rounded=1"
        fs = 16 if node["level"] == 0 else 13
        fb = "1" if node["level"] == 0 else "0"

        if node["level"] == 0:
            style = f'ellipse;whiteSpace=wrap;html=1;fillColor={color};fontColor=#FFFFFF;fontSize={fs};fontStyle={fb}'
        else:
            style = f'rounded=1;whiteSpace=wrap;html=1;fillColor={color};fontColor=#FFFFFF;fontSize={fs}'

        xml = (
            f'<mxCell id="{node_id}" value="{label}" '
            f'style="{style}" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            f'</mxCell>'
        )

        ok = self.drawio.edit_diagram(self.page_name, [
            {"operation": "update", "cell_id": node_id, "new_xml": xml}
        ])
        if ok:
            self.save_state()  # ⟵ persistant
        return ok

    def delete_node(self, node_id: str) -> bool:
        """Supprime un nœud et ses connexions"""
        if node_id not in self.nodes:
            raise MindmapError(f"Nœud {node_id} inconnu")
        if node_id == self.root_id:
            raise MindmapError("Impossible de supprimer le root")

        # Supprimer aussi les enfants (récursivement)
        children = [nid for nid, n in self.nodes.items()
                    if n.get("parent") == node_id]
        for cid in children:
            self.delete_node(cid)

        ok = self.drawio.edit_diagram(self.page_name, [
            {"operation": "delete", "cell_id": node_id}
        ])
        if ok:
            del self.nodes[node_id]
            self.save_state()  # ⟵ persistant
        return ok

    def get_canvas_state(self) -> str:
        """Retourne une description textuelle de l'état courant du canvas"""
        if not self.nodes:
            return "Canvas vide"

        lines = [f"Canvas: {len(self.nodes)} nœuds"]
        for nid, n in self.nodes.items():
            parent_label = self.nodes.get(n["parent"], {}).get("label", "—") if n["parent"] else "ROOT"
            lines.append(
                f"  [{nid}] {n['label']} ({n['color']}) "
                f"→ parent: {parent_label}, "
                f"pos=({n['x']:.0f},{n['y']:.0f})"
            )
        return "\n".join(lines)

    def get_node_by_label(self, label: str) -> Optional[str]:
        """Trouve un nœud par son label (insensible à la casse)"""
        label_lower = label.lower().strip()
        for nid, n in self.nodes.items():
            if n["label"].lower() == label_lower:
                return nid
        # Fuzzy : si pas exact, cherche le plus proche
        matches = [(nid, n) for nid, n in self.nodes.items()
                   if label_lower in n["label"].lower()]
        if matches:
            return matches[0][0]
        return None

    # ─── Méthodes privées ─────────────────────────────────────────

    def _pick_angle(self, parent_id: str) -> int:
        """Choisit un angle pour un nouvel enfant en évitant les collisions"""
        parent = self.nodes[parent_id]
        existing = [
            self.nodes[cid]["y"] for cid, cn in self.nodes.items()
            if cn.get("parent") == parent_id and cid != parent_id
        ]

        if parent["level"] == 0:
            # Root : gauche ou droite selon le nombre d'enfants
            angles = LAYOUT_RIGHT
        else:
            # Sous-branches : répartir harmonieusement
            angles = LAYOUT_RIGHT[:4] + LAYOUT_LEFT[:3]

        # Éviter les angles déjà très proches en y
        if existing:
            base_y = parent["y"]
            for angle in angles:
                y_candidate = base_y + BRANCH_DISTANCE * math.sin(math.radians(angle))
                if not any(abs(y_candidate - ey) < 50 for ey in existing):
                    return angle
        return angles[len(existing) % len(angles)]

    def _pick_color(self, parent_id: str) -> str:
        """Choisit une couleur pour un nouvel enfant"""
        parent = self.nodes[parent_id]
        if parent["level"] == 0:
            # Palettes distinctes par niveau
            level = len([n for n in self.nodes.values() if n.get("parent") == parent_id])
            return COLOR_PALETTE[level % len(COLOR_PALETTE)]
        else:
            # Sous-branches : variante plus pâle ou même couleur
            return "#90CAF9"  # bleu clair par défaut

    def _avoid_collisions(self, x: float, y: float, w: float, h: float) -> tuple[float, float]:
        """Décale légèrement pour éviter les chevauchements avec les nœuds existants"""
        margin = 20
        for nid, n in self.nodes.items():
            nx, ny = n["x"], n["y"]
            nw = ROOT_WIDTH if n["level"] == 0 else NODE_WIDTH
            nh = ROOT_HEIGHT if n["level"] == 0 else NODE_HEIGHT
            # Vérifier chevauchement
            if abs(x - nx) < (w + nw) / 2 + margin and abs(y - ny) < (h + nh) / 2 + margin:
                # Décaler en y
                y += nh + margin
        return x, y

    def get_diagram_xml(self) -> Optional[str]:
        """Récupère le XML du draw.io (pour déboguer ou sauvegarder)"""
        return self.drawio.get_diagram()

    # ─── Persistance ─────────────────────────────────────────────

    def save_state(self):
        """Sauvegarde l'état du mindmap sur disque (persistant entre sessions)"""
        os.makedirs(SAVE_DIR, exist_ok=True)
        state = {
            "nodes": self.nodes,
            "root_id": self.root_id,
            "page_name": self.page_name,
            "_next_id": self._next_id,
        }
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[MindmapAgent] ⚠️ Échec save_state: {e}")

    def load_state(self) -> bool:
        """Restaure l'état depuis le disque. Retourne True si réussi."""
        if not os.path.exists(SAVE_PATH):
            return False
        try:
            with open(SAVE_PATH) as f:
                state = json.load(f)
            self.nodes = state.get("nodes", {})
            self.root_id = state.get("root_id")
            self.page_name = state.get("page_name", "Page-1")
            self._next_id = state.get("_next_id", 2)
            print(f"[MindmapAgent] ✅ État restauré: {len(self.nodes)} nœuds")
            return True
        except Exception as e:
            print(f"[MindmapAgent] ⚠️ Échec load_state: {e}")
            return False

    def clear_saved_state(self):
        """Supprime l'état sauvegardé (recommencer à zéro)"""
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
        self.reset_state()
        print("[MindmapAgent] 🧹 État effacé")


# ─── Agent Loop: plan → exécute ─────────────────────────────────────

class MindmapAgentLoop:
    """
    Orchestrateur qui utilise LLM + MindmapAgent.
    Le LLM planifie, l'agent exécute, le canvas est l'état.
    """

    def __init__(self, debug: bool = False):
        self.agent = MindmapAgent()
        self.llm = None  # lazy init
        self.debug = debug
        self.history: list[dict] = []  # historique des opérations
        # Auto-restore de l'état persistant
        restored = self.agent.load_state()
        if restored:
            print(f"[MindmapAgentLoop] ✅ State restauré: {len(self.agent.nodes)} nœuds")

    def _get_llm(self):
        """Lazy init du LLM (évite l'import circulaire)"""
        if self.llm is None:
            from models.llm_client import get_llm
            self.llm = get_llm()
        return self.llm

    def create_mindmap(self, prompt: str) -> dict:
        """
        Crée une mindmap complète depuis une phrase utilisateur.

        Pipeline :
        1. LLM planifie la structure (root, branches, sous-branches)
        2. Agent exécute chaque nœud un par un
        3. Retourne le résultat
        """
        llm = self._get_llm()

        # ── 1. LLM planifie ──
        plan = self._plan_structure(prompt)
        if self.debug:
            print(f"[MindmapAgent] Plan: {json.dumps(plan, indent=2)}")

        self.history = []

        # ── 2. Agent exécute ──
        try:
            self.agent.ensure_session()

            # Root
            root_id = self.agent.add_root(plan.get("root", "Mindmap"))
            self.history.append({"action": "add_root", "id": root_id, "label": plan.get("root", "Mindmap")})

            # Branches niveau 1
            for i, branch in enumerate(plan.get("branches", [])):
                angle = branch.get("angle", LAYOUT_RIGHT[i % len(LAYOUT_RIGHT)])
                nid = self.agent.add_node(
                    parent_id=root_id,
                    label=branch["label"],
                    angle=angle,
                    color=branch.get("color", COLOR_PALETTE[i % len(COLOR_PALETTE)]),
                )
                self.history.append({"action": "add_branch", "id": nid, "label": branch["label"]})

                # Sous-branches
                for j, sub in enumerate(branch.get("children", [])):
                    sub_angle = angle + (-15 if j % 2 == 0 else 15)
                    sub_id = self.agent.add_node(
                        parent_id=nid,
                        label=sub["label"],
                        angle=sub_angle,
                        color="#90CAF9",  # bleu clair
                    )
                    self.history.append({"action": "add_sub", "id": sub_id, "label": sub["label"]})

            state = self.agent.get_canvas_state()
            return {
                "status": "success",
                "operations": len(self.history),
                "nodes": len(self.agent.nodes),
                "history": self.history,
                "canvas": state,
            }

        except MindmapError as e:
            return {"status": "error", "error": str(e), "history": self.history}
        except Exception as e:
            return {"status": "error", "error": f"{type(e).__name__}: {str(e)[:200]}", "history": self.history}

    def edit_mindmap(self, prompt: str) -> dict:
        """
        Édite une mindmap existante.

        Pipeline :
        1. LLM lit l'état du canvas
        2. LLM décide quoi faire (add / update_color / delete / move)
        3. Agent exécute
        """
        llm = self._get_llm()

        # Vérifier qu'il y a bien un canvas
        if not self.agent.nodes:
            return {"status": "error", "error": "Canvas vide. Créez d'abord une mindmap avec create_mindmap"}

        canvas_state = self.agent.get_canvas_state()

        # LLM décide de l'opération
        operation = self._classify_edit(prompt, canvas_state)
        if self.debug:
            print(f"[MindmapAgent] Edit operation: {json.dumps(operation, indent=2)}")

        if "error" in operation:
            return {"status": "error", "error": operation["error"]}

        try:
            action = operation["action"]

            if action == "add":
                parent_id = operation.get("parent_id", self.agent.root_id)
                if parent_id not in self.agent.nodes:
                    parent_id = self.agent.root_id
                nid = self.agent.add_node(
                    parent_id=parent_id,
                    label=operation["label"],
                    angle=operation.get("angle"),
                    color=operation.get("color"),
                )
                self.history.append({"action": "add", "id": nid, "label": operation["label"]})
                return {"status": "success", "action": "add", "id": nid, "label": operation["label"]}

            elif action == "update_color":
                node_id = operation.get("node_id")
                if not node_id:
                    # Chercher par label
                    node_id = self.agent.get_node_by_label(operation.get("label", ""))
                if not node_id:
                    return {"status": "error", "error": f"Nœud '{operation.get('label')}' introuvable"}
                ok = self.agent.update_node(node_id, color=operation["color"])
                self.history.append({"action": "update_color", "id": node_id, "color": operation["color"]})
                return {"status": "success" if ok else "error", "action": "update_color", "id": node_id}

            elif action == "delete":
                node_id = operation.get("node_id")
                if not node_id:
                    node_id = self.agent.get_node_by_label(operation.get("label", ""))
                if not node_id:
                    return {"status": "error", "error": f"Nœud '{operation.get('label')}' introuvable"}
                ok = self.agent.delete_node(node_id)
                self.history.append({"action": "delete", "id": node_id})
                return {"status": "success" if ok else "error", "action": "delete"}

            elif action == "update_label":
                node_id = operation.get("node_id")
                if not node_id:
                    node_id = self.agent.get_node_by_label(operation.get("label", ""))
                if not node_id:
                    return {"status": "error", "error": f"Nœud introuvable"}
                ok = self.agent.update_node(node_id, label=operation["new_label"])
                self.history.append({"action": "update_label", "id": node_id, "new_label": operation["new_label"]})
                return {"status": "success" if ok else "error", "action": "update_label"}

            else:
                return {"status": "error", "error": f"Action inconnue: {action}"}

        except (MindmapError, Exception) as e:
            return {"status": "error", "error": str(e)[:300]}

    def _plan_structure(self, prompt: str) -> dict:
        """
        Utilise le LLM planner pour extraire la structure de la mindmap.
        Retourne : {root: str, branches: [{label, color?, children: [{label}]}]}
        """
        llm = self._get_llm()

        plan_prompt = """Tu es un architecte de mindmaps. Analyse la demande suivante et planifie la structure.

RÈGLES :
- Le root est le sujet central (1 seul)
- Les branches niveau 1 sont les grandes catégories (max 5-7)
- Les sous-branches sont des détails (max 3-4 par branche)
- Chaque nœud a un label COURT (1-4 mots)
- Donne des angles suggestifs (0=est, -90=nord, 90=sud, ±180=ouest)
- Les couleurs : blue, orange, purple, cyan, pink, green, red, grey

DEMANDE : {query}

Répond UNIQUEMENT au format JSON (pas de texte avant/après) :
{{
  "root": "sujet central",
  "branches": [
    {{
      "label": "catégorie",
      "color": "#hex",
      "angle": degrés,
      "children": [
        {{"label": "sous-catégorie"}},
        {{"label": "..."}}
      ]
    }}
  ]
}}"""

        response = llm._call(llm.planner,
            "Tu es un architecte de mindmaps. Réponds UNIQUEMENT en JSON valide.",
            plan_prompt.format(query=prompt))

        if not response:
            return {"root": "Mindmap", "branches": []}

        # Extraire le JSON de la réponse
        try:
            # Chercher un bloc JSON
            json_match = re.search(r'\{\s*.*\}', response or "", re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"root": "Mindmap", "branches": []}
        except json.JSONDecodeError:
            # Fallback : structure minimale
            return {
                "root": prompt.split()[0] if prompt else "Mindmap",
                "branches": [{"label": prompt, "children": []}],
            }

    def _classify_edit(self, prompt: str, canvas_state: str) -> dict:
        """
        Utilise le GENERATOR (Gemma 4B — rapide) pour classifier l'intention d'édition.
        Retourne : {action, label, color, parent_id, ...}
        """
        llm = self._get_llm()

        # Compacter l'état : juste les labels + relations (pas les positions)
        compact = "Nœuds actuels :\n"
        for line in canvas_state.split("\n"):
            if "[" in line and "]" in line:
                # Extraire: [N] label (#color) → parent: parent_label
                parts = line.split("→")
                node_part = parts[0].strip() if parts else line
                parent_part = parts[1].strip() if len(parts) > 1 else ""
                # Extract label
                if "]" in node_part:
                    after_bracket = node_part.split("]", 1)[1].strip()
                    label = after_bracket.split("(")[0].strip() if "(" in after_bracket else after_bracket
                    compact += f"  • {label}"
                    if parent_part and "ROOT" not in parent_part:
                        compact += f" (fils de {parent_part.replace('parent:','').strip()})"
                    compact += "\n"

        edit_prompt = f"""Décide l'opération sur la mindmap.

Nœuds :\n{compact}
Demande : {prompt}

Actions :
- add -> {{"action":"add","label":"...","parent":"nom parent","color":"#hex"}}
- update_color -> {{"action":"update_color","label":"nom","color":"#hex"}}
- delete -> {{"action":"delete","label":"nom"}}
- update_label -> {{"action":"update_label","label":"ancien","new_label":"nouveau"}}

Couleurs: rouge #F44336, vert #4CAF50, bleu #2196F3, orange #FF9800, violet #9C27B0, jaune #FFC107, cyan #00BCD4

JSON seulement."""

        response = llm._call(llm.generator,
            "Tu es un assistant mindmap. JSON uniquement.",
            edit_prompt)

        if not response:
            return {"error": "Pas de réponse du LLM"}

        try:
            json_match = re.search(r'\{\s*.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": f"Pas de JSON: {response[:80]}"}
        except json.JSONDecodeError:
            return {"error": f"JSON invalide: {response[:80]}"}

    def get_canvas_text(self) -> str:
        """Retourne l'état lisible du canvas"""
        return self.agent.get_canvas_state()


# ─── Fonctions d'accès (singleton) ──────────────────────────────────

_agent_loop: Optional[MindmapAgentLoop] = None


def get_agent(debug: bool = False) -> MindmapAgentLoop:
    global _agent_loop
    if _agent_loop is None:
        _agent_loop = MindmapAgentLoop(debug=debug)
    return _agent_loop
