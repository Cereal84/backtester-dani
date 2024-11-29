import plotly.graph_objects as go

def plot_line_chart(column_except_date, portfolio_df, portfolio_color, benchmark_color, fallback_colors):
    # Line chart for portfolio and assets with enhancements and pastel colors
    portfolio_fig = go.Figure()

    # Loop through columns and assign appropriate colors
    for i, column in enumerate(column_except_date):
        line_color = (
            benchmark_color if "benchmark" in column.lower() else
            portfolio_color if "portfolio" in column.lower() else
            fallback_colors[i % len(fallback_colors)]  # Cycle through fallback colors for others
        )
        portfolio_fig.add_trace(go.Scatter(
            x=portfolio_df["Date"],
            y=portfolio_df[column],
            mode='lines+markers',  # Add markers for better readability
            name=column,
            line=dict(
                color=line_color,  # Assign specific or fallback color
                width=3  # Thicker lines
            ),
            marker=dict(
                size=6,  # Marker size
                symbol='circle'  # Marker shape
            ),
            hovertemplate="<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>"

        ))

    # Update layout for better visuals
    portfolio_fig.update_layout(
        title={
            'text': "Performance del Portafoglio e degli Asset",
            'y': 0.9,  # Vertical alignment of the title
            'x': 0.5,  # Center align the title
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Data",
        yaxis_title="Valore Normalizzato",
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        template='plotly_white',  # Clean background style
        legend=dict(
            title="Legenda",
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.2,  # Position legend below the chart
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=60),  # Balanced margins
        hovermode='x unified'  # Combine hover labels for easier comparison
    )

    return portfolio_fig