import os
from fastapi import FastAPI
from dotenv import load_dotenv
import motor.motor_asyncio
import certifi

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

@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/venues")
async def get_venues():
    venues = await venues_collection.find().to_list(100)

    for v in venues:
        v["_id"] = str(v["_id"])

    return venues