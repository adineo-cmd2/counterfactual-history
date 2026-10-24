from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
import app.models.user  # noqa: F401
import app.models.simulation_session  # noqa: F401
import app.models.sim_step  # noqa: F401
import app.models.sim_edge  # noqa: F401
import app.models.branch_node  # noqa: F401
from app.api.routes import simulate

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Counterfactual History Simulator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4326"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(simulate.router, prefix="/api/simulate", tags=["simulate"])
