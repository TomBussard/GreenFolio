"""
Application principale Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List

from config import (DEFAULT_TICKERS, RISK_PROFILES, SUSTAINABILITY_PREFERENCES,
                   BENCHMARKS, DEFAULT_BENCHMARKS)
from data_manager import (get_stock_data, get_portfolio_historical_data,
                         calculate_portfolio_metrics, get_benchmark_data,
                         filter_stocks_by_preference)
from visualization import (create_esg_gauge, create_sector_pie,
                         create_performance_chart, create_esg_radar,
                         create_risk_return_scatter)

# Configuration de la page
st.set_page_config(
    page_title="Portefeuille d'Investissement Durable",
    page_icon="🌱",
    layout="wide"
)

# Style personnalisé
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 10px 16px;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #2ecc71;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'risk_profile' not in st.session_state:
    st.session_state.risk_profile = "Équilibré"
if 'sustainability_preference' not in st.session_state:
    st.session_state.sustainability_preference = "Multi-thématique ESG"
if 'filtered_stocks' not in st.session_state:
    st.session_state.filtered_stocks = []

def main():
    st.title("🌱 Portefeuille d'Investissement Durable")
    
    # Création des onglets
    tabs = st.tabs(["📊 Profil", "🔨 Construction", "♻️ Dashboard ESG", "📈 Analyse Risques"])
    
    # Onglet Profil
    with tabs[0]:
        show_profile_tab()
    
    # Onglet Construction
    with tabs[1]:
        show_construction_tab()
    
    # Onglet Dashboard ESG
    with tabs[2]:
        show_esg_dashboard_tab()
    
    # Onglet Analyse Risques
    with tabs[3]:
        show_risk_analysis_tab()

def show_profile_tab():
    st.header("Définition du Profil d'Investissement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Profil de Risque")
        risk_profile = st.radio(
            "Choisissez votre profil de risque",
            list(RISK_PROFILES.keys()),
            index=list(RISK_PROFILES.keys()).index(st.session_state.risk_profile),
            help="Sélectionnez le profil qui correspond le mieux à votre tolérance au risque"
        )
        st.info(RISK_PROFILES[risk_profile]["description"])
        
        # Affichage de la répartition cible
        st.write("📊 Répartition cible :")
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            st.metric("Actions", f"{RISK_PROFILES[risk_profile]['actions']*100}%")
        with col1b:
            st.metric("Obligations", f"{RISK_PROFILES[risk_profile]['obligations']*100}%")
        with col1c:
            st.metric("Monétaire", f"{RISK_PROFILES[risk_profile]['monétaire']*100}%")
    
    with col2:
        st.subheader("🌿 Préférence Durable")
        sust_pref = st.radio(
            "Choisissez votre orientation durable",
            list(SUSTAINABILITY_PREFERENCES.keys()),
            index=list(SUSTAINABILITY_PREFERENCES.keys()).index(st.session_state.sustainability_preference),
            help="Définissez votre approche en matière d'investissement durable"
        )
        st.info(SUSTAINABILITY_PREFERENCES[sust_pref]["description"])
    
    if st.button("💾 Mettre à jour le profil", type="primary"):
        # Réinitialiser le portefeuille si la préférence durable change
        if st.session_state.sustainability_preference != sust_pref:
            st.session_state.portfolio = {}
            
            # Récupérer et filtrer les stocks selon la nouvelle préférence
            all_stocks = []
            for category, tickers in DEFAULT_TICKERS.items():
                for ticker in tickers.keys():
                    stock_data = get_stock_data(ticker)
                    if stock_data:
                        all_stocks.append(stock_data)
            
            st.session_state.filtered_stocks = filter_stocks_by_preference(
                all_stocks,
                sust_pref
            )
            
        st.session_state.risk_profile = risk_profile
        st.session_state.sustainability_preference = sust_pref
        st.success("✅ Profil mis à jour avec succès!")

def show_construction_tab():
    st.header("Construction du Portefeuille")
    
    # Affichage des actifs disponibles par catégorie
    st.subheader("🎯 Univers d'Investissement")
    
    # Récupération des stocks filtrés
    if not st.session_state.filtered_stocks:
        all_stocks = []
        for category, tickers in DEFAULT_TICKERS.items():
            for ticker in tickers.keys():
                stock_data = get_stock_data(ticker)
                if stock_data:
                    all_stocks.append(stock_data)
        
        st.session_state.filtered_stocks = filter_stocks_by_preference(
            all_stocks,
            st.session_state.sustainability_preference
        )
    
    # Création d'un dictionnaire pour accéder facilement aux données filtrées
    filtered_tickers = {
        stock["ticker"]: stock 
        for stock in st.session_state.filtered_stocks
    }
    
    selected_tickers = []
    for category, tickers in DEFAULT_TICKERS.items():
        category_tickers = {
            ticker: info for ticker, info in tickers.items()
            if ticker in filtered_tickers
        }
        
        if category_tickers:
            with st.expander(f"{category} ({len(category_tickers)} actifs)", expanded=True):
                for ticker, info in category_tickers.items():
                    data = filtered_tickers[ticker]
                    col1, col2, col3, col4 = st.columns([3,2,2,1])
                    
                    with col1:
                        st.write(f"**{data['name']}** ({ticker})")
                    
                    with col2:
                        # Affichage du score ESG avec les composantes
                        st.write(f"Score ESG: **{data['esg_score']:.1f}**")
                        st.markdown(
                            f"<span style='color: #666666; font-size: 0.8em;'>"
                            f"E: {data['environmental_score']:.1f} | "
                            f"S: {data['social_score']:.1f} | "
                            f"G: {data['governance_score']:.1f}"
                            f"</span>",
                            unsafe_allow_html=True
                        )
                    
                    with col3:
                        st.write(f"Vol: {data['volatility']*100:.1f}%")
                    
                    with col4:
                        default_checked = st.session_state.risk_profile in info["default_profiles"]
                        if st.checkbox("✓", 
                                     value=default_checked,
                                     key=f"select_{ticker}"):
                            selected_tickers.append(ticker)
    
    # Gestion des pondérations
    if selected_tickers:
        st.subheader("⚖️ Pondération du Portefeuille")
        
        # Calcul des poids suggérés selon le profil
        suggested_weights = {}
        total_selected = len(selected_tickers)
        if total_selected > 0:
            base_weight = 100.0 / total_selected
            for ticker in selected_tickers:
                suggested_weights[ticker] = base_weight
        
        weights = {}
        total_weight = 0
        
        cols = st.columns(len(selected_tickers))
        for i, ticker in enumerate(selected_tickers):
            with cols[i]:
                weight = st.number_input(
                    f"{ticker}",
                    min_value=0.0,
                    max_value=100.0,
                    value=suggested_weights.get(ticker, 0.0),
                    step=5.0,
                    format="%.1f",
                    key=f"weight_{ticker}"
                )
                weights[ticker] = weight
                total_weight += weight
        
        # Barre de progression pour le total des poids
        progress = min(total_weight / 100.0, 1.0)
        st.progress(progress, text=f"Total: {total_weight:.1f}%")
        
        if abs(total_weight - 100) > 0.01:
            st.warning("⚠️ La somme des poids doit être égale à 100%")
        else:
            if st.button("💾 Valider le portefeuille", type="primary"):
                st.session_state.portfolio = {t: w/100 for t, w in weights.items()}
                st.success("✅ Portefeuille mis à jour avec succès!")

def show_esg_dashboard_tab():
    st.header("Dashboard ESG")
    
    if not st.session_state.portfolio:
        st.warning("⚠️ Veuillez d'abord construire votre portefeuille dans l'onglet Construction")
        return
    
    # Calcul des métriques du portefeuille
    metrics = calculate_portfolio_metrics(
        st.session_state.portfolio,
        sustainability_preference=st.session_state.sustainability_preference
    )
    
    # Scores ESG
    st.subheader("🎯 Scores ESG")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(create_esg_gauge(
            metrics["environmental_score"],
            "Score Environnemental"
        ), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_esg_gauge(
            metrics["social_score"],
            "Score Social"
        ), use_container_width=True)
    
    with col3:
        st.plotly_chart(create_esg_gauge(
            metrics["governance_score"],
            "Score Gouvernance"
        ), use_container_width=True)
    
    # Graphiques détaillés
    st.subheader("📊 Analyse Détaillée")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_sector_pie(metrics["sector_exposure"]),
                       use_container_width=True)
    
    with col2:
        st.plotly_chart(create_esg_radar(metrics),
                       use_container_width=True)

def show_risk_analysis_tab():
    st.header("Analyse des Risques")
    
    if not st.session_state.portfolio:
        st.warning("⚠️ Veuillez d'abord construire votre portefeuille dans l'onglet Construction")
        return
    
    # Sélection de la période d'analyse
    st.subheader("📅 Période d'Analyse")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Date de début",
            value=datetime.now() - timedelta(days=365),
            min_value=datetime(2010, 1, 1),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "Date de fin",
            value=datetime.now(),
            min_value=start_date,
            max_value=datetime.now()
        )
    
    with col3:
        default_benchmark = DEFAULT_BENCHMARKS.get(st.session_state.risk_profile, "^GSPC")
        benchmark = st.selectbox(
            "Indice de référence",
            options=list(BENCHMARKS.keys()),
            index=list(BENCHMARKS.values()).index(default_benchmark),
            help="Sélectionnez l'indice de référence pour la comparaison"
        )
        benchmark_ticker = BENCHMARKS[benchmark]
    
    # Calcul des métriques avec la période sélectionnée
    metrics = calculate_portfolio_metrics(
        st.session_state.portfolio,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        benchmark_ticker,
        st.session_state.sustainability_preference
    )
    
    # Affichage des métriques de performance
    st.subheader("📊 Métriques de Performance")
    
    perf_metrics = metrics.get("performance_metrics", {})
    if perf_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Rendement Annualisé",
                f"{perf_metrics.get('annualized_return', 0)*100:.1f}%"
            )
        
        with col2:
            st.metric(
                "Volatilité Annualisée",
                f"{perf_metrics.get('annualized_volatility', 0)*100:.1f}%"
            )
        
        with col3:
            st.metric(
                "Ratio de Sharpe",
                f"{perf_metrics.get('sharpe_ratio', 0):.2f}"
            )
        
        with col4:
            st.metric(
                "Drawdown Maximum",
                f"{perf_metrics.get('max_drawdown', 0)*100:.1f}%"
            )
        
        if 'beta' in perf_metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Beta", f"{perf_metrics.get('beta', 1):.2f}")
            with col2:
                st.metric(
                    "Alpha",
                    f"{perf_metrics.get('alpha', 0)*100:.2f}%"
                )
    
    # Performance historique
    st.subheader("📈 Performance Historique")
    
    portfolio_values, _ = get_portfolio_historical_data(
        list(st.session_state.portfolio.keys()),
        list(st.session_state.portfolio.values()),
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    benchmark_values, _ = get_benchmark_data(
        benchmark_ticker,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    st.plotly_chart(
        create_performance_chart(portfolio_values, benchmark_values),
        use_container_width=True
    )
    
    # Analyse risque/rendement
    st.subheader("📊 Analyse Risque/Rendement")
    
    portfolio_data = [
        get_stock_data(ticker)
        for ticker in st.session_state.portfolio.keys()
    ]
    
    st.plotly_chart(
        create_risk_return_scatter(portfolio_data),
        use_container_width=True
    )

if __name__ == "__main__":
    main()