# Week 06 Assignment — Mini House-Price Prediction API

## Project Structure

```text
project/
├── Frontend/
│   └── Webdesign/
│       └── house_form.html
├── backend/
│   └── main.py
└── README.md
```

## How to Run the Project

### Step 1: Open the backend folder

Open the terminal in VS Code and run:

```bash
cd backend
```

### Step 2: Start the FastAPI server

```bash
uvicorn main:app --reload
```

The server will run at:

```text
http://127.0.0.1:8000
```

### Step 3: Test the API with Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

Expand `GET /predict`, click **Try it out**, and enter:

```text
area = 80
bedrooms = 3
location = hanoi
```

The returned JSON is:

```json
{
  "area": 80.0,
  "bedrooms": 3,
  "location": "hanoi",
  "predicted_price": 845000000.0
}
```

### Step 4: Test using the browser URL

The same request can be tested directly in the browser:

```text
http://127.0.0.1:8000/predict?area=80&bedrooms=3&location=hanoi
```

## Task 3 — Explanation

### Why does `/predict` still work without `location`?

`location` is an optional query parameter because it has a default value of `"other"`:

```python
location: str = "other"
```

Therefore, when `location` is not provided, FastAPI automatically uses `"other"`.

For example:

```text
http://127.0.0.1:8000/predict?area=80&bedrooms=3
```

still works.

### Why does `/predict` return a 422 error without `area`?

`area` is a required query parameter because it does not have a default value:

```python
area: float
```

FastAPI automatically validates the request. If `area` is missing, the request does not satisfy the required parameters, so FastAPI returns:

```text
422 Unprocessable Entity
```

## Task 4 — Serving the Frontend

The frontend is served directly by FastAPI using `StaticFiles`:

```python
app.mount("/static", StaticFiles(directory="../Frontend/Webdesign"), name="static")
```

The frontend can be opened at:

```text
http://127.0.0.1:8000/static/house_form.html
```

This means the frontend and backend use the same origin:

```text
127.0.0.1:8000
```

This avoids the cross-origin problem that would occur if the frontend were opened using Live Server on a different port.

## Task 5 — Connecting the Form to the API

The JavaScript in `house_form.html` reads the values of `area`, `bedrooms`, and `location` from the form.

It then sends a request using:

```javascript
fetch(`/predict?area=${area}&bedrooms=${bedrooms}&location=${location}`)
```

The URL `/predict` is a relative URL.

### Why does a relative URL work?

The frontend and the `/predict` API are served from the same FastAPI server and the same origin (`127.0.0.1:8000`). Therefore, the browser automatically sends the request to the same server.

The relative URL `/predict` is simpler than writing the full URL:

```text
http://127.0.0.1:8000/predict
```

The JavaScript then waits for the response, converts it to JSON, and displays the predicted price with thousands separators.

If the request fails, the page displays an error message instead of crashing.

## Task 6 — Bonus: POST /predict

A second `POST /predict` endpoint was added using a Pydantic model.

The model is:

```python
class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"
```

The POST endpoint receives the house information as a JSON request body.

Example:

```json
{
  "area": 80,
  "bedrooms": 3,
  "location": "hanoi"
}
```

### Difference between GET query parameters and POST JSON body

The GET endpoint sends data through the URL as query parameters:

```text
/predict?area=80&bedrooms=3&location=hanoi
```

The POST endpoint sends the data inside the request body as JSON.

## Conclusion

This project demonstrates the complete data flow:

```text
HTML Form
   ↓
JavaScript fetch()
   ↓
FastAPI /predict
   ↓
Python predict_price()
   ↓
JSON Response
   ↓
Predicted price displayed on the webpage
```
