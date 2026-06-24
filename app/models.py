from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date, Float, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="doctor")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String, nullable=False)
    phone = Column(String)
    blood_type = Column(String)
    national_id = Column(String, unique=True, nullable=True, index=True)
    address = Column(String)
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    phone = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(String, nullable=False)
    time = Column(String, nullable=False, default="09:00")
    reason = Column(Text)
    priority = Column(String, default="routine")  # emergency, urgent, routine
    status = Column(String, default="waiting")    # waiting, in_consultation, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True)

    # Symptoms
    symptoms = Column(Text, nullable=False)
    symptom_duration = Column(String)          # e.g. "3 days", "2 weeks"

    # Patient reported info
    allergies = Column(Text)                   # e.g. "Penicillin, Peanuts"
    current_medications = Column(Text)         # medicines patient is already taking
    medical_history = Column(Text)             # e.g. "Diabetes, Hypertension"
    family_history = Column(Text)              # e.g. "Father had heart disease"

    # Vital signs (merged in)
    blood_pressure = Column(String)            # e.g. "120/80"
    temperature = Column(Float)               # Celsius
    weight = Column(Float)                    # kg
    height = Column(Float)                    # cm
    heart_rate = Column(Integer)              # bpm
    oxygen_saturation = Column(Float)         # SpO2 %

    # Doctor's assessment
    diagnosis = Column(Text)
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    medicine_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PharmacyDispensing(Base):
    __tablename__ = "pharmacy_dispensing"
    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    dispensed = Column(Boolean, default=False)
    dispensed_at = Column(DateTime(timezone=True), nullable=True)
    dispensed_by = Column(String, nullable=True)   # pharmacist name
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
