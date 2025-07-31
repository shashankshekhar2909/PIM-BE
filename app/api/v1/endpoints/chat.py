from fastapi import APIRouter

router = APIRouter()

@router.post("/ask")
def ask():
    # TODO: Implement LLM ask
    return {"msg": "Ask endpoint"}

@router.post("/session")
def create_session():
    # TODO: Implement create chat session
    return {"msg": "Create chat session"}

@router.get("/session/{id}")
def resume_session(id: int):
    # TODO: Implement resume chat session
    return {"msg": f"Resume chat session {id}"}

@router.get("/favorites")
def get_favorites():
    # TODO: Implement get favorites
    return {"msg": "Get favorites"}

@router.get("/comparisons")
def get_comparisons():
    # TODO: Implement get comparisons
    return {"msg": "Get comparisons"} 