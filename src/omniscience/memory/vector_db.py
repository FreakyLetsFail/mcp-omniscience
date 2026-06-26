import os
import lancedb
from typing import List, Dict, Any
import pyarrow as pa
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self, db_path: str = "./.omniscience/lancedb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = lancedb.connect(db_path)
        
        # Load local Voyage AI model (voyage-4-nano)
        # It will automatically download the weights on first run
        self.model = SentenceTransformer("voyageai/voyage-4-nano", trust_remote_code=True)
        
        self.table_name = "symbols"
        if self.table_name not in self.db.table_names():
            self.table = None
        else:
            self.table = self.db.open_table(self.table_name)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # sentence-transformers returns numpy arrays, we convert to list
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def upsert_symbols(self, symbols: List[Dict[str, Any]]):
        if not symbols:
            return
            
        texts = [s["code"] for s in symbols]
        embeddings = self.get_embeddings(texts)
        
        data = []
        for sym, emb in zip(symbols, embeddings):
            data.append({
                "id": sym["id"],
                "file_path": sym["file_path"],
                "name": sym["name"],
                "code": sym["code"],
                "vector": emb
            })
            
        if self.table is None:
            self.table = self.db.create_table(self.table_name, data=data)
            try:
                self.table.create_fts_index("code")
            except Exception as e:
                print(f"Failed to create FTS index: {e}")
        else:
            ids_to_delete = [s["id"] for s in symbols]
            ids_str = ", ".join(f"'{id}'" for id in ids_to_delete)
            try:
                self.table.delete(f"id IN ({ids_str})")
            except Exception:
                pass
            self.table.add(data)

    def hybrid_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self.table is None:
            return []
            
        try:
            res = self.table.search(query, query_type="hybrid").limit(limit).to_list()
            return res
        except Exception:
            query_emb = self.get_embeddings([query])[0]
            res = self.table.search(query_emb).limit(limit).to_list()
            return res
