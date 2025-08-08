from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from app.deps import pagination_params

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("", response_model=schemas.PostOut, status_code=201)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db)):
    user = db.get(models.User, payload.user_id)
    if not user:
        raise HTTPException(404, "user não encontrado")
    post = models.Post(user_id=payload.user_id, content=payload.content)
    db.add(post)
    # mantém contagem denormalizada
    user.posts_count += 1
    db.commit()
    db.refresh(post)
    return post

@router.post("/{post_id}/like", status_code=204)
def like_post(post_id: int, db: Session = Depends(get_db)):
    # incremento atômico no banco
    res = db.execute(
        update(models.Post)
        .where(models.Post.id == post_id)
        .values(likes=models.Post.likes + 1)
        .execution_options(synchronize_session=False)
    )
    if res.rowcount == 0:
        raise HTTPException(404, "post não encontrado")
    db.commit()
    return

@router.get("/feed", response_model=list[schemas.PostOut])
def list_feed(p=Depends(pagination_params), db: Session = Depends(get_db)):
    stmt = (
        select(models.Post)
        .order_by(models.Post.created_at.desc(), models.Post.id.desc())
        .limit(p["limit"])
        .offset(p["offset"])
    )
    return db.scalars(stmt).all()

@router.get("/by-user/{user_id}", response_model=list[schemas.PostOut])
def list_posts_by_user(user_id: int, p=Depends(pagination_params), db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(404, "user não encontrado")
    stmt = (
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.created_at.desc())
        .limit(p["limit"])
        .offset(p["offset"])
    )
    return db.scalars(stmt).all()
