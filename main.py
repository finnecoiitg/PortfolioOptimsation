#we'll use yfinance library to obtain the market data
import yfinance as yf
import pandas as pd
from Portfolio_Optimisation import *
import streamlit as st
from streamlit import session_state as ss
import math

if 'initial_allocate_bool' not in ss:
	ss.initial_allocate_bool=0
def set_bool(key,value):
	ss[key]=value


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
		if math.isnan(df.loc[df.index[1],i]):
			flag=1
			st.write("Data not available for this period for the ticker "+str(i))
	if flag==1:
		exit(1)
	returns=df.pct_change()
	mean_returns = returns.mean()
	cov_matrix = returns.cov()
	risk_free_rate = risk_free_rate
	return stockList,mean_returns, cov_matrix, risk_free_rate

def allocation(stockList,period,risk_free_rate=0):
	stockList,mean_returns, cov_matrix, risk_free_rate=calculations(stockList,period,risk_free_rate)
	return display_calculated_ef_with_random(stockList,mean_returns, cov_matrix, risk_free_rate)

def efficient_frontier_allocate(stockList,period,target,risk_free_rate=0):
	_,mean_returns,cov_matrix,_=calculations(stockList,period,risk_free_rate)
	max_returns=efficient_return(mean_returns,cov_matrix,target)
	max_returns_allocation = pd.DataFrame(max_returns.x,index=stockList,columns=['allocation'])
	max_returns_allocation.allocation = [round(i*100,2)for i in max_returns_allocation.allocation]
	max_returns_allocation = max_returns_allocation.T
	return max_returns_allocation, max_returns.fun

numberOfStocks=st.number_input('Number of Tickers',min_value=2,on_change=set_bool, args=('initial_allocate_bool',0))
risk_free_rate=st.number_input('Risk free rate',on_change=set_bool, args=('initial_allocate_bool',0))
period=str(st.number_input("Period of analysis (Eg input value 2 represents 2 years from now)",min_value=1,on_change=set_bool, args=('initial_allocate_bool',0)))
country=st.selectbox('Choose Region of Interest',countries,on_change=set_bool, args=('initial_allocate_bool',0))
stockList=[]
for i in range(numberOfStocks):
	stockList.append(st.selectbox('Choose Ticker {}'.format(i+1),tickerList[country]).split('-')[-1])
stockList.sort()
allocate=st.button("Allocate", key="initial_allocate",on_click=set_bool, args=('initial_allocate_bool',1))
if ss.initial_allocate_bool:
	min_vol_allocation,max_sharpe_allocation=allocation(stockList,period,risk_free_rate)
	st.write("Minimum Volatility(≈Risk) Allocation")
	st.table(min_vol_allocation)
	st.write("Maximum Sharpe Allocation")
	st.table(max_sharpe_allocation)

	target=st.number_input('Required returns')
	if st.button("Efficient Frontier Allocation",on_click=set_bool, args=('initial_allocate_bool',1)):
		max_returns_allocation, volatility=efficient_frontier_allocate(stockList,period,risk_free_rate,target)
		st.write("Efficient Frontier Allocation")
		st.table(max_returns_allocation)
		st.write("with standard deviation"+str(round(volatility/math.sqrt(252)*100,2))+"%")

