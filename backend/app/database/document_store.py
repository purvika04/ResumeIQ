import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class DocumentStore:
    """Abstract interface for document collections (MongoDB or Local JSON fallback)."""

    def insert(self, collection: str, document: Dict[str, Any]) -> str:
        raise NotImplementedError

    def find_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def find_all(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def update(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def delete(self, collection: str, doc_id: str) -> bool:
        raise NotImplementedError

class LocalJsonDocumentStore(DocumentStore):
    """File-based atomic JSON document store for local development."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.collections = ["resumes_raw", "resumes_parsed", "nlp_logs"]
        for col in self.collections:
            (self.base_dir / col).mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized LocalJsonDocumentStore at {self.base_dir}")

    def _get_path(self, collection: str, doc_id: str) -> Path:
        return self.base_dir / collection / f"{doc_id}.json"

    def insert(self, collection: str, document: Dict[str, Any]) -> str:
        doc_id = document.get("id") or document.get("_id") or str(uuid.uuid4())
        doc_copy = dict(document)
        doc_copy["id"] = doc_id
        if "created_at" not in doc_copy:
            doc_copy["created_at"] = datetime.utcnow().isoformat()
        
        target_path = self._get_path(collection, doc_id)
        temp_path = target_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(doc_copy, f, indent=2, default=str)
        temp_path.replace(target_path)
        return doc_id

    def find_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        path = self._get_path(collection, doc_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def find_all(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        col_dir = self.base_dir / collection
        if not col_dir.exists():
            return []
        results = []
        for file in sorted(col_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    if query:
                        matches = all(doc.get(k) == v for k, v in query.items())
                        if matches:
                            results.append(doc)
                    else:
                        results.append(doc)
            except Exception as e:
                logger.error(f"Error reading doc {file}: {e}")
        return results

    def update(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        doc = self.find_by_id(collection, doc_id)
        if not doc:
            return False
        doc.update(updates)
        doc["updated_at"] = datetime.utcnow().isoformat()
        self.insert(collection, doc)
        return True

    def delete(self, collection: str, doc_id: str) -> bool:
        path = self._get_path(collection, doc_id)
        if path.exists():
            path.unlink()
            return True
        return False

class MongoDocumentStore(DocumentStore):
    """Production MongoDB document store."""

    def __init__(self, uri: str, db_name: str):
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[db_name]
        # Verify connection
        self.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {db_name}")

    def insert(self, collection: str, document: Dict[str, Any]) -> str:
        doc_copy = dict(document)
        doc_id = doc_copy.get("id") or str(uuid.uuid4())
        doc_copy["_id"] = doc_id
        doc_copy["id"] = doc_id
        if "created_at" not in doc_copy:
            doc_copy["created_at"] = datetime.utcnow()
        self.db[collection].replace_one({"_id": doc_id}, doc_copy, upsert=True)
        return doc_id

    def find_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db[collection].find_one({"_id": doc_id})
        if doc and "_id" in doc:
            doc["id"] = str(doc["_id"])
        return doc

    def find_all(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        cursor = self.db[collection].find(query or {}).sort("created_at", -1)
        results = []
        for doc in cursor:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            results.append(doc)
        return results

    def update(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        updates["updated_at"] = datetime.utcnow()
        res = self.db[collection].update_one({"_id": doc_id}, {"$set": updates})
        return res.modified_count > 0

    def delete(self, collection: str, doc_id: str) -> bool:
        res = self.db[collection].delete_one({"_id": doc_id})
        return res.deleted_count > 0

def get_document_store() -> DocumentStore:
    """Factory to get MongoDB store if configured and alive, else Local JSON fallback."""
    if settings.MONGODB_URI and settings.MONGODB_URI.strip():
        try:
            return MongoDocumentStore(settings.MONGODB_URI, settings.MONGODB_DB_NAME)
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB ({e}). Falling back to LocalJsonDocumentStore.")
    
    return LocalJsonDocumentStore(settings.DOCUMENT_STORE_DIR)

# Global document store instance
doc_store = get_document_store()
