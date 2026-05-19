import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import hashlib

# ============================================================
# HandyConnect Tkinter User App
# Collections used:
#   users, services, messages, reviews
# ============================================================

MONGO_URI = "mongodb+srv://harisali:qm0IN8G3CA@cluster0.miigix3.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "handyconnect"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

users_col = db["users"]
services_col = db["services"]
messages_col = db["messages"]
reviews_col = db["reviews"]


# ============================================================
# Helpers
# ============================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def now():
    return datetime.now()


def oid(value):
    if isinstance(value, ObjectId):
        return value
    return ObjectId(str(value))


def short_id(value):
    return str(value)[-6:]


def full_name(user):
    return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def make_button(parent, text, command, bg="#4A2E1E"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        font=("Arial", 10, "bold"),
        relief=tk.FLAT,
        padx=12,
        pady=8,
        cursor="hand2",
    )


def make_label(parent, text, size=11, bold=False, fg="#222222", bg="#F7F2EF"):
    return tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        font=("Arial", size, "bold" if bold else "normal"),
        anchor="w",
        justify="left",
    )


def make_entry(parent, show=None):
    entry = tk.Entry(parent, font=("Arial", 11), show=show)
    entry.pack(fill=tk.X, pady=(2, 10), ipady=5)
    return entry

def render_stars(rating):
    """Converts a float/int rating into a string of visual stars (e.g., ★★★★☆)"""
    try:
        r = round(float(rating))
    except (ValueError, TypeError):
        r = 0
    r = max(0, min(5, r)) # Clamp between 0 and 5
    return "★" * r + "☆" * (5 - r)

class StarRating(tk.Frame):
    """An interactive clickable star rating widget for Tkinter."""
    def __init__(self, parent, initial_rating=5, *args, **kwargs):
        super().__init__(parent, bg="white", *args, **kwargs)
        self.rating = initial_rating
        self.stars = []
        
        for i in range(1, 6):
            lbl = tk.Label(self, text="☆", font=("Arial", 24), bg="white", fg="#F5B041", cursor="hand2")
            lbl.pack(side=tk.LEFT, padx=2)
            # Bind left click to update the rating
            lbl.bind("<Button-1>", lambda e, val=i: self.set_rating(val))
            self.stars.append(lbl)
            
        self.update_stars()

    def set_rating(self, val):
        self.rating = val
        self.update_stars()

    def update_stars(self):
        for i, lbl in enumerate(self.stars):
            if i < self.rating:
                lbl.config(text="★")
            else:
                lbl.config(text="☆")
                
    def get(self):
        return self.rating

# ============================================================
# Main App
# ============================================================

class HandyConnectApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HandyConnect")
        self.geometry("1150x720")
        self.minsize(1000, 650)
        self.configure(bg="#F7F2EF")

        self.current_user = None

        self.header = tk.Frame(self, bg="#4A2E1E", height=75)
        self.header.pack(fill=tk.X)

        self.header_title = tk.Label(
            self.header,
            text="HandyConnect",
            bg="#4A2E1E",
            fg="white",
            font=("Arial", 24, "bold"),
        )
        self.header_title.pack(side=tk.LEFT, padx=25, pady=18)

        self.header_user = tk.Label(
            self.header,
            text="",
            bg="#4A2E1E",
            fg="#E9DFD8",
            font=("Arial", 11),
        )
        self.header_user.pack(side=tk.RIGHT, padx=25)

        self.body = tk.Frame(self, bg="#F7F2EF")
        self.body.pack(fill=tk.BOTH, expand=True)

        self.show_login()

    # ------------------------------------------------------------
    # Navigation Shell
    # ------------------------------------------------------------

    def set_header(self):
        if self.current_user:
            self.header_user.config(
                text=f"{full_name(self.current_user)} | {self.current_user.get('role', '').capitalize()}"
            )
        else:
            self.header_user.config(text="")

    def render_shell(self, active_page="home"):
        clear_frame(self.body)
        self.set_header()

        sidebar = tk.Frame(self.body, bg="#E9DFD8", width=210)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        content = tk.Frame(self.body, bg="#F7F2EF")
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=18, pady=18)

        role = self.current_user.get("role")

        make_label(sidebar, "Menu", size=15, bold=True, bg="#E9DFD8", fg="#4A2E1E").pack(
            fill=tk.X, padx=14, pady=(20, 10)
        )

        if role == "customer":
            buttons = [
                ("Browse Workers", self.show_customer_home),
                ("My Bookings", self.show_customer_bookings),
                ("Messages", self.show_messages),
                ("Reviews", self.show_customer_reviews),
                ("Profile", self.show_profile),
            ]
        else:
            buttons = [
                ("Worker Dashboard", self.show_worker_home),
                ("My Service Listing", self.show_worker_listing),
                ("Messages", self.show_messages),
                ("Reviews", self.show_worker_reviews),
                ("Profile", self.show_profile),
            ]

        for text, cmd in buttons:
            b = make_button(sidebar, text, cmd, bg="#C07B4D" if text.lower().startswith(active_page) else "#4A2E1E")
            b.pack(fill=tk.X, padx=12, pady=5)

        logout = make_button(sidebar, "Logout", self.logout, bg="#9B2226")
        logout.pack(fill=tk.X, padx=12, pady=(30, 5))

        return content

    def logout(self):
        self.current_user = None
        self.show_login()

    # ------------------------------------------------------------
    # Auth Screens
    # ------------------------------------------------------------

    def show_login(self):
        clear_frame(self.body)
        self.current_user = None
        self.set_header()

        wrapper = tk.Frame(self.body, bg="#F7F2EF")
        wrapper.pack(expand=True)

        card = tk.Frame(wrapper, bg="white", padx=35, pady=30)
        card.pack()

        make_label(card, "Login", size=24, bold=True, fg="#4A2E1E", bg="white").pack(anchor="center", pady=(0, 20))

        make_label(card, "Email", bg="white").pack(anchor="w")
        email_entry = make_entry(card)

        make_label(card, "Password", bg="white").pack(anchor="w")
        password_entry = make_entry(card, show="*")

        def do_login():
            email = email_entry.get().strip().lower()
            password = password_entry.get().strip()

            if not email or not password:
                messagebox.showerror("Validation Error", "Please enter email and password.")
                return

            user = users_col.find_one({
                "email": email,
                "password_hash": hash_password(password),
            })

            if not user:
                messagebox.showerror("Login Failed", "Invalid email or password.")
                return

            self.current_user = user

            if user.get("role") == "worker":
                self.show_worker_home()
            else:
                self.show_customer_home()

        make_button(card, "Login", do_login).pack(fill=tk.X, pady=(8, 8))
        make_button(card, "Create Account", self.show_register, bg="#C07B4D").pack(fill=tk.X)

        hint = (
            "Tip: use Insert Sample Data from the README, or register new users here.\n"
            "This demo stores SHA-256 hashes for presentation purposes."
        )
        make_label(card, hint, size=9, bg="white", fg="#666666").pack(pady=(15, 0))

    def show_register(self):
        clear_frame(self.body)
        self.set_header()

        wrapper = tk.Frame(self.body, bg="#F7F2EF")
        wrapper.pack(expand=True)

        card = tk.Frame(wrapper, bg="white", padx=35, pady=25)
        card.pack()

        make_label(card, "Create Account", size=22, bold=True, fg="#4A2E1E", bg="white").pack(anchor="center", pady=(0, 12))

        fields = {}

        for label in ["First Name", "Last Name", "Email", "Phone Number", "Password"]:
            make_label(card, label, bg="white").pack(anchor="w")
            fields[label] = make_entry(card, show="*" if label == "Password" else None)

        make_label(card, "Role", bg="white").pack(anchor="w")
        role_var = tk.StringVar(value="customer")
        role_box = ttk.Combobox(card, textvariable=role_var, values=["customer", "worker"], state="readonly")
        role_box.pack(fill=tk.X, pady=(2, 10), ipady=4)

        worker_frame = tk.Frame(card, bg="white")
        worker_frame.pack(fill=tk.X)

        make_label(worker_frame, "Profession - worker only", bg="white").pack(anchor="w")
        profession_entry = make_entry(worker_frame)

        make_label(worker_frame, "Skills comma-separated - worker only", bg="white").pack(anchor="w")
        skills_entry = make_entry(worker_frame)

        def do_register():
            first = fields["First Name"].get().strip()
            last = fields["Last Name"].get().strip()
            email = fields["Email"].get().strip().lower()
            phone = fields["Phone Number"].get().strip()
            password = fields["Password"].get().strip()
            role = role_var.get()

            if not first or not last or not email or not phone or not password:
                messagebox.showerror("Validation Error", "Please fill all required fields.")
                return

            if users_col.find_one({"email": email}):
                messagebox.showerror("Registration Error", "This email is already registered.")
                return

            user = {
                "email": email,
                "phone_number": phone,
                "password_hash": hash_password(password),
                "first_name": first,
                "last_name": last,
                "avatar_url": "",
                "role": role,
                "created_at": now(),
                "updated_at": now(),
            }

            if role == "customer":
                user.update({
                    "date_joined": now(),
                    "addresses": [],
                })
            else:
                skills = [s.strip() for s in skills_entry.get().split(",") if s.strip()]
                user.update({
                    "profession": profession_entry.get().strip() or "General Worker",
                    "skills": skills,
                    "availability": True,
                    "avg_rating": 0,
                    "verified_status": True,
                    "earnings": 0,
                })

            result = users_col.insert_one(user)
            self.current_user = users_col.find_one({"_id": result.inserted_id})

            if role == "worker":
                self.show_worker_home()
            else:
                self.show_customer_home()

        make_button(card, "Register", do_register).pack(fill=tk.X, pady=(8, 8))
        make_button(card, "Back to Login", self.show_login, bg="#C07B4D").pack(fill=tk.X)

    # ------------------------------------------------------------
    # Customer Screens
    # ------------------------------------------------------------

    def show_customer_home(self):
        content = self.render_shell("browse")
        make_label(content, "Browse Workers", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        search_frame = tk.Frame(content, bg="#F7F2EF")
        search_frame.pack(fill=tk.X, pady=10)

        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=("Arial", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        make_button(search_frame, "Search", lambda: load_workers()).pack(side=tk.LEFT, padx=8)

        list_frame = tk.Frame(content, bg="#F7F2EF")
        list_frame.pack(fill=tk.BOTH, expand=True)

        def load_workers():
            clear_frame(list_frame)
            term = search_var.get().strip().lower()

            query = {"role": "worker"}
            workers = list(users_col.find(query))

            if term:
                workers = [
                    w for w in workers
                    if term in w.get("profession", "").lower()
                    or term in " ".join(w.get("skills", [])).lower()
                    or term in full_name(w).lower()
                ]

            if not workers:
                make_label(list_frame, "No workers found.", size=12).pack(anchor="w", pady=10)
                return

            for worker in workers:
                self.worker_card(list_frame, worker)

        load_workers()

    def worker_card(self, parent, worker):
        card = tk.Frame(parent, bg="white", padx=14, pady=12, highlightbackground="#ddd", highlightthickness=1)
        card.pack(fill=tk.X, pady=6)

        title = f"{full_name(worker)} — {worker.get('profession', 'Worker')}"
        make_label(card, title, size=14, bold=True, bg="white", fg="#4A2E1E").pack(anchor="w")

        skills = ", ".join(worker.get("skills", [])) or "No skills listed"
        rating = worker.get("avg_rating", 0)
        availability = "Available" if worker.get("availability", True) else "Unavailable"

        # --- NEW CODE: Use visual stars for the average rating ---
        star_display = render_stars(rating)
        
        make_label(card, f"Skills: {skills}", bg="white").pack(anchor="w", pady=2)
        make_label(card, f"Rating: {rating} {star_display} | Status: {availability}", bg="white", fg="#F5B041" if rating > 0 else "#222222").pack(anchor="w")
        # ---------------------------------------------------------

        btns = tk.Frame(card, bg="white")
        btns.pack(anchor="e", pady=(8, 0))

        make_button(btns, "Book Worker", lambda w=worker: self.show_booking_form(w)).pack(side=tk.LEFT, padx=4)
        make_button(btns, "View Reviews", lambda w=worker: self.show_reviews_for_worker(w), bg="#C07B4D").pack(side=tk.LEFT, padx=4)

    def show_booking_form(self, worker):
        content = self.render_shell("browse")
        make_label(content, f"Book {full_name(worker)}", size=22, bold=True, fg="#4A2E1E").pack(anchor="w", pady=(0, 12))

        form = tk.Frame(content, bg="white", padx=20, pady=20)
        form.pack(fill=tk.X)

        make_label(form, "Service Title", bg="white").pack(anchor="w")
        title_entry = make_entry(form)

        make_label(form, "Description", bg="white").pack(anchor="w")
        desc_text = tk.Text(form, height=5, font=("Arial", 11))
        desc_text.pack(fill=tk.X, pady=(2, 10))

        make_label(form, "Location", bg="white").pack(anchor="w")
        location_entry = make_entry(form)

        make_label(form, "Expected Price", bg="white").pack(anchor="w")
        price_entry = make_entry(form)

        def submit():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            location = location_entry.get().strip()
            price_raw = price_entry.get().strip()

            if not title or not location:
                messagebox.showerror("Validation Error", "Please enter service title and location.")
                return

            try:
                price = float(price_raw) if price_raw else 0
            except ValueError:
                messagebox.showerror("Validation Error", "Price must be a number.")
                return

            services_col.insert_one({
                "worker_id": worker["_id"],
                "customer_id": self.current_user["_id"],
                "service_title": title,
                "description": description,
                "accepted_status": False,
                "status": "pending",
                "location": location,
                "details": {
                    "price": price,
                    "price_unit": "PKR",
                    "start_date": None,
                    "expected_end": None,
                    "completed_date": None,
                    "paid_status": False,
                    "created_at": now(),
                    "updated_at": now(),
                },
                "created_at": now(),
                "updated_at": now(),
            })

            messagebox.showinfo("Success", "Booking request sent.")
            self.show_customer_bookings()

        make_button(form, "Send Booking Request", submit).pack(anchor="e", pady=(10, 0))

    def show_customer_bookings(self):
        content = self.render_shell("my bookings")
        make_label(content, "My Bookings", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        services = list(services_col.find({"customer_id": self.current_user["_id"]}).sort("created_at", -1))

        if not services:
            make_label(content, "You have not booked any services yet.", size=12).pack(anchor="w", pady=15)
            return

        for service in services:
            self.service_card(content, service, viewer_role="customer")

    def show_customer_reviews(self):
        content = self.render_shell("reviews")
        make_label(content, "My Reviews", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        reviews = list(reviews_col.find({"customer_id": self.current_user["_id"]}).sort("review_date", -1))

        if not reviews:
            make_label(content, "You have not written any reviews yet.", size=12).pack(anchor="w", pady=15)
            return

        for review in reviews:
            self.review_card(content, review)

    # ------------------------------------------------------------
    # Worker Screens
    # ------------------------------------------------------------

    def show_worker_home(self):
        content = self.render_shell("worker dashboard")
        make_label(content, "Worker Dashboard", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        services = list(services_col.find({"worker_id": self.current_user["_id"]}).sort("created_at", -1))

        stats = tk.Frame(content, bg="#F7F2EF")
        stats.pack(fill=tk.X, pady=10)

        total = len(services)
        pending = len([s for s in services if s.get("status") == "pending"])
        completed = len([s for s in services if s.get("status") == "completed"])

        for label, value in [("Total Requests", total), ("Pending", pending), ("Completed", completed)]:
            box = tk.Frame(stats, bg="white", padx=18, pady=12)
            box.pack(side=tk.LEFT, padx=(0, 10))
            make_label(box, str(value), size=22, bold=True, bg="white", fg="#4A2E1E").pack()
            make_label(box, label, bg="white").pack()

        if not services:
            make_label(content, "No service requests yet.", size=12).pack(anchor="w", pady=15)
            return

        for service in services:
            self.service_card(content, service, viewer_role="worker")

    def show_worker_listing(self):
        content = self.render_shell("my service listing")
        make_label(content, "My Service Listing", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        form = tk.Frame(content, bg="white", padx=20, pady=20)
        form.pack(fill=tk.X, pady=10)

        make_label(form, "Profession", bg="white").pack(anchor="w")
        profession_entry = make_entry(form)
        profession_entry.insert(0, self.current_user.get("profession", ""))

        make_label(form, "Skills comma-separated", bg="white").pack(anchor="w")
        skills_entry = make_entry(form)
        skills_entry.insert(0, ", ".join(self.current_user.get("skills", [])))

        availability_var = tk.BooleanVar(value=self.current_user.get("availability", True))
        tk.Checkbutton(
            form,
            text="Available for bookings",
            variable=availability_var,
            bg="white",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 10))

        def save():
            skills = [s.strip() for s in skills_entry.get().split(",") if s.strip()]
            users_col.update_one(
                {"_id": self.current_user["_id"]},
                {
                    "$set": {
                        "profession": profession_entry.get().strip(),
                        "skills": skills,
                        "availability": availability_var.get(),
                        "updated_at": now(),
                    }
                },
            )

            self.current_user = users_col.find_one({"_id": self.current_user["_id"]})
            messagebox.showinfo("Success", "Worker listing updated.")
            self.show_worker_listing()

        make_button(form, "Save Listing", save).pack(anchor="e")

    def show_worker_reviews(self):
        content = self.render_shell("reviews")
        make_label(content, "Reviews Received", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        reviews = list(reviews_col.find({"worker_id": self.current_user["_id"]}).sort("review_date", -1))

        if not reviews:
            make_label(content, "No reviews received yet.", size=12).pack(anchor="w", pady=15)
            return

        for review in reviews:
            self.review_card(content, review)

    # ------------------------------------------------------------
    # Shared Service / Review / Message Screens
    # ------------------------------------------------------------

    def service_card(self, parent, service, viewer_role):
        worker = users_col.find_one({"_id": service.get("worker_id")})
        customer = users_col.find_one({"_id": service.get("customer_id")})

        card = tk.Frame(parent, bg="white", padx=14, pady=12, highlightbackground="#ddd", highlightthickness=1)
        card.pack(fill=tk.X, pady=6)

        status = service.get("status", "pending")
        title = f"{service.get('service_title', 'Service')} | Status: {status.capitalize()}"
        make_label(card, title, size=14, bold=True, bg="white", fg="#4A2E1E").pack(anchor="w")

        if viewer_role == "customer":
            make_label(card, f"Worker: {full_name(worker) if worker else 'Unknown'}", bg="white").pack(anchor="w")
        else:
            make_label(card, f"Customer: {full_name(customer) if customer else 'Unknown'}", bg="white").pack(anchor="w")

        make_label(card, f"Location: {service.get('location', '')}", bg="white").pack(anchor="w")
        make_label(card, f"Description: {service.get('description', '')}", bg="white").pack(anchor="w")
        make_label(card, f"Price: {service.get('details', {}).get('price', 0)} {service.get('details', {}).get('price_unit', 'PKR')}", bg="white").pack(anchor="w")

        buttons = tk.Frame(card, bg="white")
        buttons.pack(anchor="e", pady=(8, 0))

        make_button(buttons, "Message", lambda s=service: self.show_service_chat(s), bg="#C07B4D").pack(side=tk.LEFT, padx=4)

        if viewer_role == "worker":
            if status == "pending":
                make_button(buttons, "Accept", lambda s=service: self.update_service_status(s, "accepted")).pack(side=tk.LEFT, padx=4)
                make_button(buttons, "Decline", lambda s=service: self.update_service_status(s, "declined"), bg="#9B2226").pack(side=tk.LEFT, padx=4)
            elif status == "accepted":
                make_button(buttons, "Mark Completed", lambda s=service: self.update_service_status(s, "completed")).pack(side=tk.LEFT, padx=4)

        if viewer_role == "customer" and status == "completed":
            existing = reviews_col.find_one({
                "service_id": service["_id"],
                "customer_id": self.current_user["_id"],
            })
            if not existing:
                make_button(buttons, "Review", lambda s=service: self.show_review_form(s)).pack(side=tk.LEFT, padx=4)

    def update_service_status(self, service, status):
        update = {
            "status": status,
            "accepted_status": status in ["accepted", "completed"],
            "updated_at": now(),
        }

        if status == "completed":
            update["details.completed_date"] = now()

        services_col.update_one({"_id": service["_id"]}, {"$set": update})
        messagebox.showinfo("Updated", f"Service marked as {status}.")
        self.show_worker_home()

    def show_messages(self):
        content = self.render_shell("messages")
        make_label(content, "Messages", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        if self.current_user.get("role") == "customer":
            services = list(services_col.find({"customer_id": self.current_user["_id"]}).sort("updated_at", -1))
        else:
            services = list(services_col.find({"worker_id": self.current_user["_id"]}).sort("updated_at", -1))

        if not services:
            make_label(content, "No conversations yet.", size=12).pack(anchor="w", pady=15)
            return

        for service in services:
            card = tk.Frame(content, bg="white", padx=14, pady=12, highlightbackground="#ddd", highlightthickness=1)
            card.pack(fill=tk.X, pady=6)

            make_label(card, f"{service.get('service_title')} | {service.get('status', 'pending')}", size=13, bold=True, bg="white", fg="#4A2E1E").pack(anchor="w")
            make_label(card, f"Conversation ID: {short_id(service['_id'])}", bg="white").pack(anchor="w")
            make_button(card, "Open Chat", lambda s=service: self.show_service_chat(s), bg="#C07B4D").pack(anchor="e", pady=(5, 0))

    def show_service_chat(self, service):
        content = self.render_shell("messages")
        make_label(content, f"Chat: {service.get('service_title')}", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        chat_box = tk.Frame(content, bg="white", padx=15, pady=15)
        chat_box.pack(fill=tk.BOTH, expand=True, pady=10)

        messages_frame = tk.Frame(chat_box, bg="white")
        messages_frame.pack(fill=tk.BOTH, expand=True)

        def load_messages():
            clear_frame(messages_frame)
            messages = list(messages_col.find({"service_id": service["_id"]}).sort("created_at", 1))

            if not messages:
                make_label(messages_frame, "No messages yet.", bg="white").pack(anchor="w")
                return

            for msg in messages:
                sender = users_col.find_one({"_id": msg.get("sender_id")})
                sender_name = full_name(sender) if sender else "Unknown"
                text = f"{sender_name}: {msg.get('content')}"
                make_label(messages_frame, text, bg="white", fg="#222222").pack(anchor="w", pady=2)

        input_frame = tk.Frame(chat_box, bg="white")
        input_frame.pack(fill=tk.X, pady=(10, 0))

        msg_entry = tk.Entry(input_frame, font=("Arial", 11))
        msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        def send():
            content_text = msg_entry.get().strip()
            if not content_text:
                return

            messages_col.insert_one({
                "service_id": service["_id"],
                "sender_id": self.current_user["_id"],
                "content": content_text,
                "is_read": False,
                "created_at": now(),
            })
            msg_entry.delete(0, tk.END)
            load_messages()

        make_button(input_frame, "Send", send).pack(side=tk.LEFT, padx=8)

        load_messages()

    def show_review_form(self, service):
        content = self.render_shell("reviews")
        make_label(content, f"Review: {service.get('service_title')}", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        form = tk.Frame(content, bg="white", padx=20, pady=20)
        form.pack(fill=tk.X, pady=10)

        # --- NEW CODE: Interactive Star Selector ---
        make_label(form, "Click to Rate", bg="white").pack(anchor="w")
        star_selector = StarRating(form, initial_rating=5)
        star_selector.pack(anchor="w", pady=(2, 10))
        # -----------------------------------------

        make_label(form, "Comment", bg="white").pack(anchor="w")
        comment_text = tk.Text(form, height=5, font=("Arial", 11))
        comment_text.pack(fill=tk.X, pady=(2, 10))

        def submit_review():
            rating = star_selector.get()
            comment = comment_text.get("1.0", tk.END).strip()

            existing = reviews_col.find_one({
                "service_id": service["_id"],
                "customer_id": self.current_user["_id"],
            })

            if existing:
                messagebox.showerror("Review Exists", "You already reviewed this service.")
                return

            if service.get("status") != "completed":
                messagebox.showerror("Not Allowed", "Only completed services can be reviewed.")
                return

            reviews_col.insert_one({
                "customer_id": self.current_user["_id"],
                "worker_id": service["worker_id"],
                "service_id": service["_id"],
                "rating": rating,
                "comment": comment,
                "review_date": now(),
                "images": [],
            })

            self.recalculate_worker_rating(service["worker_id"])
            messagebox.showinfo("Success", "Review submitted.")
            self.show_customer_reviews()

        make_button(form, "Submit Review", submit_review).pack(anchor="e")

    def recalculate_worker_rating(self, worker_id):
        reviews = list(reviews_col.find({"worker_id": worker_id}))
        if not reviews:
            avg = 0
        else:
            avg = sum(r.get("rating", 0) for r in reviews) / len(reviews)

        users_col.update_one(
            {"_id": worker_id},
            {"$set": {"avg_rating": round(avg, 2), "updated_at": now()}},
        )

    def show_reviews_for_worker(self, worker):
        content = self.render_shell("browse")
        make_label(content, f"Reviews for {full_name(worker)}", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        reviews = list(reviews_col.find({"worker_id": worker["_id"]}).sort("review_date", -1))

        if not reviews:
            make_label(content, "No reviews for this worker yet.", size=12).pack(anchor="w", pady=15)
            return

        for review in reviews:
            self.review_card(content, review)

    def review_card(self, parent, review):
        customer = users_col.find_one({"_id": review.get("customer_id")})
        worker = users_col.find_one({"_id": review.get("worker_id")})
        service = services_col.find_one({"_id": review.get("service_id")})

        card = tk.Frame(parent, bg="white", padx=14, pady=12, highlightbackground="#ddd", highlightthickness=1)
        card.pack(fill=tk.X, pady=6)

        # --- NEW CODE: Render stars for the specific review ---
        r_val = review.get('rating', 0)
        star_display = render_stars(r_val)
        
        make_label(card, f"Rating: {star_display} ({r_val}/5)", size=14, bold=True, bg="white", fg="#F5B041").pack(anchor="w")
        # ------------------------------------------------------
        
        make_label(card, f"Service: {service.get('service_title') if service else 'Unknown'}", bg="white").pack(anchor="w")
        make_label(card, f"Customer: {full_name(customer) if customer else 'Unknown'}", bg="white").pack(anchor="w")
        make_label(card, f"Worker: {full_name(worker) if worker else 'Unknown'}", bg="white").pack(anchor="w")
        make_label(card, f"Comment: {review.get('comment', '')}", bg="white").pack(anchor="w")

    # ------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------

    def show_profile(self):
        content = self.render_shell("profile")
        make_label(content, "Profile", size=22, bold=True, fg="#4A2E1E").pack(anchor="w")

        form = tk.Frame(content, bg="white", padx=20, pady=20)
        form.pack(fill=tk.X, pady=10)

        make_label(form, "First Name", bg="white").pack(anchor="w")
        first_entry = make_entry(form)
        first_entry.insert(0, self.current_user.get("first_name", ""))

        make_label(form, "Last Name", bg="white").pack(anchor="w")
        last_entry = make_entry(form)
        last_entry.insert(0, self.current_user.get("last_name", ""))

        make_label(form, "Phone Number", bg="white").pack(anchor="w")
        phone_entry = make_entry(form)
        phone_entry.insert(0, self.current_user.get("phone_number", ""))

        if self.current_user.get("role") == "customer":
            make_label(form, "Address City", bg="white").pack(anchor="w")
            city_entry = make_entry(form)
            address = self.current_user.get("addresses", [{}])[0] if self.current_user.get("addresses") else {}
            city_entry.insert(0, address.get("city", ""))

            make_label(form, "Street", bg="white").pack(anchor="w")
            street_entry = make_entry(form)
            street_entry.insert(0, address.get("street", ""))
        else:
            city_entry = None
            street_entry = None

        def save():
            update = {
                "first_name": first_entry.get().strip(),
                "last_name": last_entry.get().strip(),
                "phone_number": phone_entry.get().strip(),
                "updated_at": now(),
            }

            if self.current_user.get("role") == "customer":
                update["addresses"] = [
                    {
                        "street": street_entry.get().strip(),
                        "city": city_entry.get().strip(),
                        "state": "",
                        "postal_code": "",
                        "country": "Pakistan",
                        "created_at": now(),
                    }
                ]

            users_col.update_one({"_id": self.current_user["_id"]}, {"$set": update})
            self.current_user = users_col.find_one({"_id": self.current_user["_id"]})
            messagebox.showinfo("Success", "Profile updated.")
            self.show_profile()

        make_button(form, "Save Profile", save).pack(anchor="e")


if __name__ == "__main__":
    app = HandyConnectApp()
    app.mainloop()
