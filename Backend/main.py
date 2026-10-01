from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Header, HTTPException, Depends, APIRouter, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import time


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "my-secret-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


app = FastAPI()
frontend_directory = Path(__file__).resolve().parent.parent / "frontend"

# app.mount("/static", StaticFiles(directory=frontend_directory), name="static")

#admin route group
admin = APIRouter(prefix="/admin", tags=["admin"])


app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://127.0.0.1:5500"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"Unhandled error on {request.url.path}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-process-time"] = str(time.perf_counter() - start)
    return response

@app.middleware("http")
async def m1(request: Request, call_next):
    print("m1 before")
    response = await call_next(request)
    print("m1 after")
    return response

@app.middleware("http")
async def m2(request: Request, call_next):
    print("m2 before")
    response = await call_next(request)
    print("m2 after")
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    print(f"{request.method} {request.url.path} ->"
          f" {response.status_code} {time.perf_counter() - start:.3f}s")
    return response

@app.get("/visits")
def count_visits(response: Response, visits: str | None = Cookie(default=None)):
    count = int(visits) if visits else 0
    count += 1
    response.set_cookie(key="visits", value=str(count),
                        httponly=True, samesite="lax")
    return {"visits": count}
class PredictionRequest(BaseModel):
    area: float
    bedrooms: int
    location: str = "unknown"

@app.get("/")
def read_root():
    return {"message": "Hello: World"}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/add")
async def add(a: int, b: int):
    await asyncio.sleep(1)  
    return {"result": a + b}

@app.get("/predict")
def predict_price(area: float, bedrooms: int, location: str = "unknown"):
    base_price = 500000000
    m2_area_price = 15000000
    bedroom_price = 50000000
    if location == "hanoi":
        location_multiplier = 1.3
    elif location == "hcmc":
        location_multiplier = 1.25
    else:
        location_multiplier = 1.0
    final_price = round(((base_price + (area * m2_area_price) + (bedrooms * bedroom_price)) * location_multiplier), 2)
    return {
        "predicted_price": final_price,
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
    }

@app.post("/predict")
def predict_price_from_body(request: PredictionRequest):
    return predict_price(request.area, request.bedrooms, request.location)

_cart = []

@app.post("/card/add")
def addCartItem(item: str):
    _cart.append(item)
    return item

@app.get("/card")
def getCart():
    print("--> Cart")
    return _cart

@app.get("/boom")
def boom():
    return 1/0

@app.get("/secure-data", dependencies=[Depends(verify_api_key)])
def secure_data():
    return {"ok": True}

@app.post("/login")
def login(response: Response):
    response.set_cookie