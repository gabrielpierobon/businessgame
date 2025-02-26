"""
Frontend routes for the Business Game web interface.
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import json

from app.models.game import GameConfig, PlayerAction, PricingDecision, ProductionDecision
from app.db.repository import GameRepository

# Create router
router = APIRouter()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the home page.
    """
    # Get list of games
    games = await GameRepository.list_games(limit=5)
    
    # Format games for display
    formatted_games = []
    for game in games:
        formatted_games.append({
            "game_id": game["metadata"]["game_id"],
            "current_quarter": game["metadata"]["current_quarter"],
            "created_at": game["metadata"]["created_at"].strftime("%Y-%m-%d %H:%M"),
            "stock_price": f"${game['stock_price']:.2f}",
            "cash": f"${game['company_state']['cash']:.2f}M",
            "market_share": f"{game['market_state']['player_market_share'] * 100:.1f}%"
        })
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "games": formatted_games}
    )


@router.get("/games/new", response_class=HTMLResponse)
async def new_game_form(request: Request):
    """
    Render the new game form.
    """
    return templates.TemplateResponse(
        "new_game.html", 
        {"request": request}
    )


@router.post("/games/new")
async def create_game(
    request: Request,
    game_name: Optional[str] = Form(None),
    initial_cash: float = Form(10.0),
    initial_assets: float = Form(50.0),
    initial_capacity: float = Form(1000),
    initial_market_size: float = Form(10000),
    initial_player_market_share: float = Form(0.3),
    initial_competitor_price: float = Form(100.0),
    price_elasticity: float = Form(1.5)
):
    """
    Create a new game from form data.
    """
    # Create game config
    config = GameConfig(
        game_name=game_name,
        initial_cash=initial_cash,
        initial_assets=initial_assets,
        initial_capacity=initial_capacity,
        initial_market_size=initial_market_size,
        initial_player_market_share=initial_player_market_share,
        initial_competitor_price=initial_competitor_price,
        price_elasticity=price_elasticity
    )
    
    # Call API to create game
    from app.api.routes import create_game as api_create_game
    game_state = await api_create_game(config)
    
    # Redirect to game page
    return RedirectResponse(
        url=f"/games/{game_state.metadata.game_id}",
        status_code=303
    )


@router.get("/games/{game_id}", response_class=HTMLResponse)
async def view_game(request: Request, game_id: str):
    """
    Render the game view page.
    """
    # Get game state
    game_state = await GameRepository.get_game(game_id)
    
    if not game_state:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
    
    # Format data for display
    game_data = {
        "game_id": game_state.metadata.game_id,
        "current_quarter": game_state.metadata.current_quarter,
        "stock_price": f"${game_state.stock_price:.2f}",
        "cash": f"${game_state.company_state.cash:.2f}M",
        "assets": f"${game_state.company_state.assets:.2f}M",
        "inventory": f"{game_state.company_state.inventory:.0f} units",
        "capacity": f"{game_state.company_state.capacity:.0f} units/quarter",
        "revenue": f"${game_state.company_state.revenue:.2f}M",
        "costs": f"${game_state.company_state.costs:.2f}M",
        "profit": f"${game_state.company_state.profit:.2f}M",
        "market_size": f"{game_state.market_state.market_size:.0f} units",
        "market_growth": f"{game_state.market_state.market_growth * 100:.1f}%",
        "competitor_price": f"${game_state.market_state.competitor_price:.2f}",
        "player_market_share": f"{game_state.market_state.player_market_share * 100:.1f}%",
        "competitor_market_share": f"{game_state.market_state.competitor_market_share * 100:.1f}%",
        "interest_rate": f"{game_state.external_state.interest_rate * 100:.1f}%",
        "inflation_rate": f"{game_state.external_state.inflation_rate * 100:.1f}%",
        "tax_rate": f"{game_state.external_state.tax_rate * 100:.1f}%"
    }
    
    # Prepare chart data
    chart_data = {
        "quarters": list(range(1, len(game_state.company_state.historical_profit) + 2)),
        "profit": [0] + game_state.company_state.historical_profit,
        "revenue": [0] + game_state.company_state.historical_revenue,
        "stock_price": [game_state.stock_price] + game_state.company_state.historical_stock_price
    }
    
    return templates.TemplateResponse(
        "game.html", 
        {
            "request": request, 
            "game": game_data, 
            "chart_data": json.dumps(chart_data)
        }
    )


@router.post("/games/{game_id}/actions")
async def submit_action(
    request: Request,
    game_id: str,
    price: float = Form(...),
    production_volume: float = Form(...)
):
    """
    Submit player actions for a quarter.
    """
    # Create player action
    action = PlayerAction(
        pricing_decision=PricingDecision(price=price),
        production_decision=ProductionDecision(volume=production_volume)
    )
    
    # Call API to submit action
    from app.api.routes import submit_action as api_submit_action
    await api_submit_action(game_id, action)
    
    # Redirect back to game page
    return RedirectResponse(
        url=f"/games/{game_id}",
        status_code=303
    ) 