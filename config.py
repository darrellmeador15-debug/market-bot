# Market Bot configuration

# Stock price filter
MIN_PRICE = 0.50
MAX_PRICE = 15.00

# NOTE: This is a minimum traded-volume filter, not a float-share filter.
# Keep separate from MIN_FLOAT when float data is added.
MIN_LIQUIDITY = 8_000_000

# Scanner tiers; entry logic must look for early setups before chasing
# stocks that have already made a large move.
MOMENTUM_LEVELS = [10, 20, 30]

# Trading windows (Eastern Time)
MORNING_START = "06:00"
MORNING_END = "12:00"
AFTERNOON_START = "15:00"
AFTERNOON_END = "18:00"
MORNING_FOCUS_START = "06:00"
MORNING_FOCUS_END = "09:00"

# Risk settings: hard planned stop and configurable profit-taking tests.
STOP_LOSS_PERCENT = 5.0
PARTIAL_PROFIT_PERCENT = 10.0
PROFIT_TARGET_PERCENT = 15.0
PROFIT_LEVELS = [10, 15, 20]

# Long-only: no short selling.
LONG_ONLY = True
SHORT_ENABLED = False
NO_MARGIN = True

# Stock restrictions
EXCLUDE_CHINA_STOCKS = True

# Safety defaults
LIVE_TRADING_ENABLED = False
PAPER_TRADING_ENABLED = True
