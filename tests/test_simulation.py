"""
Tests for the core game simulation logic.
"""
import unittest
from app.models.game import GameConfig, PlayerAction, PricingDecision, ProductionDecision
from app.core.simulation import GameSimulation


class TestGameSimulation(unittest.TestCase):
    """
    Test cases for the GameSimulation class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Create a default game config
        self.config = GameConfig(
            initial_cash=10.0,
            initial_assets=50.0,
            initial_capacity=1000,
            initial_market_size=10000,
            initial_player_market_share=0.3,
            initial_competitor_price=100.0,
            price_elasticity=1.5
        )
        
        # Initialize a game
        self.game_state = GameSimulation.initialize_game(self.config)
    
    def test_initialize_game(self):
        """
        Test that a game is initialized correctly.
        """
        # Check that the game state is initialized with the correct values
        self.assertEqual(self.game_state.company_state.cash, 10.0)
        self.assertEqual(self.game_state.company_state.assets, 50.0)
        self.assertEqual(self.game_state.company_state.capacity, 1000)
        self.assertEqual(self.game_state.market_state.market_size, 10000)
        self.assertEqual(self.game_state.market_state.player_market_share, 0.3)
        self.assertEqual(self.game_state.market_state.competitor_price, 100.0)
        self.assertEqual(self.game_state.market_state.price_elasticity, 1.5)
        self.assertEqual(self.game_state.metadata.current_quarter, 1)
    
    def test_process_player_action(self):
        """
        Test that player actions are processed correctly.
        """
        # Create a player action
        action = PlayerAction(
            pricing_decision=PricingDecision(price=100.0),
            production_decision=ProductionDecision(volume=500)
        )
        
        # Process the action
        updated_state = GameSimulation.process_player_action(self.game_state, action)
        
        # Check that the game state is updated correctly
        self.assertEqual(updated_state.metadata.current_quarter, 2)
        self.assertGreaterEqual(updated_state.company_state.inventory, 0)
        
        # Check that historical data is updated
        self.assertEqual(len(updated_state.company_state.historical_revenue), 1)
        self.assertEqual(len(updated_state.company_state.historical_profit), 1)
        self.assertEqual(len(updated_state.company_state.historical_stock_price), 1)
    
    def test_price_elasticity(self):
        """
        Test that price elasticity affects demand correctly.
        """
        # Create two player actions with different prices
        action1 = PlayerAction(
            pricing_decision=PricingDecision(price=90.0),  # Lower price
            production_decision=ProductionDecision(volume=1000)
        )
        
        action2 = PlayerAction(
            pricing_decision=PricingDecision(price=110.0),  # Higher price
            production_decision=ProductionDecision(volume=1000)
        )
        
        # Process the actions
        state1 = GameSimulation.process_player_action(self.game_state, action1)
        state2 = GameSimulation.process_player_action(self.game_state, action2)
        
        # Check that the lower price results in higher market share
        self.assertGreater(state1.market_state.player_market_share, state2.market_state.player_market_share)
    
    def test_production_capacity(self):
        """
        Test that production is limited by capacity.
        """
        # Create a player action with production volume exceeding capacity
        action = PlayerAction(
            pricing_decision=PricingDecision(price=100.0),
            production_decision=ProductionDecision(volume=2000)  # Exceeds capacity of 1000
        )
        
        # Process the action
        updated_state = GameSimulation.process_player_action(self.game_state, action)
        
        # Check that production costs reflect the higher utilization
        self.assertGreater(updated_state.company_state.costs, 0)


if __name__ == "__main__":
    unittest.main() 