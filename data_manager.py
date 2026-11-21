"""Financial data management and ESG"""

from screening import filter_stocks_by_preference as filter_stocks_by_preference

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Tuple, Optional
import logging

# Configuring the log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str) -> Optional[Dict]:
    """Recovers financial and ESG data from cached action"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty:
            logger.warning(f"Pas de données historiques pour {ticker}")
            return None

        info = stock.info
        if not info:
            logger.warning(f"Pas d'informations pour {ticker}")
            return None

        # Direct recovery of ESG scores from Yahoo Finance
        sustainability = stock.sustainability

        score_source = "Illustrative"
        if sustainability is not None and not sustainability.empty:
            try:
                # ESG scores are now directly in the index with a column 'esgScores'
                esg_data = {
                    "total": float(sustainability.loc["totalEsg", "esgScores"]),
                    "env": float(sustainability.loc["environmentScore", "esgScores"]),
                    "soc": float(sustainability.loc["socialScore", "esgScores"]),
                    "gov": float(sustainability.loc["governanceScore", "esgScores"]),
                }
                score_source = "Provider"
                logger.info(f"Scores ESG récupérés pour {ticker}: {esg_data}")

            except Exception as e:
                logger.error(f"Erreur lors de l'extraction des scores ESG pour {ticker}: {e}")
                esg_data = {"total": 19, "env": 10, "soc": 4, "gov": 5}
        else:
            esg_data = {"total": 19, "env": 10, "soc": 4, "gov": 5}
            logger.warning(f"Pas de données ESG disponibles pour {ticker}")

        # Calculation of yields and volatility
        returns = hist["Close"].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)

        data = {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "beta": info.get("beta", 1),
            "volatility": volatility,
            "esg_score": esg_data["total"],
            "score_source": score_source,
            "environmental_score": esg_data["env"],
            "social_score": esg_data["soc"],
            "governance_score": esg_data["gov"],
            "price": info.get("regularMarketPrice", 0),
            "currency": info.get("currency", "USD"),
            "returns_1y": returns.mean() * 252 * 100,  # Annualized as a percentage
        }

        return data

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données pour {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_portfolio_historical_data(
    tickers: List[str], weights: List[float], start_date: str = None, end_date: str = None
) -> Tuple[pd.Series, pd.Series]:
    """Recovers historical data for portfolio"""
    try:
        if not tickers or not weights:
            return pd.Series(), pd.Series()

        data = pd.DataFrame()
        returns = pd.DataFrame()
        valid_tickers = []
        valid_weights = []

        for ticker, weight in zip(tickers, weights):
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if not hist.empty and "Close" in hist.columns:
                data[ticker] = hist["Close"]
                returns[ticker] = hist["Close"].pct_change()
                valid_tickers.append(ticker)
                valid_weights.append(weight)

        if data.empty or not valid_tickers:
            return pd.Series(), pd.Series()

        # Normalizes weights
        total_weight = sum(valid_weights)
        normalized_weights = [w / total_weight for w in valid_weights]

        # Calculation of portfolio returns
        portfolio_returns = pd.Series(0, index=returns.index)
        for ticker, weight in zip(valid_tickers, normalized_weights):
            portfolio_returns += returns[ticker] * weight

        # Calculation of portfolio value
        portfolio_value = (1 + portfolio_returns).cumprod() * 100

        return portfolio_value, portfolio_returns

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données historiques: {str(e)}")
        return pd.Series(), pd.Series()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_benchmark_data(
    benchmark: str, start_date: str = None, end_date: str = None
) -> Tuple[pd.Series, pd.Series]:
    """Recovers historical data for the benchmark"""
    try:
        if not benchmark:
            return pd.Series(), pd.Series()

        benchmark_ticker = yf.Ticker(benchmark)
        hist = benchmark_ticker.history(start=start_date, end=end_date)

        if hist.empty or "Close" not in hist.columns:
            return pd.Series(), pd.Series()

        close_prices = hist["Close"]
        returns = close_prices.pct_change()
        normalized = (close_prices / close_prices.iloc[0]) * 100

        return normalized, returns

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données du benchmark: {str(e)}")
        return pd.Series(), pd.Series()


def calculate_metrics(returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict[str, float]:
    """Calculate advanced performance metrics"""
    try:
        if returns.empty:
            return {}

        metrics = {}

        # Annualized yield
        metrics["annualized_return"] = (1 + returns.mean()) ** 252 - 1

        # Annualised volatility
        metrics["annualized_volatility"] = returns.std() * np.sqrt(252)

        # Sharpe ratio (with risk-free rate of 2%)
        risk_free_rate = 0.02
        excess_returns = returns - risk_free_rate / 252
        if returns.std() != 0:
            metrics["sharpe_ratio"] = np.sqrt(252) * excess_returns.mean() / returns.std()
        else:
            metrics["sharpe_ratio"] = 0

        # Maximum Drawdown
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns / rolling_max - 1
        metrics["max_drawdown"] = drawdowns.min()

        # Beta et Alpha (si benchmark fourni)
        if benchmark_returns is not None and not benchmark_returns.empty:
            covariance = returns.cov(benchmark_returns)
            variance = benchmark_returns.var()

            if variance != 0:
                metrics["beta"] = covariance / variance
                metrics["alpha"] = (metrics["annualized_return"] - risk_free_rate) - metrics[
                    "beta"
                ] * ((1 + benchmark_returns.mean()) ** 252 - 1 - risk_free_rate)
            else:
                metrics["beta"] = 1
                metrics["alpha"] = 0

        return metrics

    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
        return {}


def calculate_portfolio_metrics(
    portfolio: Dict[str, float],
    start_date: str = None,
    end_date: str = None,
    benchmark: str = None,
    sustainability_preference: str = None,
) -> Dict:
    """Calculates portfolio metrics with durable preference filtering"""
    metrics = {
        "volatility": 0,
        "esg_score": 0,
        "environmental_score": 0,
        "social_score": 0,
        "governance_score": 0,
        "sector_exposure": {},
        "country_exposure": {},
        "performance_metrics": {},
    }

    if not portfolio:
        return metrics

    try:
        # Recovery of action data
        stocks_data = []
        for ticker in portfolio.keys():
            data = get_stock_data(ticker)
            if data:
                stocks_data.append(data)

        # Durable Preferential Filtering if specified
        if sustainability_preference:
            stocks_data = filter_stocks_by_preference(stocks_data, sustainability_preference)

            # Portfolio update with filtered actions only
            filtered_portfolio = {
                stock["ticker"]: portfolio[stock["ticker"]] for stock in stocks_data
            }
            portfolio = filtered_portfolio

        # Recovery of historical data
        portfolio_values, portfolio_returns = get_portfolio_historical_data(
            list(portfolio.keys()), list(portfolio.values()), start_date, end_date
        )

        # Retrieving Benchmark data if specified
        benchmark_values, benchmark_returns = None, None
        if benchmark:
            benchmark_values, benchmark_returns = get_benchmark_data(
                benchmark, start_date, end_date
            )

        # Calculation of performance metrics
        if not portfolio_returns.empty:
            metrics["performance_metrics"] = calculate_metrics(portfolio_returns, benchmark_returns)

        # Calculation of ESG metrics and exposures
        valid_weights = []
        for ticker, weight in portfolio.items():
            data = get_stock_data(ticker)
            if data:
                valid_weights.append(weight)

        if valid_weights:
            total_weight = sum(valid_weights)

            for ticker, weight in portfolio.items():
                data = get_stock_data(ticker)
                if data:
                    weight_normalized = weight / total_weight
                    metrics["esg_score"] += data["esg_score"] * weight_normalized
                    metrics["environmental_score"] += (
                        data["environmental_score"] * weight_normalized
                    )
                    metrics["social_score"] += data["social_score"] * weight_normalized
                    metrics["governance_score"] += data["governance_score"] * weight_normalized

                    sector = data["sector"]
                    if sector != "N/A":
                        metrics["sector_exposure"][sector] = (
                            metrics["sector_exposure"].get(sector, 0) + weight_normalized
                        )

                    country = data["country"]
                    if country != "N/A":
                        metrics["country_exposure"][country] = (
                            metrics["country_exposure"].get(country, 0) + weight_normalized
                        )

        return metrics

    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques du portefeuille: {str(e)}")
        return metrics
