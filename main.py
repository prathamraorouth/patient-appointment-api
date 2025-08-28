from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="Patient Appointment Booking API")

# Database setup
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor TEXT,
    date TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
""")
conn.commit()

# Models
class Patient(BaseModel):
    name: str
    age: int
    gender: str

class Appointment(BaseModel):
    patient_id: int
    doctor: str
    date: str

# Routes
@app.post("/patients")
def create_patient(patient: Patient):
    cursor.execute("INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)", 
                   (patient.name, patient.age, patient.gender))
    conn.commit()
    return {"message": "Patient registered successfully"}

@app.post("/appointments")
def create_appointment(appointment: Appointment):
    cursor.execute("SELECT * FROM patients WHERE id = ?", (appointment.patient_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Patient not found")
    
    cursor.execute("INSERT INTO appointments (patient_id, doctor, date) VALUES (?, ?, ?)",
                   (appointment.patient_id, appointment.doctor, appointment.date))
    conn.commit()
    return {"message": "Appointment booked successfully"}

@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: int):
    cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"id": row[0], "patient_id": row[1], "doctor": row[2], "date": row[3]}
