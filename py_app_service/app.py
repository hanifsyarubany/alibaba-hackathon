from fastapi import FastAPI, Depends, HTTPException
from py_app_service.database import mongo_instance
from py_app_service.models import UserCreate, OnboardCreate, ChatbotModel
from fastapi.middleware.cors import CORSMiddleware
from py_app_service.workers import prompting_worker
from py_app_service.services import chatbot
import datetime, asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Background task holder
worker_task = None

@app.on_event("startup")
async def worker_runner():
    global worker_task  # Ensure the task can be accessed globally if needed
    # Start the prompting_worker in the background without blocking FastAPI
    worker_task = asyncio.create_task(prompting_worker())
    print("Worker started in the background.")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/onboarding")
async def onboarding(data: OnboardCreate):
    existing_user = await mongo_instance["business"].find_one(
        {"business_id": data.business_id}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Business already registered")

    __bus_dict = data.dict()
    __bus_dict["success"] = None
    __bus_dict["failed"] = None
    now = datetime.datetime.now()
    __bus_dict["created_at"] = datetime.datetime.timestamp(now)
    result = await mongo_instance["business"].insert_one(__bus_dict)
    __bus_dict["_id"] = str(result.inserted_id)
    return __bus_dict


@app.get("/onboarding/{buzz_id}")
async def get_onboarding_status(buzz_id: str):
    exist_status = await mongo_instance["business"].find_one({"business_id": buzz_id})
    if not exist_status:
        raise HTTPException(status_code=400, detail="Business not registered yet")

    exist_status["_id"] = ""
    return exist_status

@app.post("/chatbot/{buzz_id}")
async def get_onboarding_status(buzz_id: str, data:ChatbotModel):
    exist_status = await mongo_instance["business"].find_one({"business_id": buzz_id})
    if not exist_status:
        raise HTTPException(status_code=400, detail="Business not registered yet")

    exist_status["_id"] = ""

    p = chatbot(buzz_id, data.question)

    return {"message": p}


@app.post("/ignore-this")
async def create_new_user(user: UserCreate):
    existing_user = await mongo_instance["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = user.dict()
    result = await mongo_instance["users"].insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return user_dict
