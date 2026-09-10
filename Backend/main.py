# from fastapi import FastAPI
# import asyncio
# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to my website!"}


# @app.get("/hello/{name}")  # Path parameter
# def hello(name: str):
#     return {"greeting": f"Hello {name}"}


# @app.get("/add")  # Query params: /add?a=2&b=3
# async def add(a: int, b: int):
#     await asyncio.sleep(3)  # Simulate a delay
#     return {"a": a, "b": b, "sum": a + b}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="../Frontend/Webdesign"), name="static")


def predict_price(area: float, bedrooms: int, location: str) -> float:
    price = 500_000_000
    price += 15_000_000 * area
    price += 50_000_000 * bedrooms

    if location.lower() == "hanoi":
        price *= 1.3
    elif location.lower() == "hcmc":
        price *= 1.25

    price = round(price / 1_000_000) * 1_000_000

    return price


@app.get("/predict")
# A normal def is enough because this endpoint does not perform asynchronous operations.
def predict(area: float, bedrooms: int, location: str = "other"):
    predicted_price = predict_price(area, bedrooms, location)

    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predicted_price
    }


# Task 6 - Bonus
class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"


@app.post("/predict")
def predict_post(house: HouseInput):
    predicted_price = predict_price(
        house.area,
        house.bedrooms,
        house.location
    )

    return {
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
        "predicted_price": predicted_price
    }

