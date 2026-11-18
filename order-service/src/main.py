from contextlib import asynccontextmanager

import fastapi
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.routes import router
from src.db.database import init_db


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    init_db()
    yield


app = fastapi.FastAPI(title="Order Service", version="1.0.0", lifespan=lifespan)
app.include_router(router)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
