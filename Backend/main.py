from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float


_items: list[ItemPublic] = []
_next_id = 1


def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None


app = FastAPI()
app.mount("/static", StaticFiles(directory="../Frontend"), name="static")


@app.get("/")
def read_root():
    return FileResponse("../Frontend/index.html")


@app.get("/app.js")
def read_app_js():
    return FileResponse("../Frontend/app.js")


@app.get("/style.css")
def read_style_css():
    return FileResponse("../Frontend/style.css")


@app.get("/items/me")
def read_item_me():
    return {"item_id": "Welcome!"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/items")
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, min_length=2),
):
    filtered = _items
    if q:
        filtered = [item for item in _items if q.lower() in item.name.lower()]
    return filtered[skip: skip + limit]


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(item: ItemCreate):
    global _next_id
    new_item = ItemPublic(id=_next_id, name=item.name, price=item.price)
    _items.append(new_item)
    _next_id += 1
    return new_item


@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, item: ItemCreate):
    existing = _find(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = ItemPublic(id=existing.id, name=item.name, price=item.price)
    index = _items.index(existing)
    _items[index] = updated_item
    return updated_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    _items.remove(item)
    return {"deleted_id": item_id, "item": item}