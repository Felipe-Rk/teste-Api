from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# User
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    posts: int | None = Field(default=0, ge=0)  # conforme exemplo do enunciado

class UserOut(BaseModel):
    id: int
    username: str
    class Config: from_attributes = True

class UserWithPostsOut(BaseModel):
    id: int
    username: str
    posts_count: int
    posts: list["PostOut"]

# Post
class PostCreate(BaseModel):
    user_id: int
    content: str = Field(min_length=1, max_length=1000)

class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    likes: int
    created_at: datetime
    class Config: from_attributes = True
