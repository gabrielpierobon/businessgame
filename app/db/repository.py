"""
Repository module for database operations related to the game.
"""
import uuid
from datetime import datetime
from typing import Optional

from app.db.mongodb import get_db
from app.models.game import GameState, PlayerAction


class GameRepository:
    """
    Repository for game-related database operations.
    """
    
    @staticmethod
    async def create_game(game_state: GameState) -> str:
        """
        Save a new game to the database.
        
        Args:
            game_state: The game state to save
            
        Returns:
            The ID of the created game
        """
        db = get_db()
        
        # Convert to dict for MongoDB storage
        game_dict = game_state.dict()
        
        # Update timestamps
        now = datetime.now()
        game_dict["metadata"]["created_at"] = now
        game_dict["metadata"]["updated_at"] = now
        
        # Insert into database
        result = await db.games.insert_one(game_dict)
        
        return str(result.inserted_id)
    
    @staticmethod
    async def get_game(game_id: str) -> Optional[GameState]:
        """
        Retrieve a game from the database.
        
        Args:
            game_id: The ID of the game to retrieve
            
        Returns:
            The game state, or None if not found
        """
        db = get_db()
        
        # Find game in database
        game_dict = await db.games.find_one({"metadata.game_id": game_id})
        
        if not game_dict:
            return None
        
        # Convert to GameState model
        return GameState.parse_obj(game_dict)
    
    @staticmethod
    async def update_game(game_state: GameState) -> bool:
        """
        Update an existing game in the database.
        
        Args:
            game_state: The updated game state
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db()
        
        # Convert to dict for MongoDB storage
        game_dict = game_state.dict()
        
        # Update timestamp
        game_dict["metadata"]["updated_at"] = datetime.now()
        
        # Update in database
        result = await db.games.replace_one(
            {"metadata.game_id": game_state.metadata.game_id},
            game_dict
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def save_player_action(game_id: str, quarter: int, action: PlayerAction) -> bool:
        """
        Save a player action to the database.
        
        Args:
            game_id: The ID of the game
            quarter: The quarter number
            action: The player action
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db()
        
        # Convert to dict for MongoDB storage
        action_dict = action.dict()
        action_dict["game_id"] = game_id
        action_dict["quarter"] = quarter
        action_dict["timestamp"] = datetime.now()
        
        # Insert into database
        result = await db.player_actions.insert_one(action_dict)
        
        return result.acknowledged
    
    @staticmethod
    async def list_games(limit: int = 10, skip: int = 0) -> list:
        """
        List games from the database.
        
        Args:
            limit: Maximum number of games to return
            skip: Number of games to skip
            
        Returns:
            List of games
        """
        db = get_db()
        
        # Find games in database
        cursor = db.games.find().sort("metadata.created_at", -1).skip(skip).limit(limit)
        
        # Convert to list
        games = await cursor.to_list(length=limit)
        
        return games 