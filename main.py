import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date, datetime
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'])

app.layout = html.Div([
    html.H1('Dashboard del Portfolio', style={'textAlign': 'center'}),
    html.Div([
        dcc.Input(id='ticker-input', type='text', placeholder='Inserisci un simbolo ticker', style={'marginRight': '10px'}),
        dcc.Input(id='percentage-input', type='number', placeholder='Percentuale', min=0, max=100, step=1, style={'marginRight': '10px'}),
        html.Button('Aggiungi', id='add-button', n_clicks=0),
    ], style={'marginBottom': '20px'}),
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='portfolio-table',
                columns=[
                    {'name': 'Ticker', 'id': 'ticker'},
                    {'name': 'Percentuale', 'id': 'percentage'},
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'backgroundColor': '#2C2C2C',
                    'color': '#FFFFFF',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': '#3C3C3C',
                    'fontWeight': 'bold'
                }
            ),
            html.Button('Rimuovi Selezionato', id='remove-button', n_clicks=0, style={'marginTop': '10px'}),
            html.Div(id='percentage-warning', style={'color': 'red', 'marginTop': '10px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Input(id='benchmark-input', type='text', placeholder='Inserisci un simbolo benchmark', style={'marginRight': '10px'}),
            html.Button('Cambia Benchmark', id='add-benchmark-button', n_clicks=0),
            dash_table.DataTable(
                id='benchmark-table',
                columns=[
                    {'name': 'Benchmark', 'id': 'benchmark'},
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'backgroundColor': '#2C2C2C',
                    'color': '#FFFFFF',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': '#3C3C3C',
                    'fontWeight': 'bold'
                }
            ),
            html.Button('Rimuovi Benchmark Selezionato', id='remove-benchmark-button', n_clicks=0, style={'marginTop': '10px'}),
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    html.Div([
        html.Label('Start Date:'),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date(date.today().year - 5, date.today().month, date.today().day),
            style={'marginRight': '10px'}
        )
    ], style={'display': 'inline-block', 'marginRight': '20px'}),

    html.Div([
        html.Label('End Date:'),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            date=date.today()
        )
    ], style={'marginTop': '20px', 'marginBottom': '20px'}),
    dcc.Graph(id='portfolio-graph'),
    dcc.Dropdown(
        id='rolling-window-dropdown',
        options=[
            {'label': '1 Anno', 'value': 252},
            {'label': '5 Anni', 'value': 252 * 5},
            {'label': '10 Anni', 'value': 252 * 10}
        ],
        value=252,  # Valore predefinito (1 anno)
        style={'width': '50%'}
    ),
    dcc.Graph(id='rolling-return-graph-1y'),
    dcc.Graph(id='drawdown-graph'),
    dcc.Graph(id='returns-histogram'),
    dcc.Graph(id='characteristics-histogram'),
    html.Button('Calcola Efficient Frontier', id='efficient-frontier-button', n_clicks=0, style={'marginTop': '20px'}),
    dcc.Graph(id='efficient-frontier-graph'),
    dcc.Graph(id='optimal-portfolio-performance-graph'),
    html.Div(id='pie-charts', style={'display': 'flex', 'justifyContent': 'space-between'}),
    dcc.Graph(id='comparison-chart'),
    dcc.Graph(id='rolling-return-graph')


], style={'padding': '20px'})
def calculate_drawdown(data):
    peak = data.cummax()
    drawdown = (data - peak) / peak
    return drawdown
@app.callback(
    [Output('portfolio-table', 'data'),
     Output('ticker-input', 'value'),
     Output('percentage-input', 'value'),
     Output('portfolio-table', 'selected_rows'),
     Output('percentage-warning', 'children')],
    [Input('add-button', 'n_clicks'),
     Input('remove-button', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('percentage-input', 'value'),
     State('portfolio-table', 'data'),
     State('portfolio-table', 'selected_rows')]
)
def update_portfolio(add_clicks, remove_clicks, ticker, percentage, rows, selected_rows):
    ctx = dash.callback_context
    if not ctx.triggered:
        return rows, '', None, [], ''

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-button' and ticker and percentage:
        rows.append({'ticker': ticker.upper(), 'percentage': percentage})
    elif button_id == 'remove-button' and selected_rows:
        rows = [row for i, row in enumerate(rows) if i not in selected_rows]

    total_percentage = sum(float(row['percentage']) for row in rows)
    warning = ''
    if total_percentage != 100:
        warning = f'Attenzione: La somma delle percentuali è {total_percentage}%, non 100%'

    return rows, '', None, [], warning

def calculate_asset_characteristics(data):
    # Calculate daily returns
    returns = data.pct_change().dropna()

    # Calculate CAGR
    total_days = (data.index[-1] - data.index[0]).days
    total_years = total_days / 365.25
    cagr = ((data.iloc[-1] / data.iloc[0]) ** (1 / total_years)) - 1

    # Calculate annualized volatility
    annual_volatility = calculate_annualized_volatility(data)

    # Calculate downward volatility
    down_volatility = calculate_annualized_down_volatility(data)

    # Calculate Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
    sharpe_ratio = calculate_sharpe_ratio(returns, 0)

    # Calculate Sortino Ratio (assuming risk-free rate of 0 for simplicity)
    sortino_ratio = calculate_sortino_ratio(returns, 0)

    return cagr, annual_volatility, down_volatility, sharpe_ratio, sortino_ratio
@app.callback(
    [Output('benchmark-table', 'data'),
     Output('benchmark-input', 'value'),
     Output('benchmark-table', 'selected_rows')],
    [Input('add-benchmark-button', 'n_clicks')],
    [State('benchmark-input', 'value'),
     State('benchmark-table', 'data')]
)
def update_benchmark(n_clicks, benchmark, rows):
    if n_clicks > 0 and benchmark:
        rows = [{'benchmark': benchmark.upper()}]
    return rows, '', []

def create_returns_histogram(returns_data, asset_labels):
    histogram_fig = go.Figure()

    for returns, label in zip(returns_data, asset_labels):
        histogram_fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,  # Adjust the number of bins as needed
            name=label
        ))

    histogram_fig.update_layout(
        title='Distribuzione dei Ritorni',
        xaxis_title='Ritorno',
        yaxis_title='Frequenza',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )

    histogram_fig.update_xaxes(gridcolor='#3C3C3C')
    histogram_fig.update_yaxes(gridcolor='#3C3C3C')

    return histogram_fig

def create_empty_warning_fig(title):
    fig = go.Figure()
    fig.add_annotation(
        x=0.5, y=0.5,
        text="Non abbastanza dati per calcolare i ritorni rolling",
        showarrow=False,
        font=dict(size=20, color="white"),
        align="center"
    )
    fig.update_layout(
        title=title,
        xaxis_title='Data',
        yaxis_title='Ritorno Rolling',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig
from dash import dcc, html, Input, Output, callback


@callback(
    [Output('portfolio-graph', 'figure'),
     Output('rolling-return-graph-1y', 'figure'),
     Output('returns-histogram', 'figure'),
     Output('characteristics-histogram', 'figure'),
     Output('drawdown-graph', 'figure')],
    [Input('portfolio-table', 'data'),
     Input('benchmark-table', 'data'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date'),
     Input('rolling-window-dropdown', 'value')]
)
def rolling_return_for_stocks(rows, benchmark_rows, start_date, end_date, rolling_window):
    if not rows or not start_date or not end_date:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Scarica i dati per tutti gli asset
    data_dict = {}
    for row in rows:
        ticker = row['ticker']
        data = yf.download(ticker, start=start_date, end=end_date)
        data_dict[ticker] = data['Close']

    # Scarica i dati per il benchmark
    if not benchmark_rows:
        benchmark_rows = [{'benchmark': '^GSPC'}]  # Default to S&P 500 if no benchmark is selected

    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = yf.download(benchmark, start=start_date, end=end_date)
        data_dict[benchmark] = data['Close']

    combined_data = pd.concat(data_dict.values(), axis=1)
    common_dates = combined_data.dropna().index

    # Filtra i dati per mantenere solo le date comuni
    for key in data_dict.keys():
        data_dict[key] = data_dict[key][common_dates]

    if len(common_dates) == 0:
        return go.Figure(), go.Figure(), go.Figure()  # Non ci sono date in comune

    # Grafico del Portfolio
    fig = go.Figure()

    portfolio_value = pd.Series(0, index=common_dates)
    total_percentage = 0

    for row in rows:
        ticker = row['ticker']
        percentage = float(row['percentage'])
        total_percentage += percentage
        data = data_dict[ticker]

        # Normalizza i prezzi al valore iniziale (valore assoluto normalizzato)
        normalized_price = data / data.iloc[0]

        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized_price,
            name=f"{ticker} ({percentage}%)",
            mode='lines'
        ))

        # Calcola il contributo pesato al valore totale del portfolio
        portfolio_value += normalized_price * (percentage / 100)

    if abs(total_percentage - 100) < 0.001:  # Usiamo una piccola tolleranza per gli errori di arrotondamento
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value,
            name='Valore Totale Portfolio',
            mode='lines',
            line=dict(color='white', width=2, dash='dash')
        ))

    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = data_dict[benchmark]
        normalized_price = data / data.iloc[0]

        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized_price,
            name=f"Benchmark: {benchmark}",
            mode='lines',
            line=dict(dash='dot')
        ))

    fig.update_layout(
        title=f'Andamento dei Componenti del Portfolio e Benchmark (dal {common_dates[0].strftime("%Y-%m-%d")} al {common_dates[-1].strftime("%Y-%m-%d")})',
        xaxis_title='Data',
        yaxis_title='Valore Normalizzato',
        legend_title='Titoli',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    # Calcolo dei rolling returns
    returns = pd.DataFrame({ticker: data.pct_change().dropna() for ticker, data in data_dict.items()})

    def filter_dates(returns, window):
        rolling_returns = returns.rolling(window=window).apply(lambda x: (1 + x).prod() - 1)
        return rolling_returns.dropna()

    # Crea l'istogramma con i ritorni degli asset
    returns_data = [returns[col] for col in returns.columns]
    histogram_fig = create_returns_histogram(returns_data, [col for col in returns.columns])

    # Crea il grafico per la finestra temporale selezionata
    rolling_returns_fig = go.Figure()

    for ticker in data_dict.keys():
        rolling_return = filter_dates(returns[ticker], rolling_window)

        if rolling_return.empty:
            rolling_returns_fig = create_empty_warning_fig(f"Rolling Return ({rolling_window // 252} Anni)")
        else:
            rolling_returns_fig.add_trace(go.Scatter(
                x=rolling_return.index,
                y=rolling_return,
                mode='lines',
                name=f'{ticker} ({rolling_window // 252} Anni)'
            ))

    # Aggiorna layout per il grafico rolling
    rolling_returns_fig.update_layout(
        title=f'Rolling Return su {rolling_window // 252} Anni',
        xaxis_title='Data',
        yaxis_title='Ritorno Rolling',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    rolling_returns_fig.update_xaxes(gridcolor='#3C3C3C')
    rolling_returns_fig.update_yaxes(gridcolor='#3C3C3C')

    characteristics = {}
    for ticker, data in data_dict.items():
        cagr, volatility, down_volatility, sharpe, sortino = calculate_asset_characteristics(data)
        characteristics[ticker] = {
            'CAGR': cagr,
            'Annualized Volatility': volatility,
            'Downward Volatility': down_volatility,
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino
        }

    # Create the characteristics histogram
    fig_characteristics = make_subplots(rows=1, cols=5, subplot_titles=('CAGR', 'Annualized Volatility', 'Downward Volatility', 'Sharpe Ratio', 'Sortino Ratio'))

    tickers = list(characteristics.keys())
    cagr_values = [char['CAGR'] for char in characteristics.values()]
    volatility_values = [char['Annualized Volatility'] for char in characteristics.values()]
    down_volatility_values = [char['Downward Volatility'] for char in characteristics.values()]
    sharpe_values = [char['Sharpe Ratio'] for char in characteristics.values()]
    sortino_values = [char['Sortino Ratio'] for char in characteristics.values()]

    fig_characteristics.add_trace(go.Bar(x=tickers, y=cagr_values, name='CAGR'), row=1, col=1)
    fig_characteristics.add_trace(go.Bar(x=tickers, y=volatility_values, name='Annualized Volatility'), row=1, col=2)
    fig_characteristics.add_trace(go.Bar(x=tickers, y=down_volatility_values, name='Downward Volatility'), row=1, col=3)
    fig_characteristics.add_trace(go.Bar(x=tickers, y=sharpe_values, name='Sharpe Ratio'), row=1, col=4)
    fig_characteristics.add_trace(go.Bar(x=tickers, y=sortino_values, name='Sortino Ratio'), row=1, col=5)

    fig_characteristics.update_layout(
        title='Asset Characteristics',
        showlegend=False,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        height=600  # Aumentiamo l'altezza per adattarci a più grafici
    )
    fig_characteristics.update_xaxes(gridcolor='#3C3C3C')
    fig_characteristics.update_yaxes(gridcolor='#3C3C3C')

    drawdown_fig = go.Figure()

    for ticker, data in data_dict.items():
        drawdown = calculate_drawdown(data)
        drawdown_fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown,
            name=ticker,
            mode='lines'
        ))

    drawdown_fig.update_layout(
        title='Drawdown',
        xaxis_title='Data',
        yaxis_title='Drawdown',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    drawdown_fig.update_xaxes(gridcolor='#3C3C3C')
    drawdown_fig.update_yaxes(gridcolor='#3C3C3C')

    return fig, rolling_returns_fig, histogram_fig,fig_characteristics, drawdown_fig

@app.callback(
    [Output('efficient-frontier-graph', 'figure'),
     Output('optimal-portfolio-performance-graph', 'figure'),
     Output('pie-charts', 'children'),
     Output('comparison-chart', 'figure'),
     Output('rolling-return-graph', 'figure')],
    [Input('efficient-frontier-button', 'n_clicks')],
    [State('portfolio-table', 'data'),
     State('benchmark-table', 'data'),
     State('start-date-picker', 'date'),
     State('end-date-picker', 'date')]
)
def calculate_efficient_frontier(n_clicks, rows, benchmark_rows, start_date, end_date):
    if not rows or not start_date or not end_date or n_clicks == 0:
        # Restituisci figure vuote e liste vuote se non ci sono dati
        empty_fig = go.Figure()
        return empty_fig, empty_fig, [], empty_fig,empty_fig

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Scarichiamo i dati per tutti gli asset
    data_dict = {}
    for row in rows:
        ticker = row['ticker']
        data = yf.download(ticker, start=start_date, end=end_date)
        data_dict[ticker] = data['Close']

    # Scarichiamo i dati per il benchmark
    if not benchmark_rows:
        benchmark_rows = [{'benchmark': '^GSPC'}]

    # Scarichiamo i dati per il benchmark
    benchmark_data = {}
    for row in benchmark_rows:
        benchmark = row['benchmark']
        data = yf.download(benchmark, start=start_date, end=end_date)
        benchmark_data[benchmark] = data['Close']

    # Troviamo la prima data in comune
    common_data = pd.concat(data_dict.values(), axis=1).dropna()
    if common_data.empty:
        return go.Figure()  # Non ci sono date in comune

    common_data.columns = [row['ticker'] for row in rows]
    returns = common_data.resample('Y').last().pct_change().dropna()

    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_portfolios = 10000
    results = np.zeros((4, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(len(rows))
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_return = np.dot(weights, mean_returns) * 12
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        results[2,i] = results[0,i] / results[1,i]
        results[3,i] = np.dot(weights, mean_returns)

    max_sharpe_idx = np.argmax(results[2])
    min_std_dev_idx = np.argmin(results[1])
    max_return_idx = np.argmax(results[0])

    # Calculate the current portfolio return and std dev
    current_weights = np.array([float(row['percentage']) / 100 for row in rows])
    current_return = np.dot(current_weights, mean_returns) * 12
    current_std_dev = np.sqrt(np.dot(current_weights.T, np.dot(cov_matrix, current_weights))) * np.sqrt(252)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=results[1],
        y=results[0],
        mode='markers',
        marker=dict(
            color=results[2],
            colorscale='Viridis',
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        )
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,max_sharpe_idx]],
        y=[results[0,max_sharpe_idx]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='diamond'),
        name='Max Sharpe Ratio'
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,min_std_dev_idx]],
        y=[results[0,min_std_dev_idx]],
        mode='markers',
        marker=dict(color='blue', size=10, symbol='diamond'),
        name='Min Volatility'
    ))

    fig.add_trace(go.Scatter(
        x=[results[1,max_return_idx]],
        y=[results[0,max_return_idx]],
        mode='markers',
        marker=dict(color='green', size=10, symbol='diamond'),
        name='Max Return'
    ))

    fig.add_trace(go.Scatter(
        x=[current_std_dev],
        y=[current_return],
        mode='markers',
        marker=dict(color='magenta', size=10, symbol='diamond'),
        name='Current Portfolio'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Rischio/Volatilità',
        yaxis_title='Ritorno',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    max_sharpe_weights = weights_record[max_sharpe_idx]
    min_vol_weights = weights_record[min_std_dev_idx]
    max_return_weights = weights_record[max_return_idx]
    current_weights = np.array([float(row['percentage']) / 100 for row in rows])

    ef_fig = create_efficient_frontier_graph(results, max_sharpe_idx, min_std_dev_idx, max_return_idx, current_std_dev,
                                             current_return)
    perf_fig = create_optimal_portfolio_performance_graph(common_data, max_sharpe_weights, min_vol_weights,
                                                          max_return_weights, current_weights, rows, benchmark_data)
    period_length = (end_date - start_date).days
    if period_length > 252 * 2:
        roll_fig = create_rolling_return_graph(common_data, max_sharpe_weights, min_vol_weights,
                                                          max_return_weights, current_weights, benchmark_data, start_date, end_date)
    else:
        roll_fig = go.Figure()

    pie_charts = create_pie_charts(rows, max_sharpe_weights, min_vol_weights, max_return_weights, current_weights)

    portfolio_data = {}
    portfolios = {
        'Max Sharpe': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights,
        'Current Portfolio': current_weights
    }

    risk_free_rate = 0.02  # Assume a 2% risk-free rate, you may want to make this dynamic

    for name, weights in portfolios.items():
        portfolio_return = (common_data * weights).sum(axis=1)
        cagr = calculate_cagr(portfolio_return)
        annualized_volatility = calculate_annualized_volatility(portfolio_return)
        annualized_down_volatility = calculate_annualized_down_volatility(portfolio_return)
        sharpe_ratio = (cagr - risk_free_rate) / annualized_volatility
        sortino = (cagr - risk_free_rate) / annualized_down_volatility
        portfolio_data[name] = {'CAGR': cagr, 'Volatility': annualized_volatility, 'Sharpe Ratio': sharpe_ratio, 'Downside Volatility': annualized_down_volatility, 'Sortino Ratio': sortino}

    # Calculate CAGR, Volatility, and Sharpe Ratio for the benchmark
    benchmark_name = benchmark_rows[0]['benchmark']  # Assume there's only one benchmark
    benchmark_return = benchmark_data[benchmark_name]
    benchmark_cagr = calculate_cagr(benchmark_return)
    benchmark_volatility = calculate_annualized_volatility(benchmark_return)
    benchmark_down_volatility = calculate_annualized_down_volatility(benchmark_return)
    benchmark_sharpe_ratio = (benchmark_cagr - risk_free_rate) / benchmark_volatility
    sortino = (benchmark_cagr - risk_free_rate) / benchmark_down_volatility
    benchmark_data = {
        'CAGR': benchmark_cagr,
        'Volatility': benchmark_volatility,
        'Sharpe Ratio': benchmark_sharpe_ratio,
        'Downside Volatility': benchmark_down_volatility,
        'Sortino Ratio': sortino
    }

    comparison_fig = create_comparison_chart(portfolio_data, benchmark_data)

    return ef_fig, perf_fig, pie_charts, comparison_fig, roll_fig

def calculate_cagr(data):
    start_value = data.iloc[0]
    end_value = data.iloc[-1]
    n_years = len(data) / 252  # Assumendo 252 giorni di trading all'anno
    cagr = (end_value / start_value) ** (1 / n_years) - 1
    return cagr

def calculate_annualized_volatility(returns):
    """
    Calcola la volatilità annualizzata dei ritorni annualizzati.
    """
    annual_returns = returns.resample('Y').last().pct_change().dropna()
    annual_volatility = annual_returns.std()
    return annual_volatility

def calculate_annualized_down_volatility(returns):
    """
    Calcola la volatilità annualizzata dei ritorni annualizzati.
    """
    annual_returns = returns.resample('Y').last().pct_change().dropna()
    annual_returns = annual_returns[annual_returns < 0]
    annual_volatility = annual_returns.std()
    return annual_volatility


def create_comparison_chart(portfolio_data, benchmark_data):
    portfolios = list(portfolio_data.keys()) + ['Benchmark']
    metrics = ['CAGR', 'Volatility', 'Sharpe Ratio', 'Downside Volatility', 'Sortino Ratio']

    # Define colors for each portfolio and the benchmark
    colors = ['red', 'blue', 'green', 'purple', 'orange']

    # Create subplots: one subplot for each metric, each with its own y-axis
    fig = make_subplots(rows=1, cols=len(metrics), shared_xaxes=False, subplot_titles=metrics)

    for i, metric in enumerate(metrics):
        for j, portfolio in enumerate(portfolios):
            data = portfolio_data[portfolio] if portfolio != 'Benchmark' else benchmark_data
            fig.add_trace(
                go.Bar(
                    name=portfolio,
                    x=[portfolio],
                    y=[data[metric]],
                    marker_color=colors[j % len(colors)],
                    showlegend=True if i == 0 else False  # Show legend only once
                ),
                row=1, col=i + 1
            )

    fig.update_layout(
        title='Confronto CAGR, Volatilità, Sharpe Ratio, Volatilità negativa e Sortino Ratio (incluso Benchmark)',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        barmode='group',
        legend=dict(
            itemclick="toggleothers",  # Allow toggling visibility of all items except the clicked one
            itemdoubleclick="toggle"  # Allow toggling visibility of the clicked item
        ),
        showlegend=False  # Hide the legend
    )

    # Update grid colors and background colors
    for i in range(len(metrics)):
        fig.update_xaxes(title_text='Portafogli', row=1, col=i + 1, gridcolor='#3C3C3C')
        fig.update_yaxes(title_text='Valore', row=1, col=i + 1, gridcolor='#3C3C3C')

    return fig
def calculate_sharpe_ratio(returns, risk_free_rate):
    """
    Calcola lo Sharpe Ratio.
    """
    excess_returns = returns - risk_free_rate
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_sortino_ratio(returns, risk_free_rate):
    """
    Calcola il Sortino Ratio.
    """
    excess_returns = returns - risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

def create_pie_charts(rows, max_sharpe_weights, min_vol_weights, max_return_weights, current_weights):
    tickers = [row['ticker'] for row in rows]

    # Definiamo una lista di colori per ogni asset
    color_map = {
        'Current Portfolio': 'blue',
        'Max Sharpe Ratio': 'red',
        'Min Volatility': 'green',
        'Max Return': 'purple'
    }
    # Generiamo colori unici per gli asset
    colors = px.colors.qualitative.Plotly[:len(tickers)]

    pie_charts = []
    portfolios = {
        'Current Portfolio': current_weights,
        'Max Sharpe Ratio': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights
    }

    for name, weights in portfolios.items():
        pie = dcc.Graph(
            figure=go.Figure(data=[go.Pie(
                labels=tickers,
                values=weights,
                textinfo='label+percent',
                insidetextorientation='radial',
                marker=dict(colors=colors)  # Associa colori agli asset
            )]),
            style={'width': '25%', 'display': 'inline-block'},
            config={'displayModeBar': False}
        )
        pie.figure.update_layout(
            title=name,
            paper_bgcolor='#1E1E1E',
            plot_bgcolor='#1E1E1E',
            font=dict(color='#FFFFFF')
        )
        pie_charts.append(pie)

    return pie_charts


def create_efficient_frontier_graph(results, max_sharpe_idx, min_std_dev_idx, max_return_idx, current_std_dev, current_return):
    fig = go.Figure()

    # Scatter plot per tutti i portafogli
    fig.add_trace(go.Scatter(
        x=results[1],
        y=results[0],
        mode='markers',
        marker=dict(
            color=results[2],
            colorscale='Viridis',
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        ),
        name='Portafogli'
    ))

    # Punto per il portafoglio con massimo Sharpe Ratio
    fig.add_trace(go.Scatter(
        x=[results[1,max_sharpe_idx]],
        y=[results[0,max_sharpe_idx]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='diamond'),
        name='Max Sharpe Ratio'
    ))

    # Punto per il portafoglio con minima volatilità
    fig.add_trace(go.Scatter(
        x=[results[1,min_std_dev_idx]],
        y=[results[0,min_std_dev_idx]],
        mode='markers',
        marker=dict(color='blue', size=10, symbol='diamond'),
        name='Min Volatility'
    ))

    # Punto per il portafoglio con massimo ritorno
    fig.add_trace(go.Scatter(
        x=[results[1,max_return_idx]],
        y=[results[0,max_return_idx]],
        mode='markers',
        marker=dict(color='green', size=10, symbol='diamond'),
        name='Max Return'
    ))

    # Punto per il portafoglio corrente
    fig.add_trace(go.Scatter(
        x=[current_std_dev],
        y=[current_return],
        mode='markers',
        marker=dict(color='magenta', size=10, symbol='diamond'),
        name='Current Portfolio'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Rischio/Volatilità',
        yaxis_title='Ritorno',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig

def create_optimal_portfolio_performance_graph(data, max_sharpe_weights, min_vol_weights, max_return_weights,
                                               current_weights, rows, benchmark_data):
    fig = go.Figure()

    # Calcola i ritorni giornalieri
    returns = data.pct_change().dropna()

    # Definisce i portafogli e i pesi
    portfolios = {
        'Max Sharpe': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights,
        'Current Portfolio': current_weights
    }

    # Calcola e aggiunge ogni portafoglio al grafico
    for name, weights in portfolios.items():
        # Calcola il ritorno ponderato del portafoglio
        portfolio_return = (returns * weights).sum(axis=1)

        # Normalizza il ritorno per il confronto
        normalized_return = (1 + portfolio_return).cumprod() / (1 + portfolio_return.iloc[0])

        fig.add_trace(go.Scatter(
            x=returns.index,
            y=normalized_return,
            mode='lines',
            name=name
        ))

    # Aggiungi i benchmark
    for benchmark, benchmark_prices in benchmark_data.items():
        normalized_benchmark = benchmark_prices / benchmark_prices.iloc[0]
        fig.add_trace(go.Scatter(
            x=normalized_benchmark.index,
            y=normalized_benchmark,
            mode='lines',
            name=f'Benchmark: {benchmark}',
            line=dict(dash='dash')
        ))

    fig.update_layout(
        title='Performance dei Portafogli Ottimali e Benchmark',
        xaxis_title='Data',
        yaxis_title='Valore Normalizzato',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig

def create_rolling_return_graph(data, max_sharpe_weights, min_vol_weights, max_return_weights,
                                current_weights, benchmark_data, start_date, end_date):
    fig = go.Figure()

    # Calcola i ritorni giornalieri
    returns = data.pct_change().dropna()

    # Definisce i portafogli e i pesi
    portfolios = {
        'Max Sharpe': max_sharpe_weights,
        'Min Volatility': min_vol_weights,
        'Max Return': max_return_weights,
        'Current Portfolio': current_weights
    }

    data_period_length = (end_date - start_date).days
    benchmark_period_length = min((prices.index[-1] - prices.index[0]).days for prices in benchmark_data.values())
    period_length = min(data_period_length, benchmark_period_length)
    rolling_windows = [252, 252*5, 252*10]  # 1 anno, 5 anni, 10 anni
    rolling_windows = [window for window in rolling_windows if window <= period_length/2]  # Filtra le finestre mobili
    window_labels = {252: '1 Anno', 252*5: '5 Anni', 252*10: '10 Anni'}

    # Memorizza le tracce per ciascun portafoglio e benchmark
    all_traces = {window: [] for window in rolling_windows}
    portfolio_dates = {window: [] for window in rolling_windows}

    for window in rolling_windows:
        for name, weights in portfolios.items():
            portfolio_return = (returns * weights).sum(axis=1)
            rolling_return = portfolio_return.dropna().rolling(window=window).apply(lambda x: (1 + x).prod() - 1)

            trace = go.Scatter(
                x=rolling_return.index,
                y=rolling_return,
                mode='lines',
                name=name + f' ({window_labels[window]})'
            )
            all_traces[window].append(trace)
            portfolio_dates[window].append(rolling_return.index)

        for benchmark, benchmark_prices in benchmark_data.items():
            benchmark_returns = benchmark_prices.pct_change().dropna()
            rolling_benchmark_return = benchmark_returns.rolling(window=window).apply(lambda x: (1 + x).prod() - 1).dropna()

            trace = go.Scatter(
                x=rolling_benchmark_return.index,
                y=rolling_benchmark_return,
                mode='lines',
                name=f'Benchmark: {benchmark} ({window_labels[window]})',
                line=dict(dash='dash')
            )
            all_traces[window].append(trace)
            portfolio_dates[window].append(rolling_benchmark_return.index)

    # Trova l'intersezione di tutte le date dei portafogli
    common_dates = {window: set(portfolio_dates[window][0]) for window in rolling_windows}

    for window in rolling_windows:
        for dates in portfolio_dates[window][1:]:
            common_dates[window] = common_dates[window].intersection(set(dates))
        common_dates[window] = sorted(list(common_dates[window]))

    # Aggiungi tracce iniziali (per esempio, per la finestra di 5 anni)
    for trace in all_traces[252]:
        fig.add_trace(trace)

    # Definisce i pulsanti del dropdown
    buttons = []
    for window in rolling_windows:
        buttons.append(dict(
            label=window_labels[window],
            method='update',
            args=[{'visible': [trace in all_traces[window] for window in rolling_windows for trace in all_traces[window]]},
                  {'title': f'Rolling Return su {window_labels[window]} dei Portafogli Ottimali e Benchmark',
                   'xaxis': {'range': [common_dates[window][0], common_dates[window][-1]]}}]
        ))

    # Aggiorna il layout con i pulsanti del dropdown
    fig.update_layout(
        title='Rolling Return su 5 Anni dei Portafogli Ottimali e Benchmark',
        xaxis_title='Data',
        yaxis_title='Ritorno Rolling 5 Anni',
        showlegend=True,
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        updatemenus=[dict(
            buttons=buttons,
            direction='down',
            showactive=True,
        )]
    )

    fig.update_xaxes(gridcolor='#3C3C3C')
    fig.update_yaxes(gridcolor='#3C3C3C')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
