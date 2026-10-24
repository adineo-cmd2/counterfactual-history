from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SimEdge(Base):
    __tablename__ = "sim_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_sessions.id"), index=True)
    from_step_id: Mapped[int] = mapped_column(Integer, ForeignKey("sim_steps.id"))
    to_step_id: Mapped[int] = mapped_column(Integer, ForeignKey("sim_steps.id"))
