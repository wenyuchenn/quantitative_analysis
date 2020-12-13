# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 10:43:28 2020

@author: wenyu
"""

from queue import Queue
BUY = 0
SELL = 1

class OrderBook(object):
    def__init__(self):
        self.bid_prices = []
        self.bid_sizes = []
        self.offer_prices = []
        self.offer_sizes = []
        self.bids = {}
        self.offers = {}
        self.unprocessed_buy_orders = Queue()
        self.unprocessed_sell_orders = Queue()
        
    def max_bid_price(self):
        if self.bids:
            return max(self.bids.keys())
        
    def max_bid_qtd(self):
        if self.bids:
            return max(self.bids.values())

    def min_offer_price(self):
        if self.offers:
            return min(self.offers.keys())
        
    def min_offer_qtd(self):
        if self.offers:
            return max(self.offers.values())
        
    def main(self):
        #determine if the new order can be filled under the original order book
        if new_order.side == BUY:
            if new_order.price >= self.min_offer_price:
                self.unprocessed_buy_orders(new_order)
            else:
                self.bids.append(new_order)
        else:
            if new_order.price <= self.max_bid_price:
                self.unprocessed_sell_orders(new_order)
            else:
                self.offers.append(new_order)
        #ensure price is the priority, then comes the time priority at the same price level
        while not unprocessed_buy_orders.empty():
            if unprocessed_buy_orders.get().size <= self.min_offer_qtd:
                self.min_offer_qtd.pop(unprocessed_buy_orders.get().size)
            else:
                while unprocessed_buy_orders.get().size >= self.min_offer_qtd:
                    self.min_offer_qtd.pop()
            
        while not unprocessed_sell_orders.empty():
            if unprocessed_sell_orders.get().size >= self.min_offer_qtd:
                self.min_buy_qtd.pop(unprocessed_sell_orders.get().size)
            else:
                while unprocessed_buy_orders.get().size <= self.min_buy_qtd:
                    self.min_buy_qtd.pop()

    def print_orderbook(self):
        print("Resulting order book after execution is: ")
        print("Buy side:")
        for i in self.bids:
            print(self.bids[i])
        print()
        print("Sell side:")
        for i in self.offers:
            print(self.offers[i])




class Order(object):
    """Initialize new orders, assume market buy order price is 1e10 and
    market sell order price is 1e-10. Orders with price quotations are 
    limit orders.
    """
    def __init__(self, side, price, size):
        self.side = side
        self.price = price
        self.size = size

    def __repr__(self):
        return f'{self.side} {self.size} units at {self.price}'
