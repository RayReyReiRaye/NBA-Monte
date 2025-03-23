# NBA Player Performance Prediction

This project is an advanced NBA analytics engine designed to predict individual player performance using machine learning, player usage metrics, and matchup-driven Monte Carlo simulations. It integrates real-time injury data and probable lineups through automated scraping and public APIs.

## Features

- Predicts expected player stats for today's NBA matchups (PTS, REB, AST, etc.)
- Uses XGBoost regression to model player minutes with consideration for usage, rest, injury status, and team context
- Runs Monte Carlo simulations to generate stat probability distributions and threshold hit rates
- Scrapes live injury reports from ESPN and starting lineups from FantasyData
- Allows manual lineup overrides for last-minute adjustments or injury speculation
- Normalizes and fuzzy matches player names to avoid ID mismatches

## Code Structure

```
nba_model/
├── config.py                  # Constants, thresholds, and mappings
├── utils.py                   # Helper functions (name matching, normalization, etc.)
├── data_fetch.py              # API and web scraping logic
├── data_processing.py         # Preprocessing, merging, and transformation logic
├── regression.py              # XGBoost-based regression model for minutes
├── simulation.py              # Monte Carlo simulation engine for stat projections
├── main.py                    # Main execution logic (interactive script or notebook)
├── requirements.txt           # Python dependencies
├── demo_notebook.ipynb        # Sample Jupyter Notebook runner
├── .gitignore                 # Files excluded from version control
├── assets/
│   └── simulation_output.png  # Example screenshot (optional)
└── README.md                  # Project overview and documentation
```

## How to Run

1. Clone this repository:

```bash
git clone https://github.com/yourusername/nba-prediction-model.git
cd nba-prediction-model
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch from a Jupyter Notebook or run `main.py` for terminal usage. The code was primarily built and tested within **VS Code** using **Jupyter Notebook**, aided by the **Data Wrangler** extension for interactive data table exploration.

## Example Output

Below is a sample output from running the simulation on the matchup `PHX @ DET`:

![Simulation Output](assets/simulation_output.png)

## Requirements

- Python 3.8+
- nba_api
- selenium
- beautifulsoup4
- webdriver_manager
- xgboost
- thefuzz
- pandas, numpy, scikit-learn

To install manually:

```bash
pip install nba_api selenium beautifulsoup4 webdriver_manager xgboost thefuzz pandas numpy scikit-learn
```

## Notes

- The system simulates game outcomes based on player roles, usage, historical data, and matchup strength.
- Custom manual starter inputs are available for override scenarios (injury speculation, rest days, etc.).
- The Monte Carlo simulation provides detailed probability distributions and projected averages for common betting props.

## License

This project is intended for educational and non-commercial purposes only.
