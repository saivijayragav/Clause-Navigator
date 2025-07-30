# 📄 Clause Navigator — Document Query Evaluator API

This FastAPI-based project uses Google's Gemini (`gemini-2.0-flash`) model and a RAG (Retrieval-Augmented Generation) pipeline to answer natural language questions from long-form documents.

## 🚀 Features

- 🔍 Accepts a large text document and a list of user questions.
- ⚡ Uses FAISS for fast semantic retrieval of relevant text chunks.
- 🧠 Uses Gemini (Generative AI) to answer each question based on top retrieved chunks.
- 🔐 Secured with JWT-based bearer token authentication.
- 🗂️ Optionally logs each request to a CSV file.

---

## 📦 Requirements

- Python 3.8+
- [Gemini API Key](https://ai.google.dev/)

---

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/saivijayragav/Clause-Navigator.git
cd Clause-Navigator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Gemini API Key

Edit `main.py`:

```python
GEMINI_API_KEY = "<your-api-key-here>"
```

Or set as an environment variable:

```bash
export GEMINI_API_KEY="your-key-here"
```

---

## ▶️ Run the Server

```bash
uvicorn main:app --reload --port 8000
```

API will be live at: [http://localhost:8000](http://localhost:8000)

---

## 📬 API Endpoint

### `POST /api/v1/hackrx/run`

**Request Body:**

```json
{
  "documents": "string",       // Full raw text content of the document
  "questions": ["Question 1", "Question 2"]
}
```

**Response:**

```json
{
  "answers": [
    "Answer to question 1",
    "Answer to question 2"
  ]
}
```

---

## 🧠 How It Works

1. Document is indexed using a custom `RAG` class and FAISS.
2. For each question:

   * Relevant chunks are retrieved based on semantic similarity.
   * A custom prompt is created and sent to Gemini.
3. The model generates an answer strictly using the retrieved context.
4. Answers are returned in a structured JSON response.

---

## 📝 Optional: Log Query to CSV

Uncomment `log_to_csv(request)` in `run_submission()` to log query metadata.

This will save:

* Timestamp
* Questions
* Raw document text

To a file called `query_log.csv`.

---

## 📂 Project Structure

```
.
├── main.py              # FastAPI app + Gemini generation logic
├── rag.py               # RAG class (FAISS + retrieval logic)
├── jwtbearer.py         # Custom JWTBearer dependency
├── query_log.csv        # Optional log file (generated on use)
├── requirements.txt     # Project dependencies
```
---
