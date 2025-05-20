import pygame
import requests
import time
import os
import csv
import platform

# --- API Key Handling ---
def get_api_key():
    api_key = os.environ.get('FINNHUB_API_KEY')
    if api_key:
        return api_key

    # Try to load from .env file
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('FINNHUB_API_KEY='):
                    return line.strip().split('=', 1)[1]

    # Prompt user and save to .env
    api_key = input("Enter your Finnhub API key: ").strip()
    with open(env_path, 'w') as f:
        f.write(f'FINNHUB_API_KEY={api_key}\n')
    return api_key

API_KEY = get_api_key()

# --- Stock Symbols Handling ---
def load_stock_symbols(filename='stocks.csv'):
    symbols = []
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip():
                    symbols.append(row[0].strip().upper())
    except FileNotFoundError:
        raise RuntimeError(f"{filename} not found. Please create it with one stock symbol per line.")
    if not symbols:
        raise RuntimeError(f"{filename} is empty. Please add at least one stock symbol.")
    return symbols

STOCK_SYMBOLS = load_stock_symbols()

DISPLAY_SIZE = (128, 128)  # Display resolution
REFRESH_INTERVAL = 5  # 5 seconds
MARKET_CHECK_INTERVAL = 300  # 5 minutes
SWITCH_INTERVAL = 30  # Switch to the next stock every 30 seconds

# Retrieve the stock data from the API
def get_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return {
        'current_price': data['c'],
        'change': data['d'],
        'percent_change': data['dp'],
    }

# Function to check if the market is open
def is_market_open():
    url = f"https://finnhub.io/api/v1/stock/market-status?exchange=US&token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("isOpen", False)  # Returns True if the market is open

# Render left-aligned text on the Pygame surface
def render_text_left(surface, text, font, x, y, color, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the word would exceed max_width
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    # Render each line
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y))
        y += font.get_linesize()

# Smooth fade transition
def fade_transition(screen, old_surface, new_surface, duration=1):
    clock = pygame.time.Clock()
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((13, 17, 23))  # Dark overlay for dark mode
    alpha_step = max(1, 255 // (duration * 30))

    # Fade out old surface
    for alpha in range(0, 256, alpha_step):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        screen.blit(old_surface, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    # Fade in new surface
    for alpha in range(255, -1, -alpha_step):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        screen.blit(new_surface, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

# Initialize Pygame
pygame.init()

# Detect OS and set display mode
if platform.system() == "Linux":
    screen = pygame.display.set_mode(DISPLAY_SIZE, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(DISPLAY_SIZE)

pygame.display.set_caption('Stock Tracker')
clock = pygame.time.Clock()

# Fonts
try:
    font_large = pygame.font.SysFont('Helvetica', 20, bold=True)
    font_medium = pygame.font.SysFont('Helvetica', 18)
    font_small = pygame.font.SysFont('Helvetica', 14)
except:
    font_large = pygame.font.SysFont('Arial', 20, bold=True)
    font_medium = pygame.font.SysFont('Arial', 18)
    font_small = pygame.font.SysFont('Arial', 14)

# Colors (GitHub dark mode palette)
BG_COLOR = (13, 17, 23)         # #0d1117
FG_COLOR = (201, 209, 217)      # #c9d1d9
GREEN = (19, 127, 54)
RED = (219, 44, 39)
YELLOW = (227, 179, 65)         # #e3b341

# --- Show loading screen immediately ---
screen.fill(BG_COLOR)
loading_surface = font_large.render("Loading...", True, FG_COLOR)
screen.blit(loading_surface, (20, 54))
pygame.display.flip()

# Now do the blocking API calls
current_stock_index = 0
market_open = is_market_open()
stock_data = get_stock_data(STOCK_SYMBOLS[current_stock_index])
last_market_check_time = time.time()
last_update_time = time.time()
last_switch_time = time.time()

# Function to render the stock screen
def create_stock_surface(symbol, stock_data):
    surface = pygame.Surface(DISPLAY_SIZE)
    surface.fill(BG_COLOR)

    # Determine price change arrow, polarity, and color
    if stock_data['change'] > 0:
        arrow = "↑"
        polarity = "+"
        change_color = GREEN
    else:
        arrow = "↓"
        polarity = ""
        change_color = RED

    # Render the stock symbol on the top left
    symbol_surface = font_large.render(symbol, True, FG_COLOR)
    surface.blit(symbol_surface, (5, 10))

    # Render "MC" on the top right if the market is closed
    if not market_open:
        mc_surface = font_large.render("MC", True, YELLOW)
        mc_x = DISPLAY_SIZE[0] - mc_surface.get_width() - 5
        mc_y = 10
        surface.blit(mc_surface, (mc_x, mc_y))

    # Render the stock data (price, change, percent change)
    render_text_left(
        surface, f"{stock_data['current_price']:.2f} USD", font_medium, 5, 40, change_color, DISPLAY_SIZE[0] - 10
    )
    render_text_left(
        surface,
        f"{polarity}{stock_data['change']:.2f} ({stock_data['percent_change']:.2f}%) {arrow} today",
        font_small,
        5,
        70,
        change_color,
        DISPLAY_SIZE[0] - 10,
    )

    return surface

# Create the initial screen
current_surface = create_stock_surface(STOCK_SYMBOLS[current_stock_index], stock_data)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()

    # Check market status periodically
    if not market_open and current_time - last_market_check_time >= MARKET_CHECK_INTERVAL:
        market_open = is_market_open()
        last_market_check_time = current_time

    # Update stock data once every 5 seconds
    if market_open and current_time - last_update_time >= REFRESH_INTERVAL:
        stock_data = get_stock_data(STOCK_SYMBOLS[current_stock_index])
        current_surface = create_stock_surface(STOCK_SYMBOLS[current_stock_index], stock_data)
        last_update_time = current_time

    # Switch to the next stock every 30 seconds
    if current_time - last_switch_time >= SWITCH_INTERVAL:
        next_index = (current_stock_index + 1) % len(STOCK_SYMBOLS)
        next_stock_data = get_stock_data(STOCK_SYMBOLS[next_index])
        next_surface = create_stock_surface(STOCK_SYMBOLS[next_index], next_stock_data)
        fade_transition(screen, current_surface, next_surface)
        current_stock_index = next_index
        current_surface = next_surface
        last_switch_time = current_time

    # Draw the current screen
    screen.blit(current_surface, (0, 0))
    pygame.display.flip()

    # Limit FPS
    clock.tick(30)

pygame.quit()