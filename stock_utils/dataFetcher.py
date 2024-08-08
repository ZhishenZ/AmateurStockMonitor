from typing import Optional, Union
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta
import pytz

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Retrieve the API key from the environment
api_key = os.getenv("RAPIDAPI_KEY")

if not api_key:
    raise EnvironmentError(
        "API key for RapidAPI is missing. Please set 'RAPIDAPI_KEY' in your environment."
    )

RAPIDAPI_BASE_URL = "https://alpha-vantage.p.rapidapi.com/query"
RAPIDAPI_HEADERS = {
    "x-rapidapi-host": "alpha-vantage.p.rapidapi.com",
    "x-rapidapi-key": api_key,
}

# These values are copied from the official API documentation
indicatorTypeSet = {
    "AssetType",
    "Description",
    "CIK",
    "Exchange",
    "Currency",
    "Country",
    "Sector",
    "Industry",
    "Address",
    "FiscalYearEnd",
    "LatestQuarter",
    "MarketCapitalization",
    "EBITDA",
    "PERatio",
    "PEGRatio",
    "BookValue",
    "DividendPerShare",
    "DividendYield",
    "EPS",
    "RevenuePerShareTTM",
    "ProfitMargin",
    "OperatingMarginTTM",
    "ReturnOnAssetsTTM",
    "ReturnOnEquityTTM",
    "RevenueTTM",
    "GrossProfitTTM",
    "DilutedEPSTTM",
    "QuarterlyEarningsGrowthYOY",
    "QuarterlyRevenueGrowthYOY",
    "AnalystTargetPrice",
    "AnalystRatingStrongBuy",
    "AnalystRatingBuy",
    "AnalystRatingHold",
    "AnalystRatingSell",
    "AnalystRatingStrongSell",
    "TrailingPE",
    "ForwardPE",
    "PriceToSalesRatioTTM",
    "PriceToBookRatio",
    "EVToRevenue",
    "EVToEBITDA",
    "Beta",
    "52WeekHigh",
    "52WeekLow",
    "50DayMovingAverage",
    "200DayMovingAverage",
    "SharesOutstanding",
    "DividendDate",
    "ExDividendDate",
}


@dataclass
class StockFundamentals:
    symbol: Optional[str] = None
    indicator_type: Optional[str] = None
    value: Optional[Union[float, str, int]] = None
    latest_trading_day: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error_message is None


def get_market_reference_date() -> str:
    """This function determines the relevant trading date based on the current time in the U.S. Eastern Time Zone.
       Since the API only provides data after market hours, this function helps to validate if cache is up to date

    Returns:
        str: date time in form YYYY-MM-DD
    """
    now = datetime.now(pytz.timezone("US/Eastern"))

    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

    if now <= market_close:
        relevant_date = now - timedelta(days=1)
    else:
        relevant_date = now

    # Adjust for weekends
    if relevant_date.weekday() == 5:  # Saturday
        relevant_date -= timedelta(days=1)  # Last Friday
    elif relevant_date.weekday() == 6:  # Sunday
        relevant_date -= timedelta(days=2)  # Last Friday

    return relevant_date.strftime("%Y-%m-%d")


def get_latest_trading_day(symbol: str) -> str:

    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "datatype": "json"}

    try:
        response = requests.get(
            RAPIDAPI_BASE_URL, headers=RAPIDAPI_HEADERS, params=params
        )
        response.raise_for_status()
        data = response.json()
        latest_trading_day = data["Global Quote"]["07. latest trading day"]
        return latest_trading_day
    except Exception as e:
        print("Unexpected Error: {}".format(str(e)))
        return None


# Since the API limitation is 5 calls per minute, add a local cache to prevent calling the API too often
indicatorDataSet = {}  # {'symbol':data}


def get_fundamental_data(symbol: str, indicatorType: str) -> StockFundamentals:
    if indicatorType not in indicatorTypeSet:
        return StockFundamentals(
            error_message=f"Input indicator type '{indicatorType}' does not exist"
        )

    params = {"function": "OVERVIEW", "symbol": symbol, "datatype": "json"}

    try:
        # First check if the data is already in the data set to save an API call
        if (symbol in indicatorDataSet) and (
            get_market_reference_date()
            == indicatorDataSet[symbol].get("LatestTradingDate")
        ):
            data = indicatorDataSet[symbol]
        else:
            response = requests.get(
                RAPIDAPI_BASE_URL, headers=RAPIDAPI_HEADERS, params=params
            )
            response.raise_for_status()
            data = response.json()
            indicatorDataSet[symbol] = data

        if "Error Message" in data:
            return StockFundamentals(
                error_message=f"Error: The symbol '{symbol}' cannot be found."
            )
        if "Note" in data:
            return StockFundamentals(
                error_message="API call frequency exceeded. Please wait and try again later."
            )

        try:

            value = data[indicatorType]

            if (symbol in indicatorDataSet) and (
                get_market_reference_date()
                == indicatorDataSet[symbol].get("LatestTradingDate")
            ):
                latest_trading_day = indicatorDataSet[symbol]["LatestTradingDate"]
            else:
                # get the latest trading day from the API and add it into the local cache
                latest_trading_day = get_latest_trading_day(symbol)
                indicatorDataSet[symbol]["LatestTradingDate"] = latest_trading_day
            return StockFundamentals(
                value=value,
                indicator_type=indicatorType,
                symbol=symbol,
                latest_trading_day=latest_trading_day,
            )
        except KeyError:
            return StockFundamentals(
                error_message="Internal Error: Unexpected response structure."
            )
    except requests.exceptions.RequestException as e:
        return StockFundamentals(error_message=f"Network Error: {str(e)}")

    except Exception as e:
        return StockFundamentals(error_message=f"Unexpected Error: {str(e)}")


@dataclass
class StockPriceResult:
    price: Optional[float] = None
    last_refreshed_est: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error_message is None


def get_stock_price(symbol: str) -> StockPriceResult:
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "datatype": "json",
    }

    try:
        response = requests.get(
            RAPIDAPI_BASE_URL, headers=RAPIDAPI_HEADERS, params=params
        )
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            return StockPriceResult(
                error_message=f"Error: The symbol '{symbol}' cannot be found."
            )
        if "Note" in data:
            return StockPriceResult(
                error_message="API call frequency exceeded. Please wait and try again later."
            )

        try:
            last_refreshed_est = data["Meta Data"]["3. Last Refreshed"]
            last_close = float(
                data["Time Series (1min)"][last_refreshed_est]["4. close"]
            )
            return StockPriceResult(
                price=last_close, last_refreshed_est=last_refreshed_est
            )
        except KeyError:
            return StockPriceResult(
                error_message="Internal Error: Unexpected response structure."
            )
    except requests.exceptions.RequestException as e:
        return StockPriceResult(error_message=f"Network Error: {str(e)}")

    except Exception as e:
        return StockPriceResult(error_message=f"Unexpected Error: {str(e)}")
