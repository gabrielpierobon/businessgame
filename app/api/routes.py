"""
API routes for the Business Game.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import math

from app.models.game import (
    GameState, PlayerAction, GameConfig, 
    PricingDecision, ProductionDecision, MarketingDecision, 
    RAndDDecision, CapacityDecision, SupplyChainDecision,
    FinancialDecision, LoanRequest, Investment, Dividend,
    HiringDecision, TrainingProgram, HRDecision,
    MarketEntryDecision, RegionalPricingDecision,
    RegionalSupplyDecision, InternationalDecision
)
from app.core.simulation import GameSimulation
from app.db.repository import GameRepository

# Create router
router = APIRouter()


@router.post("/games", response_model=GameState, status_code=201)
async def create_game(config: GameConfig):
    """
    Create a new game with the given configuration.
    """
    # Initialize game state
    game_state = GameSimulation.initialize_game(config)
    
    # Save to database
    await GameRepository.create_game(game_state)
    
    return game_state


@router.get("/games/{game_id}", response_model=GameState)
async def get_game(game_id: str):
    """
    Get the current state of a game.
    """
    # Retrieve game from database
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    return game_state


@router.post("/games/{game_id}/actions", response_model=GameState)
async def submit_action(
    game_id: str,
    action: PlayerAction
):
    """
    Submit player actions for a quarter and advance the game state.
    """
    # Retrieve current game state
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    # Validate inputs
    price = action.pricing_decision.price
    production_volume = action.production_decision.volume
    
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    if production_volume < 0:
        raise HTTPException(status_code=400, detail="Production volume cannot be negative")
    if production_volume > game_state.company_state.capacity:
        raise HTTPException(
            status_code=400, 
            detail=f"Production volume exceeds capacity of {game_state.company_state.capacity}"
        )
    
    # Process action and get updated state
    updated_state = GameSimulation.process_player_action(game_state, action)
    
    # Save updated state
    await GameRepository.update_game(updated_state)
    
    return updated_state


@router.get("/games/{game_id}/history")
async def get_game_history(game_id: str):
    """
    Get the history of a game's states and actions.
    """
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    # Calculate supply chain analytics
    inventory_costs = []
    capacity_utilization = []
    efficiency_gains = []
    lead_time_reductions = []
    disruption_impacts = []
    
    # New metrics for capacity
    capacity_metrics = []
    competitor_metrics = []
    market_demand = []
    
    for i in range(len(game_state.company_state.historical_revenue)):
        # Calculate inventory cost for each quarter
        if i < len(game_state.company_state.historical_supply_chain_efficiency):
            efficiency = game_state.company_state.historical_supply_chain_efficiency[i]
        else:
            efficiency = 1.0
            
        inventory = game_state.company_state.inventory
        inventory_cost = (inventory * GameSimulation.BASE_INVENTORY_COST / efficiency)
        inventory_costs.append(inventory_cost)
        
        # Calculate capacity utilization
        capacity = game_state.company_state.capacity
        utilization = (inventory / capacity * 100) if capacity > 0 else 0
        capacity_utilization.append(utilization)
        
        # Calculate efficiency gains (quarter over quarter)
        if i > 0 and i < len(game_state.company_state.historical_supply_chain_efficiency):
            prev_efficiency = game_state.company_state.historical_supply_chain_efficiency[i-1]
            current_efficiency = game_state.company_state.historical_supply_chain_efficiency[i]
            gain = ((current_efficiency - prev_efficiency) / prev_efficiency * 100)
            efficiency_gains.append(gain)
        elif i == 0:
            efficiency_gains.append(0)
            
        # Calculate lead time reductions
        if hasattr(game_state.company_state, 'supplier_lead_time'):
            lead_time = game_state.company_state.supplier_lead_time
            initial_lead_time = 2.0  # Default starting lead time
            reduction = ((initial_lead_time - lead_time) / initial_lead_time * 100)
            lead_time_reductions.append(reduction)
        else:
            lead_time_reductions.append(0)
            
        # Calculate capacity metrics
        total_market_demand = game_state.market_state.market_size
        player_demand = total_market_demand * game_state.company_state.historical_market_share[i]
        market_demand.append({
            'total': total_market_demand,
            'player': player_demand,
            'competitor': total_market_demand - player_demand
        })
        
        # Get competitor metrics
        competitor_metrics.append({
            'capacity': getattr(game_state.market_state, 'competitor_capacity', game_state.company_state.capacity),
            'capacity_utilization': getattr(game_state.market_state, 'competitor_capacity_utilization', 0.8),
            'strategy': getattr(game_state.market_state, 'competitor_strategy', 'balanced'),
            'pending_expansions': [
                {
                    'size': exp['size'],
                    'quarters_remaining': exp['quarters_remaining']
                }
                for exp in getattr(game_state.market_state, 'competitor_pending_expansions', [])
            ]
        })
        
        # Calculate capacity metrics
        capacity_metrics.append({
            'total_capacity': game_state.company_state.capacity,
            'utilization_rate': utilization / 100,
            'pending_expansions': [
                {
                    'size': exp['size'],
                    'quarters_remaining': exp['quarters_remaining']
                }
                for exp in getattr(game_state.company_state, 'pending_expansions', [])
            ],
            'expansion_cost_rate': GameSimulation.BASE_CAPACITY_COST * math.pow(
                max(100, game_state.company_state.capacity) / 1000, 
                -GameSimulation.EXPANSION_SCALE_FACTOR
            )
        })
    
    # Get active disruptions and their impacts
    active_disruptions = []
    if hasattr(game_state.company_state, 'active_disruptions'):
        for disruption in game_state.company_state.active_disruptions:
            active_disruptions.append({
                'type': disruption['type'],
                'description': disruption['description'],
                'quarters_remaining': disruption['quarters_remaining'],
                'impact': {
                    'lead_time': f"{(disruption['impact']['lead_time'] - 1) * 100:+.1f}%",
                    'efficiency': f"{(disruption['impact']['efficiency'] - 1) * 100:+.1f}%",
                    'relationship': f"{(disruption['impact']['relationship'] - 1) * 100:+.1f}%"
                }
            })
    
    # Return historical data with supply chain analytics
    return {
        "revenue": game_state.company_state.historical_revenue,
        "profit": game_state.company_state.historical_profit,
        "stock_price": game_state.company_state.historical_stock_price,
        "market_share": game_state.company_state.historical_market_share,
        "product_quality": game_state.company_state.historical_product_quality,
        "supply_chain": {
            "efficiency": getattr(game_state.company_state, 'historical_supply_chain_efficiency', []),
            "inventory_costs": inventory_costs,
            "capacity_utilization": capacity_utilization,
            "efficiency_gains": efficiency_gains,
            "lead_time_reductions": lead_time_reductions,
            "active_disruptions": active_disruptions,
            "current_metrics": {
                "efficiency": getattr(game_state.company_state, 'supply_chain_efficiency', 1.0),
                "supplier_relationship": getattr(game_state.company_state, 'supplier_relationship', 1.0),
                "lead_time": getattr(game_state.company_state, 'supplier_lead_time', 2.0),
                "competitor_efficiency": getattr(game_state.market_state, 'competitor_supply_chain_efficiency', 1.0),
                "competitor_lead_time": getattr(game_state.market_state, 'competitor_lead_time', 2.0)
            }
        },
        "capacity": {
            "historical": capacity_metrics,
            "current_metrics": {
                "capacity": game_state.company_state.capacity,
                "utilization": capacity_utilization[-1] if capacity_utilization else 0,
                "pending_expansions": getattr(game_state.company_state, 'pending_expansions', []),
                "expansion_cost_rate": GameSimulation.BASE_CAPACITY_COST * math.pow(
                    max(100, game_state.company_state.capacity) / 1000, 
                    -GameSimulation.EXPANSION_SCALE_FACTOR
                )
            }
        },
        "competitor": {
            "historical": competitor_metrics,
            "current_metrics": {
                "capacity": getattr(game_state.market_state, 'competitor_capacity', game_state.company_state.capacity),
                "capacity_utilization": getattr(game_state.market_state, 'competitor_capacity_utilization', 0.8),
                "strategy": getattr(game_state.market_state, 'competitor_strategy', 'balanced'),
                "pending_expansions": getattr(game_state.market_state, 'competitor_pending_expansions', [])
            }
        },
        "market": {
            "demand": market_demand,
            "current_metrics": {
                "total_size": game_state.market_state.market_size,
                "growth_rate": game_state.market_state.market_growth
            }
        }
    }


@router.get("/games", response_model=List[Dict[str, Any]])
async def list_games(limit: int = 10, skip: int = 0):
    """
    List all games.
    """
    games = await GameRepository.list_games(limit, skip)
    
    # Format the response
    formatted_games = []
    for game in games:
        formatted_games.append({
            "game_id": game["metadata"]["game_id"],
            "current_quarter": game["metadata"]["current_quarter"],
            "created_at": game["metadata"]["created_at"],
            "updated_at": game["metadata"]["updated_at"],
            "stock_price": game["stock_price"],
            "cash": game["company_state"]["cash"],
            "market_share": game["market_state"]["player_market_share"],
            "product_quality": game["company_state"]["product_quality"],
            "capacity": game["company_state"]["capacity"],
            "supply_chain_efficiency": game["company_state"].get("supply_chain_efficiency", 1.0)
        })
    
    return formatted_games


@router.get("/games/{game_id}/supply-chain/forecast")
async def get_supply_chain_forecast(
    game_id: str,
    quarters: int = 4
):
    """
    Get supply chain forecasts for future quarters.
    """
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    if quarters < 1 or quarters > 8:
        raise HTTPException(status_code=400, detail="Quarters must be between 1 and 8")
    
    forecasts = GameSimulation.forecast_supply_chain_metrics(game_state, quarters)
    
    return {
        "forecasts": forecasts,
        "current_metrics": {
            "efficiency": getattr(game_state.company_state, 'supply_chain_efficiency', 1.0),
            "lead_time": getattr(game_state.company_state, 'supplier_lead_time', 2.0),
            "relationship": getattr(game_state.company_state, 'supplier_relationship', 1.0)
        }
    }


@router.get("/games/{game_id}/supply-chain/investment-analysis")
async def get_investment_analysis(
    game_id: str,
    target_efficiency: float
):
    """
    Get investment recommendations for reaching target efficiency.
    """
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    if target_efficiency < 1.0 or target_efficiency > GameSimulation.SUPPLY_CHAIN_EFFICIENCY_CAP:
        raise HTTPException(
            status_code=400, 
            detail=f"Target efficiency must be between 1.0 and {GameSimulation.SUPPLY_CHAIN_EFFICIENCY_CAP}"
        )
    
    analysis = GameSimulation.calculate_optimal_investment(game_state, target_efficiency)
    
    return {
        "analysis": analysis,
        "current_metrics": {
            "efficiency": getattr(game_state.company_state, 'supply_chain_efficiency', 1.0),
            "revenue": game_state.company_state.revenue,
            "cash": game_state.company_state.cash
        }
    }


@router.get("/games/{game_id}/supply-chain/risk-analysis")
async def get_risk_analysis(game_id: str):
    """
    Get supply chain risk analysis and mitigation recommendations.
    """
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    risk_analysis = GameSimulation.analyze_disruption_risk(game_state)
    
    # Add historical disruption data
    historical_disruptions = []
    if hasattr(game_state.company_state, 'active_disruptions'):
        for disruption in game_state.company_state.active_disruptions:
            historical_disruptions.append({
                'type': disruption['type'],
                'description': disruption['description'],
                'quarters_remaining': disruption['quarters_remaining'],
                'impact': {
                    'lead_time': f"{(disruption['impact']['lead_time'] - 1) * 100:+.1f}%",
                    'efficiency': f"{(disruption['impact']['efficiency'] - 1) * 100:+.1f}%",
                    'relationship': f"{(disruption['impact']['relationship'] - 1) * 100:+.1f}%"
                }
            })
    
    return {
        "risk_analysis": risk_analysis,
        "historical_disruptions": historical_disruptions,
        "current_metrics": {
            "efficiency": getattr(game_state.company_state, 'supply_chain_efficiency', 1.0),
            "relationship": getattr(game_state.company_state, 'supplier_relationship', 1.0),
            "lead_time": getattr(game_state.company_state, 'supplier_lead_time', 2.0),
            "inventory": game_state.company_state.inventory
        }
    }


@router.get("/games/{game_id}/regions")
async def get_available_regions(game_id: str) -> Dict:
    """Get information about available regions for international expansion."""
    game_state = await GameRepository.get_game(game_id)
    
    regions = {}
    for region_name, region in game_state.market_state.regions.items():
        # Only include regions where the company doesn't have operations
        if region_name not in game_state.company_state.regions:
            regions[region_name] = {
                "market_size": region.market_size,
                "market_growth": region.market_growth,
                "currency": region.currency,
                "exchange_rate": region.exchange_rate,
                "tariff_rate": region.tariff_rate,
                "regulatory_rating": region.regulatory_rating,
                "cultural_distance": region.cultural_distance,
                "price_sensitivity": region.price_sensitivity,
                "quality_sensitivity": region.quality_sensitivity,
                "brand_sensitivity": region.brand_sensitivity,
                "logistics_cost": region.logistics_cost,
                "supplier_quality": region.supplier_quality,
                "labor_cost": region.labor_cost
            }
    
    return {
        "available_regions": regions,
        "entry_modes": list(GameSimulation.ENTRY_COSTS.keys()),
        "entry_costs": GameSimulation.ENTRY_COSTS,
        "entry_times": GameSimulation.ENTRY_TIME
    }


@router.get("/games/{game_id}/regions/{region_name}")
async def get_region_analysis(
    game_id: str,
    region_name: str,
    investment_amount: Optional[float] = None
) -> Dict:
    """Get detailed analysis of a specific region."""
    game_state = await GameRepository.get_game(game_id)
    
    if region_name not in game_state.market_state.regions:
        raise HTTPException(status_code=404, detail="Region not found")
    
    region = game_state.market_state.regions[region_name]
    
    # Basic region information
    analysis = {
        "market_info": {
            "size": region.market_size,
            "growth": region.market_growth,
            "total_potential": region.market_size * (1 + region.market_growth) ** 4
        },
        "financial_info": {
            "currency": region.currency,
            "exchange_rate": region.exchange_rate,
            "exchange_rate_volatility": game_state.metadata.config.currency_volatility,
            "tariff_rate": region.tariff_rate
        },
        "operational_info": {
            "regulatory_rating": region.regulatory_rating,
            "cultural_distance": region.cultural_distance,
            "logistics_cost": region.logistics_cost,
            "supplier_quality": region.supplier_quality,
            "labor_cost": region.labor_cost
        },
        "market_dynamics": {
            "price_sensitivity": region.price_sensitivity,
            "quality_sensitivity": region.quality_sensitivity,
            "brand_sensitivity": region.brand_sensitivity
        }
    }
    
    # Entry cost analysis if investment amount provided
    if investment_amount:
        entry_analysis = {}
        for mode, multiplier in GameSimulation.ENTRY_COSTS.items():
            base_cost = investment_amount * multiplier
            regulatory_cost = base_cost * (region.regulatory_rating - 1.0) * 0.5
            cultural_cost = base_cost * region.cultural_distance * 0.3
            total_cost = base_cost + regulatory_cost + cultural_cost
            
            entry_analysis[mode] = {
                "base_cost": base_cost,
                "regulatory_cost": regulatory_cost,
                "cultural_cost": cultural_cost,
                "total_cost": total_cost,
                "time_to_market": GameSimulation.ENTRY_TIME[mode]
            }
        analysis["entry_analysis"] = entry_analysis
    
    return analysis


@router.get("/games/{game_id}/operations/{region_name}")
async def get_regional_operations(game_id: str, region_name: str) -> Dict:
    """Get detailed information about operations in a specific region."""
    game_state = await GameRepository.get_game(game_id)
    
    if region_name not in game_state.company_state.regions:
        raise HTTPException(status_code=404, detail="No operations in this region")
    
    operation = game_state.company_state.regions[region_name]
    region = game_state.market_state.regions[region_name]
    
    # Calculate key metrics
    revenue_history = game_state.company_state.historical_regional_revenue[region_name]
    market_share_history = game_state.company_state.historical_regional_market_share[region_name]
    exchange_rate_history = game_state.company_state.historical_exchange_rates[region.currency]
    
    return {
        "performance": {
            "market_share": operation.market_share,
            "sales_volume": operation.sales_volume,
            "revenue": operation.revenue,
            "revenue_base_currency": operation.revenue * region.exchange_rate,
            "costs": operation.costs
        },
        "operations": {
            "capacity": operation.capacity,
            "inventory": operation.inventory,
            "supply_chain_efficiency": operation.supply_chain_efficiency,
            "brand_strength": operation.brand_strength,
            "distribution_network": operation.distribution_network
        },
        "partnerships": [
            {
                "name": p["name"],
                "strength": p["strength"],
                "contribution": p["contribution"]
            }
            for p in operation.local_partnerships
        ],
        "historical_data": {
            "revenue": revenue_history,
            "market_share": market_share_history,
            "exchange_rates": exchange_rate_history
        },
        "currency_exposure": game_state.company_state.currency_exposure.get(region.currency, 0.0)
    }


@router.get("/games/{game_id}/currency-analysis")
async def get_currency_analysis(game_id: str) -> Dict:
    """Get analysis of currency exposure and hedging opportunities."""
    game_state = await GameRepository.get_game(game_id)
    
    analysis = {}
    for currency, exposure in game_state.company_state.currency_exposure.items():
        if exposure == 0:
            continue
            
        # Get exchange rate history
        history = game_state.company_state.historical_exchange_rates[currency]
        
        # Calculate volatility from historical data
        if len(history) > 1:
            returns = [(history[i] - history[i-1]) / history[i-1] for i in range(1, len(history))]
            volatility = sum(r * r for r in returns) / (len(returns) - 1)
        else:
            volatility = game_state.metadata.config.currency_volatility
        
        # Calculate hedging costs and recommendations
        hedging_cost_1m = exposure * 0.01  # 1% hedging cost
        
        analysis[currency] = {
            "exposure": exposure,
            "current_rate": history[-1],
            "historical_rates": history,
            "volatility": volatility,
            "hedging_costs": {
                "1m": hedging_cost_1m,
                "3m": hedging_cost_1m * 2.5,
                "6m": hedging_cost_1m * 4.5
            },
            "recommendation": {
                "should_hedge": volatility > 0.1,
                "suggested_ratio": min(1.0, volatility * 5),
                "rationale": "High volatility suggests hedging"
                if volatility > 0.1
                else "Low volatility suggests minimal hedging"
            }
        }
    
    return analysis


@router.get("/games/{game_id}/market/segments")
async def get_market_segments(game_id: str) -> Dict:
    """Get detailed information about market segments."""
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    segments_data = {}
    for segment_name, segment in game_state.market_state.segments.items():
        segments_data[segment_name] = {
            "size": segment.size,
            "growth_rate": segment.growth_rate,
            "characteristics": {
                "price_sensitivity": segment.price_sensitivity,
                "quality_sensitivity": segment.quality_sensitivity,
                "brand_sensitivity": segment.brand_sensitivity,
                "innovation_sensitivity": segment.innovation_sensitivity,
                "purchasing_power": segment.purchasing_power,
                "loyalty_factor": segment.loyalty_factor,
                "adoption_rate": segment.adoption_rate
            },
            "trends": {
                "trend_direction": segment.trend_direction,
                "trend_strength": segment.trend_strength,
                "seasonal_factors": segment.seasonal_factors
            },
            "historical_data": {
                "sizes": game_state.market_state.historical_segment_sizes[segment_name],
                "growth_rates": game_state.market_state.historical_segment_growth[segment_name]
            },
            "profitability": game_state.market_state.segment_profitability.get(segment_name, 0.0)
        }
    
    return {
        "segments": segments_data,
        "market_metrics": {
            "total_market_size": game_state.market_state.market_size,
            "market_growth": game_state.market_state.market_growth,
            "market_concentration": game_state.market_state.market_concentration,
            "consumer_sentiment": game_state.market_state.consumer_sentiment
        }
    }


@router.get("/games/{game_id}/market/trends")
async def get_market_trends(game_id: str) -> Dict:
    """Get information about active market trends."""
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    active_trends = []
    for trend in game_state.market_state.active_trends:
        active_trends.append({
            "name": trend.name,
            "strength": trend.strength,
            "duration": trend.duration,
            "quarters_active": trend.quarters_active,
            "remaining_quarters": trend.duration - trend.quarters_active,
            "impacts": {
                "segment_impact": trend.segment_impact,
                "preference_shifts": trend.preference_shifts,
                "growth_impact": trend.growth_impact
            }
        })
    
    # Get all possible trends for reference
    available_trends = {}
    for trend_name, trend_data in GameSimulation.MARKET_TRENDS.items():
        available_trends[trend_name] = {
            "typical_impacts": {
                "segment_impact": trend_data["segment_impact"],
                "preference_shifts": trend_data["preference_shifts"],
                "growth_impact": trend_data["growth_impact"]
            }
        }
    
    return {
        "active_trends": active_trends,
        "available_trends": available_trends,
        "market_conditions": {
            "consumer_sentiment": game_state.market_state.consumer_sentiment,
            "market_growth": game_state.market_state.market_growth,
            "economic_cycle": game_state.external_state.economic_cycle
        }
    }


@router.get("/games/{game_id}/competition")
async def get_competition_analysis(game_id: str) -> Dict:
    """Get detailed analysis of market competition."""
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    competitors_data = {}
    for comp_name, competitor in game_state.market_state.competitors.items():
        competitors_data[comp_name] = {
            "market_position": {
                "market_share": competitor.market_share,
                "price": competitor.price,
                "product_quality": competitor.product_quality,
                "brand_strength": competitor.brand_strength
            },
            "strategy": {
                "price_strategy": competitor.price_strategy,
                "quality_strategy": competitor.quality_strategy,
                "innovation_strategy": competitor.innovation_strategy,
                "segment_focus": competitor.segment_focus
            },
            "capabilities": {
                "r_and_d": competitor.r_and_d_capability,
                "marketing": competitor.marketing_effectiveness,
                "production": competitor.production_efficiency,
                "financial_strength": competitor.financial_strength
            },
            "historical_data": {
                "prices": competitor.historical_prices,
                "market_share": competitor.historical_market_share,
                "quality": competitor.historical_quality
            }
        }
    
    # Calculate competitive metrics
    player_share = game_state.market_state.player_market_share
    total_competitor_share = sum(comp.market_share for comp in game_state.market_state.competitors.values())
    
    # Calculate price positioning
    avg_competitor_price = sum(
        comp.price for comp in game_state.market_state.competitors.values()
    ) / len(game_state.market_state.competitors)
    
    player_price_position = (
        "premium" if game_state.company_state.price > avg_competitor_price * 1.1
        else "discount" if game_state.company_state.price < avg_competitor_price * 0.9
        else "balanced"
    )
    
    return {
        "competitors": competitors_data,
        "market_structure": {
            "player_market_share": player_share,
            "total_competitor_share": total_competitor_share,
            "market_concentration": game_state.market_state.market_concentration,
            "number_of_competitors": len(game_state.market_state.competitors)
        },
        "competitive_position": {
            "price_position": player_price_position,
            "quality_comparison": {
                "player": game_state.company_state.product_quality,
                "market_average": sum(
                    comp.product_quality for comp in game_state.market_state.competitors.values()
                ) / len(game_state.market_state.competitors)
            },
            "brand_strength_comparison": {
                "player": game_state.company_state.marketing_effectiveness,
                "market_average": sum(
                    comp.brand_strength for comp in game_state.market_state.competitors.values()
                ) / len(game_state.market_state.competitors)
            }
        },
        "segment_leadership": {
            segment: max(
                [("player", player_share)] +
                [(comp_name, comp.market_share * comp.segment_focus.get(segment, 0))
                 for comp_name, comp in game_state.market_state.competitors.items()],
                key=lambda x: x[1]
            )[0]
            for segment in game_state.market_state.segments
        }
    }


@router.get("/games/{game_id}/market/forecast")
async def get_market_forecast(
    game_id: str,
    quarters_ahead: int = Query(4, ge=1, le=8)
) -> Dict:
    """Get market forecasts for future quarters."""
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    # Calculate base market growth
    base_market_size = game_state.market_state.market_size
    base_growth_rate = game_state.market_state.market_growth
    
    # Consider active trends
    trend_impacts = []
    for trend in game_state.market_state.active_trends:
        remaining_quarters = trend.duration - trend.quarters_active
        if remaining_quarters > 0:
            trend_impacts.append({
                "name": trend.name,
                "quarters_remaining": remaining_quarters,
                "growth_impact": trend.growth_impact * trend.strength
            })
    
    # Calculate segment forecasts
    segment_forecasts = {}
    for segment_name, segment in game_state.market_state.segments.items():
        quarterly_forecasts = []
        current_size = segment.size * base_market_size
        current_growth = segment.growth_rate
        
        for quarter in range(quarters_ahead):
            # Apply trend effects
            quarter_trend_impact = sum(
                impact["growth_impact"]
                for impact in trend_impacts
                if impact["quarters_remaining"] > quarter
            )
            
            # Calculate quarterly growth
            quarter_growth = current_growth + quarter_trend_impact
            current_size *= (1 + quarter_growth)
            
            # Apply seasonal factors
            season = (game_state.metadata.current_quarter + quarter - 1) % 4 + 1
            seasonal_factor = segment.seasonal_factors.get(season, 1.0)
            
            quarterly_forecasts.append({
                "quarter": game_state.metadata.current_quarter + quarter + 1,
                "market_size": current_size * seasonal_factor,
                "growth_rate": quarter_growth,
                "seasonal_factor": seasonal_factor
            })
        
        segment_forecasts[segment_name] = quarterly_forecasts
    
    return {
        "market_forecasts": {
            "total_market": [
                {
                    "quarter": game_state.metadata.current_quarter + q + 1,
                    "market_size": base_market_size * math.pow(1 + base_growth_rate, q),
                    "growth_rate": base_growth_rate
                }
                for q in range(quarters_ahead)
            ],
            "segments": segment_forecasts
        },
        "trend_impacts": trend_impacts,
        "confidence_factors": {
            "economic_cycle": game_state.external_state.economic_cycle_position,
            "consumer_confidence": game_state.external_state.consumer_confidence,
            "market_stability": 1 - abs(game_state.market_state.market_concentration - 0.5) * 2
        }
    } 