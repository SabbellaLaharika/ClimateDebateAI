import json
import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = "chroma_data"

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="climate_policies",
            embedding_function=self.embedding_function
        )
        self.load_data()

    def load_data(self):
        policies_dir = "data/policies"
        if not os.path.exists(policies_dir):
            return

        for filename in os.listdir(policies_dir):
            if filename.endswith("_policy.json"):
                with open(os.path.join(policies_dir, filename), "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                    
                    country = data.get("country")
                    if not country:
                        continue
                    
                    # Process key positions
                    for i, point in enumerate(data.get("key_positions", [])):
                        doc_id = f"{country}_key_{i}"
                        try:
                            self.collection.add(
                                documents=[point],
                                metadatas=[{"country": country, "type": "key_position"}],
                                ids=[doc_id]
                            )
                        except Exception:
                            pass # Ignore if already exists

                    # Process red lines
                    for i, point in enumerate(data.get("red_lines", [])):
                        doc_id = f"{country}_red_{i}"
                        try:
                            self.collection.add(
                                documents=[point],
                                metadatas=[{"country": country, "type": "red_line"}],
                                ids=[doc_id]
                            )
                        except Exception:
                            pass

    def retrieve(self, country: str, query: str, n_results: int = 2):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"country": country}
            )
            if results and results.get("documents") and results["documents"][0]:
                return results["documents"][0]
            return []
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

rag_service = RAGService()
