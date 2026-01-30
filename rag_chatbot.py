# =========================================================
# Xyntra Club Hackathon RAG Chatbot
# Backend: FastAPI + LangChain + OpenRouter
# Python: 3.11
# =========================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------- LangChain Imports ----------------
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
load_dotenv()

# --------------------------------------------------

# ================= CONFIG =========================
PDF_PATH = "hackathon.pdf"
DB_PATH = "faiss_index"
# =================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set")

# =================================================

# ================= APP ============================

app = FastAPI(title="Xyntra Club Hackathon Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =================================================

# ================= REQUEST MODEL =================
class Question(BaseModel):
    query: str
# =================================================

# ================= VECTOR DB =====================
def load_vector_db():
    embeddings = FakeEmbeddings(size=384)

    if os.path.exists(DB_PATH):
        return FAISS.load_local(
            DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_PATH)
    return db

vector_db = load_vector_db()
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
# =================================================

# ================= LLM (OPENROUTER) ===============
llm = ChatOpenAI(
    model="meta-llama/llama-3-8b-instruct",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://xyntra26-chatbot.onrender.com",
        "X-Title": "Xyntra'26 RAG Chatbot"
    },
    temperature=0.6,
)


# =================================================

# ================= PROMPT =========================
prompt = ChatPromptTemplate.from_template(
   """
You are the official Xyntra Club Hackathon Assistant for Xyntra'26.

Your job is to respond to users based on the rules below.
These rules are INTERNAL and MUST NOT be mentioned or explained in your response.

INTERNAL RULES (DO NOT REPEAT OR EXPLAIN):
- If the answer is clearly available in the provided context, answer using ONLY that context.
- If the question is related to Xyntra Club Hackathon or Xyntra'26 but the answer is NOT found in the context, respond EXACTLY with:
  "To know about this, visit www.Xyntra26.com or contact +91 90423 xxxxx."
- If the question is NOT related to Xyntra Club Hackathon or Xyntra'26, respond politely that you handle only Xyntra Club Hackathon related queries.
- If the user greets (e.g., Hi, Hello, Vanakkam), respond EXACTLY with:
  "Vanakkam! I am XyntraChatbot here to assist your queries."

OUTPUT RULES (STRICT):
- Do NOT mention rules, decisions, reasoning, or explanations.
- Do NOT say things like "Rule 1", "According to the context", or "Based on the rules".
- Respond with ONLY the final answer intended for the user.
- Dont answer in one world like "Yes" or "No". Provide a complete sentence.
- Keep responses short, clear, and direct




Context:
{context}

Question:
{question}
"""
)
# =================================================

# ================= RAG CHAIN ======================
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)
# =================================================

# ================= API ROUTES =====================
@app.post("/chat")
def chat(q: Question):
    if len(q.query) > 500:
        return {"answer": "Query too long. Please ask a shorter question."}

    print("QUESTION FROM UI:", q.query)
    answer = rag_chain.invoke(q.query)
    return {"answer": answer}

@app.get("/")
def health():
    return {"status": "Backend running (OpenRouter)"}
# =================================================

# ================= STATIC FILES ===================
app.mount(
    "/site",
    StaticFiles(directory="website", html=True),
    name="site"
)

app.mount(
    "/chatbot",
    StaticFiles(directory="ui", html=True),
    name="chatbot"
)
# =================================================

# ================= RUN ============================
# py -m uvicorn rag_chatbot:app --reload
# =================================================

