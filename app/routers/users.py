from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from app.deps import pagination_params

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=schemas.UserOut, status_code=201)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # checagens simples de unicidade
    if db.scalar(select(func.count()).select_from(models.User).where(models.User.username == payload.username)):
        raise HTTPException(400, "username já cadastrado")

    if db.scalar(select(func.count()).select_from(models.User).where(models.User.email == payload.email)):
        raise HTTPException(400, "email já cadastrado")

    user = models.User(
        username=payload.username, 
        email=payload.email, 
        posts_count=payload.posts or 0,
        )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("", response_model=list[schemas.UserOut])
def list_users(p=Depends(pagination_params), db: Session = Depends(get_db)):
    stmt = select(models.User).order_by(models.User.id).limit(p["limit"]).offset(p["offset"])
    return db.scalars(stmt).all()

@router.get("/with-posts", response_model=list[schemas.UserWithPostsOut])
def list_users_with_posts(
    p=Depends(pagination_params),
    posts_limit: int = 5,
    db: Session = Depends(get_db),
):
    # Pagina usuários e inclui últimos N posts de cada
    users = db.scalars(
        select(models.User).order_by(models.User.id).limit(p["limit"]).offset(p["offset"])
    ).all()

    # Evita N+1: busca posts em bloco
    if not users:
        return []
    user_ids = [u.id for u in users]
    posts = db.execute(
        select(models.Post)
        .where(models.Post.user_id.in_(user_ids))
        .order_by(models.Post.user_id, models.Post.created_at.desc())
    ).scalars().all()

    # Agrupa e corta por usuário
    posts_by_user: dict[int, list[models.Post]] = {}
    for post in posts:
        lst = posts_by_user.setdefault(post.user_id, [])
        if len(lst) < posts_limit:
            lst.append(post)

    out = []
    for u in users:
        out.append({
            "id": u.id,
            "username": u.username,
            "posts_count": u.posts_count,
            "posts": posts_by_user.get(u.id, []),
        })
    return out
