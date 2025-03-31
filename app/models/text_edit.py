from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class TextEdit(Base):
    __tablename__ = "text_edits"

    id = Column(Integer, autoincrement=True, primary_key=True)  # unique = True ??
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)

    style = Column(String(50))
    model_used = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="text_edits")
