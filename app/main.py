import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import motor.motor_asyncio
import certifi
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from enum import Enum
from datetime import date


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
events_collection = db["events"]
attendees_collection = db["attendees"]

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


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    venue_id: str = Field(..., min_length=1)  # store ObjectId as string in requests
    max_attendees: int = Field(..., ge=1)

class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    date: str | None = Field(default=None, min_length=1)
    venue_id: str | None = Field(default=None, min_length=1)
    max_attendees: int | None = Field(default=None, ge=1)



class AttendeeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)

class AttendeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    phone: str | None = Field(default=None, min_length=1)


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

@app.get("/bookings/{booking_id}")
async def get_booking_by_id(booking_id: str):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID format")
    
    oid = ObjectId(booking_id)

    booking = await bookings_collection.find_one({"_id": oid})

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not Found")
    
    booking["_id"] = str(booking["_id"])

    return booking


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


@app.get("/events")
async def get_events():
    events = await events_collection.find().to_list(100)

    for e in events:
        e["_id"] = str(e["_id"])

    return events


@app.post("/events", status_code=201)
async def create_event(payload: EventCreate):
    doc = payload.model_dump()
    result = await events_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return doc


@app.get("/events/{event_id}")
async def get_event_by_id(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid Event ID format")

    oid = ObjectId(event_id)
    event = await events_collection.find_one({"_id": oid})

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event["_id"] = str(event["_id"])
    return event


@app.put("/events/{event_id}")
async def update_event(event_id: str, payload: EventUpdate):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid Event ID format")

    oid = ObjectId(event_id)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = await events_collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    event = await events_collection.find_one({"_id": oid})
    event["_id"] = str(event["_id"])
    return event


@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid Event ID format")

    oid = ObjectId(event_id)
    result = await events_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"deleted": True, "event_id": event_id}


@app.get("/attendees")
async def get_attendees():
    attendees = await attendees_collection.find().to_list(100)

    for a in attendees:
        a["_id"] = str(a["_id"])

    return attendees


@app.post("/attendees", status_code=201)
async def create_attendee(payload: AttendeeCreate):
    doc = payload.model_dump()
    result = await attendees_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return doc


@app.get("/attendees/{attendee_id}")
async def get_attendee_by_id(attendee_id: str):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid Attendee ID format")

    oid = ObjectId(attendee_id)
    attendee = await attendees_collection.find_one({"_id": oid})

    if attendee is None:
        raise HTTPException(status_code=404, detail="Attendee not found")

    attendee["_id"] = str(attendee["_id"])
    return attendee


@app.put("/attendees/{attendee_id}")
async def update_attendee(attendee_id: str, payload: AttendeeUpdate):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid Attendee ID format")

    oid = ObjectId(attendee_id)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = await attendees_collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    attendee = await attendees_collection.find_one({"_id": oid})
    attendee["_id"] = str(attendee["_id"])
    return attendee


@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid Attendee ID format")

    oid = ObjectId(attendee_id)
    result = await attendees_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    return {"deleted": True, "attendee_id": attendee_id}

