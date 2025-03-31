from fastapi import APIRouter

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def hello():
    return {"message": "Hello from SayItNative!"}
