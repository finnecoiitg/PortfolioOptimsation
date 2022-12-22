#we'll use yfinance library to obtain the market data
import yfinance as yf
import pandas as pd
from Portfolio_Optimisation import *
import streamlit as st
import math
df=pd.read_csv('new_Tickers.csv')
countries=list(set(df['Country']))
countries.sort()
tickerList=dict([[country,[]] for country in countries])
for i in df.index:
	temp=df.loc[i]
	tickerList[temp['Country']].append(temp['object'])
for i in tickerList:
	tickerList[i].sort()
def calculations(stockList,period,risk_free_rate=0):

	symbols= " ".join(stockList)
	tickers=yf.Tickers(symbols)
	try:
		df=tickers.history(period=period+"y")['Close']
	except Exception as e:
		st.write("You might have choosen 2 same stocks!")
		st.write(e)
		return
	flag=0
	for i in df.columns:
		if math.isnan(df.loc[df.index[0],i]):
			flag=1
			print("Data not available for this period for the ticker "+str(i))
	if flag==1:
		exit(1)
	returns=df.pct_change()
	print(tickers.history(period=period+"y"))
	print(returns)
	mean_returns = returns.mean()
	cov_matrix = returns.cov()
	risk_free_rate = risk_free_rate
	return stockList,mean_returns, cov_matrix, risk_free_rate
def allocation(stockList,period,risk_free_rate=0):
	stockList,mean_returns, cov_matrix, risk_free_rate=calculations(stockList,period,risk_free_rate)
	return display_calculated_ef_with_random(stockList,mean_returns, cov_matrix, risk_free_rate)
# def efficient_frontier_allocate(stockList,period,risk,risk_free_rate=0):
# 	_,mean_returns,cov_matrix,_=calculations(stockList,period,risk_free_rate)
# 	max_returns=efficient_frontier(mean_returns,cov_matrix,[risk])
    

numberOfStocks=st.number_input('Number of Tickers',min_value=2)
risk_free_rate=st.number_input('Risk free rate')
period=str(st.number_input("Period of analysis (Eg input value 2 represents 2 years from now",min_value=1))
country=st.selectbox('Choose Region of Interest',countries)
stockList=[]
for i in range(numberOfStocks):
	stockList.append(st.selectbox('Choose Ticker {}'.format(i+1),tickerList[country],key=i).split('-')[-1])
if st.button("Allocate"):
	min_vol_allocation,max_sharpe_allocation=allocation(stockList,period,risk_free_rate)
	st.table(min_vol_allocation)
	# risk=st.number_input('Risk you can take')
	# if st.button("Efficient Frontier Allocation"):
	# 	st.table(efficient_frontier_allocate(stockList,period,risk_free_rate,risk))

	

