# Business Game

A turn-based business simulation game modeling a global manufacturing company as a Markov Decision Process.

## Description
This project implements a business simulation game where players make strategic decisions for a manufacturing company each quarter. The game models the business as a Markov Decision Process, where each state transition depends on the current state and the player's actions.

Key features:
- Make quarterly pricing and production decisions
- Compete against an AI competitor
- Track financial performance and stock price
- Visualize performance metrics over time
- Simple and intuitive web interface

## Architecture
The application follows a clean architecture with clear separation between:
- API layer (FastAPI endpoints)
- Business logic (game simulation)
- Data access layer (MongoDB repositories)

The game is implemented as a web application using:
- FastAPI for the backend API
- MongoDB for data storage
- Jinja2 templates for the frontend
- Chart.js for data visualization

## Setup

### Option 1: Local Development

1. Clone the repository
```bash
git clone https://github.com/gabrielpierobon/businessgame.git
cd businessgame
```

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Set up MongoDB
   - Install MongoDB or use a cloud service
   - Update the `.env` file with your MongoDB connection details

6. Run the application
```bash
python run.py
```

7. Open your browser and navigate to `http://localhost:8000`

### Option 2: Docker Development

1. Clone the repository
```bash
git clone https://github.com/gabrielpierobon/businessgame.git
cd businessgame
```

2. Start the application with Docker Compose
```bash
docker-compose up
```

3. Open your browser and navigate to `http://localhost:8000`

### Option 3: Docker Production

1. Clone the repository
```bash
git clone https://github.com/gabrielpierobon/businessgame.git
cd businessgame
```

2. Build the Docker image
```bash
docker build -t businessgame .
```

3. Run the container
```bash
docker run -p 8000:8000 -e MONGO_URL=mongodb://your-mongodb-host:27017 businessgame
```

4. Open your browser and navigate to `http://localhost:8000`

## Testing

To run the tests:

```bash
python run_tests.py
```

Or run individual test files:

```bash
python -m unittest tests/test_simulation.py
```

## Game Mechanics
The game simulates a manufacturing company with the following key mechanics:

1. **Pricing Decision**: Set the price for your product each quarter. Higher prices may reduce demand but increase profit margins.

2. **Production Decision**: Determine how many units to produce each quarter. Production is limited by capacity and has economies of scale.

3. **Market Dynamics**: The market responds to your pricing decisions according to price elasticity. Your market share changes based on your price relative to competitors.

4. **Competitor Behavior**: A simple AI competitor adjusts their pricing strategy in response to your decisions.

5. **Financial Outcomes**: The game calculates revenue, costs, and profits based on your decisions and market conditions.

6. **Stock Price**: Your company's stock price is calculated based on assets, earnings, and growth.

## Future Enhancements
- Investment decisions to increase capacity
- Marketing decisions to influence demand
- R&D decisions to improve product quality
- Multiple products and market segments
- More sophisticated competitor AI
- Multiplayer support

## License
[MIT](https://choosealicense.com/licenses/mit/) 