"""
🤖 Smart MCP - Couche LLM
Interface unifiée pour les modèles (local Qwen / cloud DeepSeek)
"""

import os
import json
from typing import Optional
from dataclasses import dataclass, field

from openai import OpenAI


# ── Prompts pré-paramétrés ──────────────────────────────────────────

PROMPT_GENERATE_XML = """Tu es un expert draw.io. Réponds UNIQUEMENT avec le bloc XML.

Contexte RAG : {context}

Diagramme demandé : {query}

Génère le diagramme au format XML mxGraphModel de draw.io.
Chaque nœud a une forme et une géométrie, chaque flèche a une source et une cible.
Le diagramme complet dans un bloc ```xml. NE DONNE AUCUN TEXTE HORS DU BLOC XML.

IMPORTANT pour les calendriers/plannings (AGENDA) :
- Utilise des rectangles pour chaque jour/cellule
- Dispose les jours en grille 7 colonnes (L M M J V S D)
- Ajoute un en-tête avec le mois/titre
- Utilise fillColor pour distinguer les événements
- Chaque cellule doit avoir une mxCell avec mxGeometry
- Commence TOUJOURS par <mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>

IMPORTANT pour les diagrammes de Gantt (GANTT) :
- Utilise des barres horizontales (rectangles allongés) pour chaque tâche
- Ajoute des jalons sous forme de losanges ou petits cercles
- L'axe X représente le temps (colonnes = jours/semaines/mois)
- L'axe Y liste les tâches les unes sous les autres
- Utilise fillColor pour distinguer les phases du projet
- Les dépendances entre tâches sont des flèches horizontales
- Commence TOUJOURS par <mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>"""

PROMPT_IMPROVE_XML = """Tu es un expert draw.io. Analyse ce XML et améliore-le.

XML ACTUEL :
{xml}

PROBLÈMES SIGNALÉS :
{issues}

DEMANDE :
{query}

Génère le XML amélioré."""

PROMPT_CLASSIFY_INTENT = """Analyse la demande utilisateur pour décider quelle action effectuer.

DEMANDE : {query}

Répond UNIQUEMENT au format JSON. Classes possibles :

1. **FORME** : demande de créer UNE SEULE forme géométrique (carré, cercle, triangle, losange, rectangle, flèche, etc.)
   → ex: "un carré rouge", "dessine un triangle", "ajoute un cercle bleu"
2. **TABLEAU** : demande de créer un diagramme structuré (architecture, flux, organigramme, CI/CD, séquence, réseau, microservices, ETL)
   → ex: "diagramme d'architecture 3-tiers", "flux de données ETL", "pipeline CI/CD"
3. **KANBAN** : demande de créer un tableau Kanban/board (colonnes À faire / En cours / Fait)
   → ex: "tableau kanban pour mon projet", "board de tâches"
4. **GANTT** : demande de créer un diagramme de Gantt/planning de projet/calendrier prévisionnel avec tâches, jalons, dépendances, barres horizontales
   → ex: "diagramme de Gantt planning projet", "calendrier prévisionnel chantier"
5. **AGENDA** : demande de créer un calendrier/planning mensuel/timeline
   → ex: "calendrier du mois", "planning de sprint"
6. **TEXTE** : question textuelle, pas de diagramme
   → ex: "c'est quoi draw.io?", "explique-moi"

{{
  "macro_class": "FORME|TABLEAU|KANBAN|GANTT|AGENDA|TEXTE",
  "confidence": 0.0-1.0,
  "reason": "Courte raison de la classification",
  "shapes_needed": ["liste", "des", "formes"],
  "complexity": "simple|medium|complex"
}}"""


@dataclass
class LLMConfig:
    """Configuration d'un provider LLM"""
    base_url: str
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.3
    timeout: int = 60


class LLMClient:
    """Client LLM unifié avec fallback automatique"""

    def __init__(self):
        # Provider local (Qwen via Ollama GPU)
        self.local = LLMConfig(
            base_url=os.getenv("OLLAMA_GPU_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            model=os.getenv("SMART_MCP_LOCAL_MODEL", "qwen3.5:9b-hermes"),
            max_tokens=int(os.getenv("SMART_MCP_LOCAL_MAX_TOKENS", "16384")),
            temperature=0.3,
            timeout=int(os.getenv("SMART_MCP_LOCAL_TIMEOUT", "300"))
        )
        
        # Provider cloud (DeepSeek via OpenRouter)
        self.cloud = LLMConfig(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            model=os.getenv("SMART_MCP_CLOUD_MODEL", "deepseek/deepseek-v4-flash"),
            max_tokens=int(os.getenv("SMART_MCP_CLOUD_MAX_TOKENS", "8192")),
            temperature=0.3,
            timeout=60
        )
        
        # Préférence : local > cloud
        self.prefer_local = os.getenv("SMART_MCP_PREFER_LOCAL", "true").lower() == "true"

    def _call(self, config: LLMConfig, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Appelle un LLM et retourne la réponse"""
        try:
            client = OpenAI(base_url=config.base_url, api_key=config.api_key, timeout=config.timeout)
            
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            import traceback
            print(f"[DEBUG _call] {type(e).__name__}: {e}", file=__import__('sys').stderr)
            traceback.print_exc(file=__import__('sys').stderr)
            return None

    def generate(self, prompt: str, context: str = "") -> Optional[str]:
        """Génère du XML drawio - essaie local puis cloud"""
        
        system_prompt = "Tu es un assistant spécialisé dans la création de diagrammes draw.io."
        user_prompt = PROMPT_GENERATE_XML.format(query=prompt, context=context)
        
        # Essayer local d'abord
        if self.prefer_local:
            result = self._call(self.local, system_prompt, user_prompt)
            if result:
                return result
        
        # Fallback cloud
        if self.cloud.api_key:
            result = self._call(self.cloud, system_prompt, user_prompt)
            if result:
                return result
        
        # Dernier recours : local si on avait préféré cloud
        if not self.prefer_local:
            result = self._call(self.local, system_prompt, user_prompt)
            if result:
                return result
        
        return None

    def classify_intent(self, query: str) -> dict:
        """Analyse l'intention de l'utilisateur"""
        prompt = PROMPT_CLASSIFY_INTENT.format(query=query)
        
        # Toujours essayer le local pour la classification (rapide)
        result = self._call(self.local, 
                           "Tu analyses des requêtes et réponds en JSON strict.",
                           prompt)
        
        if result:
            try:
                # Nettoyer le JSON
                result = result.strip()
                if result.startswith("```"):
                    result = result.split("\n", 1)[1]
                    result = result.rsplit("```", 1)[0]
                return json.loads(result)
            except (json.JSONDecodeError, KeyError):
                pass
        
        return {
            "type": "unknown",
            "diagram_type": "generic",
            "confidence": 0.0,
            "key_elements": [],
            "complexity": "simple"
        }

    def improve_xml(self, xml: str, query: str, issues: str = "") -> Optional[str]:
        """Améliore un XML existant — essaie cloud d'abord, fallback local si pas de clé"""
        user_prompt = PROMPT_IMPROVE_XML.format(xml=xml, issues=issues, query=query)

        # Essayer cloud d'abord (si configuré)
        if self.cloud.api_key and len(self.cloud.api_key) > 10:
            result = self._call(self.cloud, "Tu es un expert draw.io.", user_prompt)
            if result:
                return result

        # Fallback local si cloud indisponible ou a échoué
        if self.prefer_local or not self.cloud.api_key:
            result = self._call(self.local, "Tu es un expert draw.io.", user_prompt)
            if result:
                return result

        return None


# Singleton
_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client