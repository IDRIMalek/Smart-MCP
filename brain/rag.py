"""
🧠 Smart MCP - Couche RAG (ChromaDB)
Stocke et retrouve les patterns de diagrammes drawio
"""

import json
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import chromadb
from chromadb.config import Settings


@dataclass
class DiagramPattern:
    """Un pattern de diagramme appris"""
    id: str = ""
    title: str = ""
    description: str = ""
    xml_fragment: str = ""
    tags: list[str] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 1.0
    created_at: str = ""
    source: str = "user"  # user | generated | corrected


class RAGBrain:
    """Mémoire vectorielle pour les patterns de diagrammes"""

    def __init__(self, persist_dir: str = "~/.smart-mcp/brain"):
        self.persist_dir = Path(persist_dir).expanduser()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection principale pour les patterns
        col_names = [c.name for c in self.client.list_collections()]
        if "diagram_patterns" in col_names:
            self.collection = self.client.get_collection(name="diagram_patterns")
        else:
            self.collection = self.client.create_collection(
                name="diagram_patterns",
                metadata={"hnsw:space": "cosine"}
            )
        
        # Collection pour l'historique des feedbacks
        if "feedback_history" in col_names:
            self.feedback = self.client.get_collection(name="feedback_history")
        else:
            self.feedback = self.client.create_collection(name="feedback_history")

    def _make_id(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def add_pattern(self, title: str, description: str, xml_fragment: str,
                    tags: list[str] = None, source: str = "generated") -> str:
        """Ajoute un pattern à la mémoire"""
        pattern_id = self._make_id(title + description)
        tags = tags or []
        
        metadata = {
            "title": title,
            "description": description[:500],
            "tags": ",".join(tags),
            "usage_count": 0,
            "success_rate": 1.0,
            "source": source,
            "xml_length": len(xml_fragment)
        }
        
        # Texte pour l'embedding
        embedding_text = f"{title} {description} {' '.join(tags)}"
        
        self.collection.upsert(
            ids=[pattern_id],
            documents=[embedding_text],
            metadatas=[metadata]
        )
        
        # Stocker le XML à part (trop long pour l'embedding)
        xml_path = self.persist_dir / "xml" / f"{pattern_id}.xml"
        xml_path.parent.mkdir(exist_ok=True)
        xml_path.write_text(xml_fragment)
        
        return pattern_id

    def search_similar(self, query: str, n_results: int = 3, 
                       min_score: float = 0.6) -> list[dict]:
        """Recherche les patterns similaires à une requête"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        patterns = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                score = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - score  # cosine distance → similarity
                
                if similarity < min_score:
                    continue
                
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                
                # Charger le XML stocké
                xml_path = self.persist_dir / "xml" / f"{doc_id}.xml"
                xml = xml_path.read_text() if xml_path.exists() else ""
                
                patterns.append({
                    "id": doc_id,
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", "").split(","),
                    "xml": xml,
                    "similarity": round(similarity, 3),
                    "usage_count": metadata.get("usage_count", 0)
                })
        
        return patterns

    def record_feedback(self, pattern_id: str, success: bool, 
                        user_comment: str = ""):
        """Enregistre un feedback sur un pattern"""
        doc_id = self._make_id(f"fb_{pattern_id}_{success}")
        
        self.feedback.upsert(
            ids=[doc_id],
            documents=[f"Pattern {pattern_id}: {'OK' if success else 'FAIL'}: {user_comment}"],
            metadatas=[{
                "pattern_id": pattern_id,
                "success": int(success),
                "comment": user_comment[:500]
            }]
        )
        
        # Mettre à jour le taux de succès du pattern
        pattern = self.collection.get(ids=[pattern_id])
        if pattern and pattern["metadatas"]:
            meta = pattern["metadatas"][0]
            current_count = meta.get("usage_count", 0)
            current_rate = meta.get("success_rate", 1.0)
            
            new_count = current_count + 1
            new_rate = (current_rate * current_count + int(success)) / new_count
            
            self.collection.update(
                ids=[pattern_id],
                metadatas=[{
                    **meta,
                    "usage_count": new_count,
                    "success_rate": round(new_rate, 3)
                }]
            )

    def list_patterns(self, limit: int = 100) -> list[dict]:
        """Liste tous les patterns de la base"""
        data = self.collection.get(limit=limit)
        patterns = []
        for i, doc_id in enumerate(data["ids"]):
            meta = data["metadatas"][i] if data["metadatas"] else {}
            xml_path = self.persist_dir / "xml" / f"{doc_id}.xml"
            xml = xml_path.read_text() if xml_path.exists() else ""
            patterns.append({
                "id": doc_id,
                "title": meta.get("title", ""),
                "description": meta.get("description", ""),
                "tags": meta.get("tags", "").split(","),
                "source": meta.get("source", ""),
                "xml_length": meta.get("xml_length", 0),
                "xml_fragment": xml[:500]  # tronqué pour affichage
            })
        return patterns

    def get_pattern_types(self) -> dict:
        """Analyse les types de patterns présents"""
        counts = {"forme": 0, "architecture": 0, "generic": 0}
        tag_map = {
            "forme": ["forme", "shape", "couleur", "color", "palette"],
            "architecture": ["architecture", "microservices", "pipeline", "etl", "flow", "sequence", "data"],
        }
        for p in self.list_patterns():
            tags = p.get("tags", [])
            if any(t in tag_map["forme"] for t in tags):
                counts["forme"] += 1
            if any(t in tag_map["architecture"] for t in tags):
                counts["architecture"] += 1
            if not any(t in sum(tag_map.values(), []) for t in tags):
                counts["generic"] += 1
        return counts

    def get_stats(self) -> dict:
        """Statistiques du cerveau RAG"""
        return {
            "patterns_count": self.collection.count(),
            "feedback_count": self.feedback.count(),
            "persist_dir": str(self.persist_dir),
            "types": self.get_pattern_types()
        }


# Singleton
_brain: Optional[RAGBrain] = None


def get_brain(persist_dir: str = "~/.smart-mcp/brain") -> RAGBrain:
    global _brain
    if _brain is None:
        _brain = RAGBrain(persist_dir)
    return _brain