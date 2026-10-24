from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BranchNode(Base):
    __tablename__ = "branch_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_sessions.id"), index=True)
    step_id: Mapped[int] = mapped_column(Integer, ForeignKey("sim_steps.id"))
    child_session_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_sessions.id"))
    label: Mapped[str] = mapped_column(String(500), default="")
