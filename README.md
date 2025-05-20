# stock-tracker
A simple, modular stock ticker display for Raspberry Pi (or any desktop), using Pygame and the Finnhub API.  
Displays real-time stock prices and daily changes for a customizable list of stocks, with a GitHub-inspired dark mode aesthetic.

## Features

- **Dark Mode:** GitHub-like color palette for comfortable viewing.
- **Customizable Stocks:** Edit `stocks.csv` to add or remove stock symbols.
- **Secure API Key:** Store your Finnhub API key in a `.env` file (never hardcoded).
- **Automatic Updates:** Rotates through your stock list, updating prices and market status.
- **Visual Indicators:** Green/red for up/down, "MC" indicator when the market is closed.
- **Fade Transitions:** Smooth transitions between stocks.

## Setup

### 1. Clone the repository

```sh
git clone https://github.com/green4ja/stock-tracker.git
cd stock-tracker
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Get a Finnhub API Key

- Sign up at [Finnhub.io](https://finnhub.io/) for a free API key.

### 4. Configure your API Key

Create a `.env` file in the project directory with:
```
FINNHUB_API_KEY=your_actual_finnhub_api_key_here
```
Or, the program will prompt you for your key on first run.

### 5. Edit your stock list

Edit `stocks.csv` and add one stock symbol per line (e.g., `AAPL`, `GOOGL`, `TSLA`).

### 6. Run the program

```py
python main.py
```

## Usage Notes
- The display window will show a "Loading..." message while fetching data.
- The program cycles through your stock list every 30 seconds.
- Prices update every 5 seconds when the market is open.
- The display is optimized for a 128x128 window but can be adjusted in `main.py`.