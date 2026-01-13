# Database Essentials A02 - Event Management API

## Tech stack
- FastAPI (Python)
- MongoDB Atlas
- Motor (async MongoDB driver)

## Setup (local)
1. Create venv
2. Install dependencies using requirements.txt
3. Run the API locally using uvicorn
    (uvicorn app.main:app --reload)

    The api will then be available locally on http://127.0.0.1:8000  


## Deployment (Vercel)
- This project is deployed using Vercel

    - Entry point for vercek us api/index.py
    - Environment variables are set via Vercel Settings
    

## Notes
- This project uses Environment variables which are stored in  .env and not committed to git. This is done so that sensitive information is not committed. 

    A .env needs to be created in the project root with the following structure:

        MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/DB_NAME=event_management_db

MONGO_URI - MongoDB connection string.
DB_NAME - Name of the database.

For Vercel deployment and production use, these variables are set in the Vercel deployment setting.


