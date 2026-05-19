# MongoDB Layout Used by the App

## users

Stores both customers and workers.

### Customer

```json
{
  "_id": "ObjectId",
  "email": "customer@example.com",
  "phone_number": "03001234567",
  "password_hash": "hashed_password",
  "first_name": "Ali",
  "last_name": "Khan",
  "avatar_url": "",
  "role": "customer",
  "date_joined": "Date",
  "addresses": [
    {
      "street": "Street 12",
      "city": "Wah Cantt",
      "state": "Punjab",
      "postal_code": "47040",
      "country": "Pakistan",
      "created_at": "Date"
    }
  ],
  "created_at": "Date",
  "updated_at": "Date"
}
```

### Worker

```json
{
  "_id": "ObjectId",
  "email": "worker@example.com",
  "phone_number": "03111234567",
  "password_hash": "hashed_password",
  "first_name": "Ahmed",
  "last_name": "Raza",
  "avatar_url": "",
  "role": "worker",
  "profession": "Electrician",
  "skills": ["wiring", "fan repair"],
  "availability": true,
  "avg_rating": 4.5,
  "verified_status": true,
  "earnings": 0,
  "created_at": "Date",
  "updated_at": "Date"
}
```

## services

Stores bookings and service details in one document.

```json
{
  "_id": "ObjectId",
  "worker_id": "ObjectId",
  "customer_id": "ObjectId",
  "service_title": "Fan Repair",
  "description": "Ceiling fan is making noise.",
  "accepted_status": false,
  "status": "pending",
  "location": "Wah Cantt",
  "details": {
    "price": 1500,
    "price_unit": "PKR",
    "start_date": null,
    "expected_end": null,
    "completed_date": null,
    "paid_status": false,
    "created_at": "Date",
    "updated_at": "Date"
  },
  "created_at": "Date",
  "updated_at": "Date"
}
```

Possible service status values:

```text
pending
accepted
declined
completed
```

## messages

```json
{
  "_id": "ObjectId",
  "service_id": "ObjectId",
  "sender_id": "ObjectId",
  "content": "Hello, I need fan repair service.",
  "is_read": false,
  "created_at": "Date"
}
```

## reviews

```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "worker_id": "ObjectId",
  "service_id": "ObjectId",
  "rating": 5,
  "comment": "Good service.",
  "review_date": "Date",
  "images": []
}
```