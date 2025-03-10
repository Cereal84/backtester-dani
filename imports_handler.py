import pandas as pd
from config import INDEX_LIST_FILE_PATH, ETF_BASE_PATH

def match_asset_name(nomi_assets):
    mapping = pd.read_csv(INDEX_LIST_FILE_PATH)
    nomi_indici = [mapping[mapping['Fund'] == asset]['Index'].values[0] for asset in nomi_assets if
                   asset in mapping['Fund'].values]
    return nomi_indici

def importa_dati(nomi_indici):
    dati = None  # Initialize an empty dataframe for merging
    latest_start_date = None  # Track the latest start date
    latest_start_etf = None  # Track the ETF name with the latest start date

    for i in nomi_indici:
        # Read the data and set Date as the index
        temp_data = pd.read_csv(
            f"{ETF_BASE_PATH}/{i}.csv",  # Use the base path
            parse_dates=['Date'],
        ).set_index('Date')

        # Get the first date available for the current ETF
        first_date = temp_data.index.min()

        # Check if this ETF has a later start date than the current latest
        if latest_start_date is None or first_date > latest_start_date:
            latest_start_date = first_date
            latest_start_etf = i

        # Print the first date available for the current ETF
        first_date = temp_data.index.min()
        if dati is None:
            dati = temp_data  # For the first dataframe, initialize `dati`
        else:
            dati = pd.concat([dati, temp_data], axis=1)  # Concatenate on index (Date)

    dati.dropna(inplace=True)  # Drop rows with missing values
    #If this is nan it means that there are no rows in comune between the ETFs so the output will be empty :TODO
    # Normalize all the columns making them start from 100
    dati = dati / dati.iloc[0] * 100

    # Prepare the warning message
    first_date_str = latest_start_date.strftime('%Y-%m')
    warning = [first_date_str, latest_start_etf]

    return dati, warning

def load_asset_list(file_path):
    """Carica e processa la lista degli asset da un file CSV."""
    try:
        data = pd.read_csv(file_path)
        asset_list = [
            {
                "label": row["Fund"],
                "value": row["Fund"],
                "search": f"{row['Fund']} {row['ISIN']} {row['Tickers']}",
            }
            for _, row in data.iterrows()
        ]
        return asset_list
    except FileNotFoundError:
        print(f"Errore: Il file {file_path} non è stato trovato.")
        return []
    except Exception as e:
        print(f"Si è verificato un errore durante il caricamento della lista degli asset: {e}")
        return []