import os
import hashlib
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# Database Configuration
# ============================================================
MONGO_URI = os.getenv("ATLAS_URI")
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
    return users_col.find_one(
        {
            "email": email,
            "password_hash": hash_password(password),
        }
    )


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
    return reviews_col.find_one(
        {
            "service_id": service_id,
            "customer_id": customer_id,
        }
    )


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


def mark_as_read(service_id, current_user_id):
    messages_col.update_many(
        {
            "service_id": service_id,
            "sender_id": {
                "$ne": current_user_id
            },  # This will set the reciever's messages to read
        },
        {
            "$set": {
                "is_read": True,
            }
        },
    )


def get_customer_message_services(
    customer_id, search_text="", filter_type="all", sort_type="newest"
):
    pipeline = [
        {"$match": {"customer_id": customer_id}},
        {
            "$lookup": {
                "from": "users",
                "localField": "worker_id",
                "foreignField": "_id",
                "as": "worker",
            }
        },
        {"$unwind": {"path": "$worker", "preserveNullAndEmptyArrays": True}},
    ]

    if search_text.strip():
        pipeline.append(
            {
                "$match": {
                    "$or": [
                        {"service_title": {"$regex": search_text, "$options": "i"}},
                        {"worker.first_name": {"$regex": search_text, "$options": "i"}},
                        {"worker.last_name": {"$regex": search_text, "$options": "i"}},
                        {"worker.profession": {"$regex": search_text, "$options": "i"}},
                    ]
                }
            }
        )

    if filter_type == "accepted_true":
        pipeline.append({"$match": {"accepted_status": True}})

    elif filter_type == "accepted_false":
        pipeline.append({"$match": {"accepted_status": False}})

    elif filter_type == "status_completed":
        pipeline.append({"$match": {"status": "completed"}})

    elif filter_type == "status_pending":
        pipeline.append({"$match": {"status": "pending"}})

    pipeline.append(
        {
            "$addFields": {
                "peer_name": {
                    "$concat": [
                        {"$ifNull": ["$worker.first_name", ""]},
                        " ",
                        {"$ifNull": ["$worker.last_name", ""]},
                    ]
                }
            }
        }
    )

    if sort_type == "peer_name_asc":
        pipeline.append({"$sort": {"peer_name": 1}})

    elif sort_type == "service_title_asc":
        pipeline.append({"$sort": {"service_title": 1}})

    elif sort_type == "completed_date_asc":
        pipeline.append({"$sort": {"details.completed_date": 1}})

    elif sort_type == "completed_date_desc":
        pipeline.append({"$sort": {"details.completed_date": -1}})

    else:
        pipeline.append({"$sort": {"created_at": -1}})

    pipeline.append(
        {
            "$project": {
                "worker": 1,
                "worker_id": 1,
                "customer_id": 1,
                "service_title": 1,
                "description": 1,
                "location": 1,
                "accepted_status": 1,
                "status": 1,
                "details": 1,
                "created_at": 1,
                "updated_at": 1,
                "peer_name": 1,
            }
        }
    )

    return list(services_col.aggregate(pipeline))


def get_worker_message_services(
    worker_id, search_text="", filter_type="all", sort_type="newest"
):
    pipeline = [
        {"$match": {"worker_id": worker_id}},
        {
            "$lookup": {
                "from": "users",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer",
            }
        },
        {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
    ]

    if search_text.strip():
        pipeline.append(
            {
                "$match": {
                    "$or": [
                        {"service_title": {"$regex": search_text, "$options": "i"}},
                        {
                            "customer.first_name": {
                                "$regex": search_text,
                                "$options": "i",
                            }
                        },
                        {
                            "customer.last_name": {
                                "$regex": search_text,
                                "$options": "i",
                            }
                        },
                        {
                            "customer.phone_number": {
                                "$regex": search_text,
                                "$options": "i",
                            }
                        },
                    ]
                }
            }
        )

    if filter_type == "accepted_true":
        pipeline.append({"$match": {"accepted_status": True}})

    elif filter_type == "accepted_false":
        pipeline.append({"$match": {"accepted_status": False}})

    elif filter_type == "status_completed":
        pipeline.append({"$match": {"status": "completed"}})

    elif filter_type == "status_pending":
        pipeline.append({"$match": {"status": "pending"}})

    pipeline.append(
        {
            "$addFields": {
                "peer_name": {
                    "$concat": [
                        {"$ifNull": ["$customer.first_name", ""]},
                        " ",
                        {"$ifNull": ["$customer.last_name", ""]},
                    ]
                }
            }
        }
    )

    if sort_type == "peer_name_asc":
        pipeline.append({"$sort": {"peer_name": 1}})

    elif sort_type == "service_title_asc":
        pipeline.append({"$sort": {"service_title": 1}})

    elif sort_type == "completed_date_asc":
        pipeline.append({"$sort": {"details.completed_date": 1}})

    elif sort_type == "completed_date_desc":
        pipeline.append({"$sort": {"details.completed_date": -1}})

    else:
        pipeline.append({"$sort": {"created_at": -1}})

    pipeline.append(
        {
            "$project": {
                "customer": 1,
                "worker_id": 1,
                "customer_id": 1,
                "service_title": 1,
                "description": 1,
                "location": 1,
                "accepted_status": 1,
                "status": 1,
                "details": 1,
                "created_at": 1,
                "updated_at": 1,
                "peer_name": 1,
            }
        }
    )

    return list(services_col.aggregate(pipeline))
