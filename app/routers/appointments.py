from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import Optional
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/appointments", tags=["Appointments"])

VALID_PRIORITIES = ["emergency", "urgent", "routine"]

@router.post("/", status_code=201, response_model=schemas.AppointmentOut)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if appointment.priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=400, detail=f"Priority must be one of {VALID_PRIORITIES}")

    patient = db.query(models.Patient).filter(models.Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = db.query(models.Doctor).filter(models.Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.date == appointment.date,
        models.Appointment.time == appointment.time,
        models.Appointment.status != "cancelled"
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="This doctor already has an appointment at that date and time")

    new_appointment = models.Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/", response_model=list[schemas.AppointmentOut])
def get_appointments(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by_priority: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    query = db.query(models.Appointment)
    if start_date:
        query = query.filter(models.Appointment.date >= start_date)
    if end_date:
        query = query.filter(models.Appointment.date <= end_date)
    if status:
        query = query.filter(models.Appointment.status == status)
    if priority:
        query = query.filter(models.Appointment.priority == priority)
    if sort_by_priority:
        priority_order = case(
            (models.Appointment.priority == "emergency", 1),
            (models.Appointment.priority == "urgent", 2),
            (models.Appointment.priority == "routine", 3),
            else_=4
        )
        query = query.order_by(priority_order)
    return query.all()

@router.get("/{id}", response_model=schemas.AppointmentOut)
def get_appointment(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{id}/status", response_model=schemas.AppointmentOut)
def update_appointment_status(id: int, update: schemas.AppointmentStatusUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    valid_statuses = ["pending", "confirmed", "completed", "cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
    appointment = db.query(models.Appointment).filter(models.Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = update.status
    db.commit()
    db.refresh(appointment)
    return appointment
