"""Yn Security Bot - Database Module (MongoDB-like API with SQLite)."""

import json
import sqlite3
from typing import Any, Dict, List, Optional


class YnDB:
    """A MongoDB-like database interface using SQLite as backend."""

    def __init__(self, db_file: str, collection: str) -> None:
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.collection = collection
        self._create_collection()
        self._index: Dict[str, Dict[Any, List[int]]] = {}
        self._indexed_fields: set = set()

    def _create_collection(self) -> None:
        """Create the collection table if it doesn't exist."""
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.collection} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def insert_one(self, document: Dict[str, Any]) -> int:
        """Insert a single document into the collection."""
        doc_json = json.dumps(document)
        self.cursor.execute(
            f"INSERT INTO {self.collection} (doc) VALUES (?)", (doc_json,)
        )
        self.conn.commit()
        _id = self.cursor.lastrowid
        self._update_indexes_insert(_id, document)
        return _id

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple documents into the collection."""
        ids = []
        for doc in documents:
            _id = self.insert_one(doc)
            ids.append(_id)
        return ids

    def _load_all(self) -> List[Dict[str, Any]]:
        """Load all documents from the collection."""
        self.cursor.execute(f"SELECT id, doc FROM {self.collection}")
        rows = self.cursor.fetchall()
        results = []
        for _id, doc_json in rows:
            doc = json.loads(doc_json)
            doc["_id"] = _id
            results.append(doc)
        return results

    def find(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find documents matching the query."""
        if query is None or query == {}:
            return self._load_all()

        # Optimization for single field $eq queries with index
        if len(query) == 1:
            key, cond = next(iter(query.items()))
            if not isinstance(cond, dict):
                if key in self._indexed_fields:
                    ids = self._index.get(key, {}).get(cond, [])
                    return [
                        doc for doc in self._load_all() if doc["_id"] in ids
                    ]
            elif "$eq" in cond:
                if key in self._indexed_fields:
                    val = cond["$eq"]
                    ids = self._index.get(key, {}).get(val, [])
                    return [
                        doc for doc in self._load_all() if doc["_id"] in ids
                    ]

        # Fallback full scan
        all_docs = self._load_all()
        return [doc for doc in all_docs if self._matches(doc, query)]

    def _matches(self, doc: Dict[str, Any], query: Optional[Dict[str, Any]]) -> bool:
        """Check if a document matches the query."""
        if not query:
            return True
        for key, cond in query.items():
            value = self._get_value(doc, key)
            if isinstance(cond, dict):
                if not self._match_operators(value, cond):
                    return False
            else:
                if value != cond:
                    return False
        return True

    def _match_operators(self, value: Any, cond: Dict[str, Any]) -> bool:
        """Match operators for query conditions."""
        for op, cond_val in cond.items():
            if op == "$eq" and value != cond_val:
                return False
            elif op == "$ne" and value == cond_val:
                return False
            elif op == "$gt" and not (value > cond_val):
                return False
            elif op == "$gte" and not (value >= cond_val):
                return False
            elif op == "$lt" and not (value < cond_val):
                return False
            elif op == "$lte" and not (value <= cond_val):
                return False
            elif op == "$in" and value not in cond_val:
                return False
            elif op == "$nin" and value in cond_val:
                return False
        return True

    def _get_value(self, doc: Dict[str, Any], key: str) -> Any:
        """Get nested value from document using dot notation."""
        keys = key.split(".")
        v = doc
        for k in keys:
            if isinstance(v, dict) and k in v:
                v = v[k]
            else:
                return None
        return v

    def update_one(
        self, query: Dict[str, Any], update: Dict[str, Any]
    ) -> bool:
        """Update a single document matching the query."""
        docs = self.find(query)
        if not docs:
            return False
        doc = docs[0]
        _id = doc["_id"]
        updated_doc = self._apply_update(doc, update)
        updated_doc.pop("_id", None)
        doc_json = json.dumps(updated_doc)
        self.cursor.execute(
            f"UPDATE {self.collection} SET doc = ? WHERE id = ?", (doc_json, _id)
        )
        self.conn.commit()
        self.create_index_all()
        return True

    def _apply_update(
        self, doc: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply update operations to a document."""
        for op, fields in update.items():
            if op == "$set":
                for k, v in fields.items():
                    self._set_value(doc, k, v)
            elif op == "$inc":
                for k, v in fields.items():
                    old_val = self._get_value(doc, k) or 0
                    self._set_value(doc, k, old_val + v)
            elif op == "$unset":
                for k in fields.keys():
                    self._unset_value(doc, k)
        return doc

    def _set_value(self, doc: Dict[str, Any], key: str, value: Any) -> None:
        """Set a nested value in a document using dot notation."""
        keys = key.split(".")
        d = doc
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def _unset_value(self, doc: Dict[str, Any], key: str) -> None:
        """Remove a nested value from a document using dot notation."""
        keys = key.split(".")
        d = doc
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                return
            d = d[k]
        d.pop(keys[-1], None)

    def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single document matching the query."""
        docs = self.find(query)
        if not docs:
            return False
        _id = docs[0]["_id"]
        self.cursor.execute(
            f"DELETE FROM {self.collection} WHERE id = ?", (_id,)
        )
        self.conn.commit()
        self.create_index_all()
        return True

    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents matching the query."""
        docs = self.find(query)
        count = 0
        for doc in docs:
            _id = doc["_id"]
            self.cursor.execute(
                f"DELETE FROM {self.collection} WHERE id = ?", (_id,)
            )
            count += 1
        self.conn.commit()
        self.create_index_all()
        return count

    def create_index(self, field: str) -> None:
        """Create an index on a field."""
        all_docs = self._load_all()
        index = {}
        for doc in all_docs:
            val = self._get_value(doc, field)
            if val is not None:
                index.setdefault(val, []).append(doc["_id"])
        self._index[field] = index
        self._indexed_fields.add(field)

    def create_index_all(self) -> None:
        """Rebuild all indexes."""
        for field in self._indexed_fields:
            self.create_index(field)

    def _update_indexes_insert(
        self, _id: int, document: Dict[str, Any]
    ) -> None:
        """Update indexes when a document is inserted."""
        for field in self._indexed_fields:
            val = self._get_value(document, field)
            if val is not None:
                self._index.setdefault(field, {}).setdefault(val, []).append(_id)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation pipeline."""
        docs = self._load_all()
        for stage in pipeline:
            if "$match" in stage:
                docs = [doc for doc in docs if self._matches(doc, stage["$match"])]
            elif "$group" in stage:
                docs = self._aggregate_group(docs, stage["$group"])
            else:
                raise ValueError(f"Unsupported pipeline stage: {stage}")
        return docs

    def _aggregate_group(
        self, docs: List[Dict[str, Any]], group_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform group aggregation."""
        group_field = group_spec["_id"].lstrip("$")
        accumulator_fields = {k: v for k, v in group_spec.items() if k != "_id"}
        grouped = {}
        for doc in docs:
            key = self._get_value(doc, group_field)
            if key not in grouped:
                grouped[key] = {k: 0 for k in accumulator_fields}
                grouped[key]["_id"] = key
                grouped[key]["_count"] = 0

            for acc_key, acc_val in accumulator_fields.items():
                for op, field in acc_val.items():
                    val = self._get_value(doc, field.lstrip("$"))
                    if op == "$sum":
                        grouped[key][acc_key] += val if val is not None else 0
                    elif op == "$max":
                        if grouped[key][acc_key] < val:
                            grouped[key][acc_key] = val
                    elif op == "$min":
                        if grouped[key][acc_key] == 0 or grouped[key][acc_key] > val:
                            grouped[key][acc_key] = val
            grouped[key]["_count"] += 1
        return list(grouped.values())


# Database instances
db = YnDB("ankesDB.sqlite3", "groups")
db_warnings = YnDB("ankeswarn.sqlite3", "warnings")
db_freeusers = YnDB("ankesfree.sqlite3", "freeusers")
db_authorize = YnDB("ankesauth.sqlite3", "authorize")
db_stats = YnDB("ankesstats.sqlite3", "stats")
db_users = YnDB("ankesusers.sqlite3", "users")

