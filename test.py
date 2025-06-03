from contextlib import asynccontextmanager
from fastapi import FastAPI
from rich import print
from rich.panel import Panel

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print(Panel("🚀 Server started...", border_style="green"))
    yield
    print(Panel("🛑 Server is stopped...", border_style="red"))

app = FastAPI(lifespan=lifespan_handler)

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI application!"}
