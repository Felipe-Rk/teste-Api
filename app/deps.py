from fastapi import Query
from app.core.config import PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX

def pagination_params(
    limit: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX),
    offset: int = Query(0, ge=0),
):
    return {"limit": limit, "offset": offset}
