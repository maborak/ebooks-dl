from fastapi import FastAPI
from ebooksdl.utils import data

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "Lets CI on Heroku second edition"}


@app.get("/entries")
def entries():
    n = data.DataEngine()
    return {"total": n.entries()}


@app.get("/otoms/{item_id}")
def read_otom(item_id: int):
    return {"item_id": item_id}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
