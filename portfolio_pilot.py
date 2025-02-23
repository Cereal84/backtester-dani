import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash.dash_table
import plotly.graph_objects as go
from Frontend import plot_line_chart as plc
import efficent_fronteer as ef
import logging
import warnings
from Frontend.layout import LayoutManager
from factor_regression import calculate_factor_exposure
from imports_handler import match_asset_name, importa_dati, load_asset_list
from portfolio_allocation import PortfolioAllocation
from math_logic import MathLogic
import plotly.express as px
from report_generator import PortfolioReport
from summary_table import SummaryTable
from constants import factor_name_translation, custom_colorscale, pastel_colors, rolling_periods

from config import APP_TITLE, BENCHMARK_COLOR, PORTFOLIO_COLOR, SERVER_HOST, SERVER_PORT, INDEX_LIST_FILE_PATH, \
    LOGIN_INDICATOR_STYLE

warnings.filterwarnings("ignore", category=UserWarning)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Show only errors

def register_callbacks(app):
    """Registra tutti i callback per l'app Dash."""

    @app.callback(
        Output("portfolio-toast", "is_open"),
        Input("create-portfolio-button", "n_clicks"),
        State("portfolio-table", "data"),
        State('start-year-dropdown', 'value'),
        State('end-year-dropdown', 'value'),
        prevent_initial_call=True
    )
    def show_calculation_message(n_clicks, table_data, start_year, end_year):
        if n_clicks is None or not table_data:
            return False  # Non aprire il toast se non ci sono dati

        start_year = start_year or 1970
        end_year = end_year or 2024
        start_date = pd.Timestamp(f'{start_year}-01-01')
        end_date = pd.Timestamp(f'{end_year}-12-31')

        # Validate the date range
        if start_date > end_date:
            return False

        # Calcola l'allocazione totale
        try:
            total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
        except (ValueError, TypeError):
            return False  # Non aprire il toast se c'è un errore nei dati

        # Apri il toast solo se l'allocazione è corretta (100%)
        if total_percentage == 100:
            return True  # Mostra il toast se l'allocazione è esattamente 100%

        return False  # Non mostrare il toast se l'allocazione non è 100%

    @app.callback(
        [
            Output("url", "href", allow_duplicate=True),
        ],
        [
            Input("tutorial-button", "n_clicks"),
            Input("donate-button", "n_clicks"),
        ],
        prevent_initial_call=True
    )
    def handle_tutorial_and_donate(n_tutorial, n_donate):
        """Handles button clicks for tutorial and donation actions."""

        ctx = dash.callback_context

        # If no button was clicked, do nothing
        if not ctx.triggered:
            return [dash.no_update]

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        tutorial_link = "https://danieleligato-eng.notion.site/Versione-in-italiano-153922846a1680d7befcd164f03fd577"
        donate_link = "https://www.paypal.com/donate/?hosted_button_id=M378MEXMSSQT6"

        if triggered_id == "tutorial-button":
            return [tutorial_link]
        elif triggered_id == "donate-button":
            return [donate_link]

        return [dash.no_update]

    # Callback per gestire il modale di login
    @app.callback(
        [
            Output("login-modal", "is_open"),
            Output("Work-in-progress-toast", "is_open"),
        ],
        [
            Input("account-button", "n_clicks"),
            Input("login-trigger", "n_clicks"),
            Input("close-modal", "n_clicks"),
        ],
        [State("login-state", "data")],
        prevent_initial_call=True
    )
    def handle_account_and_close(n_account, n_emoji, n_close, login_state):
        """Handles button clicks for account and modal close actions."""
        ctx = dash.callback_context

        # Se nessun click è stato fatto, mantieni tutto chiuso
        if not ctx.triggered or all(x is None for x in [n_account, n_emoji, n_close]):
            return False, False

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id in ["account-button", "login-trigger"]:
            return True, dash.no_update
        elif triggered_id == "close-modal":
            return False, dash.no_update

        return False, False

    @app.callback(
        Output("report-toast", "children"),
        Output("report-toast", "is_open"),
        Input("get-summary-button", "n_clicks"),
        State("additional-feedback", "data"),
        State("login-state", "data"),
        prevent_initial_call=True
    )
    def generate_report(n_clicks, data, email):
        if not email or "logged_in" not in email:
            email = {"logged_in": False}

        if data is None:
            return "Nessuno portafoglio presente sul quale generare il report", True  # Show toast with message

        if email["logged_in"]:
            PortfolioReport().create_portfolio_report(data, email["username"])
            return "✅ Report generato con successo! Controlla la tua email ", True
        else:
            return "❌ Per ricevere il report per email è necessario essere loggati", True

    @app.callback(
        [Output("menu-button", "className"),
         Output("interval-component", "disabled")],
        [Input("menu-button", "n_clicks"),
         Input("interval-component", "n_intervals")],
        [State("menu-button", "className")]
    )
    def toggle_buttons(n_clicks, n_intervals, current_class):
        if n_clicks:
            if "active" in current_class:
                return "btn-menu", True
            else:
                return "btn-menu active", False
        elif n_intervals > 0:
            return "btn-menu", True
        return "btn-menu", True

    @app.callback(
        [
            Output("login-indicator", "children"),
            Output("login-indicator", "style")
        ],
        [
            Input("login-state", "data"),
            Input("url", "pathname")
        ],
    )
    def update_login_indicator(login_state, pathname):
        """Updates the login indicator with emoji and text based on login state."""
        if login_state and login_state.get("logged_in"):
            emoji = "👤"
            text = f"Bentornato: {login_state.get('username')}"
            style = {
                **LOGIN_INDICATOR_STYLE,
                "color": "#198754",  # Green color for logged in state
                "cursor": "pointer"  # Aggiunto per indicare cliccabilità
            }
        else:
            emoji = "👻"
            text = "Accesso non effettuato"
            style = {
                **LOGIN_INDICATOR_STYLE,
                "color": "#6c757d",  # Gray color for logged out state
                "cursor": "pointer"  # Aggiunto per indicare cliccabilità
            }

        return [
            html.Div([
                html.Span(emoji, style={"fontSize": "16px"}),
                html.Span(text, className="login-text")
            ],
                id="login-trigger",  # Aggiunto ID per il trigger
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "cursor": "pointer"  # Aggiunto per indicare cliccabilità
                }),
            style
        ]

    app.clientside_callback(
        """
          function(n_clicks) {
            if (n_clicks > 0) {
                // Open the print dialog; users can choose 'Save as PDF' in the dialog
                window.print();
            }
            return '';
        }
        """,
        Output('hidden-div', 'children'),  # Dummy output
        Input('save-pdf-button', 'n_clicks')  # Triggered by button clicks
    )

    # Callback per aggiungere un ETF alla tabella con la percentuale selezionata
    @app.callback(
        [Output('portfolio-table', 'data'),
         Output('allocation-error-toast', 'is_open')],
        [Input('add-etf-button', 'n_clicks')],
        [State('etf-dropdown', 'value'),
         State('percentage-input', 'value'),
         State('portfolio-table', 'data')]
    )
    def add_etf_to_table(n_clicks, selected_etf, selected_percentage, current_data):

        if n_clicks is None:
            # Nessun clic ancora, restituisce i dati correnti invariati
            return current_data, False

        if n_clicks > 0:
            if not selected_etf:
                return current_data, False  # Nessun ETF selezionato, nessun cambiamento

            # Assicurati che current_data sia una lista di dizionari (righe della tabella)
            if current_data is None:
                current_data = []

            # Converti in DataFrame per una manipolazione più semplice
            current_df = pd.DataFrame(current_data)

            # Controlla se l'ETF esiste già nella tabella
            if 'ETF' in current_df.columns and not current_df[current_df['ETF'] == selected_etf].empty:
                return current_data, False  # Non aggiungere ETF duplicati

            # Assicurati che selected_percentage non sia None
            if selected_percentage is None:
                selected_percentage = 0

            if selected_percentage > 100:
                selected_percentage = 100
            if selected_percentage <= 0:
                selected_percentage = 0.1

            selected_percentage = round(selected_percentage, 2)

            # Controlla se l'aggiunta della nuova percentuale supera il 100%
            total_allocated = current_df['Percentuale'].sum() if not current_df.empty else 0
            if total_allocated + selected_percentage > 100:
                return current_data, True  # Mostra il toast di errore

            # Aggiungi il nuovo ETF alla tabella
            new_row = {
                "ETF": selected_etf,
                "Percentuale": selected_percentage,
            }
            current_data.append(new_row)  # Aggiungi la nuova riga ai dati della tabella

        return current_data, False

    @app.callback(
        Output('remaining-percentage', 'children'),
        [Input('portfolio-table', 'data')]
    )
    def update_remaining_percentage(table_data):
        if not table_data:
            return html.Div([
                html.Span("Totale corrente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
                html.Span("0.00%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'marginRight': '15px'}),
                html.Span("Percentuale rimanente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
                html.Span("100.00%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'color': '#dc3545'})
            ])

        # Calcola la somma delle percentuali
        total = sum(float(row.get('Percentuale', 0)) for row in table_data)
        remaining = 100 - total

        # Determina il colore della percentuale rimanente
        color = '#198754' if remaining == 0 else '#dc3545'  # Verde se 0, rosso altrimenti

        return html.Div([
            html.Span("Totale corrente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
            html.Span(f"{total:.2f}%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'marginRight': '15px'}),
            html.Span("Percentuale rimanente: ", style={'fontSize': '0.85rem', 'color': '#6c757d'}),
            html.Span(f"{remaining:.2f}%", style={'fontSize': '0.85rem', 'fontWeight': '600', 'color': color})
        ])


    """    @app.callback(
            [Input('create-portfolio-button', 'n_clicks')],
             [State('portfolio-table', 'data')],
        )
        def update_summary_table(n_clicks, table_data):
            if table_data is None:
                return dash.no_update  # Do nothing if no data is provided
    
            summary_table_instance = SummaryTable()
            summary_table_instance.create_summary_table(table_data)
    """
    def fetching_benckmark(benchmark,dati_scalati,warnings_data):
        indice_benchmark = match_asset_name([benchmark])
        dati_benckmark, warnings_data_benchmark = importa_dati(indice_benchmark)
        dati_benckmark = dati_benckmark.loc[:, ~dati_benckmark.columns.duplicated()]
        portfolio_con_benchmark = dati_scalati.join(dati_benckmark[indice_benchmark[0]], how='inner',
                                                    rsuffix='_benchmark')
        portfolio_con_benchmark['Benchmark'] = portfolio_con_benchmark[indice_benchmark[0]] / \
                                               portfolio_con_benchmark[indice_benchmark[0]].iloc[0] * 100
        portfolio_con_benchmark = portfolio_con_benchmark.drop(columns=[indice_benchmark[0]])
        portfolio_con_benchmark['Portfolio'] = portfolio_con_benchmark['Portfolio'] / \
                                               portfolio_con_benchmark['Portfolio'].iloc[0] * 100
        if warnings_data[0] < warnings_data_benchmark[0]:
            warnings_data = warnings_data_benchmark

        return portfolio_con_benchmark, warnings_data

    # Callback per gestire la creazione del portafoglio
    @app.callback(
        [
            Output('portfolio-feedback', 'children'),
            Output('portfolio-data', 'data'),
            Output('assets-data', 'data'),
            Output('start-year-dropdown', 'options'),
            Output('end-year-dropdown', 'options'),
            Output('pesi-correnti', 'data')
        ],
        [Input('create-portfolio-button', 'n_clicks')],
        [
            State('portfolio-table', 'data'),
            State('benchmark-dropdown', 'value'),
            State('start-year-dropdown', 'value'),
            State('end-year-dropdown', 'value')
        ]
    )
    def create_portfolio(n_clicks, table_data, benchmark, start_year, end_year):
        def return_error(msg):
            return msg, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if n_clicks is None or n_clicks == 0:
            return return_error("")

        if not table_data:
            return return_error("Nessun ETF nel portafoglio da creare.")

        start_year = start_year or 1970
        end_year = end_year or 2024
        start_date, end_date = pd.Timestamp(f'{start_year}-01-01'), pd.Timestamp(f'{end_year}-12-31')

        if start_date > end_date:
            return return_error("L'anno di inizio deve essere precedente all'anno di fine.")

        # Validate and sum percentages
        try:
            total_percentage = sum(float(row.get('Percentuale', 0)) for row in table_data)
        except (ValueError, TypeError):
            return return_error("Valore percentuale non valido rilevato.")

        if total_percentage != 100:
            return return_error(
                f"L'allocazione totale deve essere esattamente del 100%. Totale attuale: {total_percentage:.2f}%.")

        # Convert data to DataFrame
        df = pd.DataFrame(table_data)
        nomi_etf = df['ETF']
        indici = match_asset_name(nomi_etf)
        dati, warnings_data = importa_dati(indici)

        # Calculate portfolio returns
        pct_change = dati.pct_change().dropna()
        dati_scalati = pct_change * df['Percentuale'].values / 100
        dati_scalati['Portfolio_return'] = dati_scalati.sum(axis=1)
        dati_scalati['Portfolio'] = 100 * (1 + dati_scalati['Portfolio_return']).cumprod()
        dati_scalati.drop(columns=['Portfolio_return'], inplace=True)
        dati_scalati.drop(dati.columns, axis=1, inplace=True)

        # Process benchmark if applicable
        portfolio_con_benchmark = dati_scalati.copy()
        if benchmark:
            portfolio_con_benchmark, warnings_data = fetching_benckmark(benchmark, dati_scalati, warnings_data)

        warnings_data_string = f"La data più lontana disponibile per l'analisi è {warnings_data[0]} poiché l'ETF {warnings_data[1]} ha dati disponibili solo a partire da quel momento."

        # Adjust date ranges
        first_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[0])
        last_portfolio_date = pd.to_datetime(portfolio_con_benchmark.index[-1])

        start_dt = max(start_date, first_portfolio_date)
        end_dt = min(end_date, last_portfolio_date)

        dati = dati.loc[start_dt:end_dt]
        portfolio_con_benchmark = portfolio_con_benchmark.loc[start_dt:end_dt]

        # Normalize data
        dati = (dati / dati.iloc[0]) * 100
        portfolio_con_benchmark = (portfolio_con_benchmark / portfolio_con_benchmark.iloc[0]) * 100

        # Generate dynamic year ranges
        first_year = first_portfolio_date.year
        dynamic_years = [{'label': str(year), 'value': year} for year in range(first_year, 2025)]

        portfolio_con_benchmark.reset_index(inplace=True)

        return warnings_data_string, portfolio_con_benchmark.to_dict('records'), dati.to_dict(
            'records'), dynamic_years, dynamic_years, {'weights': df['Percentuale'].values.tolist()}

    @app.callback(
        Output('additional-feedback', 'children'),
        Output('additional-feedback', 'data'),
        [Input('portfolio-data', 'data'),
         Input('assets-data', 'data'),
         Input('pesi-correnti', 'data')],
        prevent_initial_call=True
    )
    def plot_data(portfolio_data, dati, pesi_correnti):  # ----------- KING

        portfolio_df = pd.DataFrame(portfolio_data)
        dati_df = pd.DataFrame(dati)  # Sto ricevendo un DICT e non un DataFrame, quindi le colonne duplicate erano state rimosse
        # Questo vuol dire che se metto due ETF uguali nella lista, uno dei due verrà rimosso

        indici_usati = dati_df.columns
        country_allocation = PortfolioAllocation().calculate_country_allocation(indici_usati, pesi_correnti)
        sector_allocation = PortfolioAllocation().calculate_sector_allocation(indici_usati, pesi_correnti)

        # Ensure 'Date' column is datetime for calculations
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
        column_except_date = [col for col in portfolio_df.columns if col != 'Date']

        rolling1, rolling2, rolling3 = MathLogic.calculate_3_rolling_returns(portfolio_df, rolling_periods,
                                                                             column_except_date)

        drawdown = plc.plot_drawdown(portfolio_df, PORTFOLIO_COLOR, BENCHMARK_COLOR, column_except_date)

        # Calculate factor exposure for the portfolio
        factor_exposure_portfolio, factor_names = calculate_factor_exposure(portfolio_df[["Portfolio", "Date"]])
        factor_exposure_benchmark = None
        if 'Benchmark' in portfolio_df.columns:  # If the benchmark column exists calculate the factor exposure for the benchmark
            factor_exposure_benchmark, factor_names = calculate_factor_exposure(portfolio_df[["Benchmark", "Date"]])

        scatter_fig, pie_fig, portfolio_returns = ef.calcola_frontiera_efficente(dati_df, pesi_correnti)

        cagr_data, volatility_data, sharpe_data = MathLogic.calculate_performance_metrics(portfolio_df,
                                                                                          portfolio_returns,
                                                                                          column_except_date)
        correlation_matrix = dati_df.corr()

        # Assuming 'factor_names' is a list of factor names (probably from the regression results)
        factor_names = [cell.data for cell in factor_names]

        # Apply the translation to the factor names
        factor_names_italian = [factor_name_translation.get(name, name) for name in factor_names]

        # Create a bar chart for the factor exposure
        factor_exposure_fig = go.Figure()
        factor_exposure_fig.add_trace(go.Bar(
            x=factor_names_italian,  # Use translated names here
            y=factor_exposure_portfolio,
            name="Portfolio",
            marker=dict(color=PORTFOLIO_COLOR)
        ))

        if 'Benchmark' in portfolio_df.columns:
            factor_exposure_fig.add_trace(go.Bar(
                x=factor_names_italian,  # Use translated names here
                y=factor_exposure_benchmark,
                name="Benchmark",
                marker=dict(color=BENCHMARK_COLOR)
            ))

        factor_exposure_fig.update_layout(
            title="Esposizione ai Fattori globali di Fama-French",
            xaxis_title="Fattori",
            yaxis_title="Esposizione",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        correlation_fig = go.Figure()
        correlation_fig.add_trace(go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale=custom_colorscale
        ))

        correlation_fig.update_layout(
            title="Correlazione tra gli Asset",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        sharpe_fig = go.Figure()
        sharpe_fig.add_trace(go.Bar(
            x=sharpe_data["Portfolio"],
            y=sharpe_data["Value"],
            name="Sharpe Ratio",
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])
        ))

        sharpe_fig.update_layout(
            title="Sharpe Ratio per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Sharpe Ratio",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        # Create separate bar charts for CAGR and Volatility
        cagr_fig = go.Figure()
        cagr_fig.add_trace(go.Bar(
            x=cagr_data["Portfolio"],
            y=cagr_data["Value"],
            name="Ritorno Composto Annuo",
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])

        ))
        cagr_fig.update_layout(
            title="Ritorno Aritmetico Dei Portafogli",
            xaxis_title="Portafogli",
            yaxis_title="Ritorno (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        volatility_fig = go.Figure()
        volatility_fig.add_trace(go.Bar(
            x=volatility_data["Portfolio"],
            y=volatility_data["Value"],
            name="Volatility",
            marker=dict(color=[PORTFOLIO_COLOR, BENCHMARK_COLOR])
        ))
        volatility_fig.update_layout(
            title="Volatilità per Portafoglio",
            xaxis_title="Portafogli",
            yaxis_title="Volatilità (%)",
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        # Round values to one decimal place and format as percentages
        country_allocation['Peso'] = country_allocation['Peso'].round(1)
        country_allocation['Percentuale'] = country_allocation['Peso'].astype(str) + "%"

        # Create Treemap
        country_fig = go.Figure(go.Treemap(
            labels=country_allocation['Paese'],
            parents=[""] * len(country_allocation),  # No hierarchy
            values=country_allocation['Peso'],
            textinfo="label+text",  # Show country name + percentage
            text=country_allocation['Percentuale'],  # Display the formatted percentage
            marker=dict(colors=pastel_colors),  # Keep pastel color theme
        ))

        country_fig.update_layout(title="Allocazione geografica", title_x=0.5)

        # Create a pie chart for the sector allocation
        sector_fig = go.Figure()
        sector_fig.add_trace(go.Pie(
            labels=sector_allocation['Settore'],
            values=sector_allocation['Peso'],
            hole=0.3,
            textinfo='percent+label',  # Show both the percentage and label
            insidetextorientation='horizontal',  # Make text horizontal inside the pie
            textfont=dict(size=14, color='black'),  # Style text for better visibility
            marker=dict(
                colors=pastel_colors,  # Use pastel color palette
                line=dict(color='white', width=2)  # Add white border to make slices pop
            ),
            hoverinfo='label+percent',  # Display label and percentage on hover
            pull=[0, 0.1, 0, 0, 0, 0, 0, 0],  # Slightly "explode" the second slice for emphasis (optional)
            showlegend=False  # Hide the legend for a cleaner look
        ))

        sector_fig.update_layout(
            title="Allocazione per settore",
            title_x=0.5,  # Center the title
            plot_bgcolor='rgba(0,0,0,0)',  # Remove the background color for a cleaner look
            margin=dict(t=40, b=40, l=40, r=40),  # Adjust the margins for better spacing
        )

        # Prepare the choropleth map
        mappa = px.choropleth(country_allocation,
                              locations='Paese',
                              locationmode='country names',
                              color='Peso',
                              hover_name='Paese',
                              color_continuous_scale=px.colors.sequential.Plasma_r,  # Reverse Plasma scale
                              projection='natural earth',
                              title="Mappa dei nostri investimenti")

        portfolio_fig = plc.plot_line_chart(column_except_date, portfolio_df, PORTFOLIO_COLOR, BENCHMARK_COLOR)
        multiple_assets_plot = html.Div([
            html.Div(dcc.Graph(figure=correlation_fig), style={'width': '100%'}),  # Correlation between assets
            html.Div(dcc.Graph(figure=scatter_fig), style={'width': '100%'}),  # Efficient frontier
            html.Div(dcc.Graph(figure=pie_fig), style={'width': '100%'}),  # Efficient frontier
        ])

        single_assets_plot = html.Div([
            html.Div(dcc.Graph(figure=portfolio_fig), style={'width': '100%'}),
            html.Div(dcc.Graph(figure=cagr_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=volatility_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=sharpe_fig), style={'width': '33%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(figure=rolling1), style={'width': '100%'}),  # Rolling 3y
            html.Div(dcc.Graph(figure=rolling2), style={'width': '100%'}),  # Rolling 5y
            html.Div(dcc.Graph(figure=rolling3), style={'width': '100%'}),  # Rolling 10y
            html.Div(dcc.Graph(figure=drawdown), style={'width': '100%'}),  # Drawdown
            html.Div([
                html.Div(dcc.Graph(figure=country_fig), style={'width': '50%', 'display': 'inline-block'}),
                # Country Allocation
                html.Div(dcc.Graph(figure=sector_fig), style={'width': '50%', 'display': 'inline-block'})
                # Sector Allocation
            ], style={'width': '100%'}),
            html.Div(dcc.Graph(figure=mappa), style={'width': '100%'}),  # Country Allocation Map
            html.Div(dcc.Graph(figure=factor_exposure_fig), style={'width': '100%'})  # Factor Exposure
        ])

        if len(pesi_correnti["weights"]) > 1:  # Return all the plots if there is more than one ETF
            total_plot = [single_assets_plot, multiple_assets_plot]
        else:
            total_plot = [single_assets_plot]  # Wrap in a list for consistency

        data_output = {
            "performance_metrics": {
                "cagr_data": cagr_data.to_dict(),
                "volatility_data": volatility_data.to_dict(),
                "sharpe_data": sharpe_data.to_dict()
            },
            "allocations": {
                "country": country_allocation.to_dict(),
                "sector": sector_allocation.to_dict(),
                "factor_exposure": factor_exposure_portfolio
            }
        }

        # Return both graphs side by side, and the line chart below
        return html.Div(total_plot),data_output


def main():
    # Carica la lista degli asset
    asset_list = load_asset_list(INDEX_LIST_FILE_PATH)

    # Inizializza l'app Dash con il tema Bootstrap e stili personalizzati
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = APP_TITLE

    # Inizializza i dati della tabella
    initial_table_data = pd.DataFrame(columns=['ETF', 'Percentuale'])

    # Imposta il layout dell'app
    app.layout = LayoutManager.create_layout(asset_list, initial_table_data, app)

    # Registra i callback
    register_callbacks(app)

    # Esegui l'app
    app.run_server(port=SERVER_PORT, host=SERVER_HOST)


if __name__ == '__main__':
    main()
