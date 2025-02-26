"""
API routes for the Business Game.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.models.game import GameState, PlayerAction, GameConfig
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
async def submit_action(game_id: str, action: PlayerAction):
    """
    Submit player actions for a quarter and advance the game state.
    """
    # Retrieve current game state
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    # Process player action
    updated_state = GameSimulation.process_player_action(game_state, action)
    
    # Save player action to database
    await GameRepository.save_player_action(
        game_id, 
        game_state.metadata.current_quarter,
        action
    )
    
    # Update game state in database
    success = await GameRepository.update_game(updated_state)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update game state")
    
    return updated_state


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
            "market_share": game["market_state"]["player_market_share"]
        })
    
    return formatted_games 