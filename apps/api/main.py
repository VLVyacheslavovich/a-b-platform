from typing import Union
from fastapi import FastAPI
from .routers import experiments, assign


app = FastAPI(title="AB Platform API")
app.include_router(experiments.router)
app.include_router(assign.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

