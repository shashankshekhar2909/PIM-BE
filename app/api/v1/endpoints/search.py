from fastapi import APIRouter

router = APIRouter()

@router.post("/index/init")
def init_index():
    # TODO: Implement search index init (no Typesense)
    return {"msg": "Init search index"}

@router.post("/reindex")
def reindex():
    # TODO: Implement reindex (no Typesense)
    return {"msg": "Reindex"}

@router.get("")
def search():
    # TODO: Implement main product search (no Typesense)
    return {"msg": "Search endpoint"} 