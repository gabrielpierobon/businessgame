import requests
import json

# Get the game ID from the previous response
response = requests.get("http://localhost:8000/api/games")
games = response.json()
game_id = games[0]["game_id"]  # Get the ID of the first game

# Create a player action
action = {
    "pricing_decision": {
        "price": 97.0  # Slightly increase price to reflect quality improvements
    },
    "production_decision": {
        "volume": 950  # Further increase production to 95% capacity
    },
    "marketing_decision": {
        "budget": 2.0,  # Further increase marketing investment
        "segment_allocation": {"mass_market": 1.0},
        "channel_mix": {
            "traditional": 0.3,
            "digital": 0.5,
            "direct": 0.2
        },
        "campaign_focus": "brand_building"  # Focus on building brand strength
    },
    "r_and_d_decision": {
        "budget": 1.5,  # Increase R&D investment
        "focus": "quality_improvement"  # Continue focus on quality
    },
    "supply_chain_decision": {
        "investment": 2.0,  # Increase investment to address relationship issues
        "focus": "relationship",  # Switch back to relationship focus
        "supplier_quality": "premium",  # Upgrade to premium suppliers
        "inventory_policy": "safety_stock"  # More conservative inventory policy
    }
}

# Submit the action
response = requests.post(
    f"http://localhost:8000/api/games/{game_id}/actions",
    json=action,
    headers={"Content-Type": "application/json"}
)

print("Status Code:", response.status_code)
print("\nUpdated Game State:")
print(json.dumps(response.json(), indent=2)) 