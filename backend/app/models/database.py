"""
SQLAlchemy Database Models for AILIFF AI Engine
Aligned with actual PostgreSQL database schema
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, Text, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import DECIMAL
from datetime import datetime
import uuid
import enum

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


# ============================================================================
# ENUM TYPES (matching PostgreSQL custom types)
# ============================================================================

class UserRole(enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    SALES_ENGINEER = "sales_engineer"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class CustomerType(enum.Enum):
    """Customer classification types."""
    RETAIL = "retail"
    CONTRACTOR = "contractor"
    GOVERNMENT = "government"
    NGO = "ngo"
    CORPORATE = "corporate"
    DISTRIBUTOR = "distributor"


class InquiryType(enum.Enum):
    """Types of project inquiries."""
    PUMP_SIZING = "pump_sizing"
    WATER_TREATMENT = "water_treatment"
    SOLAR_PUMPING = "solar_pumping"
    IRRIGATION = "irrigation"
    GENERATOR = "generator"
    GENERAL = "general"


class InquiryStatus(enum.Enum):
    """Status of inquiries."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DESIGN_COMPLETE = "design_complete"
    QUOTED = "quoted"
    WON = "won"
    LOST = "lost"
    ON_HOLD = "on_hold"


class PriorityLevel(enum.Enum):
    """Priority levels for inquiries."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DesignStatus(enum.Enum):
    """Status of system designs."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"


class EquipmentCategory(enum.Enum):
    """Categories of equipment."""
    PUMP = "pump"
    SOLAR_PANEL = "solar_panel"
    INVERTER = "inverter"
    CONTROLLER = "controller"
    TANK = "tank"
    PIPE = "pipe"
    FITTING = "fitting"
    FILTER = "filter"
    TREATMENT = "treatment"
    ELECTRICAL = "electrical"
    ACCESSORY = "accessory"


class ItemCategory(enum.Enum):
    """Categories for quotation line items."""
    EQUIPMENT = "equipment"
    INSTALLATION = "installation"
    CIVIL_WORKS = "civil_works"
    ELECTRICAL = "electrical"
    COMMISSIONING = "commissioning"
    TRANSPORT = "transport"
    WARRANTY = "warranty"
    SERVICE = "service"


class QuotationStatus(enum.Enum):
    """Status of quotations."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVISED = "revised"


class InstallationStatus(enum.Enum):
    """Status of iDayliff installations."""
    PENDING = "pending"
    INSTALLED = "installed"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


# ============================================================================
# CORE TABLES
# ============================================================================

class UserModel(Base):
    """User accounts and authentication."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    department = Column(String(255), nullable=False)

    # Relationships
    assigned_inquiries = relationship("InquiryModel", foreign_keys="InquiryModel.assigned_to", back_populates="assignee")
    created_inquiries = relationship("InquiryModel", foreign_keys="InquiryModel.created_by", back_populates="creator")
    customers = relationship("CustomerModel", back_populates="sales_representative")
    system_designs = relationship("SystemDesignModel", back_populates="creator")
    quotations = relationship("QuotationModel", back_populates="creator")

    __table_args__ = (
        Index('idx_email', email),
        Index('idx_role', role),
        Index('idx_is_active', is_active),
    )


class CustomerModel(Base):
    """Customer master data synced with Business Central."""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_no = Column(String(50), unique=True, nullable=False)
    bc_customer_id = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Kenya")
    customer_type = Column(SQLEnum(CustomerType), nullable=False)
    credit_limit = Column(DECIMAL(15, 2), nullable=True)
    payment_terms = Column(String(100), nullable=True)
    sales_representative_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sales_representative = relationship("UserModel", back_populates="customers")
    inquiries = relationship("InquiryModel", back_populates="customer")
    lab_reports = relationship("LabReportModel", back_populates="customer")
    quotations = relationship("QuotationModel", back_populates="customer")
    idayliff_installations = relationship("IDayliffInstallationModel", back_populates="customer")

    __table_args__ = (
        Index('idx_customer_no', customer_no),
        Index('idx_name', name),
        Index('idx_customer_type', customer_type),
        Index('idx_sales_representative_id', sales_representative_id),
    )


class InquiryModel(Base):
    """Unified entry point for all project inquiries."""
    __tablename__ = "inquiries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inquiry_number = Column(String(50), unique=True, nullable=False)
    inquiry_type = Column(SQLEnum(InquiryType), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    site_location = Column(Text, nullable=True)
    inquiry_status = Column(SQLEnum(InquiryStatus), default=InquiryStatus.NEW)
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("CustomerModel", back_populates="inquiries")
    assignee = relationship("UserModel", foreign_keys=[assigned_to], back_populates="assigned_inquiries")
    creator = relationship("UserModel", foreign_keys=[created_by], back_populates="created_inquiries")
    lab_reports = relationship("LabReportModel", back_populates="inquiry")
    solar_assessments = relationship("SolarAssessmentModel", back_populates="inquiry")
    site_assessments = relationship("SiteAssessmentModel", back_populates="inquiry")
    system_designs = relationship("SystemDesignModel", back_populates="inquiry")
    quotations = relationship("QuotationModel", back_populates="inquiry")

    __table_args__ = (
        Index('idx_inquiry_number', inquiry_number),
        Index('idx_customer_id', customer_id),
        Index('idx_inquiry_status', inquiry_status),
        Index('idx_inquiry_type', inquiry_type),
        Index('idx_assigned_to', assigned_to),
    )


# ============================================================================
# WATER TREATMENT TABLES
# ============================================================================

class LabReportModel(Base):
    """Water quality test reports."""
    __tablename__ = "lab_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inquiry_id = Column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)  # Nullable to allow uploads without customer
    reference_no = Column(String(100), unique=True, nullable=False)
    client_name = Column(String(255), nullable=False)
    sampling_date = Column(Date, nullable=False)
    water_source = Column(String(255), nullable=False)
    site_location = Column(Text, nullable=True)
    pdf_url = Column(Text, nullable=True)
    minio_bucket = Column(String(100), nullable=True)
    minio_object_name = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inquiry = relationship("InquiryModel", back_populates="lab_reports")
    customer = relationship("CustomerModel", back_populates="lab_reports")
    parameters = relationship("WaterQualityParameterModel", back_populates="lab_report", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_reference_no', reference_no),
        Index('idx_lab_customer_id', customer_id),
        Index('idx_lab_inquiry_id', inquiry_id),
    )


class WaterQualityParameterModel(Base):
    """Individual water test parameters and results."""
    __tablename__ = "water_quality_parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_report_id = Column(UUID(as_uuid=True), ForeignKey("lab_reports.id"), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    value = Column(String(50), nullable=False)
    units = Column(String(50), nullable=True)
    who_guideline = Column(String(100), nullable=True)
    remarks = Column(String(10), nullable=True)  # PASS, FAIL, etc.

    # Relationships
    lab_report = relationship("LabReportModel", back_populates="parameters")

    __table_args__ = (
        Index('idx_lab_report_id', lab_report_id),
        Index('idx_parameter_name', parameter_name),
    )


class WaterTreatmentWorkflowResultModel(Base):
    """
    Persisted water treatment workflow result (recommendations + options).
    Used by proposal generation to load options/products by lab_report_id + workflow_id
    so the client does not need to re-send the full recommendations payload.
    """
    __tablename__ = "water_treatment_workflow_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_report_id = Column(UUID(as_uuid=True), ForeignKey("lab_reports.id"), nullable=False, index=True)
    workflow_id = Column(String(80), nullable=False, index=True)
    primary_process = Column(String(20), nullable=True)
    permeate_output_m3_hr = Column(Float, nullable=True)
    treatment_design = Column(JSONB, nullable=True)
    options = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    agent_response = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_wt_workflow_lab', lab_report_id, workflow_id),
    )


# ============================================================================
# ASSESSMENT TABLES
# ============================================================================

class SolarAssessmentModel(Base):
    """Site assessments for solar pumping systems."""
    __tablename__ = "solar_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inquiry_id = Column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=False)
    water_source_type = Column(String(50), nullable=False)
    static_water_level = Column(DECIMAL(10, 2), nullable=True)
    well_depth = Column(DECIMAL(10, 2), nullable=True)
    daily_water_requirement = Column(DECIMAL(10, 2), nullable=False)
    peak_sun_hours = Column(DECIMAL(4, 2), nullable=True)
    delivery_distance = Column(DECIMAL(10, 2), nullable=True)
    storage_capacity = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inquiry = relationship("InquiryModel", back_populates="solar_assessments")

    __table_args__ = (
        Index('idx_solar_inquiry_id', inquiry_id),
    )


class SiteAssessmentModel(Base):
    """General site assessments for pumps, generators, etc."""
    __tablename__ = "site_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inquiry_id = Column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=False)
    water_source = Column(String(100), nullable=True)
    depth_to_water = Column(DECIMAL(10, 2), nullable=True)
    power_source = Column(String(50), nullable=True)
    soil_type = Column(String(50), nullable=True)
    special_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inquiry = relationship("InquiryModel", back_populates="site_assessments")

    __table_args__ = (
        Index('idx_site_inquiry_id', inquiry_id),
    )


# ============================================================================
# DESIGN TABLES
# ============================================================================

class SystemDesignModel(Base):
    """AI-generated system designs and calculations."""
    __tablename__ = "system_designs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_number = Column(String(50), unique=True, nullable=False)
    inquiry_id = Column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=False)
    design_status = Column(SQLEnum(DesignStatus), default=DesignStatus.DRAFT)
    total_dynamic_head = Column(DECIMAL(10, 2), nullable=True)
    required_flow_rate = Column(DECIMAL(10, 2), nullable=True)
    motor_input_power_kw = Column(DECIMAL(10, 2), nullable=True)
    ai_confidence_score = Column(DECIMAL(5, 2), nullable=True)
    ai_recommendations = Column(JSONB, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inquiry = relationship("InquiryModel", back_populates="system_designs")
    creator = relationship("UserModel", back_populates="system_designs")
    quotations = relationship("QuotationModel", back_populates="system_design")


# ============================================================================
# PRODUCTS TABLES
# ============================================================================

class EquipmentModel(Base):
    """Unified product catalog synced with Business Central."""
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(SQLEnum(EquipmentCategory), nullable=False)
    model_name = Column(String(255), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    bc_item_no = Column(String(100), unique=True, nullable=True)
    specifications = Column(JSONB, nullable=True)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    quantity_available = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (one-to-one with extended tables)
    pump_specs = relationship("PumpModel", back_populates="equipment", uselist=False)
    solar_panel_specs = relationship("SolarPanelModel", back_populates="equipment", uselist=False)
    quotation_line_items = relationship("QuotationLineItemModel", back_populates="equipment")
    idayliff_installations = relationship("IDayliffInstallationModel", back_populates="equipment")

    __table_args__ = (
        Index('idx_category', category),
        Index('idx_sku', sku),
        Index('idx_bc_item_no', bc_item_no),
        Index('idx_equipment_is_active', is_active),
    )


class PumpModel(Base):
    """Extended pump specifications."""
    __tablename__ = "pumps"

    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), primary_key=True)
    motor_power_kw = Column(DECIMAL(5, 2), nullable=False)
    max_flow_rate = Column(DECIMAL(10, 2), nullable=False)
    max_head = Column(DECIMAL(10, 2), nullable=False)
    voltage_ac = Column(Integer, nullable=True)
    phase_type = Column(String(20), nullable=True)
    performance_curve_data = Column(JSONB, nullable=True)

    # Relationships
    equipment = relationship("EquipmentModel", back_populates="pump_specs")


class SolarPanelModel(Base):
    """Solar panel specifications."""
    __tablename__ = "solar_panels"

    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), primary_key=True)
    rated_power_wp = Column(Integer, nullable=False)
    voc = Column(DECIMAL(5, 2), nullable=False)
    vmp = Column(DECIMAL(5, 2), nullable=False)
    efficiency = Column(DECIMAL(5, 2), nullable=True)
    cell_type = Column(String(50), nullable=True)

    # Relationships
    equipment = relationship("EquipmentModel", back_populates="solar_panel_specs")


# ============================================================================
# PUMP CURVE DATA (for binomial expansion analysis)
# ============================================================================

class PumpCurveModel(Base):
    """
    Pump curve data with polynomial coefficients for binomial expansion:
    H(Q) = A*Q² + B*Q + C
    η(Q) = D*Q² + E*Q + F
    P(Q) = G*Q² + H*Q + I
    """
    __tablename__ = "pump_curves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False, index=True)

    # Polynomial coefficients for H-Q curve (Head vs Flow)
    hq_coef_a = Column(Float, nullable=False)  # Quadratic coefficient
    hq_coef_b = Column(Float, nullable=False)  # Linear coefficient
    hq_coef_c = Column(Float, nullable=False)  # Constant (shutoff head)

    # Polynomial coefficients for η-Q curve (Efficiency vs Flow)
    eff_coef_a = Column(Float, nullable=True)
    eff_coef_b = Column(Float, nullable=True)
    eff_coef_c = Column(Float, nullable=True)

    # Polynomial coefficients for P-Q curve (Power vs Flow)
    power_coef_a = Column(Float, nullable=True)
    power_coef_b = Column(Float, nullable=True)
    power_coef_c = Column(Float, nullable=True)

    # Operating range
    min_flow = Column(Float, nullable=False)
    max_flow = Column(Float, nullable=False)

    # Curve metadata
    impeller_diameter_mm = Column(Float, nullable=True)
    speed_rpm = Column(Integer, default=2900)

    # R² values for curve fitting quality
    hq_r_squared = Column(Float, nullable=True)
    eff_r_squared = Column(Float, nullable=True)
    power_r_squared = Column(Float, nullable=True)

    # Raw data points
    raw_curve_points = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# QUOTATIONS TABLES
# ============================================================================

class QuotationModel(Base):
    """Comprehensive quotation system for all products."""
    __tablename__ = "quotations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_number = Column(String(50), unique=True, nullable=False)
    inquiry_id = Column(UUID(as_uuid=True), ForeignKey("inquiries.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    system_design_id = Column(UUID(as_uuid=True), ForeignKey("system_designs.id"), nullable=True)
    quotation_title = Column(String(255), nullable=False)
    status = Column(SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT)
    subtotal = Column(DECIMAL(15, 2), nullable=False)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(10), default="KES")
    quotation_date = Column(Date, nullable=False)
    valid_until_date = Column(Date, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inquiry = relationship("InquiryModel", back_populates="quotations")
    customer = relationship("CustomerModel", back_populates="quotations")
    system_design = relationship("SystemDesignModel", back_populates="quotations")
    creator = relationship("UserModel", back_populates="quotations")
    line_items = relationship("QuotationLineItemModel", back_populates="quotation", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_quotation_number', quotation_number),
        Index('idx_quote_customer_id', customer_id),
        Index('idx_quote_inquiry_id', inquiry_id),
        Index('idx_status', status),
    )


class QuotationLineItemModel(Base):
    """Individual items in quotations."""
    __tablename__ = "quotation_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=True)
    item_category = Column(SQLEnum(ItemCategory), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    line_total = Column(DECIMAL(12, 2), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quotation = relationship("QuotationModel", back_populates="line_items")
    equipment = relationship("EquipmentModel", back_populates="quotation_line_items")

    __table_args__ = (
        Index('idx_quotation_id', quotation_id),
        Index('idx_equipment_id', equipment_id),
    )


# ============================================================================
# iDAYLIFF IoT TABLES
# ============================================================================

class IDayliffInstallationModel(Base):
    """Deployed pump installations with IoT monitoring."""
    __tablename__ = "idayliff_installations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installation_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=True)
    pump_model = Column(String(255), nullable=False)
    site_name = Column(String(255), nullable=False)
    status = Column(SQLEnum(InstallationStatus), default=InstallationStatus.PENDING)
    installation_date = Column(Date, nullable=False)
    warranty_expiry = Column(Date, nullable=True)
    health_score = Column(Integer, nullable=True)
    total_running_hours = Column(Integer, default=0)

    # Relationships
    customer = relationship("CustomerModel", back_populates="idayliff_installations")
    equipment = relationship("EquipmentModel", back_populates="idayliff_installations")
    telemetry_history = relationship("IDayliffTelemetryModel", back_populates="installation", cascade="all, delete-orphan")
    alarms = relationship("IDayliffAlarmModel", back_populates="installation", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_installation_no', installation_no),
        Index('idx_install_customer_id', customer_id),
        Index('idx_install_equipment_id', equipment_id),
    )


class IDayliffTelemetryModel(Base):
    """Historical telemetry data from pump sensors."""
    __tablename__ = "idayliff_telemetry_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installation_id = Column(UUID(as_uuid=True), ForeignKey("idayliff_installations.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    flow_rate = Column(DECIMAL(10, 2), nullable=True)
    pressure = Column(DECIMAL(10, 2), nullable=True)
    power_consumption = Column(DECIMAL(10, 2), nullable=True)
    temperature = Column(DECIMAL(10, 2), nullable=True)
    vibration = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    installation = relationship("IDayliffInstallationModel", back_populates="telemetry_history")

    __table_args__ = (
        Index('idx_telemetry_installation_id', installation_id),
        Index('idx_timestamp', timestamp),
    )


class IDayliffAlarmModel(Base):
    """Pump alarms and alerts."""
    __tablename__ = "idayliff_alarms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installation_id = Column(UUID(as_uuid=True), ForeignKey("idayliff_installations.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    severity = Column(String(20), nullable=False)  # info, warning, critical
    alarm_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    installation = relationship("IDayliffInstallationModel", back_populates="alarms")

    __table_args__ = (
        Index('idx_alarm_installation_id', installation_id),
        Index('idx_resolved', resolved),
    )


# ============================================================================
# WORKFLOW LOGS (for AI execution tracking)
# ============================================================================

class WorkflowLogModel(Base):
    """AI workflow execution logs."""
    __tablename__ = "workflow_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(50), index=True)
    workflow_type = Column(String(50))

    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(30))
    user_email = Column(String(255), nullable=True)

    # Agent execution
    agent_results = Column(JSONB, nullable=True)

    # Input/Output
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)

    # Performance
    total_tokens_used = Column(Integer, nullable=True)
    total_execution_time_seconds = Column(Float, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_stage = Column(String(50), nullable=True)


class WorkflowTraceModel(Base):
    """Fine-grained workflow trace events for streaming to the frontend."""
    __tablename__ = "workflow_traces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(50), index=True, nullable=False)
    user_email = Column(String(255), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_trace_workflow_time', workflow_id, created_at),
    )


class DocumentContextChunkModel(Base):
    """Chunked text extracted from product manuals for contextual retrieval."""
    __tablename__ = "document_context_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(255), nullable=False, index=True)
    subcategory = Column(String(255), nullable=True, index=True)
    source_path = Column(Text, nullable=False)
    source_name = Column(String(255), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_hash = Column(String(64), nullable=False, unique=True, index=True)
    context_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_doc_context_category', category),
        Index('idx_doc_context_subcategory', subcategory),
    )


class DepartmentsModel(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class UserFeedbacksModel(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def create_tables(engine):
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_all_models():
    """Return list of all model classes."""
    return [
        UserModel,
        CustomerModel,
        InquiryModel,
        LabReportModel,
        WaterQualityParameterModel,
        WaterTreatmentWorkflowResultModel,
        SolarAssessmentModel,
        SiteAssessmentModel,
        SystemDesignModel,
        EquipmentModel,
        PumpModel,
        SolarPanelModel,
        PumpCurveModel,
        QuotationModel,
        QuotationLineItemModel,
        IDayliffInstallationModel,
        IDayliffTelemetryModel,
        IDayliffAlarmModel,
        WorkflowLogModel,
        WorkflowTraceModel,
        DocumentContextChunkModel,
        DepartmentsModel,
        UserFeedbacksModel,
    ]
