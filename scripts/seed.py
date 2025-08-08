# scripts/seed.py
import os
import math
import argparse
from faker import Faker
from sqlalchemy import insert, text
from sqlalchemy.orm import Session
from app.db import engine, Base
from app import models

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--users", type=int, default=int(os.getenv("USERS", 1000)))
    p.add_argument("--posts-per-user", type=int, default=int(os.getenv("POSTS_PER_USER", 1000)))
    p.add_argument("--batch-size", type=int, default=int(os.getenv("BATCH_SIZE", 10000)))
    return p.parse_args()

def create_users(db: Session, qty: int, fake: Faker) -> list[int]:
    rows = []
    for i in range(qty):
        rows.append({
            "username": f"{fake.user_name()}_{i}",
            "email": f"user_{i}@example.com",
            "posts_count": 0,
        })
    # insert em lote e retornar ids
    result = db.execute(
        insert(models.User).returning(models.User.id),
        rows
    )
    return [r[0] for r in result.fetchall()]

def seed_posts(db: Session, user_ids: list[int], posts_per_user: int, batch_size: int, fake: Faker):
    total_posts = len(user_ids) * posts_per_user
    print(f"Gerando {total_posts:,} posts...")

    batch = []
    written = 0

    for uid in user_ids:
        for _ in range(posts_per_user):
            batch.append({
                "user_id": uid,
                "content": fake.text(max_nb_chars=120),
                "likes": 0,
                # created_at = default no banco (func.now())
            })
            if len(batch) >= batch_size:
                db.execute(insert(models.Post), batch)
                written += len(batch)
                batch.clear()
                # atualização do contador do usuário em massa
                # otimização simples: faz depois via UPDATE agregando
                print(f"... {written:,}/{total_posts:,}")

    if batch:
        db.execute(insert(models.Post), batch)
        written += len(batch)
        print(f"... {written:,}/{total_posts:,}")

    # Atualiza posts_count de todos os users de uma vez (Postgres)
    db.execute(text("""
        UPDATE users u
        SET posts_count = p.cnt
        FROM (
            SELECT user_id, COUNT(*)::int AS cnt
            FROM posts
            GROUP BY user_id
        ) p
        WHERE p.user_id = u.id
    """))

def main():
    args = parse_args()
    fake = Faker()

    # Cria schema
    Base.metadata.create_all(bind=engine)

    # Otimizações por backend
    with engine.connect() as conn:
        if engine.url.get_backend_name().startswith("sqlite"):
            conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            conn.exec_driver_sql("PRAGMA synchronous=OFF;")
        conn.commit()

    with Session(engine, autoflush=False, expire_on_commit=False) as db:
        # Users
        print(f"Gerando {args.users:,} usuários...")
        user_ids = create_users(db, args.users, fake)
        db.commit()
        print("Usuários ok.")

        # Posts em lote
        seed_posts(db, user_ids, args.posts_per_user, args.batch_size, fake)
        db.commit()
        print("Seed finalizado.")

if __name__ == "__main__":
    main()
