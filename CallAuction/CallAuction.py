import csv
import random

import matplotlib.pyplot as plt


def make_random_orders():
    buy_orders, sell_orders = [], []
    prices = [random.normalvariate(100, 30) for i in range(1, 1001)]
    for price in prices:
        side = random.choice(['buy', 'sell'])
        qty = int(random.normalvariate(20, 5))
        if side.lower() == 'sell':
            sell_orders.append((price, qty))
        else:
            buy_orders.append((price, qty))

    sell_orders.sort(key=lambda x: x[0], reverse=False)
    buy_orders.sort(key=lambda x: x[0], reverse=True)
    return buy_orders, sell_orders


def read_orders_from_file(file_name):
    """ Read and sort all orders from a file.
    The file contains orders in the format: price, side, quantity
    Add all orders to either buy or sell orders
    and then sort orders (buy: ascending; sell: descending)
    """

    buy_orders, sell_orders = [], []
    with open(file_name, newline='\n', encoding='utf-8') as csvfile:
        order_reader = csv.reader(csvfile)
        for order in order_reader:
            price = round(float(order[0]), 2)
            side = order[1].strip().lower()
            qty = float(order[2])
            if side.lower() == 'sell':
                sell_orders.append((price, qty))
            else:
                buy_orders.append((price, qty))

    sell_orders.sort(key=lambda x: x[0], reverse=False)
    buy_orders.sort(key=lambda x: x[0], reverse=True)
    return buy_orders, sell_orders


class CallAuction(object):

    def __init__(self, buy_orders, sell_orders):
        self.buy_orders = buy_orders
        self.sell_orders = sell_orders
        self.call_auction_table_supply = {}
        self.call_auction_table_demand = {}
        self.prices = []
        self.clearing_price = None
        self.clearing_qty = None
        self.bid_side = {}
        self.ask_side = {}

    def compute_clearing_price(self):

        # compute supply and demand
        supply = []
        for i in range(len(self.sell_orders)):
            qty_sum = 0
            for j in range(len(self.sell_orders[:i + 1])):
                qty_sum += self.sell_orders[j][1]
            supply.append((self.sell_orders[i][0], qty_sum))
        supply = dict(supply)


        demand = []
        for i in range(len(self.buy_orders)):
            qty_sum = 0
            for j in range(len(self.buy_orders[:i + 1])):
                qty_sum += self.buy_orders[j][1]
            demand.append((self.buy_orders[i][0], qty_sum))
        demand.reverse()
        demand = dict(demand)

        # create the call-auction table
        supply_prices = set(supply.keys())
        demand_prices = set(demand.keys())
        self.prices = list(demand_prices.union(supply_prices))
        self.prices.sort(reverse=False)
        self.call_auction_table_supply, self.call_auction_table_demand = {}, {}
        for index, price in enumerate(self.prices):
            if price in supply_prices:
                self.call_auction_table_supply[price] = supply[price]
            elif index == 0:
                self.call_auction_table_supply[price] = 0
            else:
                self.call_auction_table_supply[price] = \
                    self.call_auction_table_supply[self.prices[index - 1]]

        self.prices.sort(reverse=True)
        for index, price in enumerate(self.prices):
            if price in demand_prices:
                self.call_auction_table_demand[price] = demand[price]
            elif index == 0:
                self.call_auction_table_demand[price] = 0
            else:
                self.call_auction_table_demand[price] = \
                    self.call_auction_table_demand[self.prices[index - 1]]

        # iterate over prices to find the clearing price
        self.prices.sort(reverse=False)
        for price in self.prices:
            if self.call_auction_table_supply[price] >= self.call_auction_table_demand[price]:
                self.clearing_price = price
                self.clearing_qty = min(self.call_auction_table_supply[price],
                                        self.call_auction_table_demand[price])
                break


        return True if self.clearing_price else False

    def compute_orderbook(self):

        for buy_order in self.buy_orders:
            if buy_order[0] < self.clearing_price:
                if buy_order[0] in self.bid_side:
                    self.bid_side[buy_order[0]] += buy_order[1]
                else:
                    self.bid_side[buy_order[0]] = buy_order[1]

        for sell_order in self.sell_orders:
            if sell_order[0] > self.clearing_price:
                if sell_order[0] in self.ask_side:
                    self.ask_side[sell_order[0]] += sell_order[1]
                else:
                    self.ask_side[sell_order[0]] = sell_order[1]

    def plot_supply_vs_demand(self):

        fig, ax = plt.subplots()

        prices = list(self.call_auction_table_supply.keys())
        supply_qty, demand_qty = [], []
        for price in prices:
            supply_qty.append(self.call_auction_table_supply[price])
            demand_qty.append(self.call_auction_table_demand[price])

        ax.plot(prices, supply_qty, color='b', label="Supply")
        ax.plot(prices, demand_qty, color='g', label="Demand")
        ax.plot(self.clearing_price, self.clearing_qty, 'o', markersize=14, color='r')

        plt.title('Call Auction Table')
        plt.xlabel('Price')
        plt.ylabel('Quantity')
        plt.legend(loc='best')

        text = f'Price: {self.clearing_price:6.2f}\nQuantity: {self.clearing_qty:6.0f}'
        ax.annotate(text,
                    xy=(self.clearing_price, self.clearing_qty),
                    xytext=((min(prices) + max(prices)/4), self.clearing_qty),
                    va="center", ha="right",
                    bbox=dict(boxstyle='round4', fc='cyan', ec='blue', lw=2, alpha=0.5),
                    arrowprops=dict(fc='crimson', arrowstyle='->'),
                    )
        plt.show()

    def plot_orderbook(self):

        fig, ax = plt.subplots()

        ax.bar(list(self.bid_side.keys()), list(self.bid_side.values()), color='g',
               align='center', label="Bid")
        ax.bar(list(self.ask_side.keys()), list(self.ask_side.values()), color='b',
               align='center', label="Ask")

        plt.title('Initial Orderbook')
        plt.xlabel('Price')
        plt.ylabel('Quantity')
        plt.legend(loc='best')

        plt.show()


def main():
    orders_file_name = 'Orders.txt'
    buy_orders, sell_orders = read_orders_from_file(orders_file_name)
    # buy_orders, sell_orders = make_random_orders()

    call_auction = CallAuction(buy_orders, sell_orders)
    if call_auction.compute_clearing_price():
        call_auction.plot_supply_vs_demand()
    else:
        print('There is no clearing price.')
    call_auction.compute_orderbook()
    call_auction.plot_orderbook()


if __name__ == '__main__':
    main()
