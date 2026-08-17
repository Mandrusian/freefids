from datetime import datetime
import os
from bs4 import BeautifulSoup
from database import AIRCRAFT_DB, AIRLINE_DB
from fastapi import FastAPI, HTTPException
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

# Optional Twilio configuration for WhatsApp
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "your_account_sid")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
RECIPIENT_WHATSAPP = "whatsapp:+61400000000"

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


def generate_fids_csv():
  try:
    response = session.get("https://flights.cairnsairport.com.au/flights/data")
    if response.status_code != 200:
      authenticate_session()
      response = session.get("https://flights.cairnsairport.com.au/flights/data")

    data = response.json()
    flights = data.get("flights", [])

    ai_key = (
        "KEY_DEF: vector=A/D | airline=IATA | flightNumber=No | portIATA=Dest"
        " | scheduled=ISO | acType=ICAO | acRego=TailNo"
    )
    headers = [
        "id",
        "vector",
        "airline",
        "flightNumber",
        "portIATA",
        "portName",
        "terminal",
        "scheduled",
        "estimated",
        "statusMsgPublic",
        "gate",
        "stand",
        "acType",
        "acRego",
    ]

    csv_rows = [f'"# AI_INTERPRETATION_KEY: {ai_key}"', ",".join(headers)]
    for flight in flights:
      row = [
          f'"{str(flight.get(h, "")).replace('"', '""')}"' for h in headers
      ]
      csv_rows.append(",".join(row))

    filepath = "/home/xavi/Downloads/fids_automated_export.csv"
    with open(filepath, "w", encoding="utf-8") as f:
      f.write("\r\n".join(csv_rows))
    print(f"Automated CSV generated successfully at {filepath}")
    return filepath
  except Exception as e:
    print(f"Error generating CSV: {e}")
    return None


def send_whatsapp_report():
  filepath = generate_fids_csv()
  if not filepath:
    return
  try:
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        body=(
            "✈ *Cairns Airport FIDS Automated Report*\nHere is the latest 3-day"
            " scheduled flight export."
        ),
        from_=TWILIO_WHATSAPP_FROM,
        to=RECIPIENT_WHATSAPP,
    )
    print(f"WhatsApp message sent successfully! SID: {message.sid}")
  except Exception as e:
    print(f"WhatsApp dispatch note: {e}")


schedule.every(3).days.at("08:00").do(send_whatsapp_report)


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
  try:
    with open("index.html", "r", encoding="utf-8") as f:
      return f.read()
  except FileNotFoundError:
    return "<h1>index.html not found!</h1>"


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


@app.post("/api/send-whatsapp")
def trigger_whatsapp_manual():
  send_whatsapp_report()
  return {"status": "success", "message": "WhatsApp dispatch triggered."}