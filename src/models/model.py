from sqlalchemy.orm import Mapped, mapped_column
from src.models.database import Base
from sqlalchemy import String

class Users(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255),nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(50),unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))