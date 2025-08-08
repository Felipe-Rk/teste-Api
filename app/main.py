from fastapi import FastAPI
from app.db import Base, engine
from app.core.config import API_PREFIX
from app.routers import users, posts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social API", version="1.0.0")
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(posts.router, prefix=API_PREFIX)
