# GreenFolio

GreenFolio explores what happens to a portfolio when you change a sustainability preference. A user chooses a risk profile and an environmental, social or broader ESG preference, then inspects the holdings and their historical performance.

## Follow the portfolio

The profile determines the investment preferences. The construction view filters the equity universe and builds the allocation. Two further views show the portfolio's ESG exposures and its return, volatility and drawdown against a selected benchmark.

The app retrieves price and sustainability data through Yahoo Finance. When a sustainability score is unavailable, the code substitutes fixed defaults. Those values are illustrative and can affect which stocks pass a screen. [Data and screening logic](data_manager.py)

## One universe, four preferences

I ran the four screening rules on the same eight fictional companies. The environmental screen admitted two, the balanced ESG screen admitted six, the social screen admitted four and the general screen admitted seven. Lower risk scores are better. You can change a single company's inputs and see which threshold it crosses. [Offline example](example.py)

![Number of companies passing each sustainability screen](figures/screen-comparison.png)

## Run locally

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For the offline comparison, run `python example.py`. It reads no market feeds.

Portfolio by **Tom Bussard**.
