"""
SQLModel-based database layer for employee entity storage.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select

DEFAULT_DB_PATH = "sqlite:///employees.db"


class Employee(SQLModel, table=True):
    """Employee model for storing extracted document entities."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    file_path: str
    
    # Personal Info
    full_name: Optional[str] = None
    full_name_conf: Optional[float] = None
    
    # Identity Documents
    aadhaar_number: Optional[str] = None
    aadhaar_conf: Optional[float] = None
    
    pan_number: Optional[str] = None
    pan_conf: Optional[float] = None
    
    passport_number: Optional[str] = None
    passport_conf: Optional[float] = None
    
    # Contact Info
    phone_number: Optional[str] = None
    phone_conf: Optional[float] = None
    
    email: Optional[str] = None
    email_conf: Optional[float] = None
    
    # Additional Info
    dob: Optional[str] = None
    dob_conf: Optional[float] = None
    
    address: Optional[str] = None
    address_conf: Optional[float] = None
    
    gender: Optional[str] = None
    gender_conf: Optional[float] = None
    
    father_name: Optional[str] = None
    father_conf: Optional[float] = None
    
    spouse_name: Optional[str] = None
    spouse_conf: Optional[float] = None
    
    # Raw JSON of all extracted entities
    entities_json: str = Field(default="{}")
    
    # Metadata
    inserted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


def get_engine(db_path: str = DEFAULT_DB_PATH):
    """Create and return a SQLAlchemy engine."""
    return create_engine(db_path, echo=False)


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Create the database and all tables if they don't exist."""
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)


def _get_entity_value_conf(entity: Any) -> tuple[Optional[str], Optional[float]]:
    """Extract value and confidence from an entity dict.
    
    Accepts either {'value': ..., 'confidence': ...} or None.
    Returns (value_or_None, confidence_or_None).
    """
    if entity is None:
        return None, None
    if isinstance(entity, dict):
        return entity.get("value"), entity.get("confidence")
    return None, None


def save_entities(file_path: str, entities: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save extracted entities to the employee table.
    
    Args:
        file_path: Path to the source document
        entities: Dictionary of extracted entities with confidence scores
        db_path: Database connection string
        
    Returns:
        The ID of the inserted employee record
    """
    # Ensure DB/table exists
    init_db(db_path)

    # Extract values and confidence scores
    full_name, full_name_conf = _get_entity_value_conf(entities.get("FULL_NAME"))
    aadhaar_number, aadhaar_conf = _get_entity_value_conf(entities.get("AADHAAR_NUMBER"))
    pan_number, pan_conf = _get_entity_value_conf(entities.get("PAN_NUMBER"))
    passport_number, passport_conf = _get_entity_value_conf(entities.get("PASSPORT_NUMBER"))
    phone_number, phone_conf = _get_entity_value_conf(entities.get("PHONE_NUMBER"))
    email, email_conf = _get_entity_value_conf(entities.get("EMAIL_ADDRESS"))
    dob, dob_conf = _get_entity_value_conf(entities.get("DATE_OF_BIRTH"))
    address, address_conf = _get_entity_value_conf(entities.get("ADDRESS"))
    gender, gender_conf = _get_entity_value_conf(entities.get("GENDER"))
    father_name, father_conf = _get_entity_value_conf(entities.get("FATHER_NAME"))
    spouse_name, spouse_conf = _get_entity_value_conf(entities.get("SPOUSE_NAME"))

    # Create employee record
    employee = Employee(
        file_path=file_path,
        full_name=full_name,
        full_name_conf=full_name_conf,
        aadhaar_number=aadhaar_number,
        aadhaar_conf=aadhaar_conf,
        pan_number=pan_number,
        pan_conf=pan_conf,
        passport_number=passport_number,
        passport_conf=passport_conf,
        phone_number=phone_number,
        phone_conf=phone_conf,
        email=email,
        email_conf=email_conf,
        dob=dob,
        dob_conf=dob_conf,
        address=address,
        address_conf=address_conf,
        gender=gender,
        gender_conf=gender_conf,
        father_name=father_name,
        father_conf=father_conf,
        spouse_name=spouse_name,
        spouse_conf=spouse_conf,
        entities_json=json.dumps(entities, ensure_ascii=False),
    )

    # Insert and return ID
    engine = get_engine(db_path)
    with Session(engine) as session:
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee.id


def query_employees(limit: int = 100, db_path: str = DEFAULT_DB_PATH) -> List[Employee]:
    """Query recent employee records.
    
    Args:
        limit: Maximum number of records to return (ordered by most recent first)
        db_path: Database connection string
        
    Returns:
        List of Employee objects ordered by insertion time (descending)
    """
    engine = get_engine(db_path)
    with Session(engine) as session:
        statement = select(Employee).order_by(Employee.id.desc()).limit(limit)
        return session.exec(statement).all()


def query_employee_by_id(employee_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Employee]:
    """Query a single employee by ID.
    
    Args:
        employee_id: Employee record ID
        db_path: Database connection string
        
    Returns:
        Employee object or None if not found
    """
    engine = get_engine(db_path)
    with Session(engine) as session:
        return session.get(Employee, employee_id)


def query_by_aadhaar(aadhaar: str, db_path: str = DEFAULT_DB_PATH) -> List[Employee]:
    """Query employees by Aadhaar number.
    
    Args:
        aadhaar: Aadhaar number to search for
        db_path: Database connection string
        
    Returns:
        List of matching Employee objects
    """
    engine = get_engine(db_path)
    with Session(engine) as session:
        statement = select(Employee).where(Employee.aadhaar_number == aadhaar)
        return session.exec(statement).all()


def query_by_pan(pan: str, db_path: str = DEFAULT_DB_PATH) -> List[Employee]:
    """Query employees by PAN number.
    
    Args:
        pan: PAN number to search for
        db_path: Database connection string
        
    Returns:
        List of matching Employee objects
    """
    engine = get_engine(db_path)
    with Session(engine) as session:
        statement = select(Employee).where(Employee.pan_number == pan)
        return session.exec(statement).all()
