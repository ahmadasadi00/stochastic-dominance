import pandas as pd
import typing as T
import glob
import os

def clean_data(price_data_address: str) -> T.Dict:
    """A function that gets data files address and creates a dictionary of price returns
    prices could be portfolio values, we use close-close return but it can be changed in this function
    each file in price_data_address should be a csv file that the name of csv file was used as symbol
    each file should have at least two columns [`date`, `close`]
    
    Note: the frequency of the data doesn't matter as long as all the files in `price_data_address` has the same frequency

    Args:
        `price_data_address` (str): address for csv files of price data or portfolio value

    Returns:
        T.Dict: The dictionary of cleaned data that each key is the symbol and value is cleaned data
    """
    price_data = {}
    for csv_file in glob.glob(os.path.join(price_data_address, '*.csv')):
        symbol = os.path.splitext(os.path.basename(csv_file))[0]
        price = pd.read_csv(csv_file)
        price = price[['date', 'close']]
        price['date'] = pd.to_datetime(price['date'], utc=True)
        price['return'] = price['close'].pct_change()
        price_data[symbol] = price
    
    return price_data