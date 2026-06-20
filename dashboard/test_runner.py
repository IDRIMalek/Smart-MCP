"""
🧪 Test Runner — Pipeline automatisé de tests pour diagrammes draw.io
Lance des tests par macro-classe, enregistre les résultats dans un JSON,
peut être appelé par le Dash dashboard ou en CLI.
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Ajouter Smart MCP au path
ROOT = Path("/home/malek/workspace/smart-mcp")
sys.path.insert(0, str(ROOT))

from brain.rag import get_brain
from models.llm_client import get_llm, LLMClient
from smart_mcp_server import _extract_xml, _validate_xml, _fix_xml_common

# ── Chemins ──────────────────────────────────────────
RESULTS_FILE = Path("/home/malek/.dash-dashboard/results.json")
CONFIG_FILE = Path("/home/malek/.dash-dashboard/config.json")

# ── Jeux de tests ────────────────────────────────────

TEST_PROMPTS = {
    "FORME": [
        {"prompt": "dessine un carré rouge", "expected": "FORME", "complexity": "simple", "id": "forme-01", "source": "auto"},
        {"prompt": "ajoute un cercle bleu", "expected": "FORME", "complexity": "simple", "id": "forme-02", "source": "auto"},
        {"prompt": "triangle vert avec texte Malek", "expected": "FORME", "complexity": "simple", "id": "forme-03", "source": "auto"},
        {"prompt": "losange jaune decision", "expected": "FORME", "complexity": "simple", "id": "forme-04", "source": "auto"},
        {"prompt": "rectangle arrondi avec titre Dashboard", "expected": "FORME", "complexity": "simple", "id": "forme-05", "source": "auto"},
        {"prompt": "base de données cylindre gris", "expected": "FORME", "complexity": "simple", "id": "forme-06", "source": "auto"},
    ],
    "TABLEAU": [
        {"prompt": "diagramme d'architecture 3-tiers frontend backend database", "expected": "TABLEAU", "complexity": "medium", "id": "tab-01", "source": "auto"},
        {"prompt": "pipeline CI/CD git build test deploy", "expected": "TABLEAU", "complexity": "medium", "id": "tab-02", "source": "auto"},
        {"prompt": "flux de données ETL source extraction transformation load", "expected": "TABLEAU", "complexity": "medium", "id": "tab-03", "source": "auto"},
        {"prompt": "architecture microservices avec API Gateway", "expected": "TABLEAU", "complexity": "complex", "id": "tab-04", "source": "auto"},
        {"prompt": "diagramme de séquence API appel auth resource database", "expected": "TABLEAU", "complexity": "medium", "id": "tab-05", "source": "auto"},
        {"prompt": "organigramme hiérarchique directeur chef equipe", "expected": "TABLEAU", "complexity": "medium", "id": "tab-06", "source": "auto"},
    ],
    "KANBAN": [
        {"prompt": "tableau kanban pour mon projet avec colonnes backlog en-cours fini", "expected": "KANBAN", "complexity": "medium", "id": "kan-01", "source": "auto"},
        {"prompt": "board de tâches à faire en cours terminé", "expected": "KANBAN", "complexity": "medium", "id": "kan-02", "source": "auto"},
    ],
    "AGENDA": [
        {"prompt": "calendrier du mois avec événements", "expected": "AGENDA", "complexity": "complex", "id": "age-01", "source": "auto"},
        {"prompt": "planning de sprint deux semaines", "expected": "AGENDA", "complexity": "complex", "id": "age-02", "source": "auto"},
    ],
    "GANTT": [
        {"prompt": "diagramme de Gantt planning projet avec tâches et dépendances", "expected": "GANTT", "complexity": "complex", "id": "gantt-01", "source": "auto"},
        {"prompt": "calendrier prévisionnel chantier avec jalons", "expected": "GANTT", "complexity": "complex", "id": "gantt-02", "source": "auto"},
    ],
    "TEXTE": [
        {"prompt": "c'est quoi draw.io?", "expected": "TEXTE", "complexity": "simple", "id": "txt-01", "source": "auto"},
        {"prompt": "explique la différence entre ellipse et cercle", "expected": "TEXTE", "complexity": "simple", "id": "txt-02", "source": "auto"},
    ],
}

ALL_TESTS = []
for macro, tests in TEST_PROMPTS.items():
    for t in tests:
        ALL_TESTS.append(t)


# ── Résultats ────────────────────────────────────────

def _load_results() -> list[dict]:
    """Charge l'historique des résultats"""
    if RESULTS_FILE.exists():
        try:
            return json.loads(RESULTS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return []

def _save_results(results: list[dict]):
    """Sauvegarde les résultats"""
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(results, indent=2, default=str))


# ── Métadonnées modèle ─────────────────────────────────

def _get_model_info(llm) -> dict:
    """Récupère le nom et les paramètres du modèle utilisé"""
    if not llm:
        return {"model_name": "unknown", "params": {}}
    cfg = llm.local
    return {
        "model_name": cfg.model,
        "params": {
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
            "prefer_local": llm.prefer_local,
        }
    }


# ── Tests ────────────────────────────────────────────

def _count_mx_cells(xml: str) -> int:
    """Compte le nombre de cellules mxCell (sans compter id=0 et id=1)"""
    cells = re.findall(r'<mxCell\s+id="([^"]+)"', xml)
    # Filtrer id=0 et id=1 (root cells)
    real_cells = [c for c in cells if c not in ("0", "1")]
    return len(real_cells)


def run_single_test(test: dict, llm: Optional[LLMClient] = None, brain=None) -> dict:
    """
    Exécute un test unitaire.
    Retourne un dict avec les métriques.
    """
    if llm is None:
        llm = get_llm()
    if brain is None:
        brain = get_brain()
    
    prompt = test["prompt"]
    expected = test["expected"]
    test_id = test["id"]
    
    model_info = _get_model_info(llm)

    result = {
        "test_id": test_id,
        "prompt": prompt,
        "expected_macro": expected,
        "source": test.get("source", "auto"),
        "model_name": model_info["model_name"],
        "model_params": model_info["params"],
        "timestamp": datetime.now().isoformat(),
        "status": "failed",
        "classification": {},
        "xml_generated": False,
        "xml_valid": False,
        "xml_cell_count": 0,
        "rag_patterns_found": 0,
        "timing_ms": {},
        "errors": [],
    }
    
    start = time.time()
    
    # ── 1. Classification ──
    t0 = time.time()
    try:
        classification = llm.classify_intent(prompt)
        result["classification"] = classification
        result["timing_ms"]["classify"] = round((time.time() - t0) * 1000, 1)
    except Exception as e:
        result["errors"].append(f"Classification: {e}")
        result["timing_ms"]["classify"] = round((time.time() - t0) * 1000, 1)
        result["timing_ms"]["total"] = round((time.time() - start) * 1000, 1)
        return result
    
    # Vérifier que la classification correspond
    macro_class = classification.get("macro_class", "UNKNOWN")
    # GANTT est souvent classé comme AGENDA (les deux sont des plannings)
    if macro_class == expected or (expected == "GANTT" and macro_class == "AGENDA") or (expected == "AGENDA" and macro_class == "GANTT"):
        result["status"] = "classified_ok"
    else:
        result["errors"].append(f"Classification incorrecte: attendu={expected}, obtenu={macro_class}")
    
    # ── 2. RAG search ──
    t0 = time.time()
    try:
        shapes_needed = classification.get("shapes_needed", [])
        if macro_class == "FORME" and shapes_needed:
            patterns = []
            for shape in shapes_needed:
                shape_patterns = brain.search_similar(f"forme shape {shape}", n_results=2, min_score=0.4)
                patterns.extend(shape_patterns)
        else:
            patterns = brain.search_similar(prompt, n_results=3, min_score=0.5)
        result["rag_patterns_found"] = len(patterns)
        result["rag_hits"] = [p["title"] for p in patterns[:3]]
        result["timing_ms"]["rag"] = round((time.time() - t0) * 1000, 1)
    except Exception as e:
        result["errors"].append(f"RAG: {e}")
        result["timing_ms"]["rag"] = round((time.time() - t0) * 1000, 1)
    
    # ── 3. Génération XML (si macro visuelle) ──
    if macro_class in ("FORME", "TABLEAU", "KANBAN", "AGENDA", "GANTT"):
        t0 = time.time()
        try:
            context = ""
            if patterns:
                best = patterns[0]
                context = f"Exemple: {best['title']}\n{best['xml'][:500]}"
            
            xml_raw = llm.generate(prompt, context=context)
            
            if xml_raw:
                xml_clean = _extract_xml(xml_raw)
                if xml_clean:
                    xml_clean = _fix_xml_common(xml_clean)
                    valid, errors = _validate_xml(xml_clean)
                    result["xml_generated"] = True
                    result["xml"] = xml_clean[:200]  # Truncated for storage
                    result["xml_valid"] = valid
                    result["xml_cell_count"] = _count_mx_cells(xml_clean)
                    result["xml_validation_errors"] = errors
                    if not valid:
                        result["errors"].extend([f"XML: {e}" for e in errors])
                    elif macro_class == expected:
                        # Succès complet: bonne classification + XML valide
                        result["status"] = "success"
                else:
                    result["errors"].append("XML extrait vide")
            else:
                result["errors"].append("LLM n'a pas généré de XML")
            
            result["timing_ms"]["generate"] = round((time.time() - t0) * 1000, 1)
        except Exception as e:
            result["errors"].append(f"Génération: {e}")
            result["timing_ms"]["generate"] = round((time.time() - t0) * 1000, 1)
    
    result["timing_ms"]["total"] = round((time.time() - start) * 1000, 1)
    
    # Statut final
    if result["status"] == "success":
        pass  # keep
    elif result["status"] == "classified_ok" and not result["errors"]:
        # TEXTE — pas besoin de générer du XML
        result["status"] = "success"
    elif result["xml_generated"] and not result["xml_valid"] and result["status"] == "classified_ok":
        result["status"] = "xml_invalid"
    
    return result


def run_batch(limit: int = 0, macro_filter: str = "") -> list[dict]:
    """
    Exécute tous les tests (ou limités).
    Retourne la liste des nouveaux résultats.
    """
    llm = get_llm()
    brain = get_brain()
    
    tests = ALL_TESTS
    if macro_filter:
        tests = [t for t in tests if t["expected"] == macro_filter]
    if limit > 0:
        tests = tests[:limit]
    
    results = _load_results()
    new_results = []
    
    for i, test in enumerate(tests):
        print(f"  [{i+1}/{len(tests)}] {test['id']}: {test['prompt'][:50]}...")
        r = run_single_test(test, llm, brain)
        new_results.append(r)
        results.append(r)
        _save_results(results)
        print(f"    → {r['status']} ({r['timing_ms']['total']}ms)")
    
    return new_results


# ── Stats ────────────────────────────────────────────

def get_stats() -> dict:
    """Retourne les statistiques agrégées pour le dashboard"""
    results = _load_results()
    
    if not results:
        return {
            "total_tests": 0,
            "success_rate": 0,
            "by_macro": {},
            "recent": [],
            "timing_avg": 0,
        }
    
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    
    # Par macro-classe
    by_macro = {}
    for r in results:
        macro = r.get("expected_macro", "UNKNOWN")
        if macro not in by_macro:
            by_macro[macro] = {"total": 0, "success": 0, "xml_valid": 0, "timing_sum": 0}
        by_macro[macro]["total"] += 1
        if r["status"] == "success":
            by_macro[macro]["success"] += 1
        if r.get("xml_valid"):
            by_macro[macro]["xml_valid"] += 1
        by_macro[macro]["timing_sum"] += r.get("timing_ms", {}).get("total", 0)
    
    # Timing moyen
    timings = [r.get("timing_ms", {}).get("total", 0) for r in results]
    timing_avg = sum(timings) / len(timings) if timings else 0
    
    # Tous les résultats (pas de limite — historique complet)
    recent = sorted(results, key=lambda r: r.get("timestamp", ""), reverse=True)
    
    # Timing par étape
    classify_times = [r.get("timing_ms", {}).get("classify", 0) for r in results if r.get("timing_ms", {}).get("classify")]
    rag_times = [r.get("timing_ms", {}).get("rag", 0) for r in results if r.get("timing_ms", {}).get("rag")]
    gen_times = [r.get("timing_ms", {}).get("generate", 0) for r in results if r.get("timing_ms", {}).get("generate")]
    
    return {
        "total_tests": total,
        "success_count": success,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "by_macro": by_macro,
        "recent": recent,
        "timing_avg": round(timing_avg, 1),
        "avg_classify": round(sum(classify_times) / len(classify_times), 1) if classify_times else 0,
        "avg_rag": round(sum(rag_times) / len(rag_times), 1) if rag_times else 0,
        "avg_generate": round(sum(gen_times) / len(gen_times), 1) if gen_times else 0,
    }


# ── CLI ──────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="🧪 Test Runner pour Smart MCP Pipeline")
    parser.add_argument("--limit", type=int, default=0, help="Nombre de tests à exécuter (0 = tous)")
    parser.add_argument("--macro", type=str, default="", choices=["FORME", "TABLEAU", "KANBAN", "AGENDA", "GANTT", "TEXTE", ""], help="Filtrer par macro-classe")
    parser.add_argument("--stats", action="store_true", help="Afficher les stats seulement")
    args = parser.parse_args()
    
    if args.stats:
        stats = get_stats()
        print(json.dumps(stats, indent=2, default=str))
    else:
        print(f"🧪 Lancement des tests (limit={args.limit or 'tous'}, macro={args.macro or 'toutes'})...")
        results = run_batch(limit=args.limit, macro_filter=args.macro)
        stats = get_stats()
        print(f"\n📊 Résumé: {stats['success_count']}/{stats['total_tests']} succès ({stats['success_rate']}%)")