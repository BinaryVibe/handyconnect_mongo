# HandyConnect Tkinter User App

This is a simple user-facing HandyConnect application using:

- Python
- Tkinter
- MongoDB Atlas
- pymongo

It is not a database manager. It behaves like a small version of the HandyConnect app.

## Implemented Features

### Authentication
- Register as customer
- Register as worker
- Login
- Role-based dashboard

### Customer Features
- Browse/search workers
- View worker skills, availability, and rating
- Book a worker
- View own bookings
- Message worker for a booked service
- Review completed services
- Edit profile/address

### Worker Features
- View booking requests
- Accept/decline requests
- Mark accepted services as completed
- Edit worker service listing
- Update profession, skills, and availability
- Message customers
- View received reviews

### Excluded
- Admin moderation
- Reporting
- Real payment gateway
- File/image uploads
- Email password reset

## MongoDB Collections

The app uses only:

- users
- services
- messages
- reviews

## Setup

Install requirements:

```bash
pip install -r requirements.txt
```

Open both `app.py` and `seed_data.py`.

Replace:

```python
MONGO_URI = "mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
```

with your actual MongoDB Atlas connection string.

## Add Sample Data

Run:

```bash
python seed_data.py
```

Demo accounts:

```text
Customer: customer@example.com / 123456
Worker 1: electrician@example.com / 123456
Worker 2: plumber@example.com / 123456
```

## Run App

```bash
python app.py
```

## Suggested Presentation Flow

1. Run `seed_data.py`.
2. Login as customer.
3. Browse workers.
4. Book a worker.
5. Open messages and send a message.
6. Logout.
7. Login as worker.
8. Accept the booking.
9. Mark booking as completed.
10. Logout.
11. Login as customer.
12. Review the completed service.
13. Show that the worker rating updates.