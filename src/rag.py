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
        self.collection = self.client.get_or_create_collection(
            name="diagram_patterns",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Collection pour l'historique des feedbacks
        self.feedback = self.client.get_or_create_collection(
            name="feedback_history"
        )

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

    def get_stats(self) -> dict:
        """Statistiques du cerveau RAG"""
        return {
            "patterns_count": self.collection.count(),
            "feedback_count": self.feedback.count(),
            "persist_dir": str(self.persist_dir)
        }


# Singleton
_brain: Optional[RAGBrain] = None


def get_brain(persist_dir: str = "~/.smart-mcp/brain") -> RAGBrain:
    global _brain
    if _brain is None:
        _brain = RAGBrain(persist_dir)
    return _brain