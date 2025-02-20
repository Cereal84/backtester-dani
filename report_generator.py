from email_sender import EmailSender

class PortfolioReport:
    def create_portfolio_report(self, data, receiver_email):
        email_message = ""

        # Greeting
        email_message += "Ciao, sono Dani! 😊\n\n"
        email_message += "Grazie per aver utilizzato PortfolioPilot, ecco il tuo report:\n\n"

        # CAGR
        if 'cagr_data' in data['performance_metrics']:
            email_message += "=== 📈 Tasso di Crescita Annuo Composto (CAGR) ===\n"
            cagr_value = data['performance_metrics']['cagr_data']['Value']['0']
            email_message += f"Portfolio CAGR: {cagr_value:.2f}%\n\n"

        # Volatility
        if 'volatility_data' in data['performance_metrics']:
            email_message += "=== 📊 Dati di Volatilità ===\n"
            volatility_value = data['performance_metrics']['volatility_data']['Value']['1']
            email_message += f"Portfolio Volatilità: {volatility_value:.2f}%\n\n"

        # Sharpe Ratio
        if 'sharpe_data' in data['performance_metrics']:
            email_message += "=== 🧠 Rapporto di Sharpe ===\n"
            sharpe_value = data['performance_metrics']['sharpe_data']['Value']['2']
            email_message += f"Portfolio Sharpe Ratio: {sharpe_value:.2f}\n\n"

        # Country Allocation
        if 'country' in data['allocations']:
            email_message += "=== 🌍 Allocazione per Paese ===\n"
            for i in data['allocations']['country']['Paese'].keys():
                country = data['allocations']['country']['Paese'][i]
                percent = data['allocations']['country']['Percentuale'][i]
                email_message += f"{country}: {percent}%\n"
            email_message += "\n"

        # Sector Allocation
        if 'sector' in data['allocations']:
            email_message += "=== 🏙️ Allocazione Settoriale ===\n"
            for i in data['allocations']['sector']['Settore'].keys():
                sector = data['allocations']['sector']['Settore'][i]
                weight = data['allocations']['sector']['Peso'][i]
                email_message += f"{sector}: {weight:.2f}%\n"
            email_message += "\n"

        # Factor Exposure
        if 'factor_exposure' in data['allocations']:
            email_message += "=== 🔍 Esposizione ai Fattori ===\n"
            email_message += "Fattori: Market, Size, Value, Profitability, Investments\n"
            email_message += ", ".join(map(str, data['allocations']['factor_exposure'])) + "\n\n"

        # Closing
        email_message += "Grazie per aver dato un'occhiata al report! Se hai domande, non esitare a scrivermi. 💌\n\n"
        email_message += "A presto!\nDani"

        subject = "📊 Report del PortfolioPilot"

        EmailSender().send_email(receiver_email, subject, email_message)

