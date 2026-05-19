from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import hashlib

MONGO_URI = "mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "handyconnect"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

users = db["users"]
services = db["services"]
messages = db["messages"]
reviews = db["reviews"]

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def now():
    return datetime.now()

users.delete_many({})
services.delete_many({})
messages.delete_many({})
reviews.delete_many({})

customer_id = ObjectId()
worker1_id = ObjectId()
worker2_id = ObjectId()
service_id = ObjectId()

users.insert_many([
    {
        "_id": customer_id,
        "email": "customer@example.com",
        "phone_number": "03001234567",
        "password_hash": hash_password("123456"),
        "first_name": "Ali",
        "last_name": "Khan",
        "avatar_url": "",
        "role": "customer",
        "date_joined": now(),
        "addresses": [
            {
                "street": "Street 12",
                "city": "Wah Cantt",
                "state": "Punjab",
                "postal_code": "47040",
                "country": "Pakistan",
                "created_at": now()
            }
        ],
        "created_at": now(),
        "updated_at": now()
    },
    {
        "_id": worker1_id,
        "email": "electrician@example.com",
        "phone_number": "03111234567",
        "password_hash": hash_password("123456"),
        "first_name": "Ahmed",
        "last_name": "Raza",
        "avatar_url": "",
        "role": "worker",
        "profession": "Electrician",
        "skills": ["wiring", "fan repair", "switchboard repair"],
        "availability": True,
        "avg_rating": 5,
        "verified_status": True,
        "earnings": 0,
        "created_at": now(),
        "updated_at": now()
    },
    {
        "_id": worker2_id,
        "email": "plumber@example.com",
        "phone_number": "03221234567",
        "password_hash": hash_password("123456"),
        "first_name": "Usman",
        "last_name": "Malik",
        "avatar_url": "",
        "role": "worker",
        "profession": "Plumber",
        "skills": ["pipe repair", "water leakage", "bathroom fitting"],
        "availability": True,
        "avg_rating": 4,
        "verified_status": True,
        "earnings": 0,
        "created_at": now(),
        "updated_at": now()
    }
])

services.insert_one({
    "_id": service_id,
    "worker_id": worker1_id,
    "customer_id": customer_id,
    "service_title": "Fan Repair",
    "description": "Ceiling fan is making noise.",
    "accepted_status": True,
    "status": "completed",
    "location": "Wah Cantt",
    "details": {
        "price": 1500,
        "price_unit": "PKR",
        "start_date": None,
        "expected_end": None,
        "completed_date": now(),
        "paid_status": True,
        "created_at": now(),
        "updated_at": now()
    },
    "created_at": now(),
    "updated_at": now()
})

messages.insert_many([
    {
        "service_id": service_id,
        "sender_id": customer_id,
        "content": "Hello, I need fan repair service.",
        "is_read": True,
        "created_at": now()
    },
    {
        "service_id": service_id,
        "sender_id": worker1_id,
        "content": "I can visit today.",
        "is_read": False,
        "created_at": now()
    }
])

reviews.insert_one({
    "customer_id": customer_id,
    "worker_id": worker1_id,
    "service_id": service_id,
    "rating": 5,
    "comment": "Good service and quick response.",
    "review_date": now(),
    "images": []
})

print("Sample data inserted.")
print()
print("Demo logins:")
print("Customer: customer@example.com / 123456")
print("Worker 1: electrician@example.com / 123456")
print("Worker 2: plumber@example.com / 123456")