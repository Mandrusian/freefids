from datetime import datetime
import os
from bs4 import BeautifulSoup
from database import AIRCRAFT_DB, AIRLINE_DB
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import requests
import schedule
import time
from twilio.rest import Client

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


@app.post("/api/auth")
def authenticate_user(data: dict = Body(...)):
  password = data.get("password")
  if password == "vaggs54" or password == "admin":
    return {"status": "success", "message": "Authenticated successfully."}
  return {"status": "error", "message": "Invalid access credentials."}


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