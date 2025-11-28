
"""EA analysis table component"""
import dash_bootstrap_components as dbc
import pandas as pd
from web.helpers import load_transactions

def create_ea_analysis_table():
    transactions = load_transactions()

    if transactions.empty:
        return dbc.Alert("No transaction data available", color="light", className="text-center text-muted")

    rows = []
    for ea_name in transactions['EA_Name'].unique():
        ea_trans = transactions[transactions['EA_Name'] == ea_name]

        total_trades = len(ea_trans)
        winning_trades = (ea_trans['Profit'] > 0).sum()
        losing_trades = (ea_trans['Profit'] < 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades else 0
        total_profit = ea_trans['Profit'].sum()
        avg_profit = ea_trans['Profit'].mean()
        max_profit = ea_trans['Profit'].max()
        max_loss = ea_trans['Profit'].min()

        rows.append({
            'EA Name': ea_name,
            'Total Trades': total_trades,
            'Win Rate (%)': f"{win_rate:.1f}",
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Total Profit ($)': f"{total_profit:,.2f}",
            'Avg Profit ($)': f"{avg_profit:,.2f}",
            'Max Profit ($)': f"{max_profit:,.2f}",
            'Max Loss ($)': f"{max_loss:,.2f}",
        })

    df = pd.DataFrame(rows)
    df = df.sort_values('Total Trades', ascending=False)

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0",
        style={'fontSize': '14px'}
    )
