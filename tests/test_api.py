"""
Tests for the API endpoints.
"""
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from main import app


class TestAPIEndpoints(unittest.TestCase):
    """
    Test cases for the API endpoints.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.client = TestClient(app)
        
    def test_home_page(self):
        """
        Test that the home page returns a 200 status code.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
    
    @patch("app.repositories.game_repository.GameRepository")
    def test_create_game(self, mock_repo):
        """
        Test that a new game can be created.
        """
        # Mock the repository
        mock_instance = mock_repo.return_value
        mock_instance.create_game.return_value = "test_game_id"
        
        # Make the request
        response = self.client.post("/games", json={
            "player_name": "Test Player",
            "difficulty": "normal"
        })
        
        # Check the response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["game_id"], "test_game_id")
        
    @patch("app.repositories.game_repository.GameRepository")
    def test_get_game(self, mock_repo):
        """
        Test that a game can be retrieved.
        """
        # Mock the repository
        mock_instance = mock_repo.return_value
        mock_instance.get_game.return_value = {
            "game_id": "test_game_id",
            "current_quarter": 1,
            "player_name": "Test Player"
        }
        
        # Make the request
        response = self.client.get("/games/test_game_id")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["game_id"], "test_game_id")
        
    @patch("app.repositories.game_repository.GameRepository")
    @patch("app.core.simulation.GameSimulation")
    def test_submit_action(self, mock_simulation, mock_repo):
        """
        Test that player actions can be submitted.
        """
        # Mock the repository and simulation
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.get_game.return_value = {
            "game_id": "test_game_id",
            "current_quarter": 1
        }
        mock_repo_instance.update_game.return_value = True
        
        mock_simulation.process_player_action.return_value = {
            "game_id": "test_game_id",
            "current_quarter": 2
        }
        
        # Make the request
        response = self.client.post("/games/test_game_id/actions", data={
            "price": "100.0",
            "production_volume": "500"
        })
        
        # Check the response
        self.assertEqual(response.status_code, 302)  # Redirect


if __name__ == "__main__":
    unittest.main() 