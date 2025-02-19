from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, INDEX_LIST_FILE_PATH, \
    LOGIN_INDICATOR_STYLE

# Map the factor names to Italian using the dictionary
factor_name_translation = {
    "Mkt-RF": "Mercato-RF",
    "SMB": "Small Cap",
    "HML": "Value",
    "RMW": "Profitabilità",
    "CMA": "Investimenti conservativi",
    "RF": "Tasso privo di rischio",
}

custom_colorscale = [
    [0, BENCHMARK_COLOR],  # Start of the scale
    [1, PORTFOLIO_COLOR]  # End of the scale
]

# Define pastel colors
pastel_colors = [
    '#AEC6CF', '#FFD1DC', '#FFB3DE', '#B5EAEA', '#C2F0C2',
    '#FFBCB3', '#FFCC99', '#D9EAD3', '#D5A6BD', '#FF6666'
]

rolling_periods = [36, 60, 120]
