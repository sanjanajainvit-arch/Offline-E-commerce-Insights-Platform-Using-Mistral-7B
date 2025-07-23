from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from query_engine import handle_question

logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="E-commerce AI Agent",
    description="Ask questions about ad sales, total sales, and product eligibility.",
    version="1.0"
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "E-commerce AI Agent is running"}

@app.post("/query")
def query_data(request: QuestionRequest):
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        answer = handle_question(request.question.strip())
        return {"question": request.question, "answer": answer, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to E-commerce AI Agent",
            "endpoints": {"health": "/health", "query": "/query (POST)", "docs": "/docs"}}
