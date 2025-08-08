# tests/test_seed_one_million.py
import os
import subprocess
import sqlalchemy as sa
import pytest

USERS = 1000
POSTS_PER_USER = 1000
EXPECTED_POSTS = USERS * POSTS_PER_USER

@pytest.mark.heavy
def test_seed_one_million():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/social")
    assert db_url.startswith("postgresql+psycopg2"), (
        "Este teste pesado exige Postgres. Ajuste DATABASE_URL para o banco do docker-compose."
    )

    engine = sa.create_engine(db_url, future=True)

    # 1) Reset das tabelas (evita lixo de runs anteriores)
    with engine.begin() as conn:
        conn.execute(sa.text("TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE;"))

    # 2) Rodar o seed oficial: 1000 x 1000
    env = os.environ.copy()
    env["USERS"] = str(USERS)
    env["POSTS_PER_USER"] = str(POSTS_PER_USER)
    env["BATCH_SIZE"] = env.get("BATCH_SIZE", "20000")

    # Dica: este comando deve ser executado **dentro do container** ou local
    # com DATABASE_URL apontando para o Postgres do compose.
    subprocess.run(["python", "-m", "scripts.seed"], check=True, env=env)

    # 3) Asserts objetivos
    with engine.connect() as conn:
        users = conn.execute(sa.text("SELECT COUNT(*) FROM users")).scalar_one()
        posts = conn.execute(sa.text("SELECT COUNT(*) FROM posts")).scalar_one()
        min_max_avg = conn.execute(sa.text("""
            WITH c AS (
              SELECT user_id, COUNT(*) AS cnt
              FROM posts
              GROUP BY user_id
            )
            SELECT MIN(cnt) AS min_cnt, MAX(cnt) AS max_cnt, AVG(cnt)::int AS avg_cnt
            FROM c;
        """)).one()

    assert users == USERS
    assert posts == EXPECTED_POSTS
    assert min_max_avg.min_cnt == POSTS_PER_USER
    assert min_max_avg.max_cnt == POSTS_PER_USER
    assert min_max_avg.avg_cnt == POSTS_PER_USER
