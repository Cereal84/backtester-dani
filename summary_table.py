import pandas as pd
from config import ETF_OVERVIEW_FILE_PATH,INDEX_LIST_FILE_PATH
class SummaryTable:
    def create_summary_table(self, data):
        etf_data = pd.read_csv(ETF_OVERVIEW_FILE_PATH)
        required_columns = [
            'name', 'isin', 'strategy', 'currency', 'hedged', 'securities_lending',
            'dividends', 'ter', 'replication', 'size', 'number_of_holdings'
        ]
        summary_table = etf_data[required_columns]
        data_df = pd.DataFrame(data)
        my_etf = summary_table[summary_table['name'].isin(data_df['ETF'])]






if __name__ == "__main__":
    SummaryTable().create_summary_table("data")