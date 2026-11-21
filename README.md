# GreenFolio

GreenFolio explores what happens to a portfolio when you change a sustainability preference. A user chooses a risk profile and an environmental, social or broader ESG preference, then inspects the holdings and their historical performance.

## Follow the portfolio

The profile determines the investment preferences. The construction view filters the equity universe and builds the allocation. Two further views show the portfolio's ESG exposures and its return, volatility and drawdown against a selected benchmark.

The app retrieves price and sustainability data through Yahoo Finance. When a sustainability score is unavailable, the code substitutes fixed defaults. Those values are illustrative and can affect which stocks pass a screen. [Data and screening logic](data_manager.py)

## Run locally

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The original project also includes a written presentation. [Project report](Projet.pdf)
