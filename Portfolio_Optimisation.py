#importing libraries required
import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
import streamlit as st

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
    '''
    Gives standard deviation, returns calculated for the portfolio with given weights and mean_returns.
    '''
    returns = np.sum(mean_returns*weights ) *252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return std, returns


def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    '''
    Negative Sharpe Ratio: calculated because to maximize the sharpe ration we are using scipy.optimize.minimize method. Therefore maximizing our sharpe ratio is equivalent to minimizing negative sharpe ration.
    '''
    p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
    return -(p_ret - risk_free_rate) / p_var


def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
    '''
    Based on calculated returns, covariance matrix and provided risk free rate, it returns the weights which provides the maximum sharpe ratio.
    The algorithm used for minimizing negative sharpe ratio (maximizing sharpe ratio) is Sequential Least Squares Programming (SLSQP) with the bounds on weights having value in the range (0,1) and constraints that sum of weights = 1.
    '''
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def portfolio_volatility(weights, mean_returns, cov_matrix):
    '''
    Gives standard deviation of returns over a time horizon of 1 year.
    '''
    return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]

def min_variance(mean_returns, cov_matrix):
    '''
    Based on calculated returns and covariance matrix, it returns the weights which provides the minimum portfolio volatility.
    The algorithm used for minimizing variance is Sequential Least Squares Programming (SLSQP) with the bounds on weights having value in the range (0,1) and constraints that sum of weights = 1.
    '''
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args,method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def efficient_return(mean_returns, cov_matrix, target):
    '''
    Based on calculated returns, covariance matrix and provided target returns it returns the weights which provides the minimum portfolio volatility (measured risk as considered by Harry Markowitz).
    The algorithm used for minimizing variance is Sequential Least Squares Programming (SLSQP) with the bounds on weights having value in the range (0,1) and constraints that sum of weights = 1 and portfolio returns for current allocated weights is equal to target returns.
    '''
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)

    def portfolio_return(weights):
        return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[1]

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for asset in range(num_assets))
    result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def efficient_frontier(mean_returns, cov_matrix, returns_range):
    efficients = []
    for ret in returns_range:
        efficients.append(efficient_return(mean_returns, cov_matrix, ret))
    return efficients

def display_calculated_ef_with_random(stockList,mean_returns, cov_matrix, risk_free_rate):
    max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
    # sdp, rp = portfolio_annualised_performance(max_sharpe.x, mean_returns, cov_matrix)
    max_sharpe_allocation = pd.DataFrame(max_sharpe.x,index=stockList,columns=['allocation'])
    max_sharpe_allocation.allocation = [round(i*100,2)for i in max_sharpe_allocation.allocation]
    max_sharpe_allocation = max_sharpe_allocation.T
    

    min_vol = min_variance(mean_returns, cov_matrix)
    # sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix)
    min_vol_allocation = pd.DataFrame(min_vol.x,index=stockList,columns=['allocation'])
    min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T
    return min_vol_allocation,max_sharpe_allocation
    

