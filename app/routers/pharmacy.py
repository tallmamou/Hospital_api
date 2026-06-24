from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

@router.post("/", status_code=201, response_model=schemas.PharmacyDispensingOut)
def record_dispensing(
    data: schemas.PharmacyDispensingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    prescription = db.query(models.Prescription).filter(
        models.Prescription.id == data.prescription_id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    record = models.PharmacyDispensing(
        prescription_id=data.prescription_id,
        dispensed=data.dispensed,
        dispensed_by=data.dispensed_by,
        notes=data.notes,
        dispensed_at=datetime.now(timezone.utc) if data.dispensed else None
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/prescription/{prescription_id}", response_model=schemas.PharmacyDispensingOut)
def get_dispensing_status(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    record = db.query(models.PharmacyDispensing).filter(
        models.PharmacyDispensing.prescription_id == prescription_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="No dispensing record found")
    return record
