from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    posts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        index=True
        )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True, 
        nullable=False
        )
    content: Mapped[str] = mapped_column(
        Text, 
        nullable=False
        )
    likes: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=func.now()
        )

    user = relationship("User", back_populates="posts")

Index("ix_posts_created_at_desc", Post.created_at.desc())
Index("ix_posts_user_id_created_at", Post.user_id, Post.created_at.desc())
