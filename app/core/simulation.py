"""
Core game simulation logic for the Business Game.
"""
import uuid
import math
from datetime import datetime
from typing import Tuple

from app.models.game import (
    GameState, CompanyState, MarketState, ExternalState, GameMetadata,
    PlayerAction, GameConfig
)


class GameSimulation:
    """
    Core game simulation logic.
    """
    
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
            historical_revenue=[],
            historical_profit=[],
            historical_stock_price=[]
        )
        
        # Initialize market state
        competitor_market_share = 1.0 - config.initial_player_market_share
        market_state = MarketState(
            market_size=config.initial_market_size,
            market_growth=0.02,  # 2% quarterly growth by default
            competitor_price=config.initial_competitor_price,
            competitor_market_share=competitor_market_share,
            player_market_share=config.initial_player_market_share,
            price_elasticity=config.price_elasticity
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
            stock_price=50.0  # Initial stock price
        )
        
        # Calculate initial stock price
        game_state.stock_price = GameSimulation._calculate_stock_price(game_state)
        
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
        
        # Calculate demand based on price elasticity
        demand = GameSimulation._calculate_demand(updated_state, price)
        
        # Calculate sales (limited by production + inventory)
        available_units = updated_state.company_state.inventory + production_volume
        sales_volume = min(demand, available_units)
        
        # Update inventory
        new_inventory = available_units - sales_volume
        
        # Calculate financial results
        revenue = sales_volume * price
        production_cost = GameSimulation._calculate_production_cost(production_volume, updated_state.company_state.capacity)
        operating_cost = GameSimulation._calculate_operating_cost(updated_state.company_state.assets)
        total_cost = production_cost + operating_cost
        
        # Calculate profit before tax
        profit_before_tax = revenue - total_cost
        
        # Apply tax
        tax = max(0, profit_before_tax * updated_state.external_state.tax_rate)
        profit_after_tax = profit_before_tax - tax
        
        # Update competitor behavior
        GameSimulation._update_competitor_behavior(updated_state, price)
        
        # Update market conditions
        GameSimulation._update_market_conditions(updated_state)
        
        # Update company state
        updated_state.company_state.cash += profit_after_tax
        updated_state.company_state.inventory = new_inventory
        updated_state.company_state.revenue = revenue
        updated_state.company_state.costs = total_cost
        updated_state.company_state.profit = profit_after_tax
        
        # Update historical data
        updated_state.company_state.historical_revenue.append(revenue)
        updated_state.company_state.historical_profit.append(profit_after_tax)
        
        # Calculate new stock price
        stock_price = GameSimulation._calculate_stock_price(updated_state)
        updated_state.stock_price = stock_price
        updated_state.company_state.historical_stock_price.append(stock_price)
        
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
        
        return demand
    
    @staticmethod
    def _calculate_production_cost(volume: float, capacity: float) -> float:
        """
        Calculate production cost based on volume and capacity.
        
        Args:
            volume: Production volume
            capacity: Production capacity
            
        Returns:
            The production cost
        """
        # Base cost per unit
        base_cost_per_unit = 50.0
        
        # Calculate capacity utilization
        utilization = volume / capacity
        
        # Apply economies of scale (lower cost at higher utilization)
        if utilization <= 0.7:
            # Normal production cost
            cost_multiplier = 1.0
        elif utilization <= 0.9:
            # Slight economies of scale
            cost_multiplier = 0.95
        else:
            # Overtime costs (higher cost when approaching capacity)
            cost_multiplier = 1.1
        
        # Calculate total production cost
        production_cost = volume * base_cost_per_unit * cost_multiplier
        
        # Convert to millions for consistency
        return production_cost / 1000000
    
    @staticmethod
    def _calculate_operating_cost(assets: float) -> float:
        """
        Calculate fixed operating costs based on assets.
        
        Args:
            assets: Company assets value
            
        Returns:
            The operating cost
        """
        # Operating costs as a percentage of assets
        operating_cost_rate = 0.05
        
        return assets * operating_cost_rate
    
    @staticmethod
    def _update_competitor_behavior(game_state: GameState, player_price: float) -> None:
        """
        Update competitor behavior based on player actions.
        
        Args:
            game_state: The current game state
            player_price: The player's price
        """
        # Simple competitor pricing strategy: adjust price based on player's price
        # with some randomness to make the game more interesting
        competitor_adjustment_factor = 0.2  # How quickly competitor responds
        
        # Calculate price difference
        price_difference = player_price - game_state.market_state.competitor_price
        
        # Adjust competitor price (with some lag)
        new_competitor_price = game_state.market_state.competitor_price + (price_difference * competitor_adjustment_factor)
        
        # Ensure competitor price doesn't go too low
        new_competitor_price = max(70.0, new_competitor_price)
        
        # Update competitor price
        game_state.market_state.competitor_price = new_competitor_price
        
        # Update market shares
        player_share = game_state.market_state.player_market_share
        competitor_share = 1.0 - player_share
        
        game_state.market_state.competitor_market_share = competitor_share
    
    @staticmethod
    def _update_market_conditions(game_state: GameState) -> None:
        """
        Update market conditions for the next quarter.
        
        Args:
            game_state: The current game state
        """
        # Apply market growth
        game_state.market_state.market_size *= (1 + game_state.market_state.market_growth)
        
        # Fluctuate market growth rate slightly to make the game more dynamic
        current_growth = game_state.market_state.market_growth
        growth_adjustment = (0.5 - 0.5) * 0.01  # Random adjustment between -0.5% and +0.5%
        new_growth = current_growth + growth_adjustment
        
        # Keep growth rate within reasonable bounds
        new_growth = max(0.01, min(0.05, new_growth))
        game_state.market_state.market_growth = new_growth
        
        # Update external economic factors
        # These could be made more complex in future versions
        game_state.external_state.interest_rate = max(0.005, min(0.02, game_state.external_state.interest_rate))
        game_state.external_state.inflation_rate = max(0.002, min(0.01, game_state.external_state.inflation_rate))
    
    @staticmethod
    def _calculate_stock_price(game_state: GameState) -> float:
        """
        Calculate stock price based on earnings, growth, and market conditions.
        
        Args:
            game_state: The current game state
            
        Returns:
            The calculated stock price
        """
        company = game_state.company_state
        
        # Base price on assets and cash
        base_value = (company.assets + company.cash) * 5
        
        # Apply earnings multiple if there are historical profits
        earnings_multiple = 10.0  # P/E ratio
        if company.historical_profit:
            # Use average of last 4 quarters or all available quarters
            profit_window = min(4, len(company.historical_profit))
            recent_profits = company.historical_profit[-profit_window:]
            avg_profit = sum(recent_profits) / profit_window
            
            # Apply earnings component
            earnings_component = avg_profit * earnings_multiple
        else:
            earnings_component = 0
        
        # Apply growth component if there are at least 2 quarters of data
        growth_component = 0
        if len(company.historical_profit) >= 2:
            # Calculate profit growth rate
            latest_profit = company.historical_profit[-1]
            previous_profit = company.historical_profit[-2]
            
            if previous_profit > 0:
                profit_growth = (latest_profit - previous_profit) / previous_profit
                # Apply growth premium (higher growth = higher multiple)
                growth_component = base_value * max(0, profit_growth) * 2
        
        # Calculate final stock price
        stock_price = base_value + earnings_component + growth_component
        
        # Ensure stock price doesn't go below a minimum value
        return max(10.0, stock_price) 