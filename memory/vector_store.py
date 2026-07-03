# memory/vector_store.py
import chromadb
from chromadb.utils import embedding_functions

import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

class VectorMemory:
    def __init__(self):
        print("[Vector DB] Connecting to ChromaDB...")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # ⚡ THE PIVOT: Zero-RAM Cloud Embeddings via Hugging Face API
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("🚨 Warning: HF_TOKEN missing in .env")
            
        self.cloud_ef = embedding_functions.HuggingFaceEmbeddingFunction(
            api_key=hf_token,
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Updating collection to use the cloud embedding function
        self.collection = self.client.get_or_create_collection(
            name="customer_issues",
            embedding_function=self.cloud_ef
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

    def check_duplicate(self, issue_text: str):
        print(f"[Vector DB] Checking for duplicates...")
        try:
            # Trying to contact Hugging Face API
            results = self.collection.query(
                query_texts=[issue_text],
                n_results=1
            )
            
            if results and results['distances'] and len(results['distances'][0]) > 0:
                distance = results['distances'][0][0]
                if distance < 1.0: 
                    print(f"      ↳ [Duplicate Found] Distance: {distance}")
                    return results['documents'][0][0]
            
            print("      ↳ [No Duplicate] This is a new issue.")
            return None
            
        except Exception as e:
            # ⚡ THE SAFETY NET: If Hugging Face is down, don't crash. Just bypass.
            print(f"🚨 [Vector DB Warning] Cloud API offline or failed. Bypassing duplicate check. Error: {str(e)[:50]}...")
            return None
vector_memory = VectorMemory()            