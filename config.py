# Market Bot configuration

# Stock price filter
MIN_PRICE = 0.50
MAX_PRICE = 15.00

# Minimum volume/liquidity
MIN_LIQUIDITY = 8_000_000

# Momentum levels
MOMENTUM_LEVELS = [10, 20, 30]

# Trading windows
MORNING_START = "06:00"
MORNING_END = "12:00"

AFTERNOON_START = "15:00"
AFTERNOON_END = "18:00"

# Morning momentum focus
MORNING_FOCUS_START = "06:00"
MORNING_FOCUS_END = "09:00"

# Risk settings
STOP_LOSS_PERCENT = 5.0
PARTIAL_PROFIT_PERCENT = 15.0
PROFIT_TARGET_PERCENT = 25.0

# Additional profit levels for testing
PROFIT_LEVELS = [8, 10, 15, 20, 25, 30]

# Trading modes
LONG_ONLY = False
SHORT_ENABLED = True
NO_MARGIN = True

# Stock restrictions
EXCLUDE_CHINA_STOCKS = True

# Safety
LIVE_TRADING_ENABLED = False
PAPER_TRADING_ENABLED = True
