from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SimStep(Base):
    __tablename__ = "sim_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_sessions.id"), index=True)
    gen: Mapped[int] = mapped_column(Integer, default=0)
    idx: Mapped[int] = mapped_column(Integer, default=0)
    domain: Mapped[str] = mapped_column(String(100), default="")
    year_range: Mapped[str] = mapped_column(String(100), default="")
    event: Mapped[str] = mapped_column(Text, default="")
    probability: Mapped[str] = mapped_column(String(50), default="medium")
    analogy: Mapped[str] = mapped_column(Text, default="")
