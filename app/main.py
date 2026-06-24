from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import auth, patients, doctors, appointments, prescriptions, consultations, pharmacy

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Management API - Guinea", version="3.0.0")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(consultations.router)
app.include_router(prescriptions.router)
app.include_router(pharmacy.router)

@app.get("/")
def root():
    return {"message": "🏥 Hospital Management API - République de Guinée"}
