
"""Cumulative profit chart component"""
import plotly.graph_objs as go
from web.helpers import load_transactions

def create_profit_chart():
    transactions = load_transactions()

    if transactions.empty or 'Profit' not in transactions.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No transaction data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    fig = go.Figure()

    for ea_name in transactions['EA_Name'].unique():
        ea_trans = transactions[transactions['EA_Name'] == ea_name].copy()
        ea_trans = ea_trans.sort_values('TimeOpen')
        ea_trans['CumulativeProfit'] = ea_trans['Profit'].cumsum()

        fig.add_trace(go.Scatter(
            x=ea_trans['TimeOpen'],
            y=ea_trans['CumulativeProfit'],
            mode='lines+markers',
            name=ea_name,
            line=dict(width=2)
        ))

    fig.update_layout(
        title="Cumulative Profit by EA",
        xaxis_title="Date",
        yaxis_title="Cumulative Profit ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig
