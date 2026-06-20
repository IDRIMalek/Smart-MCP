"""
⚡ Smart MCP - Orchestrateur principal
Pont langage-naturel → dessin drawio avec mémoire vectorielle
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from brain.rag import get_brain
from models.llm_client import get_llm
from mcp_client.drawio import get_drawio


console = Console()


# ── Extraction XML depuis une réponse LLM ──────────────────────────

def extract_xml(text: str) -> Optional[str]:
    """Extrait du XML <mxGraphModel> du texte"""
    # Chercher dans les blocs de code
    match = re.search(r'```(?:xml)?\s*(<mxGraphModel>.*?</mxGraphModel>)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Chercher directement
    match = re.search(r'(<mxGraphModel>.*?</mxGraphModel>)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return None


def extract_json(text: str) -> Optional[dict]:
    """Extrait du JSON d'une réponse"""
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Chercher directement
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None


# ── Orchestrateur ──────────────────────────────────────────────────

class SmartMCP:
    """Orchestrateur Smart MCP"""

    def __init__(self, verbose: bool = True):
        self.brain = get_brain()
        self.llm = get_llm()
        self.drawio = get_drawio()
        self.verbose = verbose

    def _log(self, step: str, message: str):
        if self.verbose:
            console.print(Panel(f"[bold]{step}[/bold]\n{message}", 
                               border_style="blue", width=80))

    def process(self, query: str) -> dict:
        """Point d'entrée : traite une demande utilisateur"""
        
        result = {
            "query": query,
            "success": False,
            "steps": [],
            "diagram_url": None,
            "error": None
        }
        
        # ════════════════════════════════════════
        # ÉTAPE 1 : Analyser l'intention
        # ════════════════════════════════════════
        self._log("🔍 Analyse", f"Classification de la requête...")
        
        intent = self.llm.classify_intent(query)
        result["steps"].append({"step": "analyse", "intent": intent})
        
        if intent.get("confidence", 0) < 0.3:
            result["error"] = "Requête non comprise ou hors scope"
            self._log("❌ Erreur", result["error"])
            return result
        
        # ════════════════════════════════════════
        # ÉTAPE 2 : Chercher des patterns similaires
        # ════════════════════════════════════════
        self._log("🧠 Mémoire", f"Recherche de patterns similaires...")
        
        similar = self.brain.search_similar(query)
        context = ""
        
        if similar:
            context = f"Patterns similaires trouvés ({len(similar)}) :\n"
            for p in similar:
                context += f"- {p['title']} (similitude: {p['similarity']})\n"
                if p['xml']:
                    context += f"  XML: {p['xml'][:200]}...\n"
            
            self._log("📚 Patterns", context[:500])
        else:
            self._log("📚 Patterns", "Aucun pattern similaire trouvé (base neuve)")
        
        result["steps"].append({"step": "patterns", "found": len(similar), "similar": similar})
        
        # ════════════════════════════════════════
        # ÉTAPE 3 : Générer le diagramme
        # ════════════════════════════════════════
        self._log("🎨 Génération", "Génération du XML drawio via LLM...")
        
        xml = self.llm.generate(query, context)
        if not xml:
            result["error"] = "Échec de génération du XML (LLM indisponible)"
            self._log("❌ Erreur", result["error"])
            return result
        
        # Extraire le XML propre
        clean_xml = extract_xml(xml) or xml
        
        self._log("📄 XML Généré", clean_xml[:500] + ("..." if len(clean_xml) > 500 else ""))
        result["steps"].append({"step": "generation", "xml": clean_xml[:1000]})
        
        # ════════════════════════════════════════
        # ÉTAPE 4 : Exécuter (créer le diagramme)
        # ════════════════════════════════════════
        self._log("🚀 Exécution", "Création du diagramme drawio...")
        
        # Démarrer une session
        if not self.drawio.session_active:
            self.drawio.start_session()
        
        # Créer le diagramme
        success = self.drawio.create_new_diagram(clean_xml)
        if not success:
            result["error"] = "Échec d'exécution sur le MCP Drawio"
            self._log("❌ Erreur", result["error"])
            return result
        
        result["success"] = True
        result["diagram_url"] = "http://192.168.1.100:8080/?mcp=... (session drawio active)"
        
        self._log("✅ Succès", "Diagramme créé avec succès !")
        
        # ════════════════════════════════════════
        # ÉTAPE 5 : Apprendre (sauvegarder le pattern)
        # ════════════════════════════════════════
        title = intent.get("diagram_type", "generic") + " diagram"
        tags = intent.get("key_elements", []) + [intent.get("diagram_type", "generic")]
        tags = list(set(tags))  # déduplication
        
        pattern_id = self.brain.add_pattern(
            title=title,
            description=query,
            xml_fragment=clean_xml[:2000],
            tags=tags,
            source="generated"
        )
        
        self._log("💾 Apprentissage", f"Pattern sauvegardé: {pattern_id}")
        result["pattern_id"] = pattern_id
        result["steps"].append({"step": "learning", "pattern_id": pattern_id})
        
        return result

    def improve(self, query: str, issues: str = "") -> dict:
        """Améliore le diagramme actuel en se basant sur le feedback"""
        
        current_xml = self.drawio.get_diagram()
        if not current_xml:
            return {"success": False, "error": "Aucun diagramme actif"}
        
        improved = self.llm.improve_xml(current_xml, query, issues)
        if not improved:
            return {"success": False, "error": "Échec d'amélioration"}
        
        clean_xml = extract_xml(improved) or improved
        
        success = self.drawio.create_new_diagram(clean_xml)
        return {
            "success": success,
            "xml": clean_xml[:500]
        }

    def stats(self) -> dict:
        """Statistiques du système"""
        brain_stats = self.brain.get_stats()
        return {
            "brain": brain_stats,
            "session_active": self.drawio.session_active
        }


# ── CLI ────────────────────────────────────────────────────────────

def cli():
    """Interface en ligne de commande interactive"""
    import sys
    
    smart = SmartMCP()
    
    console.print(Panel.fit(
        "[bold blue]⚡ Smart MCP[/bold blue]\n"
        "Pont langage-naturel → Diagrammes drawio\n"
        "Tape 'exit' pour quitter, 'stats' pour les stats",
        border_style="blue"
    ))
    
    while True:
        try:
            query = console.input("\n[bold yellow]❯[/bold yellow] ").strip()
            
            if query.lower() in ("exit", "quit"):
                break
            if query.lower() == "stats":
                stats = smart.stats()
                console.print(json.dumps(stats, indent=2))
                continue
            if not query:
                continue
            
            result = smart.process(query)
            
            if result["success"]:
                console.print(Panel(
                    f"[green]✅ Diagramme créé ![/green]\n"
                    f"Pattern ID: {result.get('pattern_id', '?')}\n"
                    f"Étapes: {len(result['steps'])}",
                    title="Succès", border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[red]❌ {result.get('error', 'Erreur inconnue')}[/red]",
                    title="Échec", border_style="red"
                ))
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Erreur: {e}[/red]")
    
    console.print("[blue]À bientôt ![/blue]")


if __name__ == "__main__":
    cli()