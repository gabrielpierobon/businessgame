"""
Tests for the game models.
"""
import unittest
from app.models.game import (
    GameConfig, 
    PlayerAction, 
    PricingDecision, 
    ProductionDecision,
    CompanyState,
    MarketState,
    GameState,
    GameMetadata
)


class TestGameModels(unittest.TestCase):
    """
    Test cases for the game models.
    """
    
    def test_game_config(self):
        """
        Test that GameConfig can be created with valid parameters.
        """
        config = GameConfig(
            initial_cash=10.0,
            initial_assets=50.0,
            initial_capacity=1000,
            initial_market_size=10000,
            initial_player_market_share=0.3,
            initial_competitor_price=100.0,
            price_elasticity=1.5
        )
        
        self.assertEqual(config.initial_cash, 10.0)
        self.assertEqual(config.initial_assets, 50.0)
        self.assertEqual(config.initial_capacity, 1000)
        self.assertEqual(config.initial_market_size, 10000)
        self.assertEqual(config.initial_player_market_share, 0.3)
        self.assertEqual(config.initial_competitor_price, 100.0)
        self.assertEqual(config.price_elasticity, 1.5)
    
    def test_player_action(self):
        """
        Test that PlayerAction can be created with valid decisions.
        """
        pricing = PricingDecision(price=100.0)
        production = ProductionDecision(volume=500)
        action = PlayerAction(
            pricing_decision=pricing,
            production_decision=production
        )
        
        self.assertEqual(action.pricing_decision.price, 100.0)
        self.assertEqual(action.production_decision.volume, 500)
    
    def test_company_state(self):
        """
        Test that CompanyState can be created and updated.
        """
        company = CompanyState(
            cash=1000.0,
            assets=5000.0,
            capacity=1000,
            inventory=200,
            production=0,
            sales=0,
            revenue=0.0,
            costs=0.0,
            profit=0.0,
            stock_price=10.0,
            historical_revenue=[],
            historical_profit=[],
            historical_stock_price=[]
        )
        
        # Test initial state
        self.assertEqual(company.cash, 1000.0)
        self.assertEqual(company.assets, 5000.0)
        
        # Test updating state
        company.cash += 500.0
        company.revenue = 1000.0
        company.costs = 700.0
        company.profit = company.revenue - company.costs
        company.historical_revenue.append(company.revenue)
        company.historical_profit.append(company.profit)
        
        self.assertEqual(company.cash, 1500.0)
        self.assertEqual(company.profit, 300.0)
        self.assertEqual(company.historical_revenue, [1000.0])
        self.assertEqual(company.historical_profit, [300.0])
    
    def test_game_state(self):
        """
        Test that GameState can be created with all components.
        """
        company = CompanyState(
            cash=1000.0,
            assets=5000.0,
            capacity=1000,
            inventory=200,
            production=0,
            sales=0,
            revenue=0.0,
            costs=0.0,
            profit=0.0,
            stock_price=10.0,
            historical_revenue=[],
            historical_profit=[],
            historical_stock_price=[]
        )
        
        market = MarketState(
            market_size=10000,
            player_market_share=0.3,
            competitor_price=100.0,
            price_elasticity=1.5
        )
        
        metadata = GameMetadata(
            game_id="test_game",
            player_name="Test Player",
            current_quarter=1,
            start_date="2023-01-01",
            last_updated="2023-01-01"
        )
        
        game_state = GameState(
            company_state=company,
            market_state=market,
            metadata=metadata
        )
        
        self.assertEqual(game_state.company_state.cash, 1000.0)
        self.assertEqual(game_state.market_state.market_size, 10000)
        self.assertEqual(game_state.metadata.game_id, "test_game")
        self.assertEqual(game_state.metadata.current_quarter, 1)


if __name__ == "__main__":
    unittest.main() 