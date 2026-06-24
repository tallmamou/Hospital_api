from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/", status_code=201, response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can register patients")
    new_patient = models.Patient(**patient.model_dump(), user_id=current_user.id)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/", response_model=list[schemas.PatientOut])
def get_patients(search: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    query = db.query(models.Patient)
    if search:
        query = query.filter(or_(models.Patient.first_name.ilike(f"%{search}%"), models.Patient.last_name.ilike(f"%{search}%")))
    return query.all()

@router.get("/{id}", response_model=schemas.PatientOut)
def get_patient(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{id}", response_model=schemas.PatientOut)
def update_patient(id: int, updates: schemas.PatientUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update patients")
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{id}", status_code=204)
def delete_patient(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can delete patients")
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()

@router.get("/{id}/appointments", response_model=list[schemas.AppointmentOut])
def get_patient_history(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db.query(models.Appointment).filter(models.Appointment.patient_id == id).all()

@router.get("/{id}/full-history", response_model=schemas.PatientFullHistory)
def get_patient_full_history(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == id).all()
    appointment_ids = [a.id for a in appointments]

    consultations = db.query(models.Consultation).filter(
        models.Consultation.appointment_id.in_(appointment_ids)
    ).all()

    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.appointment_id.in_(appointment_ids)
    ).all()

    return {
        "patient": patient,
        "appointments": appointments,
        "consultations": consultations,
        "prescriptions": prescriptions
    }
