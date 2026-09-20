# Week 07 — Extended Lab 4

FastAPI routing and request/response practice.

## Run the API

```text
```powershell
cd "C:\New folder\Backend"
..\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the API with Swagger UI.

## Lab 4 endpoints

- `GET /items`: filtering, searching, sorting, and pagination envelope.
- `POST /items`: creates an item and rejects duplicate names with `409`.
- `PUT /items/{item_id}`: replaces an item and checks duplicate names.
- `PATCH /items/{item_id}`: changes only fields sent by the client.
- `GET /items/{item_id}` and `DELETE /items/{item_id}`: retrieve or delete an item.
- `POST /predict/house-price`: validates a request body and returns a toy VND prediction.

### List query parameters

`GET /items` accepts:

```text
skip=0&limit=10&min_price=0&max_price=100000&q=phone&sort_by=price&order=desc
```

Filtering and searching happen before sorting, and sorting happens before `skip`/`limit` slicing. The response is:

```json
{
   "items": [],
   "total": 0,
   "skip": 0,
   "limit": 10
}
```

### PATCH example

```json
{
   "price": 250000
}
```

Only `price` changes; the existing `name` remains unchanged. An unknown item returns `404`.

### House-price example

```json
{
   "area_sqm": 80,
   "bedrooms": 3,
   "distance_to_center_km": 5
}
```

The request returns a response such as:

```json
{
   "predicted_price": 1235000000,
   "currency": "VND"
}
```

`area_sqm` must be greater than `0`, and `bedrooms` must be at least `0`. Invalid values return `422` automatically through Pydantic `Field` validation.

