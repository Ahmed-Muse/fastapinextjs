"""
Pydantic Schemas for AILIFF AI Engine
Aligned with actual PostgreSQL database schema
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# ============================================================================
# ENUMS (matching database types)
# ============================================================================

class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    SALES_ENGINEER = "sales_engineer"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class CustomerType(str, Enum):
    """Customer classification types."""
    RETAIL = "retail"
    CONTRACTOR = "contractor"
    GOVERNMENT = "government"
    NGO = "ngo"
    CORPORATE = "corporate"
    DISTRIBUTOR = "distributor"


class InquiryType(str, Enum):
    """Types of project inquiries."""
    PUMP_SIZING = "pump_sizing"
    WATER_TREATMENT = "water_treatment"
    SOLAR_PUMPING = "solar_pumping"
    IRRIGATION = "irrigation"
    GENERATOR = "generator"
    GENERAL = "general"


class InquiryStatus(str, Enum):
    """Status of inquiries."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DESIGN_COMPLETE = "design_complete"
    QUOTED = "quoted"
    WON = "won"
    LOST = "lost"
    ON_HOLD = "on_hold"


class PriorityLevel(str, Enum):
    """Priority levels for inquiries."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DesignStatus(str, Enum):
    """Status of system designs."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"


class EquipmentCategory(str, Enum):
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


class ItemCategory(str, Enum):
    """Categories for quotation line items."""
    EQUIPMENT = "equipment"
    INSTALLATION = "installation"
    CIVIL_WORKS = "civil_works"
    ELECTRICAL = "electrical"
    COMMISSIONING = "commissioning"
    TRANSPORT = "transport"
    WARRANTY = "warranty"
    SERVICE = "service"


class QuotationStatus(str, Enum):
    """Status of quotations."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVISED = "revised"


class InstallationStatus(str, Enum):
    """Status of iDayliff installations."""
    PENDING = "pending"
    INSTALLED = "installed"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class Currency(str, Enum):
    """Supported currencies."""
    KES = "KES"
    UGX = "UGX"
    TZS = "TZS"
    USD = "USD"
    EUR = "EUR"


class WaterSourceType(str, Enum):
    """Types of water sources."""
    BOREHOLE = "borehole"
    RIVER = "river"
    DAM = "dam"
    MUNICIPAL = "municipal"
    RAINWATER = "rainwater"
    WELL = "well"
    LAKE = "lake"


class TreatmentObjective(str, Enum):
    """Water treatment objectives."""
    POTABLE = "potable"
    IRRIGATION = "irrigation"
    INDUSTRIAL = "industrial"
    WASTEWATER = "wastewater"
    SWIMMING_POOL = "swimming_pool"


class PumpType(str, Enum):
    """Types of water pumps."""
    SUBMERSIBLE = "submersible"
    CENTRIFUGAL = "centrifugal"
    BOREHOLE = "borehole"
    SURFACE = "surface"
    BOOSTER = "booster"
    SOLAR = "solar"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseSchema):
    """Base user schema."""
    name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    role: UserRole
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserInDB(UserResponse):
    """Schema for user in database (includes password hash)."""
    password: str


# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================

class CustomerBase(BaseSchema):
    """Base customer schema."""
    customer_no: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="Kenya", max_length=100)
    customer_type: CustomerType
    credit_limit: Optional[Decimal] = Field(None, decimal_places=2)
    payment_terms: Optional[str] = Field(None, max_length=100)


class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    bc_customer_id: Optional[str] = Field(None, max_length=100)
    sales_representative_id: Optional[UUID] = None


class CustomerUpdate(BaseSchema):
    """Schema for updating a customer."""
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: UUID
    bc_customer_id: Optional[str] = None
    sales_representative_id: Optional[UUID] = None
    is_active: bool = True
    created_at: datetime


class CustomerBrief(BaseSchema):
    """Brief customer info for nested responses."""
    id: UUID
    customer_no: str
    name: str
    customer_type: CustomerType


# ============================================================================
# INQUIRY SCHEMAS
# ============================================================================

class InquiryBase(BaseSchema):
    """Base inquiry schema."""
    inquiry_type: InquiryType
    title: str = Field(..., max_length=255)
    site_location: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM


class InquiryCreate(InquiryBase):
    """Schema for creating an inquiry."""
    customer_id: UUID
    assigned_to: Optional[UUID] = None


class InquiryUpdate(BaseSchema):
    """Schema for updating an inquiry."""
    title: Optional[str] = None
    site_location: Optional[str] = None
    inquiry_status: Optional[InquiryStatus] = None
    priority: Optional[PriorityLevel] = None
    assigned_to: Optional[UUID] = None


class InquiryResponse(InquiryBase):
    """Schema for inquiry response."""
    id: UUID
    inquiry_number: str
    customer_id: UUID
    inquiry_status: InquiryStatus = InquiryStatus.NEW
    assigned_to: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    customer: Optional[CustomerBrief] = None


# ============================================================================
# WATER QUALITY / LAB REPORT SCHEMAS
# ============================================================================

class WaterQualityParameterBase(BaseSchema):
    """Base water quality parameter schema."""
    parameter_name: str = Field(..., max_length=100)
    value: str = Field(..., max_length=50)
    units: Optional[str] = Field(None, max_length=50)
    who_guideline: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = Field(None, max_length=10)  # PASS, FAIL


class WaterQualityParameterCreate(WaterQualityParameterBase):
    """Schema for creating a water quality parameter."""
    pass


class WaterQualityParameterResponse(WaterQualityParameterBase):
    """Schema for water quality parameter response."""
    id: UUID
    lab_report_id: UUID


class LabReportBase(BaseSchema):
    """Base lab report schema."""
    client_name: str = Field(..., max_length=255)
    sampling_date: date
    water_source: str = Field(..., max_length=255)
    site_location: Optional[str] = None


class LabReportCreate(LabReportBase):
    """Schema for creating a lab report."""
    inquiry_id: Optional[UUID] = None
    customer_id: UUID
    parameters: List[WaterQualityParameterCreate] = Field(default_factory=list)


class LabReportUpdate(BaseSchema):
    """Schema for updating a lab report."""
    client_name: Optional[str] = None
    sampling_date: Optional[date] = None
    water_source: Optional[str] = None
    site_location: Optional[str] = None
    pdf_url: Optional[str] = None


class LabReportResponse(LabReportBase):
    """Schema for lab report response."""
    id: UUID
    inquiry_id: Optional[UUID] = None
    customer_id: UUID
    reference_no: str
    pdf_url: Optional[str] = None
    created_at: datetime
    parameters: List[WaterQualityParameterResponse] = Field(default_factory=list)


# ============================================================================
# ASSESSMENT SCHEMAS
# ============================================================================

class SolarAssessmentBase(BaseSchema):
    """Base solar assessment schema."""
    water_source_type: str = Field(..., max_length=50)
    static_water_level: Optional[Decimal] = None
    well_depth: Optional[Decimal] = None
    daily_water_requirement: Decimal
    peak_sun_hours: Optional[Decimal] = None
    delivery_distance: Optional[Decimal] = None
    storage_capacity: Optional[Decimal] = None


class SolarAssessmentCreate(SolarAssessmentBase):
    """Schema for creating a solar assessment."""
    inquiry_id: UUID


class SolarAssessmentResponse(SolarAssessmentBase):
    """Schema for solar assessment response."""
    id: UUID
    inquiry_id: UUID
    created_at: datetime


class SiteAssessmentBase(BaseSchema):
    """Base site assessment schema."""
    water_source: Optional[str] = Field(None, max_length=100)
    depth_to_water: Optional[Decimal] = None
    power_source: Optional[str] = Field(None, max_length=50)
    soil_type: Optional[str] = Field(None, max_length=50)
    special_requirements: Optional[str] = None


class SiteAssessmentCreate(SiteAssessmentBase):
    """Schema for creating a site assessment."""
    inquiry_id: UUID


class SiteAssessmentResponse(SiteAssessmentBase):
    """Schema for site assessment response."""
    id: UUID
    inquiry_id: UUID
    created_at: datetime


# ============================================================================
# SYSTEM DESIGN SCHEMAS
# ============================================================================

class AIRecommendation(BaseSchema):
    """AI-generated recommendation."""
    pump_model: Optional[str] = None
    pump_sku: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    alternatives: List[str] = Field(default_factory=list)


class SystemDesignBase(BaseSchema):
    """Base system design schema."""
    total_dynamic_head: Optional[Decimal] = None
    required_flow_rate: Optional[Decimal] = None
    motor_input_power_kw: Optional[Decimal] = None
    ai_confidence_score: Optional[Decimal] = Field(None, ge=0, le=100)
    ai_recommendations: Optional[Dict[str, Any]] = None


class SystemDesignCreate(SystemDesignBase):
    """Schema for creating a system design."""
    inquiry_id: UUID


class SystemDesignUpdate(BaseSchema):
    """Schema for updating a system design."""
    design_status: Optional[DesignStatus] = None
    total_dynamic_head: Optional[Decimal] = None
    required_flow_rate: Optional[Decimal] = None
    motor_input_power_kw: Optional[Decimal] = None
    ai_confidence_score: Optional[Decimal] = None
    ai_recommendations: Optional[Dict[str, Any]] = None


class SystemDesignResponse(SystemDesignBase):
    """Schema for system design response."""
    id: UUID
    design_number: str
    inquiry_id: UUID
    design_status: DesignStatus = DesignStatus.DRAFT
    created_by: UUID
    created_at: datetime


# ============================================================================
# EQUIPMENT SCHEMAS
# ============================================================================

class EquipmentBase(BaseSchema):
    """Base equipment schema."""
    name: str = Field(..., max_length=255)
    category: EquipmentCategory
    model_name: str = Field(..., max_length=255)
    manufacturer: str = Field(..., max_length=255)
    sku: str = Field(..., max_length=100)
    unit_price: Decimal = Field(..., decimal_places=2)
    specifications: Optional[Dict[str, Any]] = None


class EquipmentCreate(EquipmentBase):
    """Schema for creating equipment."""
    bc_item_no: Optional[str] = Field(None, max_length=100)
    quantity_available: int = 0


class EquipmentUpdate(BaseSchema):
    """Schema for updating equipment."""
    name: Optional[str] = None
    unit_price: Optional[Decimal] = None
    specifications: Optional[Dict[str, Any]] = None
    quantity_available: Optional[int] = None
    is_active: Optional[bool] = None


class EquipmentResponse(EquipmentBase):
    """Schema for equipment response."""
    id: UUID
    bc_item_no: Optional[str] = None
    quantity_available: int = 0
    is_active: bool = True
    created_at: datetime


class EquipmentBrief(BaseSchema):
    """Brief equipment info for nested responses."""
    id: UUID
    name: str
    sku: str
    category: EquipmentCategory
    unit_price: Decimal


# ============================================================================
# PUMP SCHEMAS
# ============================================================================

class PumpSpecsBase(BaseSchema):
    """Base pump specifications schema."""
    motor_power_kw: Decimal = Field(..., decimal_places=2)
    max_flow_rate: Decimal = Field(..., decimal_places=2)
    max_head: Decimal = Field(..., decimal_places=2)
    voltage_ac: Optional[int] = None
    phase_type: Optional[str] = Field(None, max_length=20)
    performance_curve_data: Optional[Dict[str, Any]] = None


class PumpCreate(PumpSpecsBase):
    """Schema for creating pump specs (linked to equipment)."""
    equipment_id: UUID


class PumpResponse(PumpSpecsBase):
    """Schema for pump specs response."""
    equipment_id: UUID
    equipment: Optional[EquipmentResponse] = None


class PumpCurveCoefficients(BaseSchema):
    """Polynomial coefficients for pump curves."""
    # H = A*Q² + B*Q + C
    hq_coef_a: float = Field(..., description="Quadratic coefficient for H-Q")
    hq_coef_b: float = Field(..., description="Linear coefficient for H-Q")
    hq_coef_c: float = Field(..., description="Constant (shutoff head)")

    # Efficiency curve (optional)
    eff_coef_a: Optional[float] = None
    eff_coef_b: Optional[float] = None
    eff_coef_c: Optional[float] = None

    # Power curve (optional)
    power_coef_a: Optional[float] = None
    power_coef_b: Optional[float] = None
    power_coef_c: Optional[float] = None


class PumpCurveCreate(PumpCurveCoefficients):
    """Schema for creating pump curve data."""
    equipment_id: UUID
    min_flow: float
    max_flow: float
    impeller_diameter_mm: Optional[float] = None
    speed_rpm: int = 2900
    raw_curve_points: Optional[List[Dict[str, float]]] = None


class PumpCurveResponse(PumpCurveCoefficients):
    """Schema for pump curve response."""
    id: UUID
    equipment_id: UUID
    min_flow: float
    max_flow: float
    impeller_diameter_mm: Optional[float] = None
    speed_rpm: int
    hq_r_squared: Optional[float] = None
    eff_r_squared: Optional[float] = None
    power_r_squared: Optional[float] = None
    created_at: datetime


# ============================================================================
# SOLAR PANEL SCHEMAS
# ============================================================================

class SolarPanelSpecsBase(BaseSchema):
    """Base solar panel specifications schema."""
    rated_power_wp: int
    voc: Decimal = Field(..., decimal_places=2)
    vmp: Decimal = Field(..., decimal_places=2)
    efficiency: Optional[Decimal] = Field(None, decimal_places=2)
    cell_type: Optional[str] = Field(None, max_length=50)


class SolarPanelCreate(SolarPanelSpecsBase):
    """Schema for creating solar panel specs."""
    equipment_id: UUID


class SolarPanelResponse(SolarPanelSpecsBase):
    """Schema for solar panel specs response."""
    equipment_id: UUID
    equipment: Optional[EquipmentResponse] = None


# ============================================================================
# QUOTATION SCHEMAS
# ============================================================================

class QuotationLineItemBase(BaseSchema):
    """Base quotation line item schema."""
    item_category: ItemCategory
    description: str
    quantity: Decimal = Field(..., decimal_places=2)
    unit_price: Decimal = Field(..., decimal_places=2)
    sort_order: int = 0


class QuotationLineItemCreate(QuotationLineItemBase):
    """Schema for creating a quotation line item."""
    equipment_id: Optional[UUID] = None


class QuotationLineItemResponse(QuotationLineItemBase):
    """Schema for quotation line item response."""
    id: UUID
    quotation_id: UUID
    equipment_id: Optional[UUID] = None
    line_total: Decimal
    created_at: datetime
    equipment: Optional[EquipmentBrief] = None


class QuotationBase(BaseSchema):
    """Base quotation schema."""
    quotation_title: str = Field(..., max_length=255)
    currency: str = Field(default="KES", max_length=10)
    quotation_date: date
    valid_until_date: date


class QuotationCreate(QuotationBase):
    """Schema for creating a quotation."""
    inquiry_id: UUID
    customer_id: UUID
    system_design_id: Optional[UUID] = None
    line_items: List[QuotationLineItemCreate] = Field(default_factory=list)


class QuotationUpdate(BaseSchema):
    """Schema for updating a quotation."""
    quotation_title: Optional[str] = None
    status: Optional[QuotationStatus] = None
    valid_until_date: Optional[date] = None


class QuotationResponse(QuotationBase):
    """Schema for quotation response."""
    id: UUID
    quotation_number: str
    inquiry_id: UUID
    customer_id: UUID
    system_design_id: Optional[UUID] = None
    status: QuotationStatus = QuotationStatus.DRAFT
    subtotal: Decimal
    total_amount: Decimal
    created_by: UUID
    created_at: datetime
    line_items: List[QuotationLineItemResponse] = Field(default_factory=list)
    customer: Optional[CustomerBrief] = None


class QuotationSummary(BaseSchema):
    """Summary quotation info for lists."""
    id: UUID
    quotation_number: str
    quotation_title: str
    customer_name: str
    status: QuotationStatus
    total_amount: Decimal
    currency: str
    quotation_date: date
    valid_until_date: date


# ============================================================================
# iDAYLIFF IoT SCHEMAS
# ============================================================================

class IDayliffInstallationBase(BaseSchema):
    """Base iDayliff installation schema."""
    pump_model: str = Field(..., max_length=255)
    site_name: str = Field(..., max_length=255)
    installation_date: date
    warranty_expiry: Optional[date] = None


class IDayliffInstallationCreate(IDayliffInstallationBase):
    """Schema for creating an iDayliff installation."""
    customer_id: UUID
    equipment_id: Optional[UUID] = None


class IDayliffInstallationUpdate(BaseSchema):
    """Schema for updating an iDayliff installation."""
    site_name: Optional[str] = None
    status: Optional[InstallationStatus] = None
    warranty_expiry: Optional[date] = None
    health_score: Optional[int] = Field(None, ge=0, le=100)
    total_running_hours: Optional[int] = None


class IDayliffInstallationResponse(IDayliffInstallationBase):
    """Schema for iDayliff installation response."""
    id: UUID
    installation_no: str
    customer_id: UUID
    equipment_id: Optional[UUID] = None
    status: InstallationStatus = InstallationStatus.PENDING
    health_score: Optional[int] = None
    total_running_hours: int = 0
    customer: Optional[CustomerBrief] = None


class IDayliffTelemetryBase(BaseSchema):
    """Base telemetry data schema."""
    timestamp: datetime
    flow_rate: Optional[Decimal] = None
    pressure: Optional[Decimal] = None
    power_consumption: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    vibration: Optional[Decimal] = None


class IDayliffTelemetryCreate(IDayliffTelemetryBase):
    """Schema for creating telemetry data."""
    installation_id: UUID


class IDayliffTelemetryResponse(IDayliffTelemetryBase):
    """Schema for telemetry data response."""
    id: UUID
    installation_id: UUID
    created_at: datetime


class IDayliffAlarmBase(BaseSchema):
    """Base alarm schema."""
    timestamp: datetime
    severity: str = Field(..., max_length=20)  # info, warning, critical
    alarm_type: str = Field(..., max_length=50)
    message: str


class IDayliffAlarmCreate(IDayliffAlarmBase):
    """Schema for creating an alarm."""
    installation_id: UUID


class IDayliffAlarmUpdate(BaseSchema):
    """Schema for updating an alarm."""
    resolved: bool = True
    resolved_at: Optional[datetime] = None


class IDayliffAlarmResponse(IDayliffAlarmBase):
    """Schema for alarm response."""
    id: UUID
    installation_id: UUID
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: datetime


# ============================================================================
# HYDRAULIC CALCULATION SCHEMAS
# ============================================================================

class PipeSpecification(BaseSchema):
    """Pipe specification for hydraulic calculations."""
    material: str = Field(default="HDPE", description="Pipe material")
    diameter_mm: float = Field(..., gt=0, description="Internal diameter in mm")
    length_m: float = Field(..., gt=0, description="Total pipe length in meters")
    roughness_coefficient: float = Field(default=150, description="Hazen-Williams C factor")


class HydraulicInput(BaseSchema):
    """Input parameters for hydraulic calculations."""
    water_source: WaterSourceType
    static_water_level_m: float = Field(..., ge=0)
    dynamic_water_level_m: Optional[float] = Field(None, ge=0)
    delivery_head_m: float = Field(..., ge=0)
    required_pressure_bar: float = Field(default=0, ge=0)
    required_flow_m3_h: float = Field(..., gt=0)
    daily_demand_liters: Optional[float] = Field(None, gt=0)
    operating_hours: float = Field(default=8, gt=0, le=24)
    pipe: PipeSpecification
    num_elbows_90: int = Field(default=0, ge=0)
    num_elbows_45: int = Field(default=0, ge=0)
    num_tees: int = Field(default=0, ge=0)
    num_valves: int = Field(default=0, ge=0)
    num_check_valves: int = Field(default=0, ge=0)


class HydraulicResult(BaseSchema):
    """Results from hydraulic calculations."""
    static_head_m: float
    friction_loss_m: float
    minor_losses_m: float
    pressure_head_m: float
    total_dynamic_head_m: float
    flow_rate_m3_h: float
    flow_rate_l_s: float
    recommended_power_kw: float
    hydraulic_efficiency: float
    safety_factor: float = 1.15
    calculation_notes: List[str] = Field(default_factory=list)


# ============================================================================
# PUMP RECOMMENDATION SCHEMAS
# ============================================================================

class PumpOperatingPoint(BaseSchema):
    """Operating point on pump curve."""
    flow_m3_h: float
    head_m: float
    efficiency_percent: Optional[float] = None
    power_kw: Optional[float] = None


class PumpMatch(BaseSchema):
    """Matched pump result."""
    equipment_id: UUID
    sku: str
    model: str
    manufacturer: str
    motor_power_kw: float
    operating_point: PumpOperatingPoint
    bep_proximity_percent: float = Field(..., ge=0, le=100)
    match_score: float = Field(..., ge=0, le=100)
    is_recommended: bool = False
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    unit_price: Decimal


# ============================================================================
# SOLAR SYSTEM DESIGN SCHEMAS
# ============================================================================

class SolarResourceData(BaseSchema):
    """Solar resource data for a location."""
    latitude: float
    longitude: float
    city_name: Optional[str] = None
    annual_avg_psh: float
    worst_month_psh: float
    best_month_psh: float
    monthly_psh: Dict[str, float] = Field(default_factory=dict)
    optimal_tilt_angle: float
    data_source: str = "calculated"


class SolarArrayDesign(BaseSchema):
    """Solar array sizing result."""
    total_power_kwp: float
    panel_wattage: int
    num_panels: int
    array_configuration: str
    estimated_daily_output_kwh: float
    system_efficiency: float = 0.85
    oversizing_factor: float = 1.25


class SolarSystemROI(BaseSchema):
    """Solar system ROI calculation."""
    system_cost: Decimal
    annual_savings: Decimal
    payback_period_years: float
    npv_10_years: Optional[Decimal] = None
    irr_percent: Optional[float] = None


# ============================================================================
# API REQUEST/RESPONSE SCHEMAS
# ============================================================================

class PumpSizingRequest(BaseSchema):
    """Request for pump sizing."""
    inquiry_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    hydraulic_input: HydraulicInput
    include_solar_option: bool = False
    budget_limit: Optional[Decimal] = None
    preferred_brands: List[str] = Field(default_factory=list)


class PumpSizingResponse(BaseSchema):
    """Response from pump sizing."""
    request_id: str
    hydraulic_analysis: HydraulicResult
    recommendations: List[PumpMatch]
    solar_design: Optional[SolarArrayDesign] = None
    ai_explanation: str
    processing_time_seconds: float


class QuoteGenerationRequest(BaseSchema):
    """Request to generate a quotation."""
    inquiry_id: UUID
    customer_id: UUID
    project_name: str
    pump_sizing_response: Optional[PumpSizingResponse] = None
    additional_items: List[QuotationLineItemCreate] = Field(default_factory=list)
    apply_customer_discount: bool = True
    include_installation: bool = True
    include_commissioning: bool = True
    valid_days: int = Field(default=30, ge=7, le=90)


class QuoteGenerationResponse(BaseSchema):
    """Response with generated quotation."""
    quotation: QuotationResponse
    document_url: Optional[str] = None
    processing_time_seconds: float


# ============================================================================
# AGENT COMMUNICATION SCHEMAS
# ============================================================================

class AgentTask(BaseSchema):
    """Task for an AI agent."""
    task_id: str
    agent_name: str
    task_type: str
    input_data: Dict[str, Any]
    priority: int = 1
    timeout_seconds: int = 300


class AgentResult(BaseSchema):
    """Result from an AI agent."""
    task_id: str
    agent_name: str
    success: bool
    output_data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_seconds: float
    tokens_used: Optional[int] = None


class WorkflowState(BaseSchema):
    """State of a multi-agent workflow."""
    workflow_id: str
    workflow_type: str
    current_stage: str
    completed_stages: List[str] = Field(default_factory=list)
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)
    final_output: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "in_progress"


# ============================================================================
# BUSINESS CENTRAL INTEGRATION SCHEMAS
# ============================================================================

class BCCustomerSync(BaseSchema):
    """Schema for syncing customer from Business Central."""
    bc_customer_id: str
    customer_no: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: str = "Kenya"
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None


class BCItemSync(BaseSchema):
    """Schema for syncing item/equipment from Business Central."""
    bc_item_no: str
    description: str
    unit_price: Decimal
    inventory: int
    blocked: bool = False


class BCPriceResponse(BaseSchema):
    """Price response from Business Central."""
    bc_item_no: str
    unit_price: Decimal
    currency: str = "KES"
    discount_percent: Optional[Decimal] = None
    price_valid_from: Optional[date] = None
    price_valid_to: Optional[date] = None
