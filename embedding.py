from langchain.embeddings.base import Embeddings
import ollama
class OllamaEmbeddings(Embeddings):
    def __init__(self, model="nomic-embed-text:latest"):
        self.model = model

    def embed_documents(self, texts):
        return [ollama.embed(model=self.model, input=t).embeddings[0] for t in texts]

    def embed_query(self, text):
        return ollama.embed(model=self.model, input=text).embeddings[0]
    