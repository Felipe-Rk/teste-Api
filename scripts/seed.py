import math
from faker import Faker
from sqlalchemy import insert
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal, Base
from app import models

fake = Faker()

USERS = 1000
POSTS_PER_USER = 1000
BATCH = 10_000  # lote de inserts para não estourar memória

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Usuários
        if db.query(models.User).count() < USERS:
            users_data = [
                {"username": f"user_{i}", "email": f"user_{i}@example.com", "posts_count": 0}
                for i in range(USERS)
            ]
            db.execute(insert(models.User), users_data)
            db.commit()

        user_ids = [u.id for u in db.query(models.User.id).order_by(models.User.id)]
        total_posts = USERS * POSTS_PER_USER
        print(f"Gerando {total_posts:,} posts...")

        # Inserção por lotes
        remaining = total_posts
        idx_user = 0
        buffer = []
        for _ in range(total_posts):
            uid = user_ids[idx_user]
            buffer.append({
                "user_id": uid,
                "content": fake.sentence(nb_words=12),
            })
            idx_user = (idx_user + 1) % len(user_ids)

            if len(buffer) >= BATCH:
                db.execute(insert(models.Post), buffer)
                buffer.clear()
                db.commit()

        if buffer:
            db.execute(insert(models.Post), buffer)
            db.commit()

        # Atualiza posts_count via agregação (mais rápido que ORM durante geração)
        with engine.begin() as conn:
            conn.exec_driver_sql("""
                UPDATE users u
                SET posts_count = p.cnt
                FROM (
                    SELECT user_id, COUNT(*)::int AS cnt
                    FROM posts
                    GROUP BY user_id
                ) p
                WHERE u.id = p.user_id
            """)
        print("Seed finalizado.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
