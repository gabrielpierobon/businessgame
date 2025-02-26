"""
Pydantic models for the Business Game.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CompanyState(BaseModel):
    """
    Represents the financial and operational state of the company.
    """
    cash: float = Field(..., description="Available cash in millions")
    assets: float = Field(..., description="Total assets value in millions")
    inventory: float = Field(..., description="Current inventory in units")
    capacity: float = Field(..., description="Production capacity in units per quarter")
    
    # Financial metrics
    revenue: float = Field(0.0, description="Revenue from last quarter in millions")
    costs: float = Field(0.0, description="Costs from last quarter in millions")
    profit: float = Field(0.0, description="Profit from last quarter in millions")
    
    # Historical data
    historical_revenue: List[float] = Field(default_factory=list, description="Historical revenue data")
    historical_profit: List[float] = Field(default_factory=list, description="Historical profit data")
    historical_stock_price: List[float] = Field(default_factory=list, description="Historical stock price data")


class MarketState(BaseModel):
    """
    Represents the current market conditions.
    """
    market_size: float = Field(..., description="Total market size in units")
    market_growth: float = Field(..., description="Market growth rate as decimal")
    competitor_price: float = Field(..., description="Competitor's current price")
    competitor_market_share: float = Field(..., description="Competitor's market share as decimal")
    player_market_share: float = Field(..., description="Player's market share as decimal")
    
    # Market elasticity parameters
    price_elasticity: float = Field(..., description="Price elasticity of demand")


class ExternalState(BaseModel):
    """
    Represents external economic factors and regulations.
    """
    interest_rate: float = Field(..., description="Current interest rate as decimal")
    inflation_rate: float = Field(..., description="Current inflation rate as decimal")
    tax_rate: float = Field(..., description="Corporate tax rate as decimal")
    regulatory_burden: float = Field(..., description="Regulatory cost factor as decimal")


class GameMetadata(BaseModel):
    """
    Metadata about the game state.
    """
    game_id: str = Field(..., description="Unique identifier for the game")
    current_quarter: int = Field(..., description="Current quarter number")
    created_at: datetime = Field(default_factory=datetime.now, description="Game creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


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


class PlayerAction(BaseModel):
    """
    Represents all player decisions for a quarter.
    """
    pricing_decision: PricingDecision
    production_decision: ProductionDecision


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
    
    # Optional custom name for the game
    game_name: Optional[str] = Field(None, description="Custom name for the game")
    
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
                "game_name": "My Business Simulation"
            }
        } 