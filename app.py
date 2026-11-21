"""
Application principale Streamlit
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import (
    DEFAULT_TICKERS,
    RISK_PROFILES,
    SUSTAINABILITY_PREFERENCES,
    BENCHMARKS,
    DEFAULT_BENCHMARKS,
)
from example import compare
from data_manager import (
    get_stock_data,
    get_portfolio_historical_data,
    calculate_portfolio_metrics,
    get_benchmark_data,
    filter_stocks_by_preference,
)
from visualization import (
    create_esg_gauge,
    create_sector_pie,
    create_performance_chart,
    create_esg_radar,
    create_risk_return_scatter,
)

# Page Configuration
st.set_page_config(page_title="GreenFolio", layout="wide")

# Custom Style
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Initialization of the status session
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = "Équilibré"
if "sustainability_preference" not in st.session_state:
    st.session_state.sustainability_preference = "Multi-thématique ESG"
if "filtered_stocks" not in st.session_state:
    st.session_state.filtered_stocks = None


def clear_screen():
    st.session_state.filtered_stocks = None
    st.session_state.portfolio = {}


def screened_universe(preference):
    candidates = []
    for category in DEFAULT_TICKERS.values():
        for ticker in category:
            data = get_stock_data(ticker)
            if data and (st.session_state.allow_defaults or data["score_source"] == "Provider"):
                candidates.append(data)
    return filter_stocks_by_preference(candidates, preference)


def main():
    st.title("GreenFolio")

    source = st.sidebar.radio("Workspace", ["Screen comparison", "Portfolio builder"])
    if source == "Screen comparison":
        st.write("Apply four sustainability screens to the same eight fictional companies.")
        outcomes = compare()
        counts = pd.Series(
            {name: len(names) for name, names in outcomes.items()}, name="Companies selected"
        )
        st.bar_chart(counts)
        st.dataframe(
            pd.DataFrame(
                {
                    "Screen": list(outcomes),
                    "Companies passing": [", ".join(names) for names in outcomes.values()],
                }
            ),
            hide_index=True,
        )
        st.caption("Each row uses the same scores. Lower values mean lower measured risk.")
        return
    st.sidebar.checkbox(
        "Include illustrative scores when provider data are missing",
        key="allow_defaults",
        on_change=clear_screen,
    )
    # Creating tabs
    tabs = st.tabs(["Profile", "Portfolio", "ESG exposures", "Risk analysis"])

    # Profile tab
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
    st.header("Investment preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk profile")
        risk_profile = st.radio(
            "Risk profile",
            list(RISK_PROFILES.keys()),
            format_func={
                "Prudent": "Conservative",
                "Équilibré": "Balanced",
                "Dynamique": "Growth",
            }.get,
            index=list(RISK_PROFILES.keys()).index(st.session_state.risk_profile),
            help="Select the profile that best matches your risk tolerance",
        )
        st.info(RISK_PROFILES[risk_profile]["description"])

        # View target distribution
        st.write("Target distribution:")
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            st.metric("Equities", f"{RISK_PROFILES[risk_profile]['actions'] * 100}%")
        with col1b:
            st.metric("Bonds", f"{RISK_PROFILES[risk_profile]['obligations'] * 100}%")
        with col1c:
            st.metric("Cash", f"{RISK_PROFILES[risk_profile]['monétaire'] * 100}%")

    with col2:
        st.subheader("Sustainability preference")
        sust_pref = st.radio(
            "Choisissez votre orientation durable",
            list(SUSTAINABILITY_PREFERENCES.keys()),
            format_func={
                "Net Zéro": "Environmental",
                "Multi-thématique ESG": "Balanced ESG",
                "Solidaire": "Social",
            }.get,
            index=list(SUSTAINABILITY_PREFERENCES.keys()).index(
                st.session_state.sustainability_preference
            ),
            help="Define your approach to sustainable investment",
        )
        st.info(SUSTAINABILITY_PREFERENCES[sust_pref]["description"])

    if st.button("Update Profile", type="primary"):
        # Reset portfolio if sustainable preference changes
        if st.session_state.sustainability_preference != sust_pref:
            st.session_state.portfolio = {}

            # Recover and filter stocks according to new preference
            st.session_state.filtered_stocks = screened_universe(sust_pref)

        st.session_state.risk_profile = risk_profile
        st.session_state.sustainability_preference = sust_pref
        st.success("Profile updated.")


def show_construction_tab():
    st.header("Portfolio construction")

    # Display of assets available by category
    st.subheader("Investment universe")

    # Recovery of filtered stocks
    if st.session_state.filtered_stocks is None:
        st.session_state.filtered_stocks = screened_universe(
            st.session_state.sustainability_preference
        )
    if not st.session_state.filtered_stocks:
        st.info("No companies meet this screen with the available scores.")

    # Creating a dictionary to easily access filtered data
    filtered_tickers = {stock["ticker"]: stock for stock in st.session_state.filtered_stocks}

    selected_tickers = []
    for category, tickers in DEFAULT_TICKERS.items():
        category_tickers = {
            ticker: info for ticker, info in tickers.items() if ticker in filtered_tickers
        }

        if category_tickers:
            with st.expander(f"{category} ({len(category_tickers)} stocks)", expanded=True):
                for ticker, info in category_tickers.items():
                    data = filtered_tickers[ticker]
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                    with col1:
                        st.write(f"**{data['name']}** ({ticker})")

                    with col2:
                        # Display ESG score with components
                        st.write(f"ESG risk: **{data['esg_score']:.1f}**")
                        st.caption(data["score_source"])
                        st.markdown(
                            f"<span style='color: #666666; font-size: 0.8em;'>"
                            f"E: {data['environmental_score']:.1f} | "
                            f"S: {data['social_score']:.1f} | "
                            f"G: {data['governance_score']:.1f}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    with col3:
                        st.write(f"Vol: {data['volatility'] * 100:.1f}%")

                    with col4:
                        default_checked = st.session_state.risk_profile in info["default_profiles"]
                        if st.checkbox("", value=default_checked, key=f"select_{ticker}"):
                            selected_tickers.append(ticker)

    # Weighting management
    if selected_tickers:
        st.subheader("Portfolio weighting")

        # Calculation of suggested weights according to profile
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
                    key=f"weight_{ticker}",
                )
                weights[ticker] = weight
                total_weight += weight

        # Progress bar for total weight
        progress = min(total_weight / 100.0, 1.0)
        st.progress(progress, text=f"Total: {total_weight:.1f}%")

        if abs(total_weight - 100) > 0.01:
            st.warning("The sum of the weights must be equal to 100%")
        else:
            if st.button("Validate the portfolio", type="primary"):
                st.session_state.portfolio = {t: w / 100 for t, w in weights.items()}
                st.success("Portfolio successfully updated!")


def show_esg_dashboard_tab():
    st.header("ESG exposures")

    if not st.session_state.portfolio:
        st.warning("Please first build your wallet in the Construction tab")
        return

    # Calculation of portfolio metrics
    metrics = calculate_portfolio_metrics(
        st.session_state.portfolio,
        sustainability_preference=st.session_state.sustainability_preference,
    )

    # Scores ESG
    st.subheader(" Scores ESG")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            create_esg_gauge(metrics["environmental_score"], "Score Environnemental"),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            create_esg_gauge(metrics["social_score"], "Score Social"), use_container_width=True
        )

    with col3:
        st.plotly_chart(
            create_esg_gauge(metrics["governance_score"], "Score Gouvernance"),
            use_container_width=True,
        )

    # Detailed graphs
    st.subheader("Detailed analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_sector_pie(metrics["sector_exposure"]), use_container_width=True)

    with col2:
        st.plotly_chart(create_esg_radar(metrics), use_container_width=True)


def show_risk_analysis_tab():
    st.header("Risk analysis")

    if not st.session_state.portfolio:
        st.warning("Please first build your wallet in the Construction tab")
        return

    # Selection of the period of analysis
    st.subheader("Analysis period")
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input(
            "Start date",
            value=datetime.now() - timedelta(days=365),
            min_value=datetime(2010, 1, 1),
            max_value=datetime.now(),
        )

    with col2:
        end_date = st.date_input(
            "Date de fin", value=datetime.now(), min_value=start_date, max_value=datetime.now()
        )

    with col3:
        default_benchmark = DEFAULT_BENCHMARKS.get(st.session_state.risk_profile, "^GSPC")
        benchmark = st.selectbox(
            "Reference index",
            options=list(BENCHMARKS.keys()),
            index=list(BENCHMARKS.values()).index(default_benchmark),
            help="Select the benchmark for comparison",
        )
        benchmark_ticker = BENCHMARKS[benchmark]

    # Calculation of the metrics with the selected period
    metrics = calculate_portfolio_metrics(
        st.session_state.portfolio,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        benchmark_ticker,
        st.session_state.sustainability_preference,
    )

    # Display performance metrics
    st.subheader("Performance metrics")

    perf_metrics = metrics.get("performance_metrics", {})
    if perf_metrics:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Annualized yield", f"{perf_metrics.get('annualized_return', 0) * 100:.1f}%")

        with col2:
            st.metric(
                "Volatility Annualized",
                f"{perf_metrics.get('annualized_volatility', 0) * 100:.1f}%",
            )

        with col3:
            st.metric("Ratio de Sharpe", f"{perf_metrics.get('sharpe_ratio', 0):.2f}")

        with col4:
            st.metric("Drawdown Maximum", f"{perf_metrics.get('max_drawdown', 0) * 100:.1f}%")

        if "beta" in perf_metrics:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Beta", f"{perf_metrics.get('beta', 1):.2f}")
            with col2:
                st.metric("Alpha", f"{perf_metrics.get('alpha', 0) * 100:.2f}%")

    # Performance historique
    st.subheader(" Performance Historique")

    portfolio_values, _ = get_portfolio_historical_data(
        list(st.session_state.portfolio.keys()),
        list(st.session_state.portfolio.values()),
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

    benchmark_values, _ = get_benchmark_data(
        benchmark_ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    st.plotly_chart(
        create_performance_chart(portfolio_values, benchmark_values), use_container_width=True
    )

    # Risk/return analysis
    st.subheader("Risk and return")

    portfolio_data = [get_stock_data(ticker) for ticker in st.session_state.portfolio.keys()]

    st.plotly_chart(create_risk_return_scatter(portfolio_data), use_container_width=True)


if __name__ == "__main__":
    main()
