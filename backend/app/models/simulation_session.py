from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    premise: Mapped[str] = mapped_column(Text, default="")
    divergence_year: Mapped[int] = mapped_column(Integer, default=0)
    parent_session_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("simulation_sessions.id"), nullable=True, default=None
    )
    branch_from_step_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sim_steps.id"), nullable=True, default=None
    )
    branch_note: Mapped[str] = mapped_column(Text, default="")
