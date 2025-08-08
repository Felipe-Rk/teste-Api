# scripts/seed.py (trechos principais)
import os
from tqdm import tqdm
from sqlalchemy import insert
from app.db import SessionLocal
from app import models

USERS = int(os.getenv("USERS", 100))
POSTS_PER_USER = int(os.getenv("POSTS_PER_USER", 50))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10000))

def gen_users(n):
    for i in range(n):
        yield {"username": f"user{i}", "email": f"user{i}@example.com"}

def gen_posts(user_id, n):
    for j in range(n):
        yield {"user_id": user_id, "title": f"Post {j} - u{user_id}", "content": "..."}

def bulk_insert(conn, table, rows, batch_size=BATCH_SIZE):
    buf = []
    for r in rows:
        buf.append(r)
        if len(buf) >= batch_size:
            conn.execute(insert(table), buf)
            buf.clear()
    if buf:
        conn.execute(insert(table), buf)

def main():
    assert "postgresql" in os.getenv("DATABASE_URL", ""), "Seed grande exige Postgres"

    with SessionLocal() as session, session.begin():
        # Usuários com progresso
        print(f"Gerando {USERS} usuários...")
        bulk_insert(session, models.User.__table__, tqdm(gen_users(USERS), total=USERS))

    # Posts por usuário com progresso aninhado
    with SessionLocal() as session, session.begin():
        print(f"Gerando {USERS * POSTS_PER_USER:,} posts ({POSTS_PER_USER} por usuário)...")
        # barra externa por usuário
        for u_id in tqdm(range(1, USERS + 1), total=USERS, desc="Usuários"):
            posts_iter = gen_posts(u_id, POSTS_PER_USER)
            # barra interna por posts do usuário
            posts_iter = tqdm(posts_iter, total=POSTS_PER_USER, leave=False, desc=f"u{u_id:05d}")
            bulk_insert(session, models.Post.__table__, posts_iter)

    print("Seed concluído.")
    
if __name__ == "__main__":
    main()
