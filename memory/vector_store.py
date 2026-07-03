# memory/vector_store.py
import chromadb
from chromadb.utils import embedding_functions

class VectorMemory:
    def __init__(self):
        # Local persistent memory (data save rahega)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # BGE ya MiniLM fast embeddings ke liye best hote hain
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Collection create karo
        self.collection = self.chroma_client.get_or_create_collection(
            name="customer_feedback",
            embedding_function=self.sentence_transformer_ef
        )

    def add_issue(self, issue_id: str, text: str, metadata: dict = None):
        """Naya bug report vector graph me daalo"""
        if metadata is None:
            metadata = {}
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[issue_id]
        )

    def check_duplicate(self, new_text: str, threshold: float = 0.85):
        """Check karo agar ye bug pehle bhi kisi ne report kiya hai"""
        results = self.collection.query(
            query_texts=[new_text],
            n_results=1
        )
        
        # Agar distances (similarity) ek limit se kam hai, matlab duplicate mil gaya!
        if results['distances'] and results['distances'][0]:
            distance = results['distances'][0][0]
            if distance < (1.0 - threshold): # Chroma uses distance, not cosine similarity directly
                return {"is_duplicate": True, "matched_id": results['ids'][0][0]}
                
        return {"is_duplicate": False}

vector_memory = VectorMemory()