# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 14:59:08 2020

@author: wenyu
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import scipy.stats as stats

#data processing
call = pd.read_excel("CallAuction.xlsx", header=2)
callauc = call.dropna(axis=1)
del callauc['Volume']

#determine maximum execution volume
supply = callauc['Supply'].values
demand = callauc['Demand'].values
T = len(supply)
number = range(T)
exvolume = np.zeros(T)
for x,y,i in zip(supply, demand, number):
    exvolume[i] = min(x, y)
callauc['exvolume'] = exvolume
exevolume = exvolume.max()
print('Maximum execution volume is ', exevolume)

#find execution price
expricerow = callauc.loc[callauc['exvolume'].idxmax()]
exprice = expricerow['Price']
exdemand = expricerow['Demand']
print('Opening price is ', exprice)


#initial opening order book after the call auction

for i in number[expricerow.name:]:
    if callauc.Demand[i] > 0:
        callauc.Demand[i] = 0
    if callauc.LimitBuyOrders[i] > 0:
        callauc.LimitBuyOrders[i] = 0
    callauc.Supply[i] -= exevolume

for z in number[:expricerow.name]:
    if callauc.Supply[z] > 0:
        callauc.Supply[z] = 0
    if callauc.LimitSellOrders[z] > 0:
        callauc.LimitSellOrders[z] = 0
    callauc.Demand[z] -= exevolume

del callauc['exvolume']
print('Order book after the call auction')
print(callauc)
    
callauc.to_csv("orderbook.csv")