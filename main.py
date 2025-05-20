import pygame
import requests
import time

API_KEY = 'cu58a99r01qqj8u5v9j0cu58a99r01qqj8u5v9jg'  # My API Key for Finnhub
STOCK_SYMBOLS = ['AMPX', 'VOO', 'JPM']  # List of stock symbols
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
    overlay.fill((255, 255, 255))  # White overlay
    alpha_step = 255 // (duration * 30)

    for alpha in range(0, 256, alpha_step):
        screen.blit(old_surface, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    for alpha in range(255, -1, -alpha_step):
        screen.blit(new_surface, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)  # Set the resolution
pygame.display.set_caption('Stock Tracker')
clock = pygame.time.Clock()

# Fonts
try:
    font_large = pygame.font.SysFont('Helvetica', 20, bold=True)  # Large font for the symbol
    font_medium = pygame.font.SysFont('Helvetica', 18)  # Medium font for the price
    font_small = pygame.font.SysFont('Helvetica', 14)  # Small font for the change info
except:
    # Fallback in case Helvetica is not available
    font_large = pygame.font.SysFont('Arial', 20, bold=True)
    font_medium = pygame.font.SysFont('Arial', 18)
    font_small = pygame.font.SysFont('Arial', 14)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (19, 127, 54)
RED = (219, 44, 39)
YELLOW = (218, 165, 32)

# Initial setup
current_stock_index = 0
market_open = is_market_open()
stock_data = get_stock_data(STOCK_SYMBOLS[current_stock_index])
last_market_check_time = time.time()
last_update_time = time.time()
last_switch_time = time.time()

# Function to render the stock screen
def create_stock_surface(symbol, stock_data):
    surface = pygame.Surface(DISPLAY_SIZE)
    surface.fill(WHITE)

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
    symbol_surface = font_large.render(symbol, True, BLACK)
    surface.blit(symbol_surface, (5, 10))

    # Render "MC" on the top right if the market is closed
    if not market_open:
        mc_surface = font_large.render("MC", True, YELLOW)
        mc_x = DISPLAY_SIZE[0] - mc_surface.get_width() - 5  # Align to the right
        mc_y = 10  # Same vertical alignment as the symbol
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