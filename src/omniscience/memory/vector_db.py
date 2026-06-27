import os
import lancedb
from typing import List, Dict, Any
import pyarrow as pa
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self, db_path: str = "./.omniscience/lancedb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = lancedb.connect(db_path)
        
        # We load the model lazily to prevent blocking the MCP handshake
        self.model = None
        
        self.table_name = "symbols"
        if self.table_name not in self.db.table_names():
            self.table = None
        else:
            self.table = self.db.open_table(self.table_name)

    def _get_model(self):
        if self.model is None:
            import warnings
            warnings.filterwarnings('ignore')
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
            # Detect Apple Silicon (MPS) or CUDA
            import torch
            device = "cpu"
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
                
            self.model = SentenceTransformer("voyageai/voyage-4-nano", trust_remote_code=True, device=device)
        return self.model

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        model = self._get_model()
        embeddings = model.encode(texts)
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
