# API Social — FastAPI + SQLAlchemy + Docker

## Descrição

Este projeto é uma API RESTful para um sistema social simplificado, onde é possível gerenciar **usuários** e suas **postagens**.  
Ele foi desenvolvido para demonstrar boas práticas com **FastAPI**, **SQLAlchemy** e **PostgreSQL**, incluindo geração massiva de dados para testes de performance.

O projeto inclui:
- Endpoints para CRUD de usuários e posts;
- Script de **seed** capaz de gerar até **1.000 usuários × 1.000 posts/usuário** (1 milhão de registros);
- Testes automatizados com Pytest;
- Containerização com Docker Compose.

---

## Tecnologias utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) — Framework web rápido e moderno em Python
- [SQLAlchemy 2.x](https://docs.sqlalchemy.org/) — ORM para interação com banco de dados
- [PostgreSQL 16](https://www.postgresql.org/) — Banco de dados relacional
- [Pytest](https://docs.pytest.org/) — Framework de testes
- [Docker Compose](https://docs.docker.com/compose/) — Orquestração de containers

---

## Como rodar o projeto

### 1) Clonar repositório
```bash
git clone <url-do-repo>
cd teste-Api
```

### 2) Subir containers
```bash
docker compose up -d --build
```

- API: [http://localhost:8000](http://localhost:8000)  
- Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)  
- Banco de dados: `postgresql://postgres:postgres@localhost:5432/social`

---

## Popular o banco (Seed)

O script `scripts/seed.py` cria usuários e posts no banco.

### Desenvolvimento (rápido)
```bash
docker compose run --rm api bash -lc \
'USERS=50 POSTS_PER_USER=20 BATCH_SIZE=10000 python -m scripts.seed'
```

### Teste oficial (1.000 usuários × 1.000 posts/usuário)
```bash
docker compose run --rm api bash -lc \
'USERS=1000 POSTS_PER_USER=1000 BATCH_SIZE=20000 python -m scripts.seed'
```

**Saída esperada:**
```
Gerando 1,000 usuários...
Usuários ok.
Gerando 1,000,000 posts...
... 20,000/1,000,000
... 40,000/1,000,000
...
```

### Reset do banco antes do seed (opcional)
```bash
docker compose exec db psql -U postgres -d social -c \
"TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE;"
```

---

## Executar os testes

### Testes rápidos (unitários e smoke)
```bash
docker compose run --rm api bash -lc "pytest -q"
```

### Teste pesado (gera 1 milhão de posts)
> Marcado como `@pytest.mark.heavy` para evitar execução acidental.
```bash
docker compose run --rm api bash -lc "pytest -q -m heavy tests/test_seed_one_million.py"
```

---

## Estrutura do projeto

```
app/
  core/           # Configurações e inicialização
  models.py       # Modelos SQLAlchemy
  routers/        # Rotas organizadas por domínio
  schemas.py      # Schemas Pydantic
  main.py         # Ponto de entrada da API
scripts/
  seed.py         # Script de geração de dados
tests/
  test_smoke.py   # Testes básicos
Dockerfile
docker-compose.yml
requirements.txt
```

---

## Observações

- Para o seed massivo, **utilize Postgres** (não SQLite);
- Ajuste `BATCH_SIZE` para equilibrar velocidade e uso de memória;
- Para ambientes de teste, reduza `USERS` e `POSTS_PER_USER` para execução mais rápida;
- Remova a chave `version:` do `docker-compose.yml` para evitar o warning do Compose.
