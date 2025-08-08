from fastapi import Depends, FastAPI
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
# from rag import RAG
import uvicorn
from jwtbearer import JWTBearer
from datetime import datetime
import os
import csv
import time
import ast
import json
from dotenv import load_dotenv
load_dotenv()

KEY1 = os.getenv('KEY1')
KEY2 = os.getenv('KEY2')
# Configure Gemini
genai.configure(api_key=KEY1)
model = genai.GenerativeModel("gemini-2.5-flash")

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
    You can infer answers from the documents on your own.
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


def makeGeminiCall(request):
    global model, KEY1, KEY2 
    try:
        prompt_template = """
        You are given a document: {documents}

        Answer the following questions based on the content of the document.
        If there is no answers for the question in the document answer on your own. 
        Try your best to give or infer answer from the document. 
        Refer to the page numbers, line number in that page and the sections or topics that you find the answer from.
        Also quote the lines in the document to ensure validity, remember to only use single quotes to quote.
        **IMPORTANT: ALWAYS RETURN A STRING WITH DOUBLE QUOTES. DO NOT USE DOUBLE QUOTES INSIDES.** 
        Here are the questions: {questions}

        Return ONLY a valid Python list of strings: [answer1, answer2, ...]
        - Keep the answers concise
        - Each string must be properly enclosed in double quotes.
        - Do not include newline characters inside strings.
        - Do not use triple quotes or backslashes.
        - Do not include any introductory text.
        - Output must be parseable by Python's ast.literal_eval()

        Return only the list, and nothing else.
        """

        PROMPT = prompt_template.format(
        documents=request.documents,
        questions=request.questions
        )
        response = model.generate_content(PROMPT)

        return response.text.strip()
    except RecursionError:
        print("Recursion limit exceeded — stopping retries.")
        raise
    except Exception as e:
        print("API Key switching!")
        KEY1, KEY2 = KEY2, KEY1
        genai.configure(api_key=KEY1)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        return makeGeminiCall(request=request)

def parse_to_list(input_data):
    print(input_data)
    try:
        input_data = input_data[input_data.index('['):input_data.rindex(']')+1]
        return ast.literal_eval(input_data)
    except Exception as e:
        print("Parsing failed:", e)
        return ["Error: Could not parse Gemini response."]

@app.post("/api/v1/hackrx/run")
async def run_submission(request: QueryRequest, token: str = Depends(JWTBearer())):
    print(request)
    # Extract
    # rag = RAG()
    # rag.create_faiss_index(request.documents)  # Index document
    # print("Creating faiss complete: ", time.time() - start)
    # answers = []
    # for question in request.questions:
    #     chunks = rag.retrieval(question)  # RAG-style context retrieval
    #     answer = generate_answer_gemini(question, chunks)
    #     answers.append(answer)
    start = time.time()
    answers = parse_to_list(makeGeminiCall(request))
    print("Generate gemini answers complete: ", time.time() - start)
    for i, ans in enumerate(answers):
        print(f"{i}: {repr(ans)} (type: {type(ans)})")    
    print(QueryResponse(answers=answers))
    return QueryResponse(answers=answers)

def log_to_json(request: QueryRequest, filename="query_log.json"):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "questions": request.questions,
        "documents": request.documents
    }

    # Load existing logs if file exists, else start a new list
    if os.path.isfile(filename):
        with open(filename, mode="r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new entry and write back
    data.append(log_entry)
    with open(filename, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



