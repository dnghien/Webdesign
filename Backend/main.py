from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float


class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int


class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float


class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "Frontend"
_items: list[ItemPublic] = []
_next_id = 1


def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None


def _name_exists(name: str, excluded_id: int | None = None) -> bool:
    normalized_name = name.casefold()
    return any(
        item.id != excluded_id and item.name.casefold() == normalized_name
        for item in _items
    )


app = FastAPI()
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/app.js")
def read_app_js():
    return FileResponse(FRONTEND_DIR / "app.js")


@app.get("/style.css")
def read_style_css():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/items/me")
def read_item_me():
    return {"item_id": "Welcome!"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/items", response_model=ItemListResponse)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    filtered = _items
    if min_price is not None:
        filtered = [item for item in filtered if item.price >= min_price]
    if max_price is not None:
        filtered = [item for item in filtered if item.price <= max_price]
    if q:
        filtered = [item for item in filtered if q.casefold() in item.name.casefold()]

    filtered = sorted(
        filtered,
        key=lambda item: getattr(item, sort_by),
        reverse=order == "desc",
    )
    total = len(filtered)
    return ItemListResponse(
        items=filtered[skip: skip + limit],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(item: ItemCreate):
    global _next_id
    if _name_exists(item.name):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    new_item = ItemPublic(id=_next_id, name=item.name, price=item.price)
    _items.append(new_item)
    _next_id += 1
    return new_item


@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, item: ItemCreate):
    existing = _find(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.name.casefold() != existing.name.casefold() and _name_exists(item.name, item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    updated_item = ItemPublic(id=existing.id, name=item.name, price=item.price)
    index = _items.index(existing)
    _items[index] = updated_item
    return updated_item


@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, item: ItemUpdate):
    existing = _find(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = item.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"].casefold() != existing.name.casefold():
        if _name_exists(updates["name"], item_id):
            raise HTTPException(status_code=409, detail="Item with this name already exists")

    updated_item = existing.model_copy(update=updates)
    _items[_items.index(existing)] = updated_item
    return updated_item


@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(request: HousePriceRequest):
    price = (
        request.area_sqm * 15_000_000
        - request.distance_to_center_km * 5_000_000
        + request.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price)


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    _items.remove(item)
    return {"deleted_id": item_id, "item": item}
