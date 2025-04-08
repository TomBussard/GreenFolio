"""
Configuration de l'application
"""

# Liste des actions durables par défaut
DEFAULT_TICKERS = {
    "Technologies": {
        "AAPL": {"name": "Apple Inc.", "default_profiles": ["Équilibré", "Dynamique"]},
        "MSFT": {"name": "Microsoft Corp.", "default_profiles": ["Prudent", "Équilibré", "Dynamique"]},
        "GOOGL": {"name": "Alphabet Inc.", "default_profiles": ["Dynamique"]},
        "NVDA": {"name": "NVIDIA Corp.", "default_profiles": ["Dynamique"]},
        "CRM": {"name": "Salesforce", "default_profiles": ["Équilibré", "Dynamique"]},
        "ADBE": {"name": "Adobe Inc.", "default_profiles": ["Dynamique"]},
        "CSCO": {"name": "Cisco Systems", "default_profiles": ["Prudent", "Équilibré"]},
        "INTC": {"name": "Intel Corporation", "default_profiles": ["Prudent", "Équilibré"]}
    },
    "Énergies Renouvelables": {
        "ENPH": {"name": "Enphase Energy", "default_profiles": ["Dynamique"]},
        "SEDG": {"name": "SolarEdge Technologies", "default_profiles": ["Dynamique"]},
        "NEE": {"name": "NextEra Energy", "default_profiles": ["Prudent", "Équilibré"]},
        "FSLR": {"name": "First Solar", "default_profiles": ["Dynamique"]},
        "RUN": {"name": "Sunrun Inc.", "default_profiles": ["Dynamique"]},
        "BEP": {"name": "Brookfield Renewable", "default_profiles": ["Prudent", "Équilibré"]}
    },
    "Mobilité Durable": {
        "TSLA": {"name": "Tesla Inc.", "default_profiles": ["Dynamique"]},
        "NIO": {"name": "NIO Inc.", "default_profiles": ["Dynamique"]},
        "RIVN": {"name": "Rivian Automotive", "default_profiles": ["Dynamique"]},
        "ALB": {"name": "Albemarle Corporation", "default_profiles": ["Équilibré"]},
        "GM": {"name": "General Motors", "default_profiles": ["Équilibré"]}
    },
    "Santé": {
        "JNJ": {"name": "Johnson & Johnson", "default_profiles": ["Prudent", "Équilibré"]},
        "ABBV": {"name": "AbbVie Inc.", "default_profiles": ["Prudent", "Équilibré"]},
        "AMGN": {"name": "Amgen Inc.", "default_profiles": ["Équilibré"]},
        "UNH": {"name": "UnitedHealth Group", "default_profiles": ["Prudent", "Équilibré"]},
        "DHR": {"name": "Danaher Corporation", "default_profiles": ["Équilibré"]},
        "TMO": {"name": "Thermo Fisher Scientific", "default_profiles": ["Équilibré"]},
        "ISRG": {"name": "Intuitive Surgical", "default_profiles": ["Dynamique"]},
        "GILD": {"name": "Gilead Sciences", "default_profiles": ["Prudent", "Équilibré"]}
    },
    "Finance Durable": {
        "BLK": {"name": "BlackRock Inc.", "default_profiles": ["Prudent", "Équilibré"]},
        "MS": {"name": "Morgan Stanley", "default_profiles": ["Équilibré"]},
        "GS": {"name": "Goldman Sachs", "default_profiles": ["Dynamique"]},
        "JPM": {"name": "JPMorgan Chase", "default_profiles": ["Prudent", "Équilibré"]},
        "V": {"name": "Visa Inc.", "default_profiles": ["Prudent", "Équilibré"]},
        "MA": {"name": "Mastercard", "default_profiles": ["Équilibré"]},
        "SPGI": {"name": "S&P Global", "default_profiles": ["Équilibré"]},
        "SCHW": {"name": "Charles Schwab", "default_profiles": ["Équilibré"]}
    },
    "Économie Circulaire": {
        "WM": {"name": "Waste Management", "default_profiles": ["Prudent"]},
        "RSG": {"name": "Republic Services", "default_profiles": ["Prudent"]},
        "TTEK": {"name": "Tetra Tech", "default_profiles": ["Équilibré"]},
        "WSM": {"name": "Williams-Sonoma", "default_profiles": ["Équilibré"]},
        "KHC": {"name": "Kraft Heinz", "default_profiles": ["Prudent"]},
        "DNKG": {"name": "Danone", "default_profiles": ["Prudent"]},
    },
    "Eau": {
        "AWK": {"name": "American Water Works", "default_profiles": ["Prudent"]},
        "XYL": {"name": "Xylem Inc.", "default_profiles": ["Équilibré"]},
        "WTRG": {"name": "Essential Utilities", "default_profiles": ["Prudent"]},
        "PNR": {"name": "Pentair", "default_profiles": ["Équilibré"]},
        "VIE": {"name": "Veolia Environnement", "default_profiles": ["Prudent"]},
        "ECL": {"name": "Ecolab Inc.", "default_profiles": ["Équilibré"]},
        "IEX": {"name": "IDEX Corporation", "default_profiles": ["Équilibré"]}
    },
    "Agriculture Durable": {
        "ADM": {"name": "Archer-Daniels-Midland", "default_profiles": ["Prudent"]},
        "DE": {"name": "Deere & Company", "default_profiles": ["Équilibré"]},
        "CTVA": {"name": "Corteva Inc.", "default_profiles": ["Équilibré"]},
        "NTR": {"name": "Nutrien Ltd.", "default_profiles": ["Équilibré"]},
        "FMC": {"name": "FMC Corporation", "default_profiles": ["Équilibré"]},
        "SMG": {"name": "Scotts Miracle-Gro", "default_profiles": ["Dynamique"]},
        "AGCO": {"name": "AGCO Corporation", "default_profiles": ["Équilibré"]},
        "TSN": {"name": "Tyson Foods", "default_profiles": ["Prudent"]}
    },
    "Construction Durable": {
        "CAT": {"name": "Caterpillar Inc.", "default_profiles": ["Équilibré"]},
        "VMC": {"name": "Vulcan Materials", "default_profiles": ["Équilibré"]},
        "MLM": {"name": "Martin Marietta", "default_profiles": ["Équilibré"]},
        "CARR": {"name": "Carrier Global", "default_profiles": ["Équilibré"]},
        "JCI": {"name": "Johnson Controls", "default_profiles": ["Équilibré"]},
        "GNRC": {"name": "Generac Holdings", "default_profiles": ["Dynamique"]},
        "LIN": {"name": "Linde plc", "default_profiles": ["Prudent", "Équilibré"]},
        "SHW": {"name": "Sherwin-Williams", "default_profiles": ["Équilibré"]}
    }
}
# Profils de risque prédéfinis
RISK_PROFILES = {
    "Prudent": {
        "actions": 0.30,
        "obligations": 0.60,
        "monétaire": 0.10,
        "volatilité_max": 10,
        "description": "Privilégie la sécurité du capital avec une exposition limitée aux actions"
    },
    "Équilibré": {
        "actions": 0.60,
        "obligations": 0.35,
        "monétaire": 0.05,
        "volatilité_max": 15,
        "description": "Recherche un compromis entre rendement et risque"
    },
    "Dynamique": {
        "actions": 0.90,
        "obligations": 0.10,
        "monétaire": 0.00,
        "volatilité_max": 25,
        "description": "Maximise le rendement potentiel avec une forte exposition aux actions"
    }
}

# Préférences durables
SUSTAINABILITY_PREFERENCES = {
    "Net Zéro": {
        "exclusions": ["coal", "oil", "gas"],
        "min_environmental_score": 70,
        "description": "Vise la neutralité carbone, exclut les énergies fossiles"
    },
    "Multi-thématique ESG": {
        "min_esg_score": 60,
        "balanced_weights": True,
        "description": "Approche équilibrée sur les critères ESG"
    },
    "Solidaire": {
        "min_social_score": 70,
        "impact_focus": True,
        "description": "Privilégie l'impact social positif"
    }
}

# Paramètres de visualisation
CHART_COLORS = {
    "green": "#2ecc71",
    "red": "#e74c3c",
    "blue": "#3498db",
    "orange": "#f39c12",
    "purple": "#9b59b6"
}

# Benchmarks disponibles
BENCHMARKS = {
    "S&P 500": "^GSPC",
    "NASDAQ Composite": "^IXIC",
    "Dow Jones": "^DJI",
    "MSCI World": "URTH",
    "MSCI ESG Leaders": "SUSA"
}

# Benchmark par défaut selon le profil
DEFAULT_BENCHMARKS = {
    "Prudent": "^GSPC",  # S&P 500 pour profil prudent
    "Équilibré": "URTH", # MSCI World pour profil équilibré
    "Dynamique": "^IXIC" # NASDAQ pour profil dynamique
}