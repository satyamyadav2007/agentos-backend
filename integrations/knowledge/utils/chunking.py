from typing import List, Dict, Any

class SmartChunker:
    @staticmethod
    def chunk_document(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Splits document into overlapping semantic chunks for Vector DB."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += (chunk_size - overlap)
            
        return chunks