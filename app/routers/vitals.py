from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/vitals", tags=["Vital Signs"])

@router.post("/", status_code=201, response_model=schemas.VitalSignOut)
def create_vital_sign(vital: schemas.VitalSignCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can record vital signs")
    appointment = db.query(models.Appointment).filter(models.Appointment.id == vital.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    new_vital = models.VitalSign(**vital.model_dump())
    db.add(new_vital)
    db.commit()
    db.refresh(new_vital)
    return new_vital

@router.get("/appointment/{appointment_id}", response_model=list[schemas.VitalSignOut])
def get_vitals_for_appointment(appointment_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    return db.query(models.VitalSign).filter(models.VitalSign.appointment_id == appointment_id).all()
