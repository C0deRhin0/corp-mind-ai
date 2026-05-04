from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_ask import router

app = FastAPI(title="corp-mind-ai", version="0.2.0-poc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
