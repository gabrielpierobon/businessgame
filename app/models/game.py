"""
Pydantic models for the Business Game.
"""
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
import uuid


class Employee(BaseModel):
    """
    Represents an employee in the company.
    """
    id: str = Field(..., description="Employee ID")
    department: str = Field(..., description="Department (production, rd, marketing, supply_chain)")
    level: int = Field(1, description="Employee level (1-5)")
    salary: float = Field(..., description="Annual salary in thousands")
    productivity: float = Field(1.0, description="Productivity multiplier")
    satisfaction: float = Field(1.0, description="Satisfaction level")
    experience: int = Field(0, description="Quarters of experience")
    skills: Dict[str, float] = Field(default_factory=dict, description="Skill levels by area")
    training_history: List[Dict] = Field(default_factory=list, description="Training history")


class RegionalOperation(BaseModel):
    """
    Represents company operations in a specific region.
    """
    market_share: float = Field(0.0, description="Market share in the region")
    sales_volume: float = Field(0.0, description="Sales volume in units")
    revenue: float = Field(0.0, description="Revenue in local currency")
    costs: float = Field(0.0, description="Costs in local currency")
    inventory: float = Field(0.0, description="Local inventory in units")
    capacity: float = Field(0.0, description="Local production capacity")
    brand_strength: float = Field(0.0, description="Brand strength in region")
    distribution_network: float = Field(0.0, description="Distribution network strength")
    local_partnerships: List[Dict] = Field(default_factory=list, description="Local business partnerships")
    entry_mode: str = Field("none", description="Market entry mode (export, partnership, subsidiary)")
    entry_date: Optional[datetime] = Field(None, description="Date of market entry")
    investment_level: float = Field(0.0, description="Cumulative investment in millions USD")


class Region(BaseModel):
    """Model for international regions."""
    name: str = Field(..., description="Region name")
    market_size: float = Field(..., description="Regional market size in units")
    market_growth: float = Field(..., description="Regional market growth rate")
    currency: str = Field(..., description="Local currency code")
    exchange_rate: float = Field(..., description="Exchange rate to base currency")
    tariff_rate: float = Field(0.0, description="Import tariff rate")
    regulatory_rating: float = Field(1.0, description="Regulatory complexity (1.0 = standard)")
    cultural_distance: float = Field(1.0, description="Cultural distance from home market")
    competitor_presence: List[Dict] = Field(default_factory=list, description="Regional competitor details")
    
    # Regional preferences
    price_sensitivity: float = Field(1.0, description="Regional price sensitivity")
    quality_sensitivity: float = Field(1.0, description="Regional quality sensitivity")
    brand_sensitivity: float = Field(1.0, description="Regional brand sensitivity")
    
    # Supply chain characteristics
    logistics_cost: float = Field(1.0, description="Regional logistics cost multiplier")
    supplier_quality: float = Field(1.0, description="Regional supplier quality rating")
    labor_cost: float = Field(1.0, description="Regional labor cost multiplier")


class CompanyState(BaseModel):
    """
    Represents the current state of the player's company.
    """
    cash: float = Field(..., description="Available cash in millions")
    assets: float = Field(..., description="Total assets in millions")
    total_debt: float = Field(0.0, description="Total debt in millions")
    inventory: float = Field(..., description="Current inventory in units")
    capacity: float = Field(..., description="Production capacity in units")
    revenue: float = Field(..., description="Current revenue in millions")
    costs: float = Field(..., description="Current costs in millions")
    profit: float = Field(..., description="Current profit in millions")
    stock_price: float = Field(100.0, description="Current stock price")
    
    # R&D and Quality metrics
    r_and_d_level: float = Field(1.0, description="R&D level multiplier")
    product_quality: float = Field(1.0, description="Product quality rating")
    brand_strength: float = Field(1.0, description="Brand strength rating")
    supply_chain_efficiency: float = Field(1.0, description="Supply chain efficiency rating")
    marketing_effectiveness: float = Field(1.0, description="Marketing effectiveness rating")
    
    # Supply chain metrics
    supplier_lead_time: float = Field(1.0, description="Average supplier lead time in quarters")
    supplier_quality_rating: float = Field(1.0, description="Supplier quality rating")
    supply_chain_reliability: float = Field(1.0, description="Supply chain reliability score")
    inventory_turnover: float = Field(4.0, description="Inventory turnover rate per year")
    supplier_relationship: float = Field(1.0, description="Supplier relationship strength multiplier")
    supplier_count: int = Field(1, description="Number of active suppliers")
    supplier_diversity: float = Field(1.0, description="Supplier diversity score")
    active_disruptions: List[Dict[str, Any]] = Field(default_factory=list, description="Active supply chain disruptions")
    
    # Historical data
    historical_revenue: List[float] = Field(default_factory=list, description="Historical revenue")
    historical_profit: List[float] = Field(default_factory=list, description="Historical profit")
    historical_stock_price: List[float] = Field(default_factory=list, description="Historical stock prices")
    historical_product_quality: List[float] = Field(default_factory=list, description="Historical product quality")
    historical_supply_chain_efficiency: List[float] = Field(default_factory=list, description="Historical supply chain efficiency")
    historical_regional_revenue: Dict[str, List[float]] = Field(default_factory=dict, description="Historical revenue by region")
    historical_regional_market_share: Dict[str, List[float]] = Field(default_factory=dict, description="Historical market share by region")
    historical_exchange_rates: Dict[str, List[float]] = Field(default_factory=dict, description="Historical exchange rates by currency")
    
    # Regional operations
    regional_operations: Dict[str, RegionalOperation] = Field(default_factory=dict, description="Operations by region")
    
    # Employees
    employees: Dict[str, List[Employee]] = Field(default_factory=dict, description="Employees by department")
    
    # Pending changes
    pending_expansions: List[Dict[str, Any]] = Field(default_factory=list, description="Pending capacity expansions")
    loans: List[Dict[str, Any]] = Field(default_factory=list, description="Active loans")
    investments: List[Dict[str, Any]] = Field(default_factory=list, description="Active investments")
    dividend_history: List[Dict[str, Any]] = Field(default_factory=list, description="Dividend payment history")


class MarketSegment(BaseModel):
    """Model for market segments."""
    name: str = Field(..., description="Segment name")
    size: float = Field(..., description="Segment size as proportion of total market")
    growth_rate: float = Field(..., description="Segment-specific growth rate")
    
    # Segment preferences
    price_sensitivity: float = Field(1.0, description="Price sensitivity multiplier")
    quality_sensitivity: float = Field(1.0, description="Quality sensitivity multiplier")
    brand_sensitivity: float = Field(1.0, description="Brand sensitivity multiplier")
    innovation_sensitivity: float = Field(1.0, description="Innovation sensitivity multiplier")
    
    # Segment characteristics
    purchasing_power: float = Field(1.0, description="Relative purchasing power")
    loyalty_factor: float = Field(1.0, description="Customer loyalty strength")
    adoption_rate: float = Field(1.0, description="New product adoption rate")
    
    # Segment trends
    seasonal_factors: Dict[str, float] = Field(
        default_factory=lambda: {str(i): 1.0 for i in range(1, 5)},
        description="Quarterly seasonal factors"
    )
    trend_direction: float = Field(0.0, description="Current trend direction (-1.0 to 1.0)")
    trend_strength: float = Field(1.0, description="Strength of current trend")


class Competitor(BaseModel):
    """Model for individual competitors."""
    name: str = Field(..., description="Competitor name")
    market_share: float = Field(..., description="Current market share")
    price: float = Field(..., description="Current price")
    product_quality: float = Field(1.0, description="Product quality level")
    brand_strength: float = Field(1.0, description="Brand strength")
    
    # Strategy indicators
    price_strategy: str = Field("balanced", description="Price strategy (aggressive, balanced, premium)")
    quality_strategy: str = Field("balanced", description="Quality strategy (low_cost, balanced, premium)")
    innovation_strategy: str = Field("balanced", description="Innovation strategy (follower, balanced, leader)")
    
    # Segment focus
    segment_focus: Dict[str, float] = Field(
        default_factory=dict,
        description="Focus allocation across segments"
    )
    
    # Resources and capabilities
    r_and_d_capability: float = Field(1.0, description="R&D capability level")
    marketing_effectiveness: float = Field(1.0, description="Marketing effectiveness")
    production_efficiency: float = Field(1.0, description="Production efficiency")
    financial_strength: float = Field(1.0, description="Financial strength indicator")
    
    # Historical data
    historical_prices: List[float] = Field(default_factory=list)
    historical_market_share: List[float] = Field(default_factory=list)
    historical_quality: List[float] = Field(default_factory=list)


class MarketTrend(BaseModel):
    """Model for market trends."""
    name: str = Field(..., description="Trend name")
    strength: float = Field(..., description="Trend strength (0.0 to 1.0)")
    duration: int = Field(..., description="Expected duration in quarters")
    quarters_active: int = Field(0, description="Quarters trend has been active")
    
    # Impact factors
    segment_impact: Dict[str, float] = Field(
        default_factory=dict,
        description="Impact on different segments"
    )
    preference_shifts: Dict[str, float] = Field(
        default_factory=dict,
        description="Shifts in consumer preferences"
    )
    growth_impact: float = Field(0.0, description="Impact on market growth")


class MarketState(BaseModel):
    """
    Represents the current market state.
    """
    market_size: float = Field(..., description="Total market size in units")
    market_growth: float = Field(0.02, description="Market growth rate")
    player_market_share: float = Field(..., description="Player's market share")
    competitor_market_share: float = Field(..., description="Competitors' combined market share")
    competitor_price: float = Field(..., description="Average competitor price")
    competitor_quality: float = Field(1.0, description="Average competitor product quality")
    competitor_brand: float = Field(1.0, description="Average competitor brand strength")
    competitor_efficiency: float = Field(1.0, description="Average competitor operational efficiency")
    competitor_innovation: float = Field(1.0, description="Average competitor innovation level")
    competitor_supply_chain: float = Field(1.0, description="Average competitor supply chain efficiency")
    competitor_marketing: float = Field(1.0, description="Average competitor marketing effectiveness")
    competitor_r_and_d: float = Field(1.0, description="Average competitor R&D level")
    price_elasticity: float = Field(..., description="Price elasticity of demand")
    quality_elasticity: float = Field(1.0, description="Quality elasticity of demand")
    marketing_elasticity: float = Field(1.0, description="Marketing elasticity of demand")
    consumer_sentiment: float = Field(1.0, description="Consumer sentiment index (1.0 = neutral)")
    
    # Market dynamics
    market_concentration: float = Field(0.0, description="Market concentration (HHI)")
    market_maturity: float = Field(0.5, description="Market maturity level (0-1)")
    entry_barriers: float = Field(1.0, description="Market entry barriers level")
    industry_profitability: float = Field(0.1, description="Industry average profitability")
    
    # Market segments
    segments: Dict[str, MarketSegment] = Field(default_factory=dict, description="Market segments")
    segment_growth_rates: Dict[str, float] = Field(default_factory=dict, description="Growth rates by segment")
    segment_profitability: Dict[str, float] = Field(default_factory=dict, description="Profitability by segment")
    historical_segment_sizes: Dict[str, List[float]] = Field(default_factory=dict, description="Historical segment sizes")
    historical_segment_growth: Dict[str, List[float]] = Field(default_factory=dict, description="Historical segment growth rates")
    
    # International markets
    regions: Dict[str, Region] = Field(default_factory=dict, description="Available regions")
    global_demand_correlation: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Demand correlation between regions")
    trade_barriers: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Trade barriers between regions")
    
    # Competition
    competitors: Dict[str, Competitor] = Field(default_factory=dict, description="Competitor information")
    active_trends: List[MarketTrend] = Field(default_factory=list, description="Active market trends")
    
    # Historical market data
    historical_market_size: List[float] = Field(default_factory=list, description="Historical market sizes")
    historical_market_growth: List[float] = Field(default_factory=list, description="Historical market growth rates")
    historical_competitor_prices: List[float] = Field(default_factory=list, description="Historical competitor prices")
    historical_competitor_quality: List[float] = Field(default_factory=list, description="Historical competitor quality levels")
    historical_consumer_sentiment: List[float] = Field(default_factory=list, description="Historical consumer sentiment values")


class ExternalState(BaseModel):
    """
    Represents external economic factors and regulations.
    """
    interest_rate: float = Field(..., description="Current interest rate as decimal")
    inflation_rate: float = Field(..., description="Current inflation rate as decimal")
    tax_rate: float = Field(..., description="Corporate tax rate as decimal")
    regulatory_burden: float = Field(..., description="Regulatory cost factor as decimal")
    
    # Phase 4: Enhanced external factors
    economic_cycle: str = Field("neutral", description="Current economic cycle (boom, recession, neutral)")
    economic_cycle_position: float = Field(0.0, description="Position in economic cycle (-1.0 to 1.0)")
    raw_material_costs: float = Field(1.0, description="Raw material cost multiplier")
    labor_costs: float = Field(1.0, description="Labor cost multiplier")
    consumer_confidence: float = Field(1.0, description="Consumer confidence index")
    
    # Random events
    active_events: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Currently active random events affecting the game"
    )


class GameMetadata(BaseModel):
    """
    Metadata about the game state.
    """
    game_id: str = Field(..., description="Unique identifier for the game")
    current_quarter: int = Field(..., description="Current quarter number")
    created_at: datetime = Field(default_factory=datetime.now, description="Game creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    difficulty: str = Field("normal", description="Game difficulty level")
    scenario: str = Field("standard", description="Game scenario type")


class GameState(BaseModel):
    """
    Represents the entire game state.
    """
    company_state: CompanyState
    market_state: MarketState
    external_state: ExternalState
    metadata: GameMetadata
    
    # Derived values
    stock_price: float = Field(0.0, description="Current stock price")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ProductionDecision(BaseModel):
    """
    Represents the production volume decision for a quarter.
    """
    volume: float = Field(..., description="Production volume in units", ge=0)


class PricingDecision(BaseModel):
    """
    Represents the pricing decision for a quarter.
    """
    price: float = Field(..., description="Product price per unit", gt=0)


class MarketingDecision(BaseModel):
    """
    Enhanced marketing decision model.
    """
    budget: float = Field(..., description="Marketing budget in millions", ge=0)
    
    # Segment-specific allocation
    segment_allocation: Dict[str, float] = Field(
        default_factory=dict,
        description="Allocation of budget across segments"
    )
    
    # Marketing mix
    channel_mix: Dict[str, float] = Field(
        default_factory=lambda: {
            "traditional": 0.4,
            "digital": 0.4,
            "direct": 0.2
        },
        description="Marketing channel allocation"
    )
    
    # Campaign focus
    campaign_focus: str = Field(
        "balanced",
        description="Campaign focus (brand_building, sales_activation, product_launch)"
    )
    
    # Promotional activities
    promotional_activities: Dict[str, float] = Field(
        default_factory=dict,
        description="Budget allocation for promotional activities"
    )


class ProductStrategy(BaseModel):
    """Model for product strategy decisions."""
    target_segments: List[str] = Field(..., description="Target market segments")
    positioning: str = Field(
        "balanced",
        description="Product positioning (value, balanced, premium)"
    )
    feature_focus: Dict[str, float] = Field(
        default_factory=dict,
        description="Resource allocation across product features"
    )
    innovation_level: float = Field(
        1.0,
        description="Innovation level for new features (1.0 = industry average)"
    )


class RAndDDecision(BaseModel):
    """
    Represents the R&D investment decision for a quarter.
    """
    budget: float = Field(..., description="R&D budget in millions", ge=0)
    focus: str = Field("balanced", description="R&D focus area (cost_reduction, quality_improvement, innovation, balanced)")


class CapacityDecision(BaseModel):
    """
    Represents the capacity expansion decision for a quarter.
    """
    expansion: float = Field(0.0, description="Capacity expansion in units", ge=0)


class SupplyChainDecision(BaseModel):
    """
    Represents the supply chain management decision for a quarter.
    """
    investment: float = Field(0.0, description="Supply chain investment in millions", ge=0)
    supplier_quality: str = Field("standard", description="Supplier quality level (economy, standard, premium)")
    inventory_policy: str = Field("balanced", description="Inventory policy (lean, balanced, safety_stock)")
    focus: str = Field("balanced", description="Investment focus (balanced, efficiency, relationship, lead_time)")
    supply_chain_focus: str = Field("balanced", description="Supply chain focus area (balanced, efficiency, relationship, lead_time)")


class LoanRequest(BaseModel):
    """Model for loan requests."""
    amount: float = Field(..., description="Amount of loan requested in millions")
    term: int = Field(..., description="Loan term in quarters")


class Investment(BaseModel):
    """Model for investment decisions."""
    type: str = Field(..., description="Type of investment (bonds, stocks, money_market)")
    amount: float = Field(..., description="Amount to invest in millions")
    term: int = Field(..., description="Investment term in quarters")


class Dividend(BaseModel):
    """Model for dividend decisions."""
    amount: float = Field(..., description="Amount of dividend to pay in millions")


class FinancialDecision(BaseModel):
    """Model for financial decisions."""
    loan_request: Optional[LoanRequest] = None
    investment: Optional[Investment] = None
    dividend: Optional[Dividend] = None


class TrainingProgram(BaseModel):
    """Model for training programs."""
    budget: float = Field(..., description="Training budget in millions")
    focus: str = Field(..., description="Training focus (skills, productivity, satisfaction)")
    departments: List[str] = Field(..., description="Target departments for training")


class HiringDecision(BaseModel):
    """Model for hiring decisions."""
    department: str = Field(..., description="Department to hire for")
    count: int = Field(..., description="Number of employees to hire")
    skill_requirement: float = Field(1.0, description="Minimum skill level required")
    salary_budget: float = Field(..., description="Annual salary budget per employee in thousands")


class HRDecision(BaseModel):
    """Model for HR management decisions."""
    hiring: Optional[HiringDecision] = None
    training: Optional[TrainingProgram] = None
    salary_adjustments: Dict[str, float] = Field(
        default_factory=dict,
        description="Salary adjustments by department (percentage)"
    )


class MarketEntryDecision(BaseModel):
    """Model for market entry decisions."""
    region_name: str = Field(..., description="Target region name")
    entry_mode: str = Field(..., description="Entry mode (export, partnership, subsidiary)")
    initial_investment: float = Field(..., description="Initial investment in millions")
    capacity_allocation: float = Field(0.0, description="Production capacity allocation")
    marketing_budget: float = Field(0.0, description="Initial marketing budget")
    pricing_strategy: str = Field("market_based", description="Pricing strategy (market_based, premium, penetration)")
    local_partnerships: List[str] = Field(default_factory=list, description="Local partners to engage with")


class RegionalPricingDecision(BaseModel):
    """Model for regional pricing decisions."""
    region_name: str = Field(..., description="Region name")
    price: float = Field(..., description="Price in local currency")
    promotion_budget: float = Field(0.0, description="Regional promotion budget")


class RegionalSupplyDecision(BaseModel):
    """Model for regional supply decisions."""
    region_name: str = Field(..., description="Region name")
    production_volume: float = Field(0.0, description="Local production volume")
    import_volume: float = Field(0.0, description="Import volume from other regions")
    export_volume: float = Field(0.0, description="Export volume to other regions")
    supplier_development: float = Field(0.0, description="Investment in local supplier development")


class InternationalDecision(BaseModel):
    """Model for international operations decisions."""
    market_entry: Optional[MarketEntryDecision] = None
    regional_pricing: Dict[str, RegionalPricingDecision] = Field(default_factory=dict)
    regional_supply: Dict[str, RegionalSupplyDecision] = Field(default_factory=dict)
    currency_hedging: Dict[str, float] = Field(default_factory=dict, description="Currency hedging positions")


class PlayerAction(BaseModel):
    """
    Represents all player decisions for a quarter.
    """
    pricing_decision: PricingDecision
    production_decision: ProductionDecision
    marketing_decision: Optional[MarketingDecision] = None
    r_and_d_decision: Optional[RAndDDecision] = None
    capacity_decision: Optional[CapacityDecision] = None
    supply_chain_decision: Optional[SupplyChainDecision] = None
    financial_decision: Optional[FinancialDecision] = None
    hr_decision: Optional[HRDecision] = None
    international_decision: Optional[InternationalDecision] = None
    
    # Enhanced marketing and product decisions
    product_strategy: Optional[ProductStrategy] = None
    
    # Segment-specific decisions
    segment_focus: Dict[str, float] = Field(
        default_factory=dict,
        description="Resource allocation across segments"
    )
    
    # Competitive response
    competitive_response: Dict[str, str] = Field(
        default_factory=dict,
        description="Response strategy to specific competitors"
    )


class GameConfig(BaseModel):
    """
    Configuration parameters for a new game.
    """
    initial_cash: float = Field(10.0, description="Initial cash in millions")
    initial_assets: float = Field(50.0, description="Initial assets in millions")
    initial_capacity: float = Field(1000, description="Initial production capacity in units")
    initial_market_size: float = Field(10000, description="Initial market size in units")
    initial_player_market_share: float = Field(0.3, description="Initial player market share")
    initial_competitor_price: float = Field(100.0, description="Initial competitor price")
    price_elasticity: float = Field(1.5, description="Price elasticity of demand")
    
    # Phase 3-5: Enhanced configuration
    difficulty: str = Field("normal", description="Game difficulty (easy, normal, hard)")
    market_segments_enabled: bool = Field(False, description="Enable multiple market segments")
    random_events_enabled: bool = Field(False, description="Enable random events")
    economic_cycles_enabled: bool = Field(False, description="Enable economic cycles")
    advanced_competitors_enabled: bool = Field(False, description="Enable advanced AI competitors")
    
    # Optional custom name for the game
    game_name: Optional[str] = Field(None, description="Custom name for the game")
    
    # International configuration
    international_enabled: bool = Field(False, description="Enable international operations")
    starting_regions: List[str] = Field(default_factory=list, description="Initially available regions")
    currency_volatility: float = Field(0.1, description="Base currency volatility")
    trade_complexity: float = Field(1.0, description="Complexity of international trade")
    
    class Config:
        schema_extra = {
            "example": {
                "initial_cash": 10.0,
                "initial_assets": 50.0,
                "initial_capacity": 1000,
                "initial_market_size": 10000,
                "initial_player_market_share": 0.3,
                "initial_competitor_price": 100.0,
                "price_elasticity": 1.5,
                "difficulty": "normal",
                "market_segments_enabled": False,
                "random_events_enabled": False,
                "economic_cycles_enabled": False,
                "advanced_competitors_enabled": False,
                "game_name": "My Business Simulation",
                "international_enabled": False,
                "starting_regions": [],
                "currency_volatility": 0.1,
                "trade_complexity": 1.0
            }
        } 