import matplotlib.pyplot as plt
import numpy as np
from random import gauss
from math import exp, sqrt


class Configuration:
    def __init__(self, number_of_simulations, number_of_timesteps):
        self.number_of_simulations = number_of_simulations
        self.number_of_timesteps = number_of_timesteps


class OptionTrade:
    def __init__(self, underlying, strike, risk_free_rate, volatility, time_to_maturity, barrier, number_of_simulations, number_of_timesteps, option_type='upin'):
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity
        self.option_type = option_type
        self.barrier = barrier
        self.number_of_simulations = number_of_simulations
        self.number_of_timesteps = number_of_timesteps
        self.delta_t = self.time_to_maturity/self.number_of_timesteps


class GbmModel:
    def __init__(self, configuration):
        self.configuration = configuration

    def simulate(self, trade):
        prices = [(0.0, trade.underlying)]
        timestep = trade.time_to_maturity / self.configuration.number_of_timesteps
        times = np.linspace(timestep, trade.time_to_maturity, self.configuration.number_of_timesteps)
        for time in times:
            drift = (trade.risk_free_rate - 0.5 * (trade.volatility ** 2.0)) * timestep
            diffusion = trade.volatility * np.sqrt(timestep) * np.random.normal(0, 1)
            price = prices[-1][1] * np.exp(drift + diffusion)
            prices.append((time, price))
        return prices


class OptionTradePayoffPricer:
    def __init__(self, underlying, strike, risk_free_rate, volatility, time_to_maturity, barrier, number_of_simulations, number_of_timesteps, option_type='upin'):
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity
        self.option_type = option_type
        self.barrier = barrier
        self.number_of_simulations = number_of_simulations
        self.number_of_timesteps = number_of_timesteps
        self.delta_t = self.time_to_maturity/self.number_of_timesteps

    def calculate_price(self, trade, payoff_prices_per_simulation):
        if trade.option_type == 'upin':
            return self.__calculate_call_price(trade, payoff_prices_per_simulation)
        elif trade.option_type == 'upout':
            return self.__calculate_put_price(trade, payoff_prices_per_simulation)
        
    def call_payoff(self,s):
        """use to price a call"""
        self.cp = max(s - self.strike, 0.0)
        return self.cp

    def __calculate_call_price(self, trade, payoff_prices_per_simulation):
        payoffs = []
        
        for i in range(0, self.number_of_simulations):
            self.stock_path = []
            self.S_j = self.underlying
            for j in range(0, int(self.number_of_timesteps - 1)):
                self.xi = gauss(0,1.0)
    
                self.S_j *= (exp((self.risk_free_rate - .5*self.volatility * self.volatility) * self.delta_t + self.volatility *sqrt(self.delta_t) * self.xi))
    
                self.stock_path.append(self.S_j)
            if max(self.stock_path) > self.barrier:
                payoffs.append(self.call_payoff(self.stock_path[-1]))
            elif max(self.stock_path) < self.barrier:
                payoffs.append(0)
        discount_rate = np.exp(-1.0 * trade.risk_free_rate * trade.time_to_maturity)
        np_payoffs = np.array(payoffs, dtype=float) 
        np_Vi = discount_rate*np_payoffs 
        payoff = np.average(np_Vi)
        return payoff


    def __calculate_put_price(self, trade, payoff_prices_per_simulation):
        payoffs = []
        
        for i in range(0, self.number_of_simulations):
            self.stock_path = []
            self.S_j = self.underlying
            for j in range(0, int(self.number_of_timesteps - 1)):
                self.xi = gauss(0,1.0)
    
                self.S_j *= (exp((self.risk_free_rate - .5*self.volatility * self.volatility) * self.delta_t + self.volatility *sqrt(self.delta_t) * self.xi))
    
                self.stock_path.append(self.S_j)
            if max(self.stock_path) > self.barrier:
                payoffs.append(0)
            elif max(self.stock_path) < self.barrier:
                payoffs.append(self.call_payoff(self.stock_path[-1]))
        discount_rate = np.exp(-1.0 * trade.risk_free_rate * trade.time_to_maturity)
        np_payoffs = np.array(payoffs, dtype=float) 
        np_Vi = discount_rate*np_payoffs 
        payoff = np.average(np_Vi)
        return payoff


class MonteCarloEngineSimulator:
    # class level attributes
    times, paths = [], []

    def __init__(self, configuration, model):
        self.configuration = configuration
        self.model = model

    def simulate(self, trade, trade_pricer):
        payoff_prices_per_simulation = []
        for simulation_index in range(self.configuration.number_of_simulations):
            prices_per_simulation = self.model.simulate(trade)
            payoff_prices_per_simulation.append(prices_per_simulation[-1][1])
            MonteCarloEngineSimulator.add_simulation_path(prices_per_simulation, trade)
        MonteCarloEngineSimulator.plot_simulation_paths(trade)
        return trade_pricer.calculate_price(trade, payoff_prices_per_simulation)

    @staticmethod
    def add_simulation_path(prices_per_simulation, trade):
        x, y = [], []
        for price_per_simulation in prices_per_simulation:
            x.append(price_per_simulation[0])
            y.append(price_per_simulation[1])

        MonteCarloEngineSimulator.times.append(x)
        MonteCarloEngineSimulator.paths.append(y)

    @staticmethod
    def plot_simulation_paths(trade):
        for index in range(len(MonteCarloEngineSimulator.times)):
            plt.plot(MonteCarloEngineSimulator.times[index], MonteCarloEngineSimulator.paths[index])
        strike_line_x = [0.0, trade.time_to_maturity]
        strike_line_y = [trade.strike, trade.strike]
        plt.plot(strike_line_x, strike_line_y, 'k-' )
        plt.ylabel('Underlying')
        plt.xlabel('Timestep')
        plt.show()


def main():
    configuration = Configuration(1000, 252)
    trade = OptionTrade(90, 100, 0.05, 0.25, 1, 105, 1000, 252, 'upin')
    model = GbmModel(configuration)
    trade_pricer = OptionTradePayoffPricer(90, 100, 0.05, 0.25, 1, 105, 1000, 252, 'C')
    simulator = MonteCarloEngineSimulator(configuration, model)
    price = simulator.simulate(trade, trade_pricer)
    print(f'Call Price up-and-in: {price:10.4e}')

    trade = OptionTrade(90, 100, 0.05, 0.25, 1, 105, 1000, 252, 'upout')
    model = GbmModel(configuration)
    trade_pricer = OptionTradePayoffPricer(90, 100, 0.05, 0.25, 1, 105, 1000, 252, 'P')
    simulator = MonteCarloEngineSimulator(configuration, model)
    price = simulator.simulate(trade, trade_pricer)
    print(f'Call Price up-and-out: {price:10.4e}')


if __name__ == '__main__':
    main()
