from datetime import datetime
import os
from bs4 import BeautifulSoup
from database import AIRCRAFT_DB, AIRLINE_DB
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import requests

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

# Shared persistent user store pre-populated with an example pending user for testing
USER_STORE = {
    "xottovaggs@gmail.com": {"name": "Xavi (Admin)", "status": "normal"},
    "testuser@gmail.com": {"name": "Test Aviator", "status": "pending"},
}


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
        "Referer": "https://flights.cairnsairport.com.au/login",
    }
    payload = {"_token": csrf_token, "email": EMAIL, "password": PASSWORD}
    login_response = session.post(
        "https://flights.cairnsairport.com.au/login", data=payload, headers=headers
    )
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
  email = data.get("email", "").strip().lower()
  name = data.get("name", "").strip()
  if not email or not name:
    return {"status": "error", "message": "Email and Name are required."}

  if email in USER_STORE:
    return {
        "status": "error",
        "message": "Account already exists. Please log in.",
    }

  USER_STORE[email] = {"name": name, "status": "pending"}
  return {
      "status": "success",
      "message": "Registration received. Please wait for admin approval.",
  }


@app.post("/api/login")
def login_user(data: dict = Body(...)):
  email = data.get("email", "").strip().lower()
  user = USER_STORE.get(email)

  if not user:
    return {
        "status": "error",
        "message": "Account not found. Please create an account.",
    }

  if user["status"] == "pending":
    return {
        "status": "pending",
        "message": (
            "Your account is awaiting approval from Cairns Airport"
            " administration."
        ),
    }

  if user["status"] == "suspended":
    return {
        "status": "error",
        "message": "This account has been suspended.",
    }

  return {
      "status": "normal",
      "name": user["name"],
      "message": "Login successful.",
  }


@app.post("/api/admin/login")
def admin_login(data: dict = Body(...)):
  password = data.get("password")
  if password == "vaggs54":
    return {"status": "success", "message": "Admin authenticated."}
  return {"status": "error", "message": "Incorrect administrator password."}


@app.get("/api/admin/users")
def admin_get_users():
  return USER_STORE


@app.post("/api/admin/set-status")
def admin_set_status(data: dict = Body(...)):
  email = data.get("email", "").strip().lower()
  status = data.get("status")
  if email in USER_STORE and status in ["normal", "pending", "suspended"]:
    USER_STORE[email]["status"] = status
    return {
        "status": "success",
        "message": f"Updated status for {email}.",
    }
  return {"status": "error", "message": "User not found."}


@app.post("/api/admin/delete-user")
def admin_delete_user(data: dict = Body(...)):
  email = data.get("email", "").strip().lower()
  if email in USER_STORE:
    del USER_STORE[email]
    return {"status": "success", "message": f"Deleted user {email}."}
  return {"status": "error", "message": "User not found."}


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