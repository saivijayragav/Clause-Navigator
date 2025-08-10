from fastapi import Depends, FastAPI
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
from rag import RAG
import uvicorn
from jwtbearer import JWTBearer
from datetime import datetime
import os
import csv
import time
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize FastAPI app
app = FastAPI()
    
# Request & Response models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

# Gemini generation function
def generate_answer_gemini(question: str, chunks: list):
    context = "\n\n".join(chunks[:3])  # Top 3 chunks
    prompt = f"""
    You are an assistant to help users navigate documents and answer their queries.

    Use only the following context to answer the question.

    Context:
    {context}

    Question: {question}

    Instructions:
    - Based ONLY on the above context, answer the question with clear and concise sentences.
    - Keep the sentences concise.
    - Each sentence should answer one distinct sub-question or point.
    - Do NOT use any JSON, bullet points, numbers, or other list formatting.
    - Do NOT use special character or escape characters
    - Do NOT add any introductory or concluding text—only the answer sentences.

    Answer now:
    """
    response = model.generate_content(prompt)
    return response.text.strip()



@app.post("/api/v1/hackrx/run")
async def run_submission(request: QueryRequest, token: str = Depends(JWTBearer())):
    # log_to_csv(request)
    # Extract
    rag = RAG()
    start = time.time()
    print("Starting...", )
    rag.create_faiss_index(request.documents)  # Index document
    print("Creating faiss complete: ", time.time() - start)
    answers = []
    for question in request.questions:
        chunks = rag.retrieval(question)  # RAG-style context retrieval
        answer = generate_answer_gemini(question, chunks)
        answers.append(answer)
    print("Generate gemini answers complete: ", time.time() - start)
    return QueryResponse(answers=answers)

def log_to_csv(request: QueryRequest, filename="query_log.csv"):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(["timestamp", "questions", "documents"])
        
        writer.writerow([
            datetime.now().isoformat(),
            "; ".join(request.questions),
            request.documents
        ])
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)



