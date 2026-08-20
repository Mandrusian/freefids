from datetime import datetime
import os
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from database import AIRCRAFT_DB, AIRLINE_DB

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL = "xottovaggs@gmail.com"
PASSWORD = "vaggs54"

session = requests.Session()

USER_FILE = "users.json"
CHAT_FILE = "chats.json"

ACTIVE_USERS = set()

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "xottovaggs@gmail.com": {"name": "Xavi (Admin)", "chat_name": "Xavi", "status": "normal"},
        "testuser@gmail.com": {"name": "Test Aviator", "chat_name": "TestPilot", "status": "pending"}
    }

def save_users(users):
    try:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_chats(chats):
    try:
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(chats, f, indent=4)
    except Exception as e:
        print(f"Error saving chats: {e}")

USER_STORE = load_users()
CHAT_STORE = load_chats()

def authenticate_session():
    print("Authenticating with Cairns Airport FIDS...")
    try:
        login_page = session.get("https://flights.cairnsairport.com.au/login")
        xsrf_cookie = session.cookies.get("XSRF-TOKEN")
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "_token"})
        csrf_token = token_input["value"] if token_input else ""

        headers = {
            "X-XSRF-TOKEN": xsrf_cookie,
            "Referer": "https://flights.cairnsairport.com.au/login"
        }
        payload = {"_token": csrf_token, "email": EMAIL, "password": PASSWORD}
        login_response = session.post("https://flights.cairnsairport.com.au/login", data=payload, headers=headers)
        if login_response.status_code in [200, 302]:
            print("Authentication successful.")
            return True
        return False
    except Exception as e:
        print(f"Auth error: {e}")
        return False

authenticate_session()

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "index.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>index.html not found in repository root!</h1>"

@app.post("/api/signup")
def register_user(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()
    if not email or not name:
        return {"status": "error", "message": "Email and Name are required."}
    
    if email in USER_STORE:
        return {"status": "error", "message": "Account already exists. Please log in."}
    
    USER_STORE[email] = {"name": name, "chat_name": name.split()[0], "status": "pending"}
    save_users(USER_STORE)
    return {"status": "success", "message": "Registration received. Please wait for admin approval."}

@app.post("/api/login")
def login_user(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    user = USER_STORE.get(email)
    
    if not user:
        return {"status": "error", "message": "Account not found. Please create an account."}
    
    if user["status"] == "pending":
        return {"status": "pending", "message": "Your account is awaiting approval from Cairns Airport administration."}
    
    if user["status"] == "suspended":
        return {"status": "error", "message": "This account has been suspended."}
        
    ACTIVE_USERS.add(email)
    return {"status": "normal", "email": email, "name": user["name"], "chat_name": user.get("chat_name", user["name"]), "message": "Login successful."}

@app.post("/api/heartbeat")
def heartbeat(data: dict = Body(...)):
    email = data.get("email", "").strip().lower()
    if email:
        ACTIVE_USERS.add(email)
    return {"online_count": max(1, len(ACTIVE_USERS))}

@app.post("/api/update-chat-name")
def update_chat_name(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    new_chat_name = data.get("chat_name", "").strip()
    if email in USER_STORE and new_chat_name:
        USER_STORE[email]["chat_name"] = new_chat_name
        save_users(USER_STORE)
        return {"status": "success", "chat_name": new_chat_name}
    return {"status": "error", "message": "Could not update display name."}

@app.post("/api/admin/login")
def admin_login(data: dict = Body(...)):
    password = data.get("password")
    if password == "vaggs54":
        ACTIVE_USERS.add("admin")
        return {"status": "success", "message": "Admin authenticated."}
    return {"status": "error", "message": "Incorrect administrator password."}

@app.get("/api/admin/users")
def admin_get_users():
    global USER_STORE
    USER_STORE = load_users()
    return USER_STORE

@app.post("/api/admin/set-status")
def admin_set_status(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    status = data.get("status")
    if email in USER_STORE and status in ["normal", "pending", "suspended"]:
        USER_STORE[email]["status"] = status
        save_users(USER_STORE)
        return {"status": "success", "message": f"Updated status for {email}."}
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/delete-user")
def admin_delete_user(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    if email in USER_STORE:
        del USER_STORE[email]
        save_users(USER_STORE)
        return {"status": "success", "message": f"Deleted user {email}."}
    return {"status": "error", "message": "User not found."}

@app.get("/api/chat/messages")
def get_messages():
    global CHAT_STORE
    CHAT_STORE = load_chats()
    return CHAT_STORE

@app.post("/api/chat/messages")
def post_message(data: dict = Body(...)):
    global CHAT_STORE
    CHAT_STORE = load_chats()
    sender = data.get("sender", "Anonymous").strip()
    text = data.get("text", "").strip()
    if text:
        msg = {
            "sender": sender,
            "text": text,
            "time": datetime.now().strftime("%H:%M")
        }
        CHAT_STORE.append(msg)
        if len(CHAT_STORE) > 100:
            CHAT_STORE = CHAT_STORE[-100:]
        save_chats(CHAT_STORE)
        return {"status": "success", "message": msg}
    return {"status": "error", "message": "Empty message."}

@app.get("/api/flights")
def get_flights():
    try:
        response = session.get("https://flights.cairnsairport.com.au/flights/data")
        if "login" in response.url or response.status_code != 200:
            authenticate_session()
            response = session.get("https://flights.cairnsairport.com.au/flights/data")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database")
def get_database():
    return JSONResponse({"aircraft": AIRCRAFT_DB, "airlines": AIRLINE_DB})
