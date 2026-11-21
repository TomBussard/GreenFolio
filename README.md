# GreenFolio

GreenFolio explores what happens to a portfolio when you change a sustainability preference. A user chooses a risk profile and an environmental, social or broader ESG preference, then inspects the holdings and their historical performance.

## Follow the portfolio

The profile determines the investment preferences. The construction view filters the equity universe and builds the allocation. Two further views show the portfolio's ESG exposures and its return, volatility and drawdown against a selected benchmark.

The live builder retrieves price and sustainability data through Yahoo Finance. Availability varies by ticker. The source and missing-data behaviour are described below.

## One universe, four preferences

I ran the four screening rules on the same eight fictional companies. The environmental screen admitted two, the balanced ESG screen admitted six, the social screen admitted four and the general screen admitted seven. Lower risk scores are better. You can change a single company's inputs and see which threshold it crosses. [Offline example](example.py)

![Number of companies passing each sustainability screen](figures/screen-comparison.png)

## Check a screen by hand

| Preference | Conditions, all of which must hold | Passing companies |
| --- | --- | --- |
| Environmental | Environmental < 4, total < 20, social and governance both < 12 | A, C |
| Balanced ESG | Total < 22, each component < 10, and at least one of environmental < 8, social < 8 or governance < 5 | A, B, C, E, F, G |
| Social | Social < 8, governance < 6 and total < 25 | B, C, E, G |
| General | Total < 25 and every component < 15 | A, B, C, D, E, F, G |

Let $E_i$, $S_i$, $G_i$ and $T_i$ be company $i$'s environmental, social, governance and total risk scores. The provider's total is a separate input to the rule. A company passes the environmental screen only when every inequality holds.

```math
\mathcal E=\{i:E_i<4,\ T_i<20,\ \max(S_i,G_i)<12\}
```

Company G has scores of 4, 4 and 4 and a total of 12. It passes the social and balanced screens. Its environmental score lands exactly on the boundary. Moving just that score from 4 to 3.9, while holding the other inputs fixed, would add G to the environmental selection.

### How the filter changes portfolio exposure

The builder suggests equal weights for the selected holdings and lets the user edit them. For any score $x_i$, the exposure view takes the weighted average over holdings $V$ for which it has data. The same aggregation can be checked on the eight-company fixture.

```math
\bar x_P=\frac{\sum_{i\in V}w_i x_i}{\sum_{i\in V}w_i}
```

| Equal-weight selection | Environmental score | Social score | Total risk score |
| --- | ---: | ---: | ---: |
| Environmental (A, C) | 2.50 | 7.50 | 15.00 |
| Social (B, C, E, G) | 5.00 | 5.25 | 14.50 |

For example, A and C have total scores of 17 and 13, so their equal-weight total is 15. The social selection improves the average social score by 2.25 points while doubling the environmental score. These quantities use only the fictional score data. In the historical view the app uses closing prices, applies the chosen weights to daily stock returns and compounds the result from a base of 100. [Screen inputs](example.py) · [Exposure and return calculations](data_manager.py)

The opening **Screen comparison** runs offline. **Portfolio builder** uses provider data when available. Missing provider scores are excluded by default. A sidebar switch can include clearly identified illustrative defaults to explore how missing data change the investable universe. [Exact selection rules](screening.py) · [Market data and performance metrics](data_manager.py) · [Portfolio charts](visualization.py)

## Run locally

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For the offline comparison, run `python example.py`. It reads no market feeds.

Tom Bussard
