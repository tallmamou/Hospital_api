from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "doctor"
    registration_code: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone: Optional[str] = None
    blood_type: Optional[str] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone: Optional[str] = None
    blood_type: Optional[str] = None
    national_id: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class PatientOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone: Optional[str]
    blood_type: Optional[str]
    national_id: Optional[str]
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    specialization: str
    phone: Optional[str] = None

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None

class DoctorOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    specialization: str
    phone: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: str
    time: str = "09:00"
    reason: Optional[str] = None
    priority: str = "routine"

class AppointmentStatusUpdate(BaseModel):
    status: str

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date: str
    time: str
    reason: Optional[str]
    priority: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class ConsultationCreate(BaseModel):
    appointment_id: int
    symptoms: str
    symptom_duration: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    blood_pressure: Optional[str] = None
    temperature: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    heart_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

class ConsultationOut(BaseModel):
    id: int
    appointment_id: int
    symptoms: str
    symptom_duration: Optional[str]
    allergies: Optional[str]
    current_medications: Optional[str]
    medical_history: Optional[str]
    family_history: Optional[str]
    blood_pressure: Optional[str]
    temperature: Optional[float]
    weight: Optional[float]
    height: Optional[float]
    heart_rate: Optional[int]
    oxygen_saturation: Optional[float]
    diagnosis: Optional[str]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class PrescriptionCreate(BaseModel):
    appointment_id: int
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    notes: Optional[str] = None

class PrescriptionOut(BaseModel):
    id: int
    appointment_id: int
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class PharmacyDispensingCreate(BaseModel):
    prescription_id: int
    dispensed: bool = False
    dispensed_by: Optional[str] = None
    notes: Optional[str] = None

class PharmacyDispensingOut(BaseModel):
    id: int
    prescription_id: int
    dispensed: bool
    dispensed_at: Optional[datetime]
    dispensed_by: Optional[str]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class PatientFullHistory(BaseModel):
    patient: PatientOut
    appointments: List[AppointmentOut]
    consultations: List[ConsultationOut]
    prescriptions: List[PrescriptionOut]
    class Config:
        from_attributes = True
