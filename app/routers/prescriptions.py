from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@router.post("/", status_code=201, response_model=schemas.PrescriptionOut)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can write prescriptions")
    appointment = db.query(models.Appointment).filter(models.Appointment.id == prescription.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    new_prescription = models.Prescription(**prescription.model_dump())
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

@router.get("/appointment/{appointment_id}", response_model=list[schemas.PrescriptionOut])
def get_prescriptions_for_appointment(appointment_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    return db.query(models.Prescription).filter(models.Prescription.appointment_id == appointment_id).all()
