from fastapi import FastAPI, Depends, HTTPException
from py_app_service.database import mongo_instance
from py_app_service.models import UserCreate

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/ignore-this")
async def create_new_user(user: UserCreate):
    existing_user = await mongo_instance["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = user.dict()
    result = await mongo_instance["users"].insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return user_dict