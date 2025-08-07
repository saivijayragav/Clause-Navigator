from langchain_community.vectorstores import FAISS
from embedding import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from embedding import OllamaEmbeddings
import helper as helper

class RAG:
    def __init__(self):
        self.embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")  # Same class from earlier

    def retrieval(self, query):
        vectorstore = FAISS.load_local("faiss_index", self.embedding_model, allow_dangerous_deserialization=True)

        results = vectorstore.similarity_search(query, k=5)
        chunks = [doc.page_content.strip() for doc in results]
        return chunks   
    
    def create_faiss_index(self, url):
        # Step 1: Extract text
        raw_text = helper.extract_text_easyocr(url)

        # Step 2: Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=50
        )
        chunks = splitter.split_text(raw_text)

        # Assume `chunks = [...]` from your chunking process
        embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")
        vectorstore = FAISS.from_texts(chunks, embedding_model)
        vectorstore.save_local("faiss_index")
        return vectorstore
    