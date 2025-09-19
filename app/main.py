from fastapi import FastAPI
from app.routers import question_type_router

app = FastAPI(
    title="IELTS Platform API",
    version="0.1.0"
)

app.include_router(question_type_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the IELTS Platform API!"}