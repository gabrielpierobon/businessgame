import requests
import json

game_config = {
    "initial_cash": 10.0,
    "initial_assets": 50.0,
    "initial_capacity": 1000,
    "initial_market_size": 10000,
    "initial_player_market_share": 0.3,
    "initial_competitor_price": 100.0,
    "price_elasticity": 1.5,
    "difficulty": "normal",
    "market_segments_enabled": False,
    "random_events_enabled": True,
    "economic_cycles_enabled": True,
    "advanced_competitors_enabled": False,
    "game_name": "Test Game",
    "international_enabled": False,
    "starting_regions": [],
    "currency_volatility": 0.1,
    "trade_complexity": 1.0
}

response = requests.post(
    "http://localhost:8000/api/games",
    json=game_config,
    headers={"Content-Type": "application/json"}
)

print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2)) 