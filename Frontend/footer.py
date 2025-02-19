from dash import html
import dash_bootstrap_components as dbc

class Footer:
    @staticmethod
    def create(counter):
        """Creates the footer component with credits and counter."""
        return dbc.Container([
            dbc.Row([
                html.Footer(
                    className="mt-5",
                    style={
                        'width': '100%',
                        'backgroundColor': '#f8f9fa',
                        'borderTop': '1px solid #dee2e6',
                        'padding': '2rem 0',
                    },
                    children=[
                        dbc.Container(
                            fluid=True,
                            style={'maxWidth': '100%', 'paddingLeft': '0', 'paddingRight': '0'},
                            children=[
                                # Container for title and counter
                                html.Div(
                                    style={'position': 'relative'},
                                    children=[
                                        # Centered title
                                        html.Div(
                                            html.H4("By Dani & Dati", className="mb-0"),
                                            className="text-center"
                                        ),
                                        # Absolutely positioned counter
                                        html.Div(
                                            counter.get_counter_component(),
                                            style={
                                                'position': 'absolute',
                                                'right': '20px',
                                                'top': '0'
                                            }
                                        )
                                    ]
                                ),

                                # Content with two separate rows
                                html.Div(
                                    className="text-center",
                                    style={'marginLeft': 'auto', 'marginRight': 'auto', 'maxWidth': '1200px'},
                                    children=[
                                        # First row: Contributors on the same line with separator
                                        dbc.Row([
                                            dbc.Col(
                                                html.Div([
                                                    html.H5("Contributors e Link utili", className="mt-4"),
                                                    html.Div([
                                                        html.Span("Koki", style={'marginRight': '10px'}),
                                                        html.Span("•", style={'marginRight': '10px'}),
                                                        html.Span("Marco Zeuli ", style={'marginRight': '10px'}),
                                                        html.Span("•", style={'marginRight': '10px'}),
                                                        html.Span("Matteo Veroni"),
                                                    ], className="text-muted")
                                                ]),
                                                width="auto",
                                                className="col-12 d-flex justify-content-center"
                                            ),
                                        ]),

                                        # Second row: Links with separator
                                        dbc.Row([
                                            dbc.Col(
                                                html.Div([
                                                    html.A(
                                                        "Codice GitHub",
                                                        href="https://github.com/daniele96l/backtester-dani",
                                                        style={'textDecoration': 'none', 'marginRight': '10px'}
                                                    ),
                                                    html.Span("•", style={'marginRight': '10px'}),  # Separator
                                                    html.A(
                                                        "Informativa sulla privacy",
                                                        href="https://danieleligato-eng.notion.site/Informativa-sulla-privacy-197922846a1680d5bc0fc50711843137",
                                                        target="_blank",
                                                        className="text-primary",
                                                        style={"text-decoration": "none", 'marginRight': '10px'}
                                                    ),
                                                    html.Span("•", style={'marginRight': '10px'}),  # Separator
                                                    html.A(
                                                        "Richiedi un ETF",
                                                        href="https://docs.google.com/spreadsheets/d/15SZ4tBYmEb1fiTOlm2oqrIK6NateE9JOCJaWoM5VtCA/edit?gid=1307392537#gid=1307392537",
                                                        target="_blank",
                                                        className="text-primary",
                                                        style={'textDecoration': 'none', 'marginRight': '10px'}
                                                    ),
                                                    html.Span("•", style={'marginRight': '10px'}),  # Separator
                                                    html.A(
                                                        "Supporta il progetto",
                                                        href="https://www.paypal.com/donate/?hosted_button_id=M378MEXMSSQT6",
                                                        target="_blank",
                                                        className="text-primary",
                                                        style={'textDecoration': 'none'}
                                                    ),
                                                ]),
                                                width="auto",
                                                className="col-12 d-flex justify-content-center"
                                            ),
                                        ]),
                                    ]
                                ),
                            ]
                        )
                    ],
                )
            ], className='mt-5'),
        ], fluid=True)
