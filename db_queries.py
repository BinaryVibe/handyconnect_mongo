import os
import hashlib
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# Database Configuration
# ============================================================
MONGO_URI = os.getenv('ATLAS_URI')
DATABASE_NAME = "handyconnect"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

users_col = db["users"]
services_col = db["services"]
messages_col = db["messages"]
reviews_col = db["reviews"]

# ============================================================
# Utilities
# ============================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def now():
    return datetime.now()

# ============================================================
# User Queries
# ============================================================
def authenticate_user(email, password):
    return users_col.find_one({
        "email": email,
        "password_hash": hash_password(password),
    })

def get_user_by_email(email):
    return users_col.find_one({"email": email})

def get_user_by_id(user_id):
    return users_col.find_one({"_id": user_id})

def insert_user(user_data):
    return users_col.insert_one(user_data)

def get_all_workers():
    return list(users_col.find({"role": "worker"}))

def update_user_profile(user_id, update_data):
    users_col.update_one({"_id": user_id}, {"$set": update_data})

# ============================================================
# Service Queries
# ============================================================
def insert_service(service_data):
    services_col.insert_one(service_data)

def get_customer_services(customer_id):
    return list(services_col.find({"customer_id": customer_id}).sort("created_at", -1))

def get_worker_services(worker_id):
    return list(services_col.find({"worker_id": worker_id}).sort("created_at", -1))

def get_service_by_id(service_id):
    return services_col.find_one({"_id": service_id})

def update_service_state(service_id, status):
    update = {
        "status": status,
        "accepted_status": status in ["accepted", "completed"],
        "updated_at": now(),
    }
    if status == "completed":
        update["details.completed_date"] = now()
    services_col.update_one({"_id": service_id}, {"$set": update})

# ============================================================
# Review Queries
# ============================================================
def get_review_by_service_and_customer(service_id, customer_id):
    return reviews_col.find_one({
        "service_id": service_id,
        "customer_id": customer_id,
    })

def insert_review(review_data):
    reviews_col.insert_one(review_data)

def get_customer_reviews(customer_id):
    return list(reviews_col.find({"customer_id": customer_id}).sort("review_date", -1))

def get_worker_reviews(worker_id):
    return list(reviews_col.find({"worker_id": worker_id}).sort("review_date", -1))

def recalculate_worker_rating(worker_id):
    reviews = list(reviews_col.find({"worker_id": worker_id}))
    if not reviews:
        avg = 0
    else:
        avg = sum(r.get("rating", 0) for r in reviews) / len(reviews)
    users_col.update_one(
        {"_id": worker_id},
        {"$set": {"avg_rating": round(avg, 2), "updated_at": now()}},
    )

# ============================================================
# Message Queries
# ============================================================
def get_service_messages(service_id):
    return list(messages_col.find({"service_id": service_id}).sort("created_at", 1))

def insert_message(message_data):
    messages_col.insert_one(message_data)
