"""Apply the sustainability screens used by the Streamlit portfolio builder."""

from math import isfinite


def filter_stocks_by_preference(stocks, preference):
    selected = []
    fields = [
        ("env", "environmental_score"),
        ("soc", "social_score"),
        ("gov", "governance_score"),
        ("total", "esg_score"),
    ]
    for stock in stocks or []:
        values = [stock.get(short, stock.get(long)) for short, long in fields]
        try:
            env, social, gov, total = map(float, values)
        except (ValueError, TypeError):
            continue
        # Missing scores used to look like zeros, which made them the best possible ratings.
        if not all(map(isfinite, (env, social, gov, total))):
            continue
        if preference == "Net Zéro":
            keep = env < 4 and total < 20 and max(social, gov) < 12
        elif preference == "Multi-thématique ESG":
            keep = total < 22 and max(env, social, gov) < 10 and (env < 8 or social < 8 or gov < 5)
        elif preference == "Solidaire":
            keep = social < 8 and gov < 6 and total < 25
        else:
            keep = total < 25 and max(env, social, gov) < 15
        if keep:
            selected.append(stock)
    return selected
