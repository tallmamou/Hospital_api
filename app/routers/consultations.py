from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/consultations", tags=["Consultations"])

@router.post("/", status_code=201, response_model=schemas.ConsultationOut)
def create_consultation(
    consultation: schemas.ConsultationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create consultations")

    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == consultation.appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing = db.query(models.Consultation).filter(
        models.Consultation.appointment_id == consultation.appointment_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Consultation already exists for this appointment")

    # Auto update appointment status to in_consultation
    appointment.status = "in_consultation"
    db.commit()

    new_consultation = models.Consultation(**consultation.model_dump())
    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)
    return new_consultation

@router.get("/appointment/{appointment_id}", response_model=schemas.ConsultationOut)
def get_consultation(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    consultation = db.query(models.Consultation).filter(
        models.Consultation.appointment_id == appointment_id
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="No consultation found for this appointment")
    return consultation

@router.put("/appointment/{appointment_id}", response_model=schemas.ConsultationOut)
def update_consultation(
    appointment_id: int,
    updates: schemas.ConsultationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update consultations")
    consultation = db.query(models.Consultation).filter(
        models.Consultation.appointment_id == appointment_id
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(consultation, key, value)
    db.commit()
    db.refresh(consultation)
    return consultation
