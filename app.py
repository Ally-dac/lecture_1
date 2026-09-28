# ECSE3038 - Week 4, Lecture 1 - starter
# Monday's API with the hard-coded list emptied.
# Run:  uvicorn app:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["devices"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


readings = []


@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))


@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404,
                            detail="No device called " + name)
    return device


@app.post("/devices", status_code=201)
def create_device(device: Device):
    existing_device = devices.find_one({"name": device.name})

    if existing_device is not None:
        raise HTTPException(
            status_code=409,
            detail="A device called " + device.name + " already exists"
        )

    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    return new_device
