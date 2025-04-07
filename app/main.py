from fastapi import FastAPI

from app.api import routers

app = FastAPI(
    title="SayItNative",
    description="An API to improve English text with AI",
    version="0.0.1"
)


app.include_router(routers.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
