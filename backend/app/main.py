from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import models
from app.database import engine
from app.routes import web_url

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="URL Shortener API", lifespan=lifespan)

origins=[
    "http://localhost:3000",
    # prod frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(web_url.router, tags=["web_urls"])

@app.get("/")
async def root():
    return {"message": "URL Shortener API"}