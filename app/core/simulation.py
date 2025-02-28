"""
Core game simulation logic for the Business Game.
"""
import uuid
import math
import random
from datetime import datetime
from typing import Tuple, Dict, List, Optional, Union, Any

from app.models.game import (
    GameState, CompanyState, MarketState, ExternalState, GameMetadata,
    PlayerAction, GameConfig, MarketSegment, MarketTrend, Competitor, ProductStrategy,
    MarketingDecision, RAndDDecision, CapacityDecision,
    SupplyChainDecision, FinancialDecision, HRDecision,
    InternationalDecision, MarketEntryDecision, RegionalPricingDecision,
    RegionalSupplyDecision, Employee, RegionalOperation, HiringDecision,
    TrainingProgram
)


class GameSimulation:
    """
    Core game simulation logic.
    """
    
    # Constants for capacity expansion
    BASE_CAPACITY_COST = 1.0  # Cost in millions per unit of capacity
    EXPANSION_SCALE_FACTOR = 0.8  # Economies of scale in capacity expansion
    CAPACITY_LEAD_TIME = 2  # Quarters until new capacity becomes available
    
    # Constants for supply chain management
    BASE_INVENTORY_COST = 0.1  # Base cost per unit of inventory per quarter
    SUPPLIER_RELATIONSHIP_DECAY = 0.1  # Rate at which supplier relationships decay
    SUPPLY_CHAIN_EFFICIENCY_CAP = 2.0  # Maximum supply chain efficiency multiplier
    SUPPLIER_LEAD_TIME_MIN = 1  # Minimum supplier lead time (quarters)
    
    # Constants for supply chain disruptions
    DISRUPTION_TYPES = {
        "supplier_bankruptcy": {
            "probability": 0.05,
            "impact": {
                "lead_time": 1.5,  # Multiplier for lead time
                "efficiency": 0.7,  # Multiplier for efficiency
                "relationship": 0.5  # Multiplier for relationship
            },
            "duration": 2  # Quarters
        },
        "natural_disaster": {
            "probability": 0.03,
            "impact": {
                "lead_time": 2.0,
                "efficiency": 0.5,
                "relationship": 0.8
            },
            "duration": 3
        },
        "logistics_disruption": {
            "probability": 0.08,
            "impact": {
                "lead_time": 1.3,
                "efficiency": 0.8,
                "relationship": 0.9
            },
            "duration": 1
        }
    }
    
    # Constants for financial management
    LOAN_INTEREST_SPREAD = 0.02  # Additional interest rate above base rate
    MAX_DEBT_TO_EQUITY_RATIO = 2.0  # Maximum allowed debt/equity ratio
    DIVIDEND_TAX_RATE = 0.15  # Tax rate on dividends
    INVESTMENT_TYPES = {
        "bonds": {
            "min_term": 4,  # quarters
            "max_term": 20,  # quarters
            "base_return": 0.03,  # quarterly return
            "risk_factor": 0.2  # volatility
        },
        "stocks": {
            "min_term": 1,
            "max_term": None,  # no maximum term
            "base_return": 0.05,
            "risk_factor": 0.4
        },
        "money_market": {
            "min_term": 1,
            "max_term": 4,
            "base_return": 0.02,
            "risk_factor": 0.1
        }
    }
    
    # Constants for HR management
    BASE_SALARY = 50.0  # Base annual salary in thousands
    HIRING_COST_MULTIPLIER = 0.5  # Hiring cost as multiple of annual salary
    TRAINING_EFFECTIVENESS_CAP = 2.0  # Maximum training effectiveness multiplier
    SATISFACTION_IMPACT = {
        "salary": 0.4,  # Impact of salary on satisfaction
        "training": 0.3,  # Impact of training on satisfaction
        "productivity": 0.3  # Impact of productivity on satisfaction
    }
    TURNOVER_THRESHOLD = 0.6  # Satisfaction level below which employees may leave
    EXPERIENCE_GAIN = 0.25  # Experience gained per quarter
    
    # Department-specific productivity multipliers
    DEPARTMENT_IMPACTS = {
        "production": {
            "capacity_utilization": 0.3,
            "quality": 0.2,
            "efficiency": 0.5
        },
        "rd": {
            "innovation": 0.4,
            "quality": 0.4,
            "efficiency": 0.2
        },
        "marketing": {
            "effectiveness": 0.6,
            "market_research": 0.4
        },
        "supply_chain": {
            "efficiency": 0.4,
            "relationship": 0.3,
            "lead_time": 0.3
        }
    }
    
    # Constants for international operations
    REGIONS = {
        "north_america": {
            "market_size": 50000,
            "market_growth": 0.02,
            "currency": "USD",
            "exchange_rate": 1.0,
            "tariff_rate": 0.0,
            "regulatory_rating": 1.0,
            "cultural_distance": 0.0,
            "price_sensitivity": 0.8,
            "quality_sensitivity": 1.2,
            "brand_sensitivity": 1.0,
            "logistics_cost": 1.0,
            "supplier_quality": 1.0,
            "labor_cost": 1.2
        },
        "europe": {
            "market_size": 40000,
            "market_growth": 0.015,
            "currency": "EUR",
            "exchange_rate": 1.1,
            "tariff_rate": 0.05,
            "regulatory_rating": 1.2,
            "cultural_distance": 0.3,
            "price_sensitivity": 0.9,
            "quality_sensitivity": 1.3,
            "brand_sensitivity": 1.1,
            "logistics_cost": 1.1,
            "supplier_quality": 1.1,
            "labor_cost": 1.3
        },
        "asia_pacific": {
            "market_size": 60000,
            "market_growth": 0.04,
            "currency": "CNY",
            "exchange_rate": 0.15,
            "tariff_rate": 0.08,
            "regulatory_rating": 1.4,
            "cultural_distance": 0.7,
            "price_sensitivity": 1.2,
            "quality_sensitivity": 0.9,
            "brand_sensitivity": 0.8,
            "logistics_cost": 0.8,
            "supplier_quality": 0.9,
            "labor_cost": 0.7
        }
    }
    
    ENTRY_COSTS = {
        "export": 1.0,  # Base cost multiplier
        "partnership": 2.0,
        "subsidiary": 5.0
    }
    
    ENTRY_TIME = {
        "export": 1,  # Quarters to establish presence
        "partnership": 2,
        "subsidiary": 4
    }
    
    # Constants for market segments
    MARKET_SEGMENTS = {
        "value": {
            "size": 0.3,
            "growth_rate": 0.015,
            "price_sensitivity": 1.5,
            "quality_sensitivity": 0.7,
            "brand_sensitivity": 0.6,
            "innovation_sensitivity": 0.5,
            "purchasing_power": 0.7,
            "loyalty_factor": 0.8,
            "adoption_rate": 0.6
        },
        "mainstream": {
            "size": 0.5,
            "growth_rate": 0.02,
            "price_sensitivity": 1.0,
            "quality_sensitivity": 1.0,
            "brand_sensitivity": 1.0,
            "innovation_sensitivity": 1.0,
            "purchasing_power": 1.0,
            "loyalty_factor": 1.0,
            "adoption_rate": 1.0
        },
        "premium": {
            "size": 0.2,
            "growth_rate": 0.025,
            "price_sensitivity": 0.6,
            "quality_sensitivity": 1.4,
            "brand_sensitivity": 1.3,
            "innovation_sensitivity": 1.5,
            "purchasing_power": 1.5,
            "loyalty_factor": 1.2,
            "adoption_rate": 1.3
        }
    }
    
    # Constants for market trends
    MARKET_TRENDS = {
        "sustainability": {
            "segment_impact": {
                "value": 0.8,
                "mainstream": 1.2,
                "premium": 1.5
            },
            "preference_shifts": {
                "quality_sensitivity": 0.2,
                "price_sensitivity": -0.1
            },
            "growth_impact": 0.01
        },
        "digital_transformation": {
            "segment_impact": {
                "value": 1.1,
                "mainstream": 1.3,
                "premium": 1.2
            },
            "preference_shifts": {
                "innovation_sensitivity": 0.3,
                "brand_sensitivity": -0.1
            },
            "growth_impact": 0.02
        },
        "economic_uncertainty": {
            "segment_impact": {
                "value": 1.3,
                "mainstream": 0.9,
                "premium": 0.7
            },
            "preference_shifts": {
                "price_sensitivity": 0.3,
                "quality_sensitivity": -0.1
            },
            "growth_impact": -0.01
        }
    }
    
    # Constants for competitor behavior
    COMPETITOR_STRATEGIES = {
        "aggressive": {
            "price_adjustment": -0.1,
            "marketing_intensity": 1.3,
            "innovation_rate": 1.1
        },
        "balanced": {
            "price_adjustment": 0.0,
            "marketing_intensity": 1.0,
            "innovation_rate": 1.0
        },
        "premium": {
            "price_adjustment": 0.1,
            "marketing_intensity": 1.2,
            "innovation_rate": 1.2
        }
    }
    
    @staticmethod
    def initialize_game(config: GameConfig) -> GameState:
        """
        Initialize a new game with default starting values.
        
        Args:
            config: Configuration parameters for the new game
            
        Returns:
            The initial game state
        """
        # Generate a unique game ID
        game_id = str(uuid.uuid4())
        
        # Initialize company state
        company_state = CompanyState(
            cash=config.initial_cash,
            assets=config.initial_assets,
            inventory=0,  # Start with no inventory
            capacity=config.initial_capacity,
            revenue=0.0,
            costs=0.0,
            profit=0.0,
            stock_price=100.0,  # Initial stock price
            historical_revenue=[],
            historical_profit=[],
            historical_stock_price=[],
            historical_regional_revenue={str(region): [] for region in config.starting_regions},
            historical_regional_market_share={str(region): [] for region in config.starting_regions},
            historical_exchange_rates={str(region): [] for region in config.starting_regions}
        )
        
        # Initialize market state
        competitor_market_share = 1.0 - config.initial_player_market_share
        market_state = MarketState(
            market_size=config.initial_market_size,
            market_growth=0.02,  # 2% quarterly growth by default
            competitor_price=config.initial_competitor_price,
            competitor_market_share=competitor_market_share,
            player_market_share=config.initial_player_market_share,
            price_elasticity=config.price_elasticity,
            competitor_quality=1.0,  # Initial competitor quality
            competitor_brand=1.0,  # Initial competitor brand strength
            competitor_efficiency=1.0,  # Initial competitor efficiency
            competitor_innovation=1.0,  # Initial competitor innovation
            competitor_supply_chain=1.0,  # Initial competitor supply chain
            competitor_marketing=1.0,  # Initial competitor marketing
            competitor_r_and_d=1.0,  # Initial competitor R&D
            global_demand_correlation={},
            trade_barriers={}
        )
        
        # Initialize external state with reasonable defaults
        external_state = ExternalState(
            interest_rate=0.01,  # 1% quarterly interest rate
            inflation_rate=0.005,  # 0.5% quarterly inflation
            tax_rate=0.25,  # 25% corporate tax
            regulatory_burden=0.05  # 5% regulatory cost factor
        )
        
        # Initialize game metadata
        metadata = GameMetadata(
            game_id=game_id,
            current_quarter=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create initial game state
        game_state = GameState(
            company_state=company_state,
            market_state=market_state,
            external_state=external_state,
            metadata=metadata,
            stock_price=100.0  # Initial stock price
        )
        
        # Calculate initial stock price
        game_state.stock_price = GameSimulation._calculate_stock_price(game_state)
        
        # Initialize international operations if enabled
        if config.international_enabled:
            # Initialize available regions
            market_state.regions = {}
            for region_name in config.starting_regions:
                if region_name in GameSimulation.REGIONS:
                    region_data = GameSimulation.REGIONS[region_name]
                    market_state.regions[str(region_name)] = Region(
                        name=str(region_name),
                        market_size=region_data["market_size"],
                        market_growth=region_data["market_growth"],
                        currency=region_data["currency"],
                        exchange_rate=region_data["exchange_rate"],
                        tariff_rate=region_data["tariff_rate"],
                        regulatory_rating=region_data["regulatory_rating"],
                        cultural_distance=region_data["cultural_distance"],
                        price_sensitivity=region_data["price_sensitivity"],
                        quality_sensitivity=region_data["quality_sensitivity"],
                        brand_sensitivity=region_data["brand_sensitivity"],
                        logistics_cost=region_data["logistics_cost"],
                        supplier_quality=region_data["supplier_quality"],
                        labor_cost=region_data["labor_cost"]
                    )
            
            # Initialize demand correlations and trade barriers with string keys
            market_state.global_demand_correlation = {
                str(r1): {str(r2): 0.3 for r2 in config.starting_regions}
                for r1 in config.starting_regions
            }
            
            market_state.trade_barriers = {
                str(r1): {str(r2): 0.1 for r2 in config.starting_regions}
                for r1 in config.starting_regions
            }
        
        # Initialize market segments if enabled
        if config.market_segments_enabled:
            market_state.segments = {}
            for segment_name, segment_data in GameSimulation.MARKET_SEGMENTS.items():
                market_state.segments[str(segment_name)] = MarketSegment(
                    name=str(segment_name),
                    **segment_data
                )
            
            # Initialize segment metrics
            market_state.segment_growth_rates = {
                str(name): data["growth_rate"]
                for name, data in GameSimulation.MARKET_SEGMENTS.items()
            }
            market_state.segment_profitability = {
                str(name): 1.0 for name in GameSimulation.MARKET_SEGMENTS.keys()
            }
            
            # Initialize historical data
            market_state.historical_segment_sizes = {
                str(name): [data["size"]]
                for name, data in GameSimulation.MARKET_SEGMENTS.items()
            }
            market_state.historical_segment_growth = {
                str(name): [data["growth_rate"]]
                for name, data in GameSimulation.MARKET_SEGMENTS.items()
            }
        
        # Initialize competitors if advanced competition is enabled
        if config.advanced_competitors_enabled:
            market_state.competitors = {
                "competitor_1": Competitor(
                    name="Competitor 1",
                    market_share=0.4,
                    price=config.initial_competitor_price,
                    product_quality=1.0,
                    brand_strength=1.0,
                    segment_focus={str(segment): value for segment, value in {
                        "mainstream": 0.6,
                        "premium": 0.4
                    }.items()}
                ),
                "competitor_2": Competitor(
                    name="Competitor 2",
                    market_share=0.3,
                    price=config.initial_competitor_price * 0.9,
                    product_quality=0.9,
                    brand_strength=0.8,
                    segment_focus={str(segment): value for segment, value in {
                        "value": 0.7,
                        "mainstream": 0.3
                    }.items()}
                )
            }
        
        return game_state
    
    @staticmethod
    def process_player_action(game_state: GameState, action: PlayerAction) -> GameState:
        """
        Process a player's quarterly decisions and update the game state.
        
        Args:
            game_state: The current game state
            action: The player's action for the quarter
            
        Returns:
            The updated game state
        """
        # Make a copy of the game state to avoid modifying the original
        updated_state = GameState.parse_obj(game_state.dict())
        
        # Extract player decisions
        price = action.pricing_decision.price
        production_volume = action.production_decision.volume
        
        # Process marketing decisions if provided
        marketing_multiplier = 1.0
        marketing_cost = 0.0
        if action.marketing_decision:
            marketing_multiplier = GameSimulation._process_marketing_decision(
                updated_state, 
                action.marketing_decision
            )
            marketing_cost = action.marketing_decision.budget
        
        # Process R&D decisions if provided
        r_and_d_cost = 0.0
        if action.r_and_d_decision:
            GameSimulation._process_r_and_d_decision(
                updated_state,
                action.r_and_d_decision
            )
            r_and_d_cost = action.r_and_d_decision.budget
        
        # Process capacity decisions if provided
        capacity_cost = 0.0
        if action.capacity_decision and action.capacity_decision.expansion > 0:
            capacity_cost = GameSimulation._process_capacity_decision(
                updated_state,
                action.capacity_decision
            )
        
        # Process supply chain decisions if provided
        supply_chain_cost = 0.0
        if action.supply_chain_decision:
            supply_chain_cost = GameSimulation._process_supply_chain_decision(
                updated_state,
                action.supply_chain_decision
            )
            
        # Process financial decisions if provided
        financial_impact = 0.0
        if action.financial_decision:
            financial_impact = GameSimulation._process_financial_decision(
                updated_state,
                action.financial_decision
            )
        
        # Process HR decisions if provided
        hr_cost = 0.0
        if action.hr_decision:
            hr_cost = GameSimulation._process_hr_decision(updated_state, action.hr_decision)
        
        # Process international decisions if provided
        international_cost = 0.0
        if action.international_decision:
            international_cost = GameSimulation._process_international_decision(
                updated_state,
                action.international_decision
            )
        
        # Process product strategy if provided
        if action.product_strategy:
            GameSimulation._process_product_strategy(game_state, action.product_strategy)
        
        # Calculate segment-specific demand
        total_demand = 0
        for segment_name, segment in game_state.market_state.segments.items():
            marketing_allocation = (
                action.marketing_decision.segment_allocation.get(segment_name, 0)
                if action.marketing_decision
                else 0
            )
            segment_demand = GameSimulation._calculate_segment_demand(
                game_state,
                segment,
                price,
                marketing_allocation
            )
            total_demand += segment_demand
        
        # Update market conditions
        GameSimulation._update_market_conditions(game_state)
        
        # Update competitor behavior
        GameSimulation._update_competitor_behavior(game_state)
        
        # Calculate demand based on price elasticity, marketing, and product quality
        base_demand = GameSimulation._calculate_demand(updated_state, price)
        quality_multiplier = math.pow(updated_state.company_state.product_quality, 
                                    updated_state.market_state.quality_elasticity)
        demand = base_demand * marketing_multiplier * quality_multiplier
        
        # Calculate sales (limited by production + inventory)
        available_units = updated_state.company_state.inventory + production_volume
        sales_volume = min(demand, available_units)
        
        # Update inventory
        new_inventory = available_units - sales_volume
        
        # Calculate financial results
        revenue = sales_volume * price
        production_cost = GameSimulation._calculate_production_cost(
            volume=production_volume, 
            capacity=updated_state.company_state.capacity,
            r_and_d_level=updated_state.company_state.r_and_d_level,
            supply_chain_efficiency=getattr(updated_state.company_state, 'supply_chain_efficiency', 1.0),
            game_state=updated_state
        )
        operating_cost = GameSimulation._calculate_operating_cost(
            assets=updated_state.company_state.assets,
            game_state=updated_state
        )
        total_cost = (production_cost + operating_cost + marketing_cost + 
                     r_and_d_cost + capacity_cost + supply_chain_cost + hr_cost + international_cost)
        
        # Calculate profit before tax
        profit_before_tax = revenue - total_cost
        
        # Apply tax
        tax = max(0, profit_before_tax * updated_state.external_state.tax_rate)
        profit_after_tax = profit_before_tax - tax
        
        # Update company state
        updated_state.company_state.cash += profit_after_tax + financial_impact
        updated_state.company_state.inventory = new_inventory
        updated_state.company_state.revenue = revenue
        updated_state.company_state.costs = total_cost
        updated_state.company_state.profit = profit_after_tax
        
        # Update marketing effectiveness based on spending
        if action.marketing_decision:
            updated_state.company_state.marketing_effectiveness = marketing_multiplier
        
        # Update historical data
        updated_state.company_state.historical_revenue.append(revenue)
        updated_state.company_state.historical_profit.append(profit_after_tax)
        updated_state.company_state.historical_stock_price.append(updated_state.stock_price)
        updated_state.company_state.historical_product_quality.append(updated_state.company_state.product_quality)
        if hasattr(updated_state.company_state, 'supply_chain_efficiency'):
            if not hasattr(updated_state.company_state, 'historical_supply_chain_efficiency'):
                updated_state.company_state.historical_supply_chain_efficiency = []
            updated_state.company_state.historical_supply_chain_efficiency.append(
                updated_state.company_state.supply_chain_efficiency
            )
        
        # Calculate new stock price
        stock_price = GameSimulation._calculate_stock_price(updated_state)
        updated_state.stock_price = stock_price
        updated_state.company_state.historical_stock_price.append(stock_price)
        
        # Process pending capacity expansions
        GameSimulation._update_capacity_expansions(updated_state)
        
        # Update international operations
        GameSimulation._update_international_operations(updated_state)
        
        # Advance to next quarter
        updated_state.metadata.current_quarter += 1
        updated_state.metadata.updated_at = datetime.now()
        
        return updated_state
    
    @staticmethod
    def _calculate_demand(game_state: GameState, price: float) -> float:
        """
        Calculate demand based on price elasticity and market conditions.
        
        Args:
            game_state: The current game state
            price: The player's price
            
        Returns:
            The calculated demand
        """
        market_state = game_state.market_state
        competitor_price = market_state.competitor_price
        
        # Calculate price ratio (player price / competitor price)
        price_ratio = price / competitor_price
        
        # Apply price elasticity to determine market share shift
        # If price_ratio > 1, player is more expensive than competitor
        # If price_ratio < 1, player is cheaper than competitor
        elasticity_effect = math.pow(price_ratio, -market_state.price_elasticity)
        
        # Calculate new market share (bounded between 0.1 and 0.9)
        base_market_share = market_state.player_market_share
        new_market_share = base_market_share * elasticity_effect
        new_market_share = max(0.1, min(0.9, new_market_share))
        
        # Calculate demand based on market share and market size
        demand = new_market_share * market_state.market_size
        
        # Apply consumer sentiment effect
        consumer_sentiment = getattr(market_state, 'consumer_sentiment', 1.0)
        demand *= consumer_sentiment
        
        return demand
    
    @staticmethod
    def _calculate_production_cost(
        volume: float,
        capacity: float,
        r_and_d_level: float = 1.0,
        supply_chain_efficiency: float = 1.0,
        game_state: Optional[GameState] = None
    ) -> float:
        """
        Calculate production cost based on volume, capacity, R&D level, and supply chain efficiency.
        
        Args:
            volume: Production volume
            capacity: Production capacity
            r_and_d_level: R&D efficiency level (higher means more efficient)
            supply_chain_efficiency: Supply chain efficiency multiplier
            game_state: Optional game state for checking disruptions
            
        Returns:
            The production cost in millions
        """
        # Base cost per unit (reduced by R&D efficiency and supply chain efficiency)
        base_cost_per_unit = 50.0 / (math.sqrt(r_and_d_level) * supply_chain_efficiency)
        
        # Calculate capacity utilization
        utilization = volume / capacity if capacity > 0 else float('inf')
        
        # Apply capacity utilization effects
        if utilization <= 0.5:
            # Underutilization penalty
            cost_multiplier = 1.2  # 20% penalty for low utilization
        elif utilization <= 0.8:
            # Optimal utilization range
            cost_multiplier = 0.9  # 10% discount for optimal utilization
        elif utilization <= 1.0:
            # High utilization
            cost_multiplier = 1.0
        else:
            # Over capacity - significant cost increase
            over_capacity_ratio = utilization - 1.0
            cost_multiplier = 1.0 + (over_capacity_ratio * 0.5)  # 50% cost increase per unit over capacity
        
        # Apply economies of scale
        scale_factor = math.log1p(volume) / math.log1p(capacity)
        scale_multiplier = max(0.8, 1.0 - (scale_factor * 0.2))  # Up to 20% discount for scale
        
        # Calculate base production cost
        base_production_cost = volume * base_cost_per_unit * cost_multiplier * scale_multiplier
        
        # Apply supply chain disruption effects if game state is provided
        if game_state and hasattr(game_state.company_state, 'active_disruptions'):
            disruption_multiplier = 1.0
            for disruption in game_state.company_state.active_disruptions:
                if disruption['quarters_remaining'] > 0:
                    disruption_multiplier *= disruption['impact'].get('efficiency', 1.0)
            base_production_cost *= disruption_multiplier
        
        # Convert to millions for consistency
        return base_production_cost / 1000000
    
    @staticmethod
    def _calculate_operating_cost(
        assets: float,
        game_state: Optional[GameState] = None
    ) -> float:
        """
        Calculate fixed operating costs based on assets and other factors.
        
        Args:
            assets: Company assets value in millions
            game_state: Optional game state for additional factors
            
        Returns:
            The operating cost in millions
        """
        # Base operating costs as a percentage of assets
        base_operating_cost = assets * 0.05  # 5% of assets
        
        if game_state:
            # Add regulatory compliance costs
            regulatory_cost = assets * game_state.external_state.regulatory_burden
            
            # Add fixed administrative costs
            admin_cost = 0.5  # Base admin cost in millions
            
            # Scale admin cost with company size
            size_factor = math.log1p(assets) / math.log1p(100)  # Normalized to 100M assets
            admin_cost *= max(1.0, size_factor)
            
            # Add employee-related overhead if HR system exists
            hr_overhead = 0.0
            if hasattr(game_state.company_state, 'employees'):
                total_employees = sum(
                    len(employees)
                    for employees in game_state.company_state.employees.values()
                )
                hr_overhead = total_employees * 0.01  # 10K per employee
            
            # Add international operations overhead
            international_overhead = 0.0
            if hasattr(game_state.company_state, 'regions'):
                for region in game_state.company_state.regions.values():
                    # Base overhead for maintaining international presence
                    international_overhead += 0.2  # 200K per region
                    # Add complexity cost based on region characteristics
                    if hasattr(region, 'regulatory_rating'):
                        international_overhead += 0.1 * (region.regulatory_rating - 1.0)
            
            # Calculate total operating cost
            total_operating_cost = (
                base_operating_cost +
                regulatory_cost +
                admin_cost +
                hr_overhead +
                international_overhead
            )
            
            # Apply inflation effect if available
            if hasattr(game_state.external_state, 'inflation_rate'):
                inflation_multiplier = 1.0 + game_state.external_state.inflation_rate
                total_operating_cost *= inflation_multiplier
            
            return total_operating_cost
        
        # If no game state provided, return only base operating cost
        return base_operating_cost
    
    @staticmethod
    def _update_competitor_behavior(game_state: GameState) -> None:
        """Update competitor behavior based on market conditions and player actions."""
        if not game_state.market_state.competitors:
            return
            
        player_price = game_state.company_state.price
        player_quality = game_state.company_state.product_quality
        market_growth = game_state.market_state.market_growth
        consumer_sentiment = getattr(game_state.market_state, 'consumer_sentiment', 1.0)
        
        for competitor in game_state.market_state.competitors.values():
            # Store historical data
            competitor.historical_prices.append(competitor.price)
            competitor.historical_market_share.append(competitor.market_share)
            competitor.historical_quality.append(competitor.product_quality)
            
            # Analyze market position
            price_position = competitor.price / player_price
            quality_position = competitor.product_quality / player_quality
            market_position = competitor.market_share / game_state.market_state.player_market_share
            
            # Determine strategy adjustments based on market conditions
            strategy = competitor.price_strategy
            strategy_factors = GameSimulation.COMPETITOR_STRATEGIES[strategy]
            
            # Base price adjustment
            price_adjustment = strategy_factors["price_adjustment"]
            
            # Adjust for market conditions
            if market_growth < 0:
                price_adjustment -= 0.05  # More aggressive in declining markets
            if consumer_sentiment < 0.8:
                price_adjustment -= 0.03  # More aggressive when consumer sentiment is low
            
            # Adjust for competitive position
            if market_position < 0.8:  # Losing market share
                if price_position > 1.1:  # If significantly more expensive
                    price_adjustment -= 0.05  # Reduce price
                elif quality_position < 0.9:  # If quality is lower
                    price_adjustment -= 0.03  # Slightly reduce price
            elif market_position > 1.2:  # Gaining market share
                if price_position < 0.9:  # If significantly cheaper
                    price_adjustment += 0.03  # Increase price
            
            # Apply price adjustment with bounds
            competitor.price *= (1 + max(-0.1, min(0.1, price_adjustment)))
            
            # Adjust quality and innovation based on market position
            base_quality_improvement = random.uniform(0.01, 0.03) * strategy_factors["innovation_rate"]
            
            # Increase quality investment if falling behind
            if quality_position < 0.9:
                base_quality_improvement *= 1.5
            
            # Adjust for market conditions
            if market_growth > 0.05:  # Strong growth
                base_quality_improvement *= 1.2
            elif consumer_sentiment > 1.2:  # High consumer confidence
                base_quality_improvement *= 1.1
            
            competitor.product_quality *= (1 + base_quality_improvement)
            
            # Update marketing and brand strategy
            base_marketing = strategy_factors["marketing_intensity"]
            
            # Adjust marketing based on conditions
            if consumer_sentiment < 0.8:
                base_marketing *= 1.2  # Increase marketing in tough times
            if market_position < 0.8:
                base_marketing *= 1.3  # Increase marketing when losing share
            
            marketing_effectiveness = base_marketing * consumer_sentiment
            brand_change = random.uniform(0.01, 0.02) * marketing_effectiveness
            competitor.brand_strength *= (1 + brand_change)
            
            # Update segment focus based on profitability and trends
            if len(game_state.market_state.segments) > 1:
                # Calculate segment attractiveness
                segment_scores = {}
                for segment_name, segment in game_state.market_state.segments.items():
                    # Base score from profitability
                    base_score = game_state.market_state.segment_profitability.get(segment_name, 0)
                    
                    # Adjust for growth
                    growth_score = segment.growth_rate * 2
                    
                    # Adjust for trends
                    trend_score = sum(
                        trend.strength * trend.segment_impact.get(segment_name, 0)
                        for trend in game_state.market_state.active_trends
                    )
                    
                    # Calculate total score
                    segment_scores[segment_name] = base_score + growth_score + trend_score
                
                # Focus on most attractive segments
                sorted_segments = sorted(
                    segment_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Gradually shift focus to top segments
                for segment_name, score in sorted_segments[:2]:  # Focus on top 2 segments
                    current_focus = competitor.segment_focus.get(segment_name, 0)
                    target_focus = min(0.6, current_focus + 0.1)
                    competitor.segment_focus[segment_name] = target_focus
                
                # Reduce focus on less attractive segments
                for segment_name, score in sorted_segments[2:]:
                    if segment_name in competitor.segment_focus:
                        competitor.segment_focus[segment_name] = max(
                            0.1,
                            competitor.segment_focus[segment_name] - 0.05
                        )

    @staticmethod
    def _update_market_conditions(game_state: GameState) -> None:
        """Update market conditions including segments and trends."""
        # Process market trends
        GameSimulation._process_market_trends(game_state)
        
        # Update segment metrics
        total_market = 0
        for segment_name, segment in game_state.market_state.segments.items():
            # Update growth rates with trend impacts
            base_growth = segment.growth_rate
            trend_impact = sum(
                trend.growth_impact * trend.strength
                for trend in game_state.market_state.active_trends
                if segment_name in trend.segment_impact
            )
            actual_growth = base_growth + trend_impact
            
            # Update segment size
            segment.size *= (1 + actual_growth)
            total_market += segment.size
            
            # Store historical data
            game_state.market_state.historical_segment_sizes[segment_name].append(segment.size)
            game_state.market_state.historical_segment_growth[segment_name].append(actual_growth)
            
            # Update profitability metrics
            revenue = game_state.company_state.revenue
            costs = game_state.company_state.costs
            if revenue > 0:
                profit_margin = (revenue - costs) / revenue
                game_state.market_state.segment_profitability[segment_name] = profit_margin
        
        # Normalize segment sizes
        for segment in game_state.market_state.segments.values():
            segment.size /= total_market
        
        # Update market concentration (HHI)
        market_shares = [
            competitor.market_share
            for competitor in game_state.market_state.competitors.values()
        ]
        market_shares.append(game_state.market_state.player_market_share)
        game_state.market_state.market_concentration = sum(
            share * share for share in market_shares
        )
        
        # Update consumer sentiment
        sentiment_factors = [
            game_state.external_state.economic_cycle_position,
            game_state.external_state.consumer_confidence,
            -abs(game_state.external_state.inflation_rate)
        ]
        
        # Add trend impact on sentiment
        trend_sentiment_impact = sum(
            trend.strength * (-0.1 if trend.name == "economic_uncertainty" else 0.05)
            for trend in game_state.market_state.active_trends
        )
        sentiment_factors.append(trend_sentiment_impact)
        
        # Calculate raw sentiment
        raw_sentiment = sum(sentiment_factors) / len(sentiment_factors)
        
        # Initialize historical_consumer_sentiment if not present
        if not hasattr(game_state.market_state, 'historical_consumer_sentiment'):
            game_state.market_state.historical_consumer_sentiment = []
            
        # Apply smoothing using historical sentiment if available
        if game_state.market_state.historical_consumer_sentiment:
            previous_sentiment = game_state.market_state.historical_consumer_sentiment[-1]
            smoothed_sentiment = previous_sentiment * 0.7 + raw_sentiment * 0.3
        else:
            smoothed_sentiment = raw_sentiment
        
        # Bound sentiment between 0.5 and 1.5
        game_state.market_state.consumer_sentiment = max(0.5, min(1.5, smoothed_sentiment))
        game_state.market_state.historical_consumer_sentiment.append(game_state.market_state.consumer_sentiment)

    @staticmethod
    def _calculate_segment_demand(
        game_state: GameState,
        segment: MarketSegment,
        price: float,
        marketing_allocation: float
    ) -> float:
        """Calculate demand for a specific market segment."""
        # Base demand from segment size
        base_demand = game_state.market_state.market_size * segment.size
        
        # Price elasticity effect
        relative_price = price / game_state.market_state.competitor_price
        price_effect = math.pow(
            relative_price,
            -game_state.market_state.price_elasticity * segment.price_sensitivity
        )
        
        # Quality effect
        quality_effect = math.pow(
            game_state.company_state.product_quality,
            game_state.market_state.quality_elasticity * segment.quality_sensitivity
        )
        
        # Marketing effect
        marketing_effect = math.pow(
            1 + marketing_allocation,
            game_state.market_state.marketing_elasticity * segment.brand_sensitivity
        )
        
        # Seasonal effect
        current_quarter = (game_state.metadata.current_quarter - 1) % 4 + 1
        seasonal_factor = segment.seasonal_factors.get(current_quarter, 1.0)
        
        # Trend effect
        trend_effect = 1.0
        for trend in game_state.market_state.active_trends:
            if segment.name in trend.segment_impact:
                trend_effect *= (1 + trend.segment_impact[segment.name] * trend.strength)
        
        # Calculate final demand
        segment_demand = (
            base_demand *
            price_effect *
            quality_effect *
            marketing_effect *
            seasonal_factor *
            trend_effect
        )
        
        return max(0, segment_demand)

    @staticmethod
    def _process_market_trends(game_state: GameState) -> None:
        """Process active market trends and their impacts."""
        # Update existing trends
        for trend in game_state.market_state.active_trends:
            trend.quarters_active += 1
            
            # Apply trend impacts
            for segment_name, impact in trend.segment_impact.items():
                if segment_name in game_state.market_state.segments:
                    segment = game_state.market_state.segments[segment_name]
                    segment.growth_rate *= (1 + impact * trend.strength)
            
            # Apply preference shifts
            for preference, shift in trend.preference_shifts.items():
                for segment in game_state.market_state.segments.values():
                    if hasattr(segment, preference):
                        current_value = getattr(segment, preference)
                        setattr(segment, preference, current_value * (1 + shift * trend.strength))
            
            # Update market growth
            game_state.market_state.market_growth += trend.growth_impact * trend.strength
            
            # Remove expired trends
            if trend.quarters_active >= trend.duration:
                game_state.market_state.active_trends.remove(trend)
        
        # Potentially introduce new trends
        if random.random() < 0.1:  # 10% chance each quarter
            available_trends = set(GameSimulation.MARKET_TRENDS.keys())
            active_trend_names = {t.name for t in game_state.market_state.active_trends}
            potential_trends = available_trends - active_trend_names
            
            if potential_trends:
                new_trend_name = random.choice(list(potential_trends))
                trend_data = GameSimulation.MARKET_TRENDS[new_trend_name]
                
                new_trend = MarketTrend(
                    name=new_trend_name,
                    strength=random.uniform(0.5, 1.0),
                    duration=random.randint(4, 8),
                    segment_impact=trend_data["segment_impact"],
                    preference_shifts=trend_data["preference_shifts"],
                    growth_impact=trend_data["growth_impact"]
                )
                
                game_state.market_state.active_trends.append(new_trend)

    @staticmethod
    def _process_product_strategy(game_state: GameState, strategy: ProductStrategy) -> None:
        """Process product strategy decisions."""
        # Adjust product quality based on positioning
        positioning_factors = {
            "value": 0.8,
            "balanced": 1.0,
            "premium": 1.2
        }
        quality_adjustment = positioning_factors[strategy.positioning]
        game_state.company_state.product_quality *= quality_adjustment
        
        # Apply innovation effects
        if strategy.innovation_level > 1.0:
            innovation_boost = (strategy.innovation_level - 1.0) * 0.1
            game_state.company_state.product_quality *= (1 + innovation_boost)
            game_state.company_state.r_and_d_level *= (1 + innovation_boost * 0.5)
        
        # Update marketing effectiveness based on targeting
        target_effectiveness = sum(
            segment.size * segment.purchasing_power
            for segment_name, segment in game_state.market_state.segments.items()
            if segment_name in strategy.target_segments
        )
        game_state.company_state.marketing_effectiveness *= (1 + target_effectiveness * 0.1)

    @staticmethod
    def _process_marketing_decision(game_state: GameState, marketing_decision) -> float:
        """
        Process marketing decisions and calculate their effect on demand.
        
        Args:
            game_state: Current game state
            marketing_decision: Player's marketing decisions
            
        Returns:
            Marketing multiplier effect on demand
        """
        # Calculate base marketing effectiveness
        # Marketing budget as percentage of revenue
        revenue = max(1.0, game_state.company_state.revenue)  # Avoid division by zero
        marketing_intensity = marketing_decision.budget / revenue
        
        # Diminishing returns on marketing spending
        base_multiplier = 1.0 + (math.log1p(marketing_intensity) * game_state.market_state.marketing_elasticity)
        
        # Apply channel mix effectiveness
        channel_effectiveness = {
            "traditional": 1.0,
            "digital": 1.2,  # Digital slightly more effective
            "direct": 1.1    # Direct marketing moderately effective
        }
        channel_multiplier = sum(
            mix * channel_effectiveness[channel]
            for channel, mix in marketing_decision.channel_mix.items()
        )
        
        # Apply campaign focus effects
        focus_multipliers = {
            "brand_building": 1.2,    # Long-term brand value
            "sales_activation": 1.3,   # Short-term sales boost
            "product_launch": 1.1      # New product introduction
        }
        focus_multiplier = focus_multipliers.get(marketing_decision.campaign_focus, 1.0)
        
        # Calculate total effectiveness
        total_multiplier = base_multiplier * channel_multiplier * focus_multiplier
        
        # Effectiveness decays over time but builds up with consistent spending
        current_effectiveness = game_state.company_state.marketing_effectiveness
        new_effectiveness = (current_effectiveness * 0.7) + (total_multiplier * 0.3)
        
        return new_effectiveness

    @staticmethod
    def _process_r_and_d_decision(game_state: GameState, r_and_d_decision) -> None:
        """
        Process R&D decisions and update product quality and efficiency.
        
        Args:
            game_state: Current game state
            r_and_d_decision: Player's R&D decisions
        """
        # Calculate R&D intensity
        revenue = max(1.0, game_state.company_state.revenue)  # Avoid division by zero
        r_and_d_intensity = r_and_d_decision.budget / revenue
        
        # Base improvement from R&D spending
        base_improvement = math.log1p(r_and_d_intensity) * 0.1  # Diminishing returns
        
        # Apply focus effects
        focus_multipliers = {
            "cost_reduction": {
                "quality": 0.5,
                "efficiency": 1.5
            },
            "quality_improvement": {
                "quality": 1.5,
                "efficiency": 0.5
            },
            "innovation": {
                "quality": 1.2,
                "efficiency": 1.0
            },
            "balanced": {
                "quality": 1.0,
                "efficiency": 1.0
            }
        }
        
        focus = r_and_d_decision.focus
        multipliers = focus_multipliers.get(focus, focus_multipliers["balanced"])
        
        # Update product quality
        quality_improvement = base_improvement * multipliers["quality"]
        game_state.company_state.product_quality *= (1 + quality_improvement)
        
        # Update R&D level (affects production efficiency)
        efficiency_improvement = base_improvement * multipliers["efficiency"]
        game_state.company_state.r_and_d_level *= (1 + efficiency_improvement)
        
        # Cap improvements
        game_state.company_state.product_quality = min(3.0, game_state.company_state.product_quality)
        game_state.company_state.r_and_d_level = min(2.0, game_state.company_state.r_and_d_level)

    @staticmethod
    def _process_capacity_decision(game_state: GameState, capacity_decision) -> float:
        """
        Process capacity expansion decision and calculate costs.
        
        Args:
            game_state: Current game state
            capacity_decision: Player's capacity expansion decision
            
        Returns:
            Cost of capacity expansion
        """
        expansion_size = capacity_decision.expansion
        
        # Calculate cost with economies of scale
        # Larger expansions get a discount based on EXPANSION_SCALE_FACTOR
        base_cost = expansion_size * GameSimulation.BASE_CAPACITY_COST
        actual_cost = base_cost * math.pow(expansion_size / 1000, -GameSimulation.EXPANSION_SCALE_FACTOR)
        
        # Add the expansion to pending expansions list
        if not hasattr(game_state.company_state, 'pending_expansions'):
            game_state.company_state.pending_expansions = []
        
        game_state.company_state.pending_expansions.append({
            'size': expansion_size,
            'quarters_remaining': GameSimulation.CAPACITY_LEAD_TIME
        })
        
        # Update assets to reflect the investment
        game_state.company_state.assets += actual_cost
        
        return actual_cost

    @staticmethod
    def _update_capacity_expansions(game_state: GameState) -> None:
        """
        Update pending capacity expansions and add completed ones to total capacity.
        
        Args:
            game_state: Current game state
        """
        if not hasattr(game_state.company_state, 'pending_expansions'):
            game_state.company_state.pending_expansions = []
        
        # Process each pending expansion
        completed_expansions = []
        remaining_expansions = []
        
        for expansion in game_state.company_state.pending_expansions:
            expansion['quarters_remaining'] -= 1
            
            if expansion['quarters_remaining'] <= 0:
                # Add the capacity
                game_state.company_state.capacity += expansion['size']
                completed_expansions.append(expansion)
            else:
                remaining_expansions.append(expansion)
        
        # Update pending expansions list
        game_state.company_state.pending_expansions = remaining_expansions 

    @staticmethod
    def _process_supply_chain_decision(game_state: GameState, supply_chain_decision) -> float:
        """
        Process supply chain decisions and calculate their effect on costs and efficiency.
        """
        # Initialize supply chain metrics if they don't exist
        if not hasattr(game_state.company_state, 'supply_chain_efficiency'):
            game_state.company_state.supply_chain_efficiency = 1.0
        if not hasattr(game_state.company_state, 'supplier_relationship'):
            game_state.company_state.supplier_relationship = 1.0
        if not hasattr(game_state.company_state, 'supplier_lead_time'):
            game_state.company_state.supplier_lead_time = 2.0
        if not hasattr(game_state.company_state, 'active_disruptions'):
            game_state.company_state.active_disruptions = []
        
        # Process active disruptions and remove expired ones
        active_disruptions = []
        for disruption in game_state.company_state.active_disruptions:
            disruption['quarters_remaining'] -= 1
            if disruption['quarters_remaining'] > 0:
                active_disruptions.append(disruption)
        game_state.company_state.active_disruptions = active_disruptions
        
        # Check for new disruptions
        for disruption_type, params in GameSimulation.DISRUPTION_TYPES.items():
            # Higher supplier relationship reduces disruption probability
            adjusted_probability = params['probability'] / game_state.company_state.supplier_relationship
            
            if random.random() < adjusted_probability:
                # Create new disruption
                new_disruption = {
                    'type': disruption_type,
                    'impact': params['impact'],
                    'quarters_remaining': params['duration'],
                    'description': GameSimulation._get_disruption_description(disruption_type)
                }
                game_state.company_state.active_disruptions.append(new_disruption)
        
        # Calculate combined impact of active disruptions
        lead_time_impact = 1.0
        efficiency_impact = 1.0
        relationship_impact = 1.0
        
        for disruption in game_state.company_state.active_disruptions:
            lead_time_impact *= disruption['impact']['lead_time']
            efficiency_impact *= disruption['impact']['efficiency']
            relationship_impact *= disruption['impact']['relationship']
        
        # Rest of the existing supply chain processing logic
        investment_intensity = supply_chain_decision.investment / game_state.company_state.revenue
        base_improvement = math.log1p(investment_intensity) * 0.2
        
        focus_multipliers = {
            "efficiency": (1.5, 0.5, 0.7),
            "relationship": (0.5, 1.5, 0.7),
            "lead_time": (0.7, 0.7, 1.5),
            "balanced": (1.0, 1.0, 1.0)
        }
        
        efficiency_mult, relationship_mult, lead_time_mult = focus_multipliers[supply_chain_decision.focus]
        
        # Update metrics with disruption impacts
        current_efficiency = game_state.company_state.supply_chain_efficiency
        efficiency_gain = base_improvement * efficiency_mult * efficiency_impact
        new_efficiency = min(
            current_efficiency * (1 + efficiency_gain),
            GameSimulation.SUPPLY_CHAIN_EFFICIENCY_CAP
        )
        game_state.company_state.supply_chain_efficiency = new_efficiency
        
        current_relationship = game_state.company_state.supplier_relationship
        relationship_gain = base_improvement * relationship_mult * relationship_impact
        new_relationship = current_relationship * (1 - GameSimulation.SUPPLIER_RELATIONSHIP_DECAY)
        new_relationship = min(new_relationship + relationship_gain, 2.0)
        game_state.company_state.supplier_relationship = new_relationship
        
        current_lead_time = game_state.company_state.supplier_lead_time
        lead_time_improvement = base_improvement * lead_time_mult / lead_time_impact
        new_lead_time = max(
            current_lead_time * (1 - lead_time_improvement),
            GameSimulation.SUPPLIER_LEAD_TIME_MIN
        )
        game_state.company_state.supplier_lead_time = new_lead_time
        
        # Calculate inventory holding costs with disruption impacts
        inventory_cost = (
            game_state.company_state.inventory * 
            GameSimulation.BASE_INVENTORY_COST / 
            (game_state.company_state.supply_chain_efficiency * efficiency_impact)
        )
        
        return supply_chain_decision.investment + inventory_cost

    @staticmethod
    def _get_disruption_description(disruption_type: str) -> str:
        """
        Get a human-readable description of a supply chain disruption.
        """
        descriptions = {
            "supplier_bankruptcy": "A key supplier has declared bankruptcy, causing significant supply chain disruptions.",
            "natural_disaster": "A natural disaster has affected multiple suppliers and logistics routes.",
            "logistics_disruption": "Major logistics disruption due to transportation infrastructure issues."
        }
        return descriptions.get(disruption_type, "Unknown supply chain disruption")

    @staticmethod
    def forecast_supply_chain_metrics(game_state: GameState, quarters_ahead: int = 4) -> Dict[str, List[float]]:
        """
        Forecast supply chain metrics for future quarters.
        
        Args:
            game_state: Current game state
            quarters_ahead: Number of quarters to forecast
            
        Returns:
            Dictionary containing forecasted metrics
        """
        forecasts = {
            'efficiency': [],
            'lead_time': [],
            'disruption_probability': [],
            'inventory_costs': [],
            'competitor_efficiency': []
        }
        
        # Get current metrics
        current_efficiency = getattr(game_state.company_state, 'supply_chain_efficiency', 1.0)
        current_lead_time = getattr(game_state.company_state, 'supplier_lead_time', 2.0)
        current_relationship = getattr(game_state.company_state, 'supplier_relationship', 1.0)
        
        # Calculate base disruption probability
        base_disruption_prob = sum(
            params['probability'] 
            for params in GameSimulation.DISRUPTION_TYPES.values()
        )
        
        # Project metrics for each quarter
        for quarter in range(quarters_ahead):
            # Efficiency naturally decays without investment
            projected_efficiency = max(
                1.0,
                current_efficiency * math.pow(0.95, quarter)  # 5% quarterly decay
            )
            forecasts['efficiency'].append(projected_efficiency)
            
            # Lead time gradually returns to baseline
            projected_lead_time = current_lead_time + (2.0 - current_lead_time) * (1 - math.pow(0.8, quarter))
            forecasts['lead_time'].append(projected_lead_time)
            
            # Relationship decays over time
            projected_relationship = max(
                1.0,
                current_relationship * math.pow(1 - GameSimulation.SUPPLIER_RELATIONSHIP_DECAY, quarter)
            )
            
            # Calculate disruption probability based on relationship
            quarter_disruption_prob = base_disruption_prob / projected_relationship
            forecasts['disruption_probability'].append(quarter_disruption_prob)
            
            # Project inventory costs
            base_inventory_cost = (
                game_state.company_state.inventory * 
                GameSimulation.BASE_INVENTORY_COST / 
                projected_efficiency
            )
            # Add uncertainty factor
            uncertainty_factor = 1.0 + (quarter * 0.1)  # 10% more uncertainty each quarter
            projected_inventory_cost = base_inventory_cost * uncertainty_factor
            forecasts['inventory_costs'].append(projected_inventory_cost)
            
            # Project competitor efficiency
            current_competitor_efficiency = getattr(
                game_state.market_state,
                'competitor_supply_chain_efficiency',
                1.0
            )
            efficiency_gap = current_efficiency - current_competitor_efficiency
            if efficiency_gap > 0:
                # Competitor tries to catch up
                catch_up_rate = min(0.1, abs(efficiency_gap) * 0.2)
                projected_competitor_efficiency = min(
                    GameSimulation.SUPPLY_CHAIN_EFFICIENCY_CAP,
                    current_competitor_efficiency * (1 + catch_up_rate) ** quarter
                )
            else:
                # Competitor maintains advantage
                projected_competitor_efficiency = current_competitor_efficiency
            
            forecasts['competitor_efficiency'].append(projected_competitor_efficiency)
        
        return forecasts
    
    @staticmethod
    def calculate_optimal_investment(game_state: GameState, target_efficiency: float) -> Dict[str, float]:
        """
        Calculate optimal supply chain investment to reach target efficiency.
        
        Args:
            game_state: Current game state
            target_efficiency: Desired efficiency level
            
        Returns:
            Dictionary with investment recommendations
        """
        current_efficiency = getattr(game_state.company_state, 'supply_chain_efficiency', 1.0)
        current_revenue = game_state.company_state.revenue
        
        if target_efficiency <= current_efficiency:
            return {
                'recommended_investment': 0.0,
                'quarters_to_target': 0,
                'roi_estimate': 0.0
            }
        
        # Calculate required improvement
        required_improvement = target_efficiency / current_efficiency - 1
        
        # Estimate investment needed based on diminishing returns formula
        # Investment = Revenue * ln(1 + required_improvement/0.2)
        base_investment = current_revenue * math.log1p(required_improvement / 0.2)
        
        # Adjust for current relationship status
        relationship_factor = 1.0 / getattr(game_state.company_state, 'supplier_relationship', 1.0)
        recommended_investment = base_investment * relationship_factor
        
        # Estimate quarters needed
        quarters_to_target = math.ceil(required_improvement / (0.2 * relationship_factor))
        
        # Estimate ROI
        efficiency_gain = target_efficiency - current_efficiency
        annual_inventory_cost = (
            game_state.company_state.inventory * 
            GameSimulation.BASE_INVENTORY_COST * 
            4  # quarters per year
        )
        annual_savings = annual_inventory_cost * (1 - current_efficiency/target_efficiency)
        roi_estimate = (annual_savings / recommended_investment - 1) * 100
        
        return {
            'recommended_investment': recommended_investment,
            'quarters_to_target': quarters_to_target,
            'roi_estimate': roi_estimate
        }
    
    @staticmethod
    def analyze_disruption_risk(game_state: GameState) -> Dict[str, Any]:
        """
        Analyze supply chain disruption risks and potential impacts.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary containing risk analysis
        """
        current_relationship = getattr(game_state.company_state, 'supplier_relationship', 1.0)
        current_efficiency = getattr(game_state.company_state, 'supply_chain_efficiency', 1.0)
        
        # Calculate base risk scores
        risk_scores = {}
        total_probability = 0
        
        for disruption_type, params in GameSimulation.DISRUPTION_TYPES.items():
            # Adjust probability based on supplier relationship
            adjusted_prob = params['probability'] / current_relationship
            total_probability += adjusted_prob
            
            # Calculate potential impact
            impact_severity = (
                params['impact']['lead_time'] * 0.3 +  # 30% weight
                params['impact']['efficiency'] * 0.4 +  # 40% weight
                params['impact']['relationship'] * 0.3  # 30% weight
            )
            
            # Calculate financial impact
            inventory_impact = (
                game_state.company_state.inventory * 
                GameSimulation.BASE_INVENTORY_COST * 
                (1/params['impact']['efficiency'] - 1/current_efficiency)
            )
            
            lead_time_impact = (
                params['impact']['lead_time'] - 1
            ) * game_state.company_state.supplier_lead_time
            
            risk_scores[disruption_type] = {
                'probability': adjusted_prob,
                'impact_severity': impact_severity,
                'duration': params['duration'],
                'financial_impact': inventory_impact * params['duration'],
                'lead_time_impact': lead_time_impact,
                'risk_score': adjusted_prob * impact_severity
            }
        
        # Calculate risk mitigation recommendations
        current_inventory_cost = (
            game_state.company_state.inventory * 
            GameSimulation.BASE_INVENTORY_COST / 
            current_efficiency
        )
        
        buffer_recommendation = math.sqrt(total_probability) * current_inventory_cost * 2
        relationship_investment = max(0, (1.5 - current_relationship) * current_inventory_cost)
        
        return {
            'risk_scores': risk_scores,
            'total_risk_probability': total_probability,
            'recommendations': {
                'safety_buffer': buffer_recommendation,
                'relationship_investment': relationship_investment,
                'suggested_focus': 'relationship' if current_relationship < 1.2 else 'efficiency'
            }
        }

    @staticmethod
    def _process_financial_decision(game_state: GameState, financial_decision) -> float:
        """
        Process financial decisions including loans, investments, and dividends.
        Returns the net cash impact of the decisions.
        """
        total_cash_impact = 0.0
        
        # Initialize financial metrics if they don't exist
        if not hasattr(game_state.company_state, 'loans'):
            game_state.company_state.loans = []
        if not hasattr(game_state.company_state, 'investments'):
            game_state.company_state.investments = []
        if not hasattr(game_state.company_state, 'total_debt'):
            game_state.company_state.total_debt = 0.0
        if not hasattr(game_state.company_state, 'dividend_history'):
            game_state.company_state.dividend_history = []
            
        # Process loan decisions
        if financial_decision.loan_request:
            loan_amount = financial_decision.loan_request.amount
            loan_term = financial_decision.loan_request.term
            
            # Calculate debt-to-equity ratio
            equity = game_state.company_state.assets - game_state.company_state.total_debt
            new_debt_ratio = (game_state.company_state.total_debt + loan_amount) / max(equity, 1.0)
            
            if new_debt_ratio <= GameSimulation.MAX_DEBT_TO_EQUITY_RATIO:
                # Calculate interest rate based on company health and market conditions
                base_rate = game_state.external_state.interest_rate
                company_risk = 1.0 - min(1.0, equity / game_state.company_state.assets)
                loan_rate = base_rate + GameSimulation.LOAN_INTEREST_SPREAD + (company_risk * 0.02)
                
                # Add loan to company state
                game_state.company_state.loans.append({
                    'amount': loan_amount,
                    'term': loan_term,
                    'rate': loan_rate,
                    'quarters_remaining': loan_term,
                    'quarterly_payment': (loan_amount * (1 + loan_rate) ** loan_term) / loan_term
                })
                
                game_state.company_state.total_debt += loan_amount
                total_cash_impact += loan_amount
        
        # Process investment decisions
        if financial_decision.investment:
            inv_type = financial_decision.investment.type
            inv_amount = financial_decision.investment.amount
            inv_term = financial_decision.investment.term
            
            if inv_type in GameSimulation.INVESTMENT_TYPES:
                inv_params = GameSimulation.INVESTMENT_TYPES[inv_type]
                
                # Validate investment term
                if (inv_params['min_term'] <= inv_term and 
                    (inv_params['max_term'] is None or inv_term <= inv_params['max_term'])):
                    
                    # Calculate expected return with some randomness
                    base_return = inv_params['base_return']
                    risk_factor = inv_params['risk_factor']
                    market_condition = 1.0 + (random.random() - 0.5) * risk_factor
                    expected_return = base_return * market_condition
                    
                    # Add investment to portfolio
                    game_state.company_state.investments.append({
                        'type': inv_type,
                        'amount': inv_amount,
                        'term': inv_term,
                        'quarters_remaining': inv_term,
                        'expected_return': expected_return,
                        'total_return': inv_amount * (1 + expected_return) ** inv_term
                    })
                    
                    total_cash_impact -= inv_amount
        
        # Process dividend decisions
        if financial_decision.dividend:
            dividend_amount = financial_decision.dividend.amount
            
            # Calculate maximum safe dividend
            max_dividend = min(
                game_state.company_state.cash * 0.5,  # Don't use more than 50% of cash
                max(0, game_state.company_state.profit)  # Don't pay more than profits
            )
            
            # Adjust dividend if it exceeds safe amount
            actual_dividend = min(dividend_amount, max_dividend)
            
            if actual_dividend > 0:
                # Apply dividend tax
                tax = actual_dividend * GameSimulation.DIVIDEND_TAX_RATE
                total_cash_impact -= (actual_dividend + tax)
                
                # Record dividend payment
                game_state.company_state.dividend_history.append({
                    'amount': actual_dividend,
                    'tax': tax,
                    'quarter': game_state.metadata.current_quarter
                })
        
        return total_cash_impact

    @staticmethod
    def _update_financial_state(game_state: GameState) -> None:
        """
        Update financial state including loans, investments, and calculate returns.
        """
        if not hasattr(game_state.company_state, 'loans'):
            return
            
        # Process loan payments
        loan_payments = 0.0
        remaining_loans = []
        
        for loan in game_state.company_state.loans:
            # Make quarterly payment
            loan_payments += loan['quarterly_payment']
            loan['quarters_remaining'] -= 1
            
            if loan['quarters_remaining'] > 0:
                remaining_loans.append(loan)
            else:
                game_state.company_state.total_debt -= loan['amount']
                
        game_state.company_state.loans = remaining_loans
        game_state.company_state.cash -= loan_payments
        
        # Process investment returns
        investment_returns = 0.0
        remaining_investments = []
        
        for inv in game_state.company_state.investments:
            inv['quarters_remaining'] -= 1
            
            if inv['quarters_remaining'] > 0:
                remaining_investments.append(inv)
            else:
                # Investment matured, calculate final return
                investment_returns += inv['total_return'] - inv['amount']
                
        game_state.company_state.investments = remaining_investments
        game_state.company_state.cash += investment_returns 

    @staticmethod
    def _process_hr_decision(game_state: GameState, hr_decision) -> float:
        """
        Process HR decisions including hiring, training, and salary adjustments.
        Returns the total cost of HR decisions.
        """
        total_cost = 0.0
        
        # Process hiring decisions
        if hr_decision.hiring:
            hiring_cost = GameSimulation._process_hiring(game_state, hr_decision.hiring)
            total_cost += hiring_cost
        
        # Process training programs
        if hr_decision.training:
            training_cost = GameSimulation._process_training(game_state, hr_decision.training)
            total_cost += training_cost
        
        # Process salary adjustments
        if hr_decision.salary_adjustments:
            salary_cost = GameSimulation._process_salary_adjustments(game_state, hr_decision.salary_adjustments)
            total_cost += salary_cost
        
        # Update employee metrics
        GameSimulation._update_employee_metrics(game_state)
        
        return total_cost

    @staticmethod
    def _process_hiring(game_state: GameState, hiring_decision: HiringDecision) -> float:
        """Process hiring decisions and calculate costs."""
        department = hiring_decision.department
        count = hiring_decision.count
        skill_req = hiring_decision.skill_requirement
        salary_budget = hiring_decision.salary_budget
        
        # Calculate hiring cost
        hiring_cost = count * salary_budget * GameSimulation.HIRING_COST_MULTIPLIER
        
        # Generate new employees
        for _ in range(count):
            # Random variation in initial metrics
            initial_skill = max(1.0, skill_req * (0.9 + random.random() * 0.2))
            initial_satisfaction = 0.8 + random.random() * 0.4
            
            new_employee = Employee(
                skill_level=initial_skill,
                experience=0.0,
                productivity=initial_skill,
                satisfaction=initial_satisfaction,
                salary=salary_budget,
                department=department,
                training_history=[]
            )
            
            game_state.company_state.employees[department].append(new_employee)
        
        # Update total salary cost
        game_state.company_state.total_salary_cost += (count * salary_budget) / 1000  # Convert to millions
        
        return hiring_cost

    @staticmethod
    def _process_training(game_state: GameState, training: TrainingProgram) -> float:
        """Process training programs and update employee metrics."""
        budget = training.budget
        focus = training.focus
        departments = training.departments
        
        # Calculate per-employee training investment
        total_employees = sum(len(game_state.company_state.employees[dept]) for dept in departments)
        if total_employees == 0:
            return 0.0
            
        investment_per_employee = budget / total_employees
        
        # Apply training effects
        for department in departments:
            for employee in game_state.company_state.employees[department]:
                # Calculate training effectiveness
                base_effect = math.log1p(investment_per_employee) * 0.2
                
                # Apply focus-specific improvements
                if focus == "skills":
                    employee.skill_level *= (1 + base_effect)
                    employee.productivity *= (1 + base_effect * 0.5)
                elif focus == "productivity":
                    employee.productivity *= (1 + base_effect)
                elif focus == "satisfaction":
                    employee.satisfaction = min(2.0, employee.satisfaction * (1 + base_effect))
                
                # Record training
                employee.training_history.append({
                    "focus": focus,
                    "investment": investment_per_employee,
                    "quarter": game_state.metadata.current_quarter
                })
        
        # Update company training effectiveness
        current_effectiveness = game_state.company_state.training_effectiveness
        new_effectiveness = current_effectiveness * (1 + math.log1p(budget) * 0.1)
        game_state.company_state.training_effectiveness = min(
            GameSimulation.TRAINING_EFFECTIVENESS_CAP,
            new_effectiveness
        )
        
        return budget

    @staticmethod
    def _process_salary_adjustments(game_state: GameState, adjustments: Dict[str, float]) -> float:
        """Process salary adjustments and calculate additional costs."""
        total_cost = 0.0
        
        for department, percentage in adjustments.items():
            if department in game_state.company_state.employees:
                for employee in game_state.company_state.employees[department]:
                    old_salary = employee.salary
                    new_salary = old_salary * (1 + percentage / 100)
                    salary_increase = new_salary - old_salary
                    
                    # Update employee salary and satisfaction
                    employee.salary = new_salary
                    satisfaction_boost = (percentage / 100) * GameSimulation.SATISFACTION_IMPACT["salary"]
                    employee.satisfaction = min(2.0, employee.satisfaction * (1 + satisfaction_boost))
                    
                    # Add to total cost (converting thousands to millions)
                    total_cost += salary_increase / 1000
                    
                    # Update company's total salary cost
                    game_state.company_state.total_salary_cost += salary_increase / 1000
        
        return total_cost

    @staticmethod
    def _update_employee_metrics(game_state: GameState) -> None:
        """Update employee metrics including experience, turnover, and department impacts."""
        for department, employees in game_state.company_state.employees.items():
            # Process each employee
            retained_employees = []
            for employee in employees:
                # Update experience and its effect on productivity
                employee.experience += GameSimulation.EXPERIENCE_GAIN
                experience_boost = math.log1p(employee.experience) * 0.1
                employee.productivity = employee.skill_level * (1 + experience_boost)
                
                # Check for turnover
                if (employee.satisfaction < GameSimulation.TURNOVER_THRESHOLD and 
                    random.random() < (GameSimulation.TURNOVER_THRESHOLD - employee.satisfaction)):
                    # Employee leaves
                    game_state.company_state.total_salary_cost -= employee.salary / 1000
                    continue
                    
                retained_employees.append(employee)
            
            # Update department employee list
            game_state.company_state.employees[department] = retained_employees
        
        # Calculate average metrics
        total_employees = sum(len(employees) for employees in game_state.company_state.employees.values())
        if total_employees > 0:
            avg_productivity = sum(
                sum(e.productivity for e in employees)
                for employees in game_state.company_state.employees.values()
            ) / total_employees
            
            avg_satisfaction = sum(
                sum(e.satisfaction for e in employees)
                for employees in game_state.company_state.employees.values()
            ) / total_employees
            
            # Update company state
            game_state.company_state.avg_productivity = avg_productivity
            game_state.company_state.avg_satisfaction = avg_satisfaction
            
            # Calculate turnover rate
            previous_total = total_employees + len([
                e for employees in game_state.company_state.employees.values()
                for e in employees if e.satisfaction < GameSimulation.TURNOVER_THRESHOLD
            ])
            turnover_rate = (previous_total - total_employees) / previous_total if previous_total > 0 else 0.0
            
            # Update historical data
            game_state.company_state.historical_productivity.append(avg_productivity)
            game_state.company_state.historical_satisfaction.append(avg_satisfaction)
            game_state.company_state.historical_turnover.append(turnover_rate)
        
        # Apply department-specific impacts
        GameSimulation._apply_department_impacts(game_state)

    @staticmethod
    def _apply_department_impacts(game_state: GameState) -> None:
        """Apply department-specific productivity impacts to company metrics."""
        for department, impacts in GameSimulation.DEPARTMENT_IMPACTS.items():
            if department not in game_state.company_state.employees:
                continue
                
            # Calculate department effectiveness
            dept_employees = game_state.company_state.employees[department]
            if not dept_employees:
                continue
                
            avg_dept_productivity = sum(e.productivity for e in dept_employees) / len(dept_employees)
            
            # Apply impacts based on department
            if department == "production":
                # Production impacts capacity utilization and quality
                game_state.company_state.capacity *= (1 + (avg_dept_productivity - 1) * impacts["capacity_utilization"])
                game_state.company_state.product_quality *= (1 + (avg_dept_productivity - 1) * impacts["quality"])
                
            elif department == "rd":
                # R&D impacts innovation rate and quality
                game_state.company_state.r_and_d_level *= (1 + (avg_dept_productivity - 1) * impacts["innovation"])
                game_state.company_state.product_quality *= (1 + (avg_dept_productivity - 1) * impacts["quality"])
                
            elif department == "marketing":
                # Marketing impacts effectiveness and market research
                game_state.company_state.marketing_effectiveness *= (1 + (avg_dept_productivity - 1) * impacts["effectiveness"])
                
            elif department == "supply_chain":
                # Supply chain impacts efficiency and supplier relationships
                if hasattr(game_state.company_state, 'supply_chain_efficiency'):
                    game_state.company_state.supply_chain_efficiency *= (1 + (avg_dept_productivity - 1) * impacts["efficiency"])
                if hasattr(game_state.company_state, 'supplier_relationship'):
                    game_state.company_state.supplier_relationship *= (1 + (avg_dept_productivity - 1) * impacts["relationship"])
                if hasattr(game_state.company_state, 'supplier_lead_time'):
                    lead_time_improvement = (avg_dept_productivity - 1) * impacts["lead_time"]
                    game_state.company_state.supplier_lead_time *= (1 - lead_time_improvement)
        
    @staticmethod
    def _process_international_decision(game_state: GameState, decision: InternationalDecision) -> float:
        """
        Process international operations decisions.
        Returns the total cost of international decisions.
        """
        total_cost = 0.0
        
        # Process market entry decision
        if decision.market_entry:
            entry_cost = GameSimulation._process_market_entry(game_state, decision.market_entry)
            total_cost += entry_cost
        
        # Process regional pricing decisions
        if decision.regional_pricing:
            for region_name, pricing in decision.regional_pricing.items():
                if region_name in game_state.company_state.regions:
                    GameSimulation._process_regional_pricing(
                        game_state,
                        region_name,
                        pricing
                    )
        
        # Process regional supply decisions
        if decision.regional_supply:
            supply_cost = 0.0
            for region_name, supply in decision.regional_supply.items():
                if region_name in game_state.company_state.regions:
                    cost = GameSimulation._process_regional_supply(
                        game_state,
                        region_name,
                        supply
                    )
                    supply_cost += cost
            total_cost += supply_cost
        
        # Process currency hedging
        if decision.currency_hedging:
            hedging_cost = GameSimulation._process_currency_hedging(
                game_state,
                decision.currency_hedging
            )
            total_cost += hedging_cost
        
        return total_cost

    @staticmethod
    def _process_market_entry(game_state: GameState, entry: MarketEntryDecision) -> float:
        """Process market entry decision and calculate costs."""
        region_name = entry.region_name
        if region_name not in game_state.market_state.regions:
            return 0.0
        
        region = game_state.market_state.regions[region_name]
        
        # Calculate entry cost based on mode and region characteristics
        base_cost = entry.initial_investment * GameSimulation.ENTRY_COSTS[entry.entry_mode]
        regulatory_cost = base_cost * (region.regulatory_rating - 1.0) * 0.5
        cultural_cost = base_cost * region.cultural_distance * 0.3
        total_cost = base_cost + regulatory_cost + cultural_cost
        
        # Initialize regional operation
        operation = RegionalOperation(
            region_name=region_name,
            market_share=0.0,
            sales_volume=0.0,
            revenue=0.0,
            costs=0.0,
            capacity=entry.capacity_allocation,
            inventory=0.0,
            supply_chain_efficiency=1.0,
            brand_strength=1.0,
            distribution_network=0.5
        )
        
        # Add partnerships if any
        if entry.local_partnerships:
            for partner in entry.local_partnerships:
                operation.local_partnerships.append({
                    "name": partner,
                    "strength": 1.0,
                    "contribution": {
                        "distribution": 0.2,
                        "market_knowledge": 0.3,
                        "supplier_network": 0.2
                    }
                })
        
        # Initialize historical data tracking
        game_state.company_state.historical_regional_revenue[region_name] = []
        game_state.company_state.historical_regional_market_share[region_name] = []
        game_state.company_state.historical_exchange_rates[region.currency] = [region.exchange_rate]
        
        # Add region to company operations
        game_state.company_state.regions[region_name] = operation
        
        return total_cost

    @staticmethod
    def _process_regional_pricing(game_state: GameState, region_name: str, pricing: RegionalPricingDecision) -> None:
        """Process regional pricing decision."""
        region = game_state.market_state.regions[region_name]
        operation = game_state.company_state.regions[region_name]
        
        # Calculate local market demand based on price sensitivity
        base_price = pricing.price / region.exchange_rate  # Convert to base currency
        price_effect = math.pow(
            base_price / game_state.market_state.competitor_price,
            -region.price_sensitivity
        )
        
        # Adjust for brand strength and quality
        brand_effect = math.pow(operation.brand_strength, region.brand_sensitivity)
        quality_effect = math.pow(
            game_state.company_state.product_quality,
            region.quality_sensitivity
        )
        
        # Calculate market share
        market_share = operation.market_share * price_effect * brand_effect * quality_effect
        market_share = max(0.05, min(0.8, market_share))  # Bound market share
        
        # Update operation metrics
        operation.market_share = market_share
        potential_sales = region.market_size * market_share
        actual_sales = min(potential_sales, operation.inventory + operation.capacity)
        operation.sales_volume = actual_sales
        operation.revenue = actual_sales * pricing.price  # In local currency
        
        # Process promotion budget
        if pricing.promotion_budget > 0:
            promotion_effect = math.log1p(pricing.promotion_budget) * 0.2
            operation.brand_strength *= (1 + promotion_effect)
            operation.brand_strength = min(2.0, operation.brand_strength)

    @staticmethod
    def _process_regional_supply(game_state: GameState, region_name: str, supply: RegionalSupplyDecision) -> float:
        """Process regional supply decision and calculate costs."""
        region = game_state.market_state.regions[region_name]
        operation = game_state.company_state.regions[region_name]
        
        total_cost = 0.0
        
        # Process local production
        if supply.production_volume > 0:
            production_cost = GameSimulation._calculate_production_cost(
                supply.production_volume,
                operation.capacity,
                game_state.company_state.r_and_d_level,
                operation.supply_chain_efficiency
            )
            production_cost *= region.labor_cost  # Adjust for local labor costs
            total_cost += production_cost
            operation.inventory += supply.production_volume
        
        # Process imports
        if supply.import_volume > 0:
            import_cost = supply.import_volume * GameSimulation.BASE_CAPACITY_COST
            import_cost *= (1 + region.tariff_rate)  # Apply tariffs
            import_cost *= region.logistics_cost  # Apply logistics costs
            total_cost += import_cost
            operation.inventory += supply.import_volume
        
        # Process exports
        if supply.export_volume > 0:
            export_cost = supply.export_volume * GameSimulation.BASE_CAPACITY_COST
            export_cost *= region.logistics_cost
            total_cost += export_cost
            operation.inventory -= supply.export_volume
        
        # Process supplier development
        if supply.supplier_development > 0:
            development_effect = math.log1p(supply.supplier_development) * 0.2
            operation.supply_chain_efficiency *= (1 + development_effect)
            operation.supply_chain_efficiency = min(
                GameSimulation.SUPPLY_CHAIN_EFFICIENCY_CAP,
                operation.supply_chain_efficiency
            )
            total_cost += supply.supplier_development
        
        return total_cost

    @staticmethod
    def _process_currency_hedging(game_state: GameState, hedging: Dict[str, float]) -> float:
        """Process currency hedging decisions and calculate costs."""
        total_cost = 0.0
        
        for currency, position in hedging.items():
            if currency not in game_state.company_state.currency_exposure:
                continue
                
            # Calculate hedging cost (simplified model)
            exposure = game_state.company_state.currency_exposure[currency]
            hedging_ratio = abs(position) / exposure if exposure > 0 else 0
            hedging_cost = exposure * hedging_ratio * 0.01  # 1% hedging cost
            
            # Update currency exposure
            game_state.company_state.currency_exposure[currency] = exposure * (1 - hedging_ratio)
            
            total_cost += hedging_cost
        
        return total_cost

    @staticmethod
    def _update_international_operations(game_state: GameState) -> None:
        """Update international operations state."""
        if not game_state.market_state.regions:
            return
            
        # Update exchange rates
        for region_name, region in game_state.market_state.regions.items():
            # Simulate exchange rate movements
            volatility = game_state.metadata.config.currency_volatility
            rate_change = random.normalvariate(0, volatility)
            new_rate = region.exchange_rate * (1 + rate_change)
            region.exchange_rate = new_rate
            
            # Update historical rates
            game_state.company_state.historical_exchange_rates[region.currency].append(new_rate)
            
            # Update market size
            region.market_size *= (1 + region.market_growth)
        
        # Update regional operations
        for region_name, operation in game_state.company_state.regions.items():
            region = game_state.market_state.regions[region_name]
            
            # Update historical data
            game_state.company_state.historical_regional_revenue[region_name].append(
                operation.revenue * region.exchange_rate  # Convert to base currency
            )
            game_state.company_state.historical_regional_market_share[region_name].append(
                operation.market_share
            )
            
            # Update currency exposure
            game_state.company_state.currency_exposure[region.currency] = operation.revenue
            
            # Decay brand strength and distribution network
            operation.brand_strength *= 0.95  # 5% quarterly decay
            operation.distribution_network *= 0.98  # 2% quarterly decay
            
            # Update partnership benefits
            for partnership in operation.local_partnerships:
                partnership["strength"] *= 0.95  # 5% quarterly decay
                
                # Apply partnership benefits
                operation.distribution_network += (
                    partnership["strength"] * 
                    partnership["contribution"]["distribution"] * 
                    0.1
                )
                operation.supply_chain_efficiency += (
                    partnership["strength"] * 
                    partnership["contribution"]["supplier_network"] * 
                    0.1
                )
        
    @staticmethod
    def _calculate_stock_price(game_state: GameState) -> float:
        """
        Calculate the company's stock price based on various factors.
        
        Args:
            game_state: Current game state
            
        Returns:
            The calculated stock price
        """
        # Get key metrics
        revenue = game_state.company_state.revenue
        profit = game_state.company_state.profit
        assets = game_state.company_state.assets
        cash = game_state.company_state.cash
        market_share = game_state.market_state.player_market_share
        consumer_sentiment = getattr(game_state.market_state, 'consumer_sentiment', 1.0)
        
        # Calculate growth rates if historical data exists
        revenue_growth = 0.0
        profit_growth = 0.0
        if (hasattr(game_state.company_state, 'historical_revenue') and 
            len(game_state.company_state.historical_revenue) > 1):
            prev_revenue = game_state.company_state.historical_revenue[-1]
            if prev_revenue > 0:
                revenue_growth = (revenue - prev_revenue) / prev_revenue
                
        if (hasattr(game_state.company_state, 'historical_profit') and 
            len(game_state.company_state.historical_profit) > 1):
            prev_profit = game_state.company_state.historical_profit[-1]
            if prev_profit > 0:
                profit_growth = (profit - prev_profit) / prev_profit
        
        # Calculate base price using P/E ratio approach
        pe_ratio = 15.0
        if profit > 0:
            # Adjust P/E ratio based on growth and market conditions
            if revenue_growth > 0:
                pe_ratio *= (1 + revenue_growth * 2)  # Growth premium
            if profit_growth > 0:
                pe_ratio *= (1 + profit_growth)
        
        # Calculate base price
        base_price = profit * pe_ratio
        
        # Apply market sentiment effect
        sentiment_multiplier = consumer_sentiment
        
        # Apply market share premium/discount
        market_share_effect = 1.0
        if market_share > 0.5:
            market_share_effect = 1.2  # Premium for market leadership
        elif market_share < 0.2:
            market_share_effect = 0.8  # Discount for small market share
        
        # Apply balance sheet strength factor
        balance_sheet_strength = min(2.0, max(0.5, (cash / max(1.0, assets))))
        
        # Apply quality and innovation premium
        quality_premium = math.pow(game_state.company_state.product_quality, 0.5)
        innovation_premium = math.pow(getattr(game_state.company_state, 'r_and_d_level', 1.0), 0.3)
        
        # Calculate final stock price
        stock_price = (base_price * 
                      sentiment_multiplier * 
                      market_share_effect * 
                      balance_sheet_strength *
                      quality_premium *
                      innovation_premium)
        
        # Ensure minimum price and smooth changes
        min_price = 1.0
        if hasattr(game_state.company_state, 'historical_stock_price') and game_state.company_state.historical_stock_price:
            prev_price = game_state.company_state.historical_stock_price[-1]
            # Limit price change to 30% per quarter
            max_change = 0.3
            min_new_price = prev_price * (1 - max_change)
            max_new_price = prev_price * (1 + max_change)
            stock_price = max(min_new_price, min(max_new_price, stock_price))
        
        return max(min_price, stock_price)
