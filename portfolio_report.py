


class PortfolioReport:
    def create_portfolio_report(portfolio_df, drawdown, factor_exposure_portfolio, factor_exposure_benchmark,
                                correlation_matrix, cagr_data, volatility_data, sharpe_data, country_allocation,
                                sector_allocation):
        # Iniziamo con un messaggio vuoto
        email_message = ""

        # Drawdown
        if drawdown is not None:
            email_message += "=== Drawdown (Perdita Massima) ===\n"
            email_message += "Il Drawdown rappresenta la massima perdita rispetto al picco precedente del portafoglio.\n"
            # Estraiamo i valori più significativi dal grafico (ad esempio, il drawdown più alto)
            max_drawdown = drawdown['data'][0]['y'].min()
            email_message += f"Drawdown massimo (portafoglio): {max_drawdown:.2%}\n\n"

        # Factor Exposure - Portfolio
        if factor_exposure_portfolio is not None:
            email_message += "=== Esposizione ai Fattori (Portafoglio) ===\n"
            email_message += "Esposizione ai fattori di rischio del portafoglio:\n"
            # Stampa i primi 5 valori
            email_message += f"{factor_exposure_portfolio.head()}\n\n"

        # Factor Exposure - Benchmark
        if factor_exposure_benchmark is not None:
            email_message += "=== Esposizione ai Fattori (Benchmark) ===\n"
            email_message += "Esposizione ai fattori di rischio del benchmark:\n"
            email_message += f"{factor_exposure_benchmark.head()}\n\n"

        # Correlation Matrix
        if correlation_matrix is not None:
            email_message += "=== Matrice di Correlazione ===\n"
            email_message += "La matrice di correlazione mostra la relazione tra le variabili.\n"
            email_message += f"{correlation_matrix.to_string()}\n\n"

        # CAGR
        if cagr_data is not None:
            email_message += "=== Tasso di Crescita Annuo Composto (CAGR) ===\n"
            email_message += "Tasso di crescita annuale composto del portafoglio e del benchmark:\n"
            portfolio_cagr = \
                cagr_data[cagr_data['Metric'] == 'CAGR'][cagr_data['Portfolio'] == 'Portfolio']['Value'].values[0]
            benchmark_cagr = \
                cagr_data[cagr_data['Metric'] == 'CAGR'][cagr_data['Portfolio'] == 'Benchmark']['Value'].values[0]
            email_message += f"Portfolio CAGR: {portfolio_cagr:.2f}%\n"
            email_message += f"Benchmark CAGR: {benchmark_cagr:.2f}%\n\n"

        # Volatility
        if volatility_data is not None:
            email_message += "=== Dati di Volatilità ===\n"
            email_message += "Volatilità annuale del portafoglio e del benchmark:\n"
            portfolio_volatility = \
                volatility_data[volatility_data['Metric'] == 'Volatility'][volatility_data['Portfolio'] == 'Portfolio'][
                    'Value'].values[0]
            benchmark_volatility = \
                volatility_data[volatility_data['Metric'] == 'Volatility'][volatility_data['Portfolio'] == 'Benchmark'][
                    'Value'].values[0]
            email_message += f"Portfolio Volatilità: {portfolio_volatility:.2f}%\n"
            email_message += f"Benchmark Volatilità: {benchmark_volatility:.2f}%\n\n"

        # Sharpe Ratio
        if sharpe_data is not None:
            email_message += "=== Rapporto di Sharpe ===\n"
            email_message += "Rapporto di Sharpe per il portafoglio e il benchmark:\n"
            portfolio_sharpe = \
                sharpe_data[sharpe_data['Metric'] == 'Sharpe Ratio'][sharpe_data['Portfolio'] == 'Portfolio'][
                    'Value'].values[0]
            benchmark_sharpe = \
                sharpe_data[sharpe_data['Metric'] == 'Sharpe Ratio'][sharpe_data['Portfolio'] == 'Benchmark'][
                    'Value'].values[0]
            email_message += f"Portfolio Sharpe Ratio: {portfolio_sharpe:.2f}\n"
            email_message += f"Benchmark Sharpe Ratio: {benchmark_sharpe:.2f}\n\n"

        # Country Allocation
        if country_allocation is not None:
            email_message += "=== Allocazione per Paese ===\n"
            email_message += "Distribuzione dell'investimento tra i vari paesi:\n"
            email_message += f"{country_allocation.head()}\n\n"

        # Sector Allocation
        if sector_allocation is not None:
            email_message += "=== Allocazione Settoriale ===\n"
            email_message += "Distribuzione dell'investimento tra i vari settori:\n"
            email_message += f"{sector_allocation.head()}\n\n"

        print(email_message)

        return email_message