from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Supply Chain Decision System",
    description="Forecasts demand and generates actionable reorder decisions",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
