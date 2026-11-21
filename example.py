"""Compare the actual screening rules on the same night fictional companies."""

from screening import filter_stocks_by_preference

SCORES = [
    (2, 9, 6, 17),
    (8, 5, 4, 17),
    (3, 6, 4, 13),
    (7, 9, 6, 22),
    (5, 6, 5, 16),
    (9, 8, 3, 20),
    (4, 4, 4, 12),
    (12, 10, 7, 29),
]
PREFERENCES = {
    "Environmental": "Net Zéro",
    "Balanced ESG": "Multi-thématique ESG",
    "Social": "Solidaire",
    "General": "General",
}


def compare():
    stocks = [
        dict(company=chr(65 + i), env=e, soc=s, gov=g, total=t)
        for i, (e, s, g, t) in enumerate(SCORES)
    ]
    return {
        name: [stock["company"] for stock in filter_stocks_by_preference(stocks, rule)]
        for name, rule in PREFERENCES.items()
    }


if __name__ == "__main__":
    for preference, names in compare().items():
        print(f"{preference}: {', '.join(names)}")
