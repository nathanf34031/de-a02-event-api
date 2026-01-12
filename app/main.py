import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import motor.motor_asyncio
import certifi
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum



load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "event_management_db")


if not MONGO_URI:
    raise RuntimeError("Mongo URI not found in .env File")

app = FastAPI(title="Event Management API")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
    )

db = client[DB_NAME]
venues_collection = db["venues"]
bookings_collection = db["bookings"]

class VenueCreate(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    capacity: int = Field(..., ge=1)

class VenueUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)
    capacity: int | None = Field(default=None, ge=1)

class BookingCreate(BaseModel):
    event_id: str = Field(..., min_length=1)
    attendee_id: str = Field(..., min_length=1)
    ticket_type: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1)

class BookingUpdate(BaseModel):
    event_id: str | None = Field(..., min_length=1)
    attendee_id: str | None = Field(..., min_length=1)
    ticket_type: str | None = Field(..., min_length=1)
    quantity: int | None = Field(..., ge=1)




@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/venues")
async def get_venues():
    venues = await venues_collection.find().to_list(100)

    for v in venues:
        v["_id"] = str(v["_id"])

    return venues

@app.post("/venues", status_code=201)
async def createVenues(payload: VenueCreate):
    doc = payload.model_dump()
    result = await venues_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return doc

@app.get("/venues/{venue_id}")
async def get_venue_by_id(venue_id: str):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid Venue ID format")
    
    oid = ObjectId(venue_id)

    venue = await venues_collection.find_one({"_id": oid})

    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not Found")
    
    venue["_id"] = str(venue["_id"])

    return venue


@app.put("/venues/{venue_id}")
async def update_venue_(venue_id: str, payload: VenueUpdate):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue ID Format")
    
    oid = ObjectId(venue_id)

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    
    result = await venues_collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    venue = await venues_collection.find_one({"_id": oid})
    venue["_id"] = str(venue["_id"])
    return venue

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue ID Format")
    
    oid = ObjectId(venue_id)

    result = await venues_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    

    return{"deleted": True, "venue_id": venue_id}
    

@app.get("/bookings")
async def get_bookings():
    bookings = await bookings_collection.find().to_list(100)

    for v in bookings:
        v["_id"] = str(v["_id"])

    return bookings


@app.post("/bookings", status_code=201)
async def createBookings(payload: BookingCreate):
    doc = payload.model_dump()
    result = await bookings_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return doc


@app.put("/bookings/{booking_id}")
async def update_booking_(booking_id: str, payload: BookingUpdate):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid Booking ID Format")
    
    oid = ObjectId(booking_id)

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    
    result = await bookings_collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking = await bookings_collection.find_one({"_id": oid})
    booking["_id"] = str(booking["_id"])
    return booking


@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid Booking ID Format")
    
    oid = ObjectId(booking_id)

    result = await bookings_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    

    return{"deleted": True, "booking_id": booking_id}