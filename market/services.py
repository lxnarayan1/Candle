import yfinance as yf
from django.core.cache import cache
from yfinance import Search


COMPANY_RANGE_MAP = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1h"),
    "3M": ("3mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y": ("1y", "1d"),
}


def get_yahoo_market_data(symbol="^NSEI", range_key="1D"):
    """
    Fetch market data from Yahoo Finance
    Supports Indian indices & stocks
    """

    period, interval = COMPANY_RANGE_MAP.get(range_key, ("1d", "5m"))

    cache_key = f"yahoo_market_{symbol}_{range_key}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)

    if hist.empty:
        raise ValueError("Market data unavailable")

    prices = hist["Close"].tolist()

   
    if range_key == "1D":
        times = hist.index.strftime("%H:%M").tolist()
    else:
        times = hist.index.strftime("%d %b").tolist()

    chart = [
        {"time": t, "value": round(p, 2)}
        for t, p in zip(times, prices)
    ]

    result = {
        "index": symbol,
        "current_value": round(prices[-1], 2),
        "gain": round(prices[-1] - prices[0], 2),
        "gain_percent": round(((prices[-1] - prices[0]) / prices[0]) * 100, 2),
        "day_range": {
            "low": round(min(prices), 2),
            "high": round(max(prices), 2),
        },
        "price_movement": chart[-50:],  
    }

   
    cache.set(cache_key, result, timeout=60)
    return result


def search_companies(query, limit=10):
    """
    Search companies using Yahoo Finance
    """
    if not query:
        return []

    search = Search(query, max_results=limit)
    quotes = search.quotes or []

    results = []

    for q in quotes:
        symbol = q.get("symbol")
        name = q.get("shortname") or q.get("longname")

        # Focus on Indian stocks & common equities
        if symbol and name:
            results.append({
                "symbol": symbol,
                "name": name,
            })

    # Sort alphabetically by company name
    results = sorted(results, key=lambda x: x["name"])

    return results[:limit]



def get_company_data(symbol, range_key="1D"):
    """
    Fetch single company data from Yahoo Finance
    LOGIN REQUIRED endpoint
    """

    if not symbol:
        raise ValueError("Symbol is required")

    period, interval = COMPANY_RANGE_MAP.get(range_key, ("1d", "5m"))

    cache_key = f"company_{symbol}_{range_key}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    ticker = yf.Ticker(symbol)

    # Price history
    hist = ticker.history(period=period, interval=interval)
    if hist.empty:
        raise ValueError("Company data not available")

    prices = hist["Close"].tolist()

    times = (
        hist.index.strftime("%H:%M").tolist()
        if range_key == "1D"
        else hist.index.strftime("%d %b").tolist()
    )

    price_movement = [
        {"time": t, "value": round(p, 2)}
        for t, p in zip(times, prices)
    ]

    info = ticker.info or {}

    result = {
        "symbol": symbol,
        "name": info.get("shortName") or info.get("longName") or symbol,
        "current_value": round(prices[-1], 2),
        "gain": round(prices[-1] - prices[0], 2),
        "gain_percent": round(
            ((prices[-1] - prices[0]) / prices[0]) * 100, 2
        ),
        "stats": {
            "open": round(hist["Open"].iloc[0], 2),
            "high": round(hist["High"].max(), 2),
            "low": round(hist["Low"].min(), 2),
            "prev_close": round(info.get("previousClose", prices[0]), 2),
            "market_cap": format_market_cap(info.get("marketCap")),
            "volume": format_volume(hist["Volume"].sum()),
        },
        "price_movement": price_movement[-60:],  # smooth chart
    }

    cache.set(cache_key, result, timeout=60)
    return result


def format_market_cap(value):
    if not value:
        return "N/A"
    for unit in ["", "K", "M", "B", "T"]:
        if abs(value) < 1000:
            return f"{value:.1f}{unit}"
        value /= 1000
    return f"{value:.1f}P"


def format_volume(value):
    if not value:
        return "N/A"
    for unit in ["", "K", "M", "B"]:
        if value < 1000:
            return f"{int(value)}{unit}"
        value /= 1000
    return f"{value:.1f}T"