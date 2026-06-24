from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/", status_code=201, response_model=schemas.DoctorOut)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    new_doctor = models.Doctor(**doctor.model_dump(), user_id=current_user.id)
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

@router.get("/", response_model=list[schemas.DoctorOut])
def get_doctors(search: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    query = db.query(models.Doctor)
    if search:
        query = query.filter(or_(models.Doctor.first_name.ilike(f"%{search}%"), models.Doctor.last_name.ilike(f"%{search}%")))
    return query.all()

@router.get("/{id}", response_model=schemas.DoctorOut)
def get_doctor(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.put("/{id}", response_model=schemas.DoctorOut)
def update_doctor(id: int, updates: schemas.DoctorUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{id}", status_code=204)
def delete_doctor(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own profile")
    db.delete(doctor)
    db.commit()

@router.get("/{id}/appointments", response_model=list[schemas.AppointmentOut])
def get_doctor_schedule(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == id).all()
