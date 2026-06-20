#!/usr/bin/env python3
"""
🧠 Smart MCP Server
Serveur MCP qui orchestre le pipeline complet : 
phrase → classification → RAG → cascade LLM → draw.io → feedback → apprentissage

Usage: python smart_mcp_server.py
Lancer en arrière-plan, Hermes le découvre automatiquement.
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ── Ajouter le projet au path ──────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from brain.rag import get_brain, DiagramPattern
from brain.seed_patterns import seed as seed_brain_data
from models.llm_client import get_llm, LLMClient
from mcp_client.drawio import get_drawio, DrawioMCPClient

# ── Configuration ──────────────────────────────────────
BUDGET_CENT = int(os.getenv("SMART_MCP_BUDGET_CENT", "500"))      # 5€ max
COST_FILE = Path(os.getenv("SMART_MCP_COST_FILE", "~/.smart-mcp/cost_tracker.json")).expanduser()
PREFER_LOCAL = os.getenv("SMART_MCP_PREFER_LOCAL", "true").lower() == "true"
DRAWIO_MCP_PATH = os.getenv(
    "DRAWIO_MCP_PATH",
    str(ROOT.parent / "mcp-server-patched/dist/index.js")
)

# ── MCP Server ─────────────────────────────────────────
mcp = FastMCP(
    "smart-mcp",
    instructions="🧠 Smart MCP — Orchestrateur de diagrammes draw.io avec RAG + cascade LLM + budget 5€"
)

# ── Budget tracker ─────────────────────────────────────

def _load_cost() -> dict:
    COST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if COST_FILE.exists():
        try:
            return json.loads(COST_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"total_cent": 0, "calls": 0, "last_reset": time.strftime("%Y-%m-%d")}

def _save_cost(data: dict):
    COST_FILE.parent.mkdir(parents=True, exist_ok=True)
    COST_FILE.write_text(json.dumps(data, indent=2))

def _check_budget() -> tuple[bool, dict]:
    """Vérifie le budget. Retourne (ok, stats)."""
    data = _load_cost()
    used_cent = data["total_cent"]
    remaining = BUDGET_CENT - used_cent
    ok = remaining > 0
    return ok, {"budget_cent": BUDGET_CENT, "used_cent": used_cent,
                "remaining_cent": remaining, "calls": data["calls"],
                "ok": ok}

def _track_cloud_usage(cent: int = 1):
    """Ajoute un coût cloud estimé. 1 cent = ~1K tokens DeepSeek V4 Flash."""
    data = _load_cost()
    data["total_cent"] += cent
    data["calls"] += 1
    _save_cost(data)

# ── Validation XML ─────────────────────────────────────

def _extract_xml(raw: str) -> str:
    """Extrait le XML draw.io pur d'une réponse LLM, peu importe le formatage."""
    if not raw or not raw.strip():
        return ""

    # Nettoyer les espaces
    cleaned = raw.strip()

    # Cas 1: ```xml ... ``` (et aussi ``` ... ```)
    for marker in ["```xml", "```"]:
        if marker in cleaned:
            parts = cleaned.split(marker, 1)
            if len(parts) > 1:
                after = parts[1].strip()
                # Prendre jusqu'au prochain ```
                end_idx = after.find("```")
                if end_idx != -1:
                    cleaned = after[:end_idx].strip()
                else:
                    cleaned = after.strip()

    # Cas 2: <mxfile> wrapper complet (ou <mxFile>)
    mxfile_pattern = re.search(r'<(mxfile|mxFile)\b', cleaned)
    if mxfile_pattern:
        tag = mxfile_pattern.group(1)
        start = mxfile_pattern.start()
        end_tag = f"</{tag}>"
        if end_tag in cleaned:
            end = cleaned.index(end_tag) + len(end_tag)
            return cleaned[start:end]

    # Cas 3: <diagram> wrapper
    if "<diagram" in cleaned and "</diagram>" in cleaned:
        # Prendre du <diagram> jusqu'à la fin du </mxGraphModel> correspondant
        start = cleaned.index("<diagram")
        if "<mxGraphModel>" in cleaned:
            end = cleaned.rindex("</mxGraphModel>") + len("</mxGraphModel>")
            # Prendre aussi la fin du </diagram> si présent
            diag_end = cleaned.find("</diagram>", end)
            if diag_end != -1:
                end = diag_end + len("</diagram>")
            return cleaned[start:end]

    # Cas 4: <mxGraphModel> brut (avec ou sans attributs)
    if "<mxGraphModel" in cleaned:
        start = cleaned.index("<mxGraphModel")
        end = cleaned.rindex("</mxGraphModel>") + len("</mxGraphModel>")
        return cleaned[start:end]

    # Cas 5: On prend tout ce qui ressemble à du XML
    return cleaned


def _validate_xml(xml_text: str) -> tuple[bool, list[str]]:
    """Valide que le XML est bien un format draw.io acceptable."""
    errors = []
    text = xml_text.strip()

    if not text:
        return False, ["XML vide"]

    # Accepte deux formats : <mxGraphModel> brut (avec ou sans attributs) OU <mxfile> wrapper
    has_mxgraph = "<mxGraphModel" in text
    has_mxfile = ("<mxfile" in text and "</mxfile>" in text) or ("<mxFile" in text and "</mxFile>" in text)

    if not has_mxgraph and not has_mxfile:
        errors.append("Format non reconnu: ni <mxGraphModel> ni <mxfile> présent")

    # Vérifier la présence de cellules root (id=0 et id=1)
    if has_mxgraph:
        cell_pattern = re.findall(r'<mxCell\s+id="([^"]+)"', text)
        if len(cell_pattern) < 2:
            errors.append("Moins de 2 cellules mxCell (id=0 et id=1 requises)")
    elif has_mxfile:
        cell_pattern = re.findall(r'<mxCell\s+id="([^"]+)"', text)
        if len(cell_pattern) < 1:
            errors.append("Aucune cellule mxCell trouvée dans le fichier")
        # Format compact accepté : <diagram> → <mxCell> sans root

    return len(errors) == 0, errors


def _fix_xml_common(xml_text: str) -> str:
    if xml_text is None:
        return None
    fixes = [
        # mxFile → mxfile (normalisation de casse)
        (r"<mxFile\b", "<mxfile"),
        (r"</mxFile>", "</mxfile>"),
        # mxCellId value="X" → mxCell id="X" (modèle fusionne tag + id)
        (r'<mxCellId\s+value="([^"]*)"', r'<mxCell id="\1" value=""'),
        # Fermeture </mxCellId> → </mxCell>
        (r'</mxCellId>', '</mxCell>'),
        # <mxGeometry" as= → <mxGeometry as= (spurious quote avant as)
        (r'<mxGeometry"\s+as=', '<mxGeometry as='),
        # mxCellId= → mxCell id= (modèle oublie l'espace)
        (r"<mxCellId=", "<mxCell id="),
        # mwGeometry → mxGeometry
        ("mwGeometry", "mxGeometry"),
        # mwCell → mxCell
        ("mwCell", "mxCell"),
        # mwFile → mxFile
        ("mwFile", "mxFile"),
        # height="" → height=" (doublons de guillemets)
        (r'=(\"[^\"]*\")(\")', r'=\1'),
        # Valeurs numériques sans guillemets (cas: width=120, mais PAS width="120")
        (r'(?<!=)\b(width)=(\d+)\b(?!\")', r'\1="\2"'),
        (r'(?<!=)\b(height)=(\d+)\b(?!\")', r'\1="\2"'),
        # Farewell " as=" à corriger
        (' as="', '" as="'),
        # Doubles quotes collées: height="60"" → height="60"
        # Requiert AU MOINS 2 quotes pour ne pas toucher les attributs valides
        (r'(=\s*"[^"]*?)("{2,})(?=\s)', lambda m: m.group(1) + '"'),
    ]
    for old, new in fixes:
        try:
            xml_text = re.sub(old, new, xml_text)
        except re.error:
            xml_text = xml_text.replace(old, new)
    # Assigner des IDs aux cellules qui n'en ont pas
    xml_text = _ensure_cell_ids(xml_text)
    return xml_text


def _ensure_cell_ids(xml_text: str) -> str:
    """Assigne des IDs auto-générés aux cellules mxCell qui n'en ont pas.
    Important : le modèle local oublie souvent les id= sur les cellules shapes/edges."""
    existing_ids = set(re.findall(r'<mxCell[^>]*?\sid="([^"]+)"', xml_text))
    next_id = 2
    while str(next_id) in existing_ids:
        next_id += 1

    # Pattern : <mxCell ... (sans id="...") ...>
    # On remplace <mxCell (sans id=) en <mxCell id="N" ...
    def _assign(m):
        nonlocal next_id
        full = m.group(0)
        while str(next_id) in existing_ids:
            next_id += 1
        new_id = str(next_id)
        existing_ids.add(new_id)
        next_id += 1
        return full.replace("<mxCell", f'<mxCell id="{new_id}"')

    xml_text = re.sub(r'<mxCell\b(?!.*?\sid=")', _assign, xml_text)

    # Si la boucle a fonctionné, on doit maintenant aussi relier les edges sans source/target
    # aux bons IDs — mais la validation stricte n'est pas requise pour le rendu draw.io
    return xml_text

# ── Pipeline principal ─────────────────────────────────

@mcp.tool(name="smart_diagram")
def smart_diagram(prompt: str) -> dict:
    """
    Pipeline complet : analyse une phrase → cherche dans RAG → génère diagramme
    → valide → envoie à draw.io → enregistre l'apprentissage.

    Paramètres :
    - prompt : phrase en français décrivant le diagramme souhaité

    Retourne un dict avec status, diagram_url, xml, patterns, classification, cost
    """
    start = time.time()
    result = {
        "status": "started",
        "prompt": prompt,
        "diagram_url": "",
        "xml": "",
        "classification": {},
        "patterns": [],
        "errors": [],
        "timing": {},
        "cost": {},
    }

    try:
        # ── 0. Vérifier budget ──
        budget_ok, cost_info = _check_budget()
        result["cost"] = cost_info
        if not budget_ok:
            result["status"] = "budget_exceeded"
            result["errors"].append(f"Budget dépassé: {cost_info['used_cent']}/{BUDGET_CENT}¢ utilisé")
            return result

        # ── 1. Classifier l'intention ──
        t0 = time.time()
        llm = get_llm()
        classification = llm.classify_intent(prompt)
        result["classification"] = classification
        result["timing"]["classify"] = round(time.time() - t0, 2)

        # ── 2. Chercher dans RAG (selon macro_class) ──
        t0 = time.time()
        brain = get_brain()
        macro_class = classification.get("macro_class", "TABLEAU")
        shapes_needed = classification.get("shapes_needed", [])
        
        patterns = []
        if macro_class == "FORME" and shapes_needed:
            # Chercher chaque forme individuellement dans ChromaDB
            for shape in shapes_needed:
                shape_patterns = brain.search_similar(f"forme shape {shape}", n_results=2, min_score=0.4)
                patterns.extend(shape_patterns)
        else:
            # Chercher les patterns de diagramme structuré
            patterns = brain.search_similar(prompt, n_results=3, min_score=0.5)
        
        # Dédoublement
        seen = set()
        unique_patterns = []
        for p in patterns:
            if p["id"] not in seen:
                seen.add(p["id"])
                unique_patterns.append(p)
        patterns = unique_patterns
        
        result["patterns"] = [{"title": p["title"], "similarity": p["similarity"], "macro_class": macro_class} for p in patterns]
        result["timing"]["rag_search"] = round(time.time() - t0, 2)

        context = ""
        if patterns:
            best = patterns[0]
            context = f"Exemple similaire: {best['title']} (score: {best['similarity']})\n{best['xml'][:500]}"

        # ── 3. Générer XML via LLM (routage intelligent selon complexité) ──
        t0 = time.time()
        used_cloud = False
        complexity = classification.get("complexity", "medium")
        xml_raw = llm.generate(prompt, context=context, complexity=complexity)

        if xml_raw:
            # Extraire le XML pur (```xml, texte avant/après, etc.)
            xml_clean = _extract_xml(xml_raw)

            if not xml_clean:
                result["status"] = "xml_empty"
                result["errors"].append("Extraction XML vide alors que le LLM a répondu")
                result["timing"]["generate"] = round(time.time() - t0, 2)
                return result

            # Corriger les erreurs courantes
            xml_clean = _fix_xml_common(xml_clean)

            # Valider
            valid, errors = _validate_xml(xml_clean)
            result["xml"] = xml_clean

            if not valid:
                # Essayer d'améliorer via cloud
                improved = llm.improve_xml(xml_clean, prompt, "; ".join(errors))
                if improved:
                    # Extraire de nouveau (le cloud rajoute aussi du texte)
                    xml_clean = _extract_xml(improved)
                    xml_clean = _fix_xml_common(xml_clean)
                    result["xml"] = xml_clean
                    used_cloud = True
                    _track_cloud_usage(2)
                    valid, errors = _validate_xml(xml_clean)

            if not valid:
                result["status"] = "xml_invalid"
                result["errors"] = errors
                result["timing"]["generate"] = round(time.time() - t0, 2)
                return result

            result["timing"]["generate"] = round(time.time() - t0, 2)

        else:
            result["status"] = "generation_failed"
            result["errors"].append("Le LLM n'a pas retourné de XML")
            result["timing"]["generate"] = round(time.time() - t0, 2)
            return result

        # Tracker si le cloud a été utilisé
        if used_cloud:
            _track_cloud_usage(1)

        # ── 4. Envoyer à draw.io ──
        t0 = time.time()
        drawio = get_drawio()

        try:
            drawio._initialize()
            drawio.create_new_diagram(xml_clean)
            result["diagram_url"] = "http://192.168.1.100:8080?mcp=smart-mcp"
        except Exception as e:
            result["errors"].append(f"draw.io: {str(e)[:200]}")
            # On peut quand même retourner le XML

        result["timing"]["drawio"] = round(time.time() - t0, 2)

        # ── 5. Apprentissage — enregistrer le pattern ──
        try:
            tags = [classification.get("diagram_type", "generic"),
                    classification.get("type", "unknown"),
                    classification.get("complexity", "simple")]
            brain.add_pattern(
                title=f"Généré: {prompt[:50]}",
                description=prompt,
                xml_fragment=xml_clean,
                tags=tags,
                source="generated"
            )
        except Exception as e:
            result["errors"].append(f"apprentissage: {str(e)[:100]}")

        # ── Succès ──
        result["status"] = "success"
        result["timing"]["total"] = round(time.time() - start, 2)
        return result

    except Exception as e:
        import traceback
        result["status"] = "error"
        result["errors"].append(f"{type(e).__name__}: {str(e)[:300]}")
        result["traceback"] = traceback.format_exc()[-500:]
        result["timing"]["total"] = round(time.time() - start, 2)
        return result


@mcp.tool(name="health")
def health() -> dict:
    """
    Vérifie l'état de tous les composants Smart MCP.

    Retourne un dict avec le statut de : RAG, LLM local, LLM cloud, draw.io, budget
    """
    status = {"status": "checking", "components": {}}

    # RAG
    try:
        brain = get_brain()
        stats = brain.get_stats()
        status["components"]["rag"] = {"status": "ok", "patterns": stats["patterns_count"],
                                        "feedback": stats["feedback_count"]}
    except Exception as e:
        status["components"]["rag"] = {"status": "error", "error": str(e)[:100]}

    # LLM local (Qwen via Ollama)
    try:
        llm = get_llm()
        import httpx
        with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
            test_resp = client.post(
                llm.local.base_url.rstrip("/v1") + "/api/generate",
                json={"model": llm.local.model, "prompt": "dis bonjour", "max_tokens": 10},
                timeout=10
            )
            test_ok = test_resp.status_code == 200
        status["components"]["local_llm"] = {
            "status": "ok" if test_ok else "error",
            "model": llm.local.model,
            "url": llm.local.base_url,
        }
    except Exception as e:
        status["components"]["local_llm"] = {"status": "error", "error": str(e)[:100]}

    # LLM cloud (DeepSeek via OpenRouter)
    try:
        cloud_key = llm.cloud.api_key
        if cloud_key and len(cloud_key) > 10:
            status["components"]["cloud_llm"] = {
                "status": "configured",
                "model": llm.cloud.model,
            }
        else:
            status["components"]["cloud_llm"] = {"status": "not_configured"}
    except Exception as e:
        status["components"]["cloud_llm"] = {"status": "error", "error": str(e)[:100]}

    # Budget
    budget_ok, cost_info = _check_budget()
    status["components"]["budget"] = cost_info

    # Draw.io MCP
    try:
        import subprocess
        proc = subprocess.Popen(
            ["node", DRAWIO_MCP_PATH, "--version"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            out, _ = proc.communicate(timeout=5)
            drawio_ok = proc.returncode == 0
        except subprocess.TimeoutExpired:
            proc.kill()
            drawio_ok = False
        status["components"]["drawio"] = {
            "status": "ok" if drawio_ok else "error",
        }
    except Exception as e:
        status["components"]["drawio"] = {"status": "error", "error": str(e)[:100]}

    status["status"] = "ok"
    return status


@mcp.tool(name="seed_brain")
def seed_brain() -> dict:
    """
    Initialise le cerveau RAG avec des patterns de diagrammes prêts à l'emploi.
    
    Utile au premier lancement pour avoir des exemples de base.
    """
    try:
        before = get_brain().get_stats()["patterns_count"]
        seed_brain_data()
        after = get_brain().get_stats()["patterns_count"]
        return {
            "status": "success",
            "before": before,
            "after": after,
            "added": after - before
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


@mcp.tool(name="track_budget")
def track_budget() -> dict:
    """
    Consulte le budget utilisé et restant.
    
    Utile pour savoir combien de crédits cloud il reste avant la limite de 5€.
    """
    budget_ok, cost_info = _check_budget()
    cost_info["status"] = "ok" if budget_ok else "limit_reached"
    return cost_info


@mcp.tool(name="get_brain_stats")
def get_brain_stats() -> dict:
    """
    Statistiques du cerveau RAG : nombre de patterns, feedbacks, etc.
    """
    try:
        brain = get_brain()
        return {"status": "ok", **brain.get_stats()}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


# ── Point d'entrée ─────────────────────────────────────

if __name__ == "__main__":
    print("🧠 Smart MCP Server — démarrage...")
    print(f"   Budget max: {BUDGET_CENT}¢ ({(BUDGET_CENT/100):.2f}€)")
    print(f"   Préférence locale: {PREFER_LOCAL}")
    print(f"   Draw.io MCP: {DRAWIO_MCP_PATH}")
    print()
    print("   Tools exposées : smart_diagram, health, seed_brain, track_budget, get_brain_stats")
    print()

    # Lancer le serveur MCP sur stdio (Hermes le connecte)
    mcp.run(transport="stdio")
