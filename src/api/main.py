from fastapi import FastAPI
from loguru import logger
from src.config import settings

app = FastAPI(title="Prism API", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Prism Fund Portfolio Optimization API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
