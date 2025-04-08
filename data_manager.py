"""
Gestion des données financières et ESG
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple, Optional
import logging
from functools import lru_cache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def filter_stocks_by_preference(stocks: List[Dict], preference: str) -> List[Dict]:
    """
    Filtre les actions en fonction de la préférence durable
    Scores ESG de Yahoo Finance : plus le score est bas, meilleure est la performance ESG
    """
    if not stocks:
        return []

    filtered_stocks = []
    
    for stock in stocks:
        env_score = stock.get("env", stock.get("environmental_score", 0))
        soc_score = stock.get("soc", stock.get("social_score", 0))
        gov_score = stock.get("gov", stock.get("governance_score", 0))
        total_score = stock.get("total", stock.get("esg_score", 0))
        
        if preference == "Net Zéro":
            # Critères pour Net Zéro:
            # - Score environnemental excellent (< 4, basé sur les meilleures performances)
            # - Score total bon (< 20, médiane observée)
            # - Autres scores acceptables
            if (env_score < 4.0 and  # Les meilleurs scores env sont entre 0.4 et 3.0
                total_score < 20.0 and  # La médiane est autour de 20
                max(soc_score, gov_score) < 12.0):  # Scores sociaux et gouvernance raisonnables
                filtered_stocks.append(stock)
                
        elif preference == "Multi-thématique ESG":
            # Critères pour Multi-thématique:
            # - Score total modéré
            # - Tous les scores individuels équilibrés
            if (total_score < 22.0 and  # Plus permissif sur le total
                max(env_score, soc_score, gov_score) < 10.0 and  # Équilibre des scores
                (env_score < 8.0 or soc_score < 8.0 or gov_score < 5.0)):  # Au moins un bon score
                filtered_stocks.append(stock)
                
        elif preference == "Solidaire":
            # Critères pour Solidaire:
            # - Focus sur le score social
            # - Bonne gouvernance
            if (soc_score < 8.0 and  # Les bons scores sociaux sont < 8
                gov_score < 6.0 and  # Gouvernance solide
                total_score < 25.0):  # Score total acceptable
                filtered_stocks.append(stock)
        else:
            # Filtre par défaut:
            # - Score total raisonnable
            # - Pas de très mauvais scores individuels
            if (total_score < 25.0 and
                max(env_score, soc_score, gov_score) < 15.0):
                filtered_stocks.append(stock)
            
    return filtered_stocks

@st.cache_data(ttl=3600)
def get_stock_data(ticker: str) -> Optional[Dict]:
    """
    Récupère les données financières et ESG d'une action avec mise en cache
    """
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
        
        # Récupération directe des scores ESG depuis Yahoo Finance
        sustainability = stock.sustainability
        
        if sustainability is not None and not sustainability.empty:
            try:
                # Les scores ESG sont maintenant directement dans l'index avec une colonne 'esgScores'
                esg_data = {
                    "total": float(sustainability.loc["totalEsg", "esgScores"]),
                    "env": float(sustainability.loc["environmentScore", "esgScores"]),
                    "soc": float(sustainability.loc["socialScore", "esgScores"]),
                    "gov": float(sustainability.loc["governanceScore", "esgScores"])
                }
                logger.info(f"Scores ESG récupérés pour {ticker}: {esg_data}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction des scores ESG pour {ticker}: {e}")
                esg_data = {"total": 19, "env": 10, "soc": 4, "gov": 5}
        else:
            esg_data = {"total": 19, "env": 10, "soc": 4, "gov": 5}
            logger.warning(f"Pas de données ESG disponibles pour {ticker}")
        
        # Calcul des rendements et volatilité
        returns = hist['Close'].pct_change().dropna()
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
            "environmental_score": esg_data["env"],
            "social_score": esg_data["soc"],
            "governance_score": esg_data["gov"],
            "price": info.get("regularMarketPrice", 0),
            "currency": info.get("currency", "USD"),
            "returns_1y": returns.mean() * 252 * 100  # Annualisé en pourcentage
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données pour {ticker}: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def get_portfolio_historical_data(tickers: List[str], weights: List[float], 
                                start_date: str = None, end_date: str = None) -> Tuple[pd.Series, pd.Series]:
    """
    Récupère les données historiques pour le portefeuille
    """
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
            
            if not hist.empty and 'Close' in hist.columns:
                data[ticker] = hist['Close']
                returns[ticker] = hist['Close'].pct_change()
                valid_tickers.append(ticker)
                valid_weights.append(weight)
        
        if data.empty or not valid_tickers:
            return pd.Series(), pd.Series()
            
        # Normalise les poids
        total_weight = sum(valid_weights)
        normalized_weights = [w/total_weight for w in valid_weights]
        
        # Calcul des rendements du portefeuille
        portfolio_returns = pd.Series(0, index=returns.index)
        for ticker, weight in zip(valid_tickers, normalized_weights):
            portfolio_returns += returns[ticker] * weight
        
        # Calcul de la valeur du portefeuille
        portfolio_value = (1 + portfolio_returns).cumprod() * 100
        
        return portfolio_value, portfolio_returns
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données historiques: {str(e)}")
        return pd.Series(), pd.Series()

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def get_benchmark_data(benchmark: str, start_date: str = None, end_date: str = None) -> Tuple[pd.Series, pd.Series]:
    """
    Récupère les données historiques pour l'indice de référence
    """
    try:
        if not benchmark:
            return pd.Series(), pd.Series()
            
        benchmark_ticker = yf.Ticker(benchmark)
        hist = benchmark_ticker.history(start=start_date, end=end_date)
        
        if hist.empty or 'Close' not in hist.columns:
            return pd.Series(), pd.Series()
            
        close_prices = hist['Close']
        returns = close_prices.pct_change()
        normalized = (close_prices / close_prices.iloc[0]) * 100
        
        return normalized, returns
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données du benchmark: {str(e)}")
        return pd.Series(), pd.Series()

def calculate_metrics(returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict[str, float]:
    """
    Calcule les métriques de performance avancées
    """
    try:
        if returns.empty:
            return {}
            
        metrics = {}
        
        # Rendement annualisé
        metrics['annualized_return'] = (1 + returns.mean()) ** 252 - 1
        
        # Volatilité annualisée
        metrics['annualized_volatility'] = returns.std() * np.sqrt(252)
        
        # Ratio de Sharpe (avec taux sans risque de 2%)
        risk_free_rate = 0.02
        excess_returns = returns - risk_free_rate/252
        if returns.std() != 0:
            metrics['sharpe_ratio'] = np.sqrt(252) * excess_returns.mean() / returns.std()
        else:
            metrics['sharpe_ratio'] = 0
        
        # Maximum Drawdown
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns/rolling_max - 1
        metrics['max_drawdown'] = drawdowns.min()
        
        # Beta et Alpha (si benchmark fourni)
        if benchmark_returns is not None and not benchmark_returns.empty:
            covariance = returns.cov(benchmark_returns)
            variance = benchmark_returns.var()
            
            if variance != 0:
                metrics['beta'] = covariance / variance
                metrics['alpha'] = (metrics['annualized_return'] - risk_free_rate) - \
                                metrics['beta'] * ((1 + benchmark_returns.mean()) ** 252 - 1 - risk_free_rate)
            else:
                metrics['beta'] = 1
                metrics['alpha'] = 0
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
        return {}

def calculate_portfolio_metrics(portfolio: Dict[str, float], 
                             start_date: str = None, 
                             end_date: str = None,
                             benchmark: str = None,
                             sustainability_preference: str = None) -> Dict:
    """
    Calcule les métriques du portefeuille avec filtrage par préférence durable
    """
    metrics = {
        "volatility": 0,
        "esg_score": 0,
        "environmental_score": 0,
        "social_score": 0,
        "governance_score": 0,
        "sector_exposure": {},
        "country_exposure": {},
        "performance_metrics": {}
    }
    
    if not portfolio:
        return metrics
    
    try:
        # Récupération des données des actions
        stocks_data = []
        for ticker in portfolio.keys():
            data = get_stock_data(ticker)
            if data:
                stocks_data.append(data)
        
        # Filtrage par préférence durable si spécifiée
        if sustainability_preference:
            stocks_data = filter_stocks_by_preference(stocks_data, sustainability_preference)
            
            # Mise à jour du portfolio avec uniquement les actions filtrées
            filtered_portfolio = {
                stock["ticker"]: portfolio[stock["ticker"]]
                for stock in stocks_data
            }
            portfolio = filtered_portfolio
        
        # Récupération des données historiques
        portfolio_values, portfolio_returns = get_portfolio_historical_data(
            list(portfolio.keys()),
            list(portfolio.values()),
            start_date,
            end_date
        )
        
        # Récupération des données du benchmark si spécifié
        benchmark_values, benchmark_returns = None, None
        if benchmark:
            benchmark_values, benchmark_returns = get_benchmark_data(benchmark, start_date, end_date)
        
        # Calcul des métriques de performance
        if not portfolio_returns.empty:
            metrics["performance_metrics"] = calculate_metrics(portfolio_returns, benchmark_returns)
        
        # Calcul des métriques ESG et expositions
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
                    metrics["environmental_score"] += data["environmental_score"] * weight_normalized
                    metrics["social_score"] += data["social_score"] * weight_normalized
                    metrics["governance_score"] += data["governance_score"] * weight_normalized
                    
                    sector = data["sector"]
                    if sector != "N/A":
                        metrics["sector_exposure"][sector] = metrics["sector_exposure"].get(sector, 0) + weight_normalized
                    
                    country = data["country"]
                    if country != "N/A":
                        metrics["country_exposure"][country] = metrics["country_exposure"].get(country, 0) + weight_normalized
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques du portefeuille: {str(e)}")
        return metrics