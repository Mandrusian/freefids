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

SUPREME_ADMIN_EMAIL = "xottovaggs@gmail.com"
PASSWORD = "vaggs54"

session = requests.Session()

USER_FILE = "users.json"
CHAT_FILE = "chats.json"
NOTICE_FILE = "notices.json"
CUSTOM_FLIGHTS_FILE = "custom_flights.json"
SYSTEM_STATE_FILE = "system_state.json"

ACTIVE_USERS = {}

def load_users():
    default_users = {
        SUPREME_ADMIN_EMAIL: {
            "name": "Xavi (Supreme Admin) 👑", 
            "chat_name": "Xavi", 
            "status": "normal", 
            "role": "supreme", 
            "rank_name": "Supreme",
            "avatar": "✈️",
            "bio": "System Overseer & Administrator.",
            "muted": False,
            "created_at": "2026-01-01"
        },
        "cybernoxal@gmail.com": {
            "name": "Daniel Bestine", 
            "chat_name": "Daniel", 
            "status": "normal", 
            "role": "admin", 
            "rank_name": "Admin",
            "avatar": "🛡️",
            "bio": "Operations & Traffic Control.",
            "muted": False,
            "created_at": "2026-01-10"
        },
        "s3592@plc.qld.edu.au": {
            "name": "Flynn Orme", 
            "chat_name": "Flynn", 
            "status": "normal", 
            "role": "user", 
            "rank_name": "Peasant",
            "avatar": "🔹",
            "bio": "Spotter & FIDS Observer.",
            "muted": False,
            "created_at": "2026-02-01"
        }
    }
    data = {}
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    for email, info in default_users.items():
        if email not in data:
            data[email] = info
    data[SUPREME_ADMIN_EMAIL] = {
        "name": "Xavi (Supreme Admin) 👑", 
        "chat_name": "Xavi", 
        "status": "normal", 
        "role": "supreme", 
        "rank_name": "Supreme",
        "avatar": "✈️",
        "bio": data.get(SUPREME_ADMIN_EMAIL, {}).get("bio", "System Overseer & Administrator."),
        "muted": False,
        "created_at": "2026-01-01"
    }
    save_users(data)
    return data

def save_users(users):
    try:
        users[SUPREME_ADMIN_EMAIL]["role"] = "supreme"
        users[SUPREME_ADMIN_EMAIL]["status"] = "normal"
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
    return [{"id": 1, "sender": "System", "email": "system@fids", "text": "Cairns Telemetry Discussion Feed online.", "time": "08:00", "color": "#94a3b8", "reactions": {}}]

def save_chats(chats):
    try:
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(chats, f, indent=4)
    except Exception as e:
        print(f"Error saving chats: {e}")

def load_notices():
    if os.path.exists(NOTICE_FILE):
        try:
            with open(NOTICE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []

def save_notices(notices):
    try:
        with open(NOTICE_FILE, "w", encoding="utf-8") as f:
            json.dump(notices, f, indent=4)
    except Exception as e:
        print(f"Error saving notices: {e}")

def load_custom_flights():
    if os.path.exists(CUSTOM_FLIGHTS_FILE):
        try:
            with open(CUSTOM_FLIGHTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_custom_flights(flights):
    try:
        with open(CUSTOM_FLIGHTS_FILE, "w", encoding="utf-8") as f:
            json.dump(flights, f, indent=4)
    except Exception as e:
        print(f"Error saving custom flights: {e}")

def load_system_state():
    if os.path.exists(SYSTEM_STATE_FILE):
        try:
            with open(SYSTEM_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"maintenance_mode": False, "maintenance_msg": "System maintenance in progress. FIDS telemetry feed temporarily paused."}

def save_system_state(state):
    try:
        with open(SYSTEM_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving system state: {e}")

USER_STORE = load_users()
CHAT_STORE = load_chats()
NOTICE_STORE = load_notices()
CUSTOM_FLIGHTS_STORE = load_custom_flights()
SYSTEM_STATE_STORE = load_system_state()

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
        payload = {"_token": csrf_token, "email": SUPREME_ADMIN_EMAIL, "password": PASSWORD}
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
        return "<h1>index.html not found!</h1>"

@app.get("/api/notices")
def get_notices():
    global NOTICE_STORE
    NOTICE_STORE = load_notices()
    return NOTICE_STORE

@app.post("/api/admin/notices/add")
def admin_add_notice(data: dict = Body(...)):
    global NOTICE_STORE, USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    
    if email not in USER_STORE or USER_STORE[email].get("role") not in ["admin", "supreme"]:
        return {"status": "error", "message": "Unauthorized."}
        
    NOTICE_STORE = load_notices()
    notice_id = data.get("id")
    
    if notice_id:
        for n in NOTICE_STORE:
            if n.get("id") == notice_id:
                n["target"] = data.get("target", "all")
                n["behavior"] = data.get("behavior", "dismissible")
                n["title"] = data.get("title", "").strip()
                n["msg"] = data.get("msg", "").strip()
                n["color"] = data.get("color", "#0284c7")
                save_notices(NOTICE_STORE)
                return {"status": "success", "notices": NOTICE_STORE}

    new_notice = {
        "id": int(datetime.now().timestamp() * 1000),
        "target": data.get("target", "all"),
        "behavior": data.get("behavior", "dismissible"),
        "title": data.get("title", "").strip(),
        "msg": data.get("msg", "").strip(),
        "color": data.get("color", "#0284c7")
    }
    NOTICE_STORE.append(new_notice)
    save_notices(NOTICE_STORE)
    return {"status": "success", "notices": NOTICE_STORE}

@app.post("/api/admin/notices/delete")
def admin_delete_notice(data: dict = Body(...)):
    global NOTICE_STORE, USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    notice_id = data.get("id")
    
    if email not in USER_STORE or USER_STORE[email].get("role") not in ["admin", "supreme"]:
        return {"status": "error", "message": "Unauthorized."}
        
    NOTICE_STORE = load_notices()
    NOTICE_STORE = [n for n in NOTICE_STORE if n.get("id") != notice_id]
    save_notices(NOTICE_STORE)
    return {"status": "success", "notices": NOTICE_STORE}

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
    
    USER_STORE[email] = {
        "name": name, 
        "chat_name": name.split()[0], 
        "status": "pending", 
        "role": "user", 
        "rank_name": "Peasant",
        "avatar": "🔹",
        "bio": "Registered personnel.",
        "muted": False,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    save_users(USER_STORE)
    return {"status": "success", "message": "Registration received. Pending administrator clearance."}

@app.post("/api/login")
def login_user(data: dict = Body(...)):
    global USER_STORE, SYSTEM_STATE_STORE
    USER_STORE = load_users()
    SYSTEM_STATE_STORE = load_system_state()
    email = data.get("email", "").strip().lower()
    user = USER_STORE.get(email)
    
    if not user:
        return {"status": "error", "message": "Account not found."}
    
    if SYSTEM_STATE_STORE.get("maintenance_mode", False) and user.get("role") not in ["admin", "supreme"]:
        return {"status": "error", "message": SYSTEM_STATE_STORE.get("maintenance_msg", "System under maintenance.")}

    if user["status"] == "pending":
        return {"status": "pending", "message": "Your account is awaiting clearance from Cairns Airport administration."}
    
    if user["status"] == "suspended":
        return {"status": "error", "message": "Account access suspended."}
        
    ACTIVE_USERS[email] = datetime.now().timestamp()
    return {
        "status": "normal", 
        "email": email, 
        "name": user["name"], 
        "chat_name": user.get("chat_name", user["name"]), 
        "role": user.get("role", "user"),
        "rank_name": user.get("rank_name", "Peasant"),
        "avatar": user.get("avatar", "🔹"),
        "bio": user.get("bio", ""),
        "muted": user.get("muted", False),
        "message": "Login successful."
    }

@app.post("/api/heartbeat")
def heartbeat(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    if email:
        ACTIVE_USERS[email] = datetime.now().timestamp()
        
    now = datetime.now().timestamp()
    active_list = []
    for em, t in list(ACTIVE_USERS.items()):
        if now - t < 35:
            if em in USER_STORE:
                active_list.append({
                    "email": em,
                    "name": USER_STORE[em]["name"],
                    "role": USER_STORE[em].get("role", "user"),
                    "rank_name": USER_STORE[em].get("rank_name", "user"),
                    "chat_name": USER_STORE[em].get("chat_name", "User")
                })
        else:
            del ACTIVE_USERS[em]
            
    return {"online_count": max(1, len(active_list)), "active_users": active_list}

@app.post("/api/user/profile")
def get_user_profile(data: dict = Body(...)):
    global USER_STORE, CHAT_STORE
    USER_STORE = load_users()
    CHAT_STORE = load_chats()
    email = data.get("email", "").strip().lower()
    chat_name = data.get("chat_name", "").strip()

    target_email = None
    if email in USER_STORE:
        target_email = email
    else:
        for em, info in USER_STORE.items():
            if info.get("chat_name", "").lower() == chat_name.lower() or info.get("name", "").lower() == chat_name.lower():
                target_email = em
                break

    if not target_email or target_email not in USER_STORE:
        return {"status": "error", "message": "User profile not found."}

    info = USER_STORE[target_email]
    msg_count = sum(1 for m in CHAT_STORE if m.get("email") == target_email)

    return {
        "status": "success",
        "email": target_email,
        "name": info.get("name"),
        "chat_name": info.get("chat_name"),
        "role": info.get("role"),
        "rank_name": info.get("rank_name"),
        "avatar": info.get("avatar", "🔹"),
        "bio": info.get("bio", "No profile bio recorded."),
        "muted": info.get("muted", False),
        "created_at": info.get("created_at", "2026-01-01"),
        "total_messages": msg_count
    }

@app.post("/api/update-profile")
def update_profile(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    new_chat_name = data.get("chat_name", "").strip()
    new_rank_name = data.get("rank_name", "").strip()
    new_avatar = data.get("avatar", "").strip()
    new_bio = data.get("bio", "").strip()
    
    if email in USER_STORE:
        if new_chat_name: USER_STORE[email]["chat_name"] = new_chat_name
        if new_rank_name: USER_STORE[email]["rank_name"] = new_rank_name
        if new_avatar: USER_STORE[email]["avatar"] = new_avatar
        if new_bio is not None: USER_STORE[email]["bio"] = new_bio
        save_users(USER_STORE)
        return {
            "status": "success", 
            "chat_name": USER_STORE[email]["chat_name"], 
            "rank_name": USER_STORE[email]["rank_name"],
            "avatar": USER_STORE[email]["avatar"],
            "bio": USER_STORE[email]["bio"]
        }
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/login")
def admin_login(data: dict = Body(...)):
    password = data.get("password")
    if password == "vaggs54":
        ACTIVE_USERS[SUPREME_ADMIN_EMAIL] = datetime.now().timestamp()
        return {"status": "success", "email": SUPREME_ADMIN_EMAIL, "name": "Xavi (Supreme Admin) 👑", "role": "supreme", "rank_name": "Supreme", "message": "Admin authenticated."}
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
    
    if email == SUPREME_ADMIN_EMAIL:
        return {"status": "error", "message": "Cannot modify Supreme Admin status."}
        
    if email in USER_STORE and status in ["normal", "pending", "suspended"]:
        USER_STORE[email]["status"] = status
        save_users(USER_STORE)
        return {"status": "success", "message": f"Updated status for {email}."}
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/set-mute")
def admin_set_mute(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    muted = data.get("muted", False)
    
    if email == SUPREME_ADMIN_EMAIL:
        return {"status": "error", "message": "Cannot mute Supreme Admin."}
        
    if email in USER_STORE:
        USER_STORE[email]["muted"] = muted
        save_users(USER_STORE)
        return {"status": "success", "message": f"Mute status updated for {email}."}
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/set-role")
def admin_set_role(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    role = data.get("role")
    
    if email == SUPREME_ADMIN_EMAIL:
        return {"status": "error", "message": "Cannot modify Supreme Admin role."}
        
    if email in USER_STORE and role in ["user", "admin"]:
        USER_STORE[email]["role"] = role
        if role == 'admin':
            USER_STORE[email]["rank_name"] = "Admin"
        else:
            USER_STORE[email]["rank_name"] = "Peasant"
        save_users(USER_STORE)
        return {"status": "success", "message": f"Updated role for {email} to {role}."}
    return {"status": "error", "message": "User not found or invalid role."}

@app.post("/api/admin/force-edit-user")
def admin_force_edit_user(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    new_name = data.get("name", "").strip()
    new_chat_name = data.get("chat_name", "").strip()
    new_rank_name = data.get("rank_name", "").strip()
    
    if email == SUPREME_ADMIN_EMAIL:
        return {"status": "error", "message": "Cannot override Supreme Admin account."}
        
    if email in USER_STORE:
        if new_name: USER_STORE[email]["name"] = new_name
        if new_chat_name: USER_STORE[email]["chat_name"] = new_chat_name
        if new_rank_name: USER_STORE[email]["rank_name"] = new_rank_name
        save_users(USER_STORE)
        return {"status": "success", "message": f"Updated user profile for {email}."}
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/delete-user")
def admin_delete_user(data: dict = Body(...)):
    global USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    
    if email == SUPREME_ADMIN_EMAIL:
        return {"status": "error", "message": "Cannot delete Supreme Admin."}
        
    if email in USER_STORE:
        del USER_STORE[email]
        save_users(USER_STORE)
        return {"status": "success", "message": f"Deleted user {email}."}
    return {"status": "error", "message": "User not found."}

@app.post("/api/admin/system-state")
def update_system_state(data: dict = Body(...)):
    global SYSTEM_STATE_STORE, USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    
    if email not in USER_STORE or USER_STORE[email].get("role") not in ["admin", "supreme"]:
        return {"status": "error", "message": "Unauthorized."}
        
    SYSTEM_STATE_STORE["maintenance_mode"] = data.get("maintenance_mode", False)
    if "maintenance_msg" in data:
        SYSTEM_STATE_STORE["maintenance_msg"] = data.get("maintenance_msg")
        
    save_system_state(SYSTEM_STATE_STORE)
    return {"status": "success", "state": SYSTEM_STATE_STORE}

@app.get("/api/admin/system-state")
def get_system_state():
    global SYSTEM_STATE_STORE
    SYSTEM_STATE_STORE = load_system_state()
    return SYSTEM_STATE_STORE

@app.post("/api/admin/inject-flight")
def admin_inject_flight(data: dict = Body(...)):
    global CUSTOM_FLIGHTS_STORE, USER_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    
    if email not in USER_STORE or USER_STORE[email].get("role") not in ["admin", "supreme"]:
        return {"status": "error", "message": "Unauthorized."}
        
    new_flight = {
        "id": f"CF-{int(datetime.now().timestamp())}",
        "vector": data.get("vector", "A"),
        "airline": data.get("airline", "VIP").upper(),
        "flightNumber": data.get("flightNumber", "1"),
        "portIATA": data.get("portIATA", "CNS").upper(),
        "portName": data.get("portName", "Cairns Local Operational"),
        "terminal": data.get("terminal", "T1"),
        "scheduled": data.get("scheduled", datetime.now().isoformat()),
        "statusMsgPublic": data.get("status", "Special Ops"),
        "gate": data.get("gate", "Bay 1"),
        "acType": data.get("acType", "GLF6").upper(),
        "acRego": data.get("acRego", "N1VIP").upper()
    }
    CUSTOM_FLIGHTS_STORE.append(new_flight)
    save_custom_flights(CUSTOM_FLIGHTS_STORE)
    return {"status": "success", "custom_flights": CUSTOM_FLIGHTS_STORE}

@app.get("/api/chat/messages")
def get_messages():
    global CHAT_STORE
    CHAT_STORE = load_chats()
    return CHAT_STORE

@app.post("/api/chat/messages")
def post_message(data: dict = Body(...)):
    global CHAT_STORE, USER_STORE
    USER_STORE = load_users()
    CHAT_STORE = load_chats()
    
    email = data.get("email", "").strip().lower()
    impersonate_email = data.get("impersonate_email", "").strip().lower()
    text = data.get("text", "").strip()
    
    posting_email = email
    if impersonate_email and impersonate_email in USER_STORE and email in USER_STORE:
        if USER_STORE[email].get("role") in ["admin", "supreme"]:
            posting_email = impersonate_email

    user_info = USER_STORE.get(posting_email, {"name": "User", "chat_name": "User", "role": "user", "rank_name": "Peasant", "muted": False})
    
    if user_info.get("muted", False):
        return {"status": "error", "message": "Your chat posting privileges are currently muted by administration."}

    role = user_info.get("role", "user")
    if role == "supreme":
        color = "#38bdf8"
    elif role == "admin":
        color = "#c084fc"
    else:
        color = "#34d399"
        
    avatar = user_info.get("avatar", "🔹")
    sender_display = f"{avatar} {user_info.get('chat_name', 'User')} [{user_info.get('rank_name', 'user')}]"
            
    if text:
        msg = {
            "id": len(CHAT_STORE) + 1,
            "sender": sender_display,
            "email": posting_email,
            "text": text,
            "time": datetime.now().strftime("%H:%M"),
            "color": color,
            "reactions": {}
        }
        CHAT_STORE.append(msg)
        if len(CHAT_STORE) > 150:
            CHAT_STORE = CHAT_STORE[-150:]
        save_chats(CHAT_STORE)
        return {"status": "success", "message": msg}
    return {"status": "error", "message": "Empty message."}

@app.post("/api/chat/react")
def react_message(data: dict = Body(...)):
    global CHAT_STORE
    CHAT_STORE = load_chats()
    msg_id = data.get("id")
    emoji = data.get("emoji")
    user = data.get("user")
    
    for m in CHAT_STORE:
        if m.get("id") == msg_id:
            if "reactions" not in m:
                m["reactions"] = {}
            if emoji not in m["reactions"]:
                m["reactions"][emoji] = []
            if user in m["reactions"][emoji]:
                m["reactions"][emoji].remove(user)
                if not m["reactions"][emoji]:
                    del m["reactions"][emoji]
            else:
                m["reactions"][emoji].append(user)
            save_chats(CHAT_STORE)
            return {"status": "success", "reactions": m["reactions"]}
    return {"status": "error", "message": "Message not found."}

@app.post("/api/chat/clear")
def clear_chat(data: dict = Body(...)):
    global USER_STORE, CHAT_STORE
    USER_STORE = load_users()
    email = data.get("email", "").strip().lower()
    if email in USER_STORE and USER_STORE[email].get("role") in ["admin", "supreme"]:
        CHAT_STORE = [{"id": 1, "sender": "System", "email": "system@fids", "text": "Chat history purged by system administrator.", "time": datetime.now().strftime("%H:%M"), "color": "#f87171", "reactions": {}}]
        save_chats(CHAT_STORE)
        return {"status": "success"}
    return {"status": "error", "message": "Unauthorized."}

@app.get("/api/flights")
def get_flights():
    try:
        response = session.get("https://flights.cairnsairport.com.au/flights/data")
        if "login" in response.url or response.status_code != 200:
            authenticate_session()
            response = session.get("https://flights.cairnsairport.com.au/flights/data")
            
        data = response.json()
        live_flights = data.get("flights", []) if isinstance(data, dict) else []
        
        custom_list = load_custom_flights()
        combined = custom_list + live_flights
        return {"flights": combined}
    except Exception as e:
        custom_list = load_custom_flights()
        return {"flights": custom_list}

@app.get("/api/database")
def get_database():
    return JSONResponse({"aircraft": AIRCRAFT_DB, "airlines": AIRLINE_DB})
