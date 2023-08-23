import numpy as np
import pandas as pd
from blessed import Terminal
from utils.progress_bar import print_progress_bar
import typing as T

Order = T.Literal[1, 2, 3]
Active_Passive = T.Literal['Active', 'Passive']

class StochasticDominance:
    
    def __init__(self, 
                 order: Order, 
                 active_passive: Active_Passive, 
                 dominance_lookback: int,
                 benchmark: str = None
                 ) -> None:
        """General setting for Stochastic Dominance object

        Args:
            order (Order): The order of calculation of dominance 
            active_passive (Active_Passive): using active returns or passive returns, active returns 
                                             means we only care about the returns minus a benchmark
            dominance_lookback (int): the lookback i.e. number of return observations we use to calculate dominance, 
                                      if it's None means use all available data between start_date and end_date
            benchmark (str, optional): the symbol of benchmark, you must provide it if you want to use active returns. Defaults to None.

        Raises:
            Exception: If you want to use Active and didn't provide a symbol for bechmark returns
        """
        self.order = order
        self.active_passive = active_passive
        self.dominance_lookback = dominance_lookback
        self.benchmark = benchmark
        if (self.benchmark is None) and (self.active_passive == 'Active'):
            raise Exception("For Dominance Calculation with active returns you need to provied a benchmark")
        pass
    
    def __calculate_dominance(self, 
                              instrument_cdf: T.Dict,
                              primary: str, 
                              second_instrument: str):
        if primary not in instrument_cdf or second_instrument not in instrument_cdf:
            return 0

        return1 = pd.DataFrame(instrument_cdf[primary])
        return2 = pd.DataFrame(instrument_cdf[second_instrument])
        
        all_returns = np.concatenate((return1['return'], return2['return']), axis=0)
        all_returns = np.sort(np.unique(all_returns))
        start_return = min(all_returns[0], 0)
        s1 = 0
        s2 = 0
        i3 = 0
        i1 = 0
        first_index = 0
        second_index = 0

        def get_next_index(ret, next_return_point, current_index):
            if len(ret) == current_index + 1:
                return current_index
            if ret['return'].loc[current_index + 1] > next_return_point:
                return current_index
            return current_index + 1

        return_index = 0
        second_is_better = True
        first_is_better = True
        
        if self.order == 3:
            for return_point in all_returns:
                if not second_is_better and not first_is_better:
                    return 0
                return_index += 1
                prev_s1 = s1
                prev_s2 = s2
                prev_i2 = prev_s2 - prev_s1
                i1_now = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                s1 = s1 + (return_point - start_return) * return1['CDF'].loc[first_index]
                s2 = s2 + (return_point - start_return) * return2['CDF'].loc[second_index]
                i2 = s2 - s1
                if np.abs(i1_now) < 0.000001:
                    rmin = return_point
                else:
                    rmin = return_point - (i2/i1_now)
                
                i3 = i3 + (prev_i2 * (rmin - start_return)) + (0.5 * i1 * (rmin - start_return)**2)
                
                if (i3 > 0) or (i2 > 0):
                    second_is_better = False
                elif (i3 < 0) or (i2 < 0):
                    first_is_better = False
                i1 = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                first_index = get_next_index(return1, return_point, first_index)
                second_index = get_next_index(return2, return_point, second_index)
                start_return = return_point
        
        elif self.order == 2:
            for return_point in all_returns:
                if not second_is_better and not first_is_better:
                    return 0
                return_index += 1
                prev_s1 = s1
                prev_s2 = s2
                prev_i2 = prev_s2 - prev_s1
                i1_now = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                s1 = s1 + (return_point - start_return) * return1['CDF'].loc[first_index]
                s2 = s2 + (return_point - start_return) * return2['CDF'].loc[second_index]
                i2 = s2 - s1
                
                if (i2 > 0):
                    second_is_better = False
                elif (i2 < 0):
                    first_is_better = False
                i1 = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                first_index = get_next_index(return1, return_point, first_index)
                second_index = get_next_index(return2, return_point, second_index)
                start_return = return_point
        
        elif self.order == 1:
            for return_point in all_returns:
                if not second_is_better and not first_is_better:
                    return 0
                return_index += 1
                prev_s1 = s1
                prev_s2 = s2
                prev_i2 = prev_s2 - prev_s1
                i1_now = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                if (i1_now > 0):
                    second_is_better = False
                elif (i1_now < 0):
                    first_is_better = False
                i1 = return2['CDF'].loc[second_index] - return1['CDF'].loc[first_index]
                first_index = get_next_index(return1, return_point, first_index)
                second_index = get_next_index(return2, return_point, second_index)
                start_return = return_point
            
        res = 0
        if second_is_better and first_is_better:
            raise Exception("Could Not both first and second be better")
        elif first_is_better:
            res = 1
        elif second_is_better:
            res = -1
        return res
    
    def __calculate_cdf(self, 
                        prices: T.Dict, 
                        names: T.List[str],):
        cdf = {}
        for instrument_name in names:
            symbol_price = prices[instrument_name]
            if self.active_passive == 'Active':
                symbol_price = symbol_price.merge(prices[self.benchmark][['return']], 
                                                  left_index=True, 
                                                  right_index=True, 
                                                  how='left', 
                                                  suffixes=('_instrument', '_benchmark'))
                symbol_price['active_return'] = (symbol_price['return_instrument'] - symbol_price['return_benchmark']).dropna()
                instrument_return = symbol_price['active_return']
                if len(instrument_return) == 0:
                    continue
                returns = np.unique(instrument_return)
                returns = np.sort(returns)
            elif self.active_passive == 'Passive':
                instrument_return = symbol_price['return'].dropna()
                if len(instrument_return) == 0:
                    continue
                returns = np.unique(instrument_return)
                returns = np.sort(returns)
            
            else:
                raise Exception('`active_passive` should be either Active or Passive')
            
            cdf[instrument_name] = []
            for ret in returns:
                current_cdf = len(instrument_return[instrument_return <= ret]) * 1.0 / len(instrument_return)
                current_c = {'CDF': current_cdf, 'return': ret}
                cdf[instrument_name].append(current_c)
        return cdf    
    
    def get_dominance(
        self,
        instrument_returns: T.Dict, 
        start_time: pd.Timestamp, 
        end_time: pd.Timestamp,
        names: T.List[str],
        ) -> T.Dict:
        """A function that gets the clean data and calculated the stochastic dominance across all names that are provided

        Args:
            instrument_returns (T.Dict): The dictionary of prices, each key is the symbol and contains tha dataframe of returns
            start_time (pd.Timestamp): the start time which we want to calculate dominance
            end_time (pd.Timestamp): the end time whicj we want to calculate dominance
            names (T.List[str]): the symbols we want to calculate dominance among them

        Returns:
            T.Dict[T.Dict]: The results of dominance, 
                    `better_count`: this name is dominant of how many other symbols
                    `worst_count`: this name is dominated by how many other symbols
                    `better_names`: the names that this name is dominant of them
                    `worst_names`: the names that this name is dominated by
                    `name`: the symbol
                    
        """
        
        if names is None:
            names = list(instrument_returns.keys())
        
        for symbol in names:
            instrument_returns[symbol] = instrument_returns[symbol][(instrument_returns[symbol]['date'] >= start_time) & 
                                                                    (instrument_returns[symbol]['date'] < end_time)]
            if (self.dominance_lookback is not None) and  (len(instrument_returns[symbol]) > self.dominance_lookback):
                instrument_returns[symbol] = instrument_returns[symbol].iloc[-self.dominance_lookback:]
        
        dominance_results_dict = {}
        instrument_cdf = self.__calculate_cdf(instrument_returns, names,)
        for name in names:
            dominance_results_dict[name] = {'better_count': 0, 'worst_count': 0, 'name': name, 'better_names': [],
                                            'worst_names': []}

        stop = len(names)
        term = Terminal()
        for i in range(0, stop):
            with term.location(0, term.height - 1):
                print_progress_bar(i, stop - 1, prefix=('%s' % "Calculate Dominance"), suffix='Complete',
                                    length=100)
            first = names[i]
            for j in range(i + 1, stop):
                second = names[j]
                dominance_result = self.__calculate_dominance(instrument_cdf, first, second)
                if dominance_result == 1:
                    dominance_results_dict[first]['better_names'].append(second)
                    dominance_results_dict[second]['worst_names'].append(first)
                    dominance_results_dict[first]['better_count'] += 1
                    dominance_results_dict[second]['worst_count'] += 1
                elif dominance_result == -1:
                    dominance_results_dict[second]['better_names'].append(first)
                    dominance_results_dict[second]['better_count'] += 1
                    dominance_results_dict[first]['worst_count'] += 1
                    dominance_results_dict[first]['worst_names'].append(second)
        
        return dominance_results_dict